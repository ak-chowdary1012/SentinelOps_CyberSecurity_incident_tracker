import html
import io
import zipfile

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.crud import list_records
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.services import model_to_dict, rows_to_csv, sanitize_export_row


router = APIRouter(prefix="/reports", tags=["Reports"])
EXPORTABLE = {"incidents", "logs", "vulnerabilities", "responses"}


def build_xlsx(rows: list[dict]) -> bytes:
    headers = list(rows[0].keys()) if rows else ["message"]
    records = rows or [{"message": "No records"}]
    sheet_rows = []
    sheet_rows.append(
        "<row>"
        + "".join(f'<c t="inlineStr"><is><t>{html.escape(str(header))}</t></is></c>' for header in headers)
        + "</row>"
    )
    for row in records:
        sheet_rows.append(
            "<row>"
            + "".join(
                f'<c t="inlineStr"><is><t>{html.escape(str(row.get(header, "")))}</t></is></c>'
                for header in headers
            )
            + "</row>"
        )

    workbook_xml = '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheets><sheet name="Report" sheetId="1" r:id="rId1" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/></sheets></workbook>'
    rels_xml = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
    workbook_rels_xml = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'
    content_types_xml = '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>'
    sheet_xml = f'<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{"".join(sheet_rows)}</sheetData></worksheet>'

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml)
        archive.writestr("_rels/.rels", rels_xml)
        archive.writestr("xl/workbook.xml", workbook_xml)
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)
        archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)
    return buffer.getvalue()


def build_pdf(title: str, rows: list[dict]) -> bytes:
    lines = [title, ""]
    for row in rows[:40]:
        lines.append(" | ".join(f"{key}: {value}" for key, value in row.items())[:110])
    if not rows:
        lines.append("No records")

    text_commands = ["BT", "/F1 10 Tf", "50 760 Td"]
    for index, line in enumerate(lines[:45]):
        escaped = str(line).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        if index:
            text_commands.append("0 -16 Td")
        text_commands.append(f"({escaped}) Tj")
    text_commands.append("ET")
    stream = "\n".join(text_commands).encode("latin-1", errors="replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = io.BytesIO()
    pdf.write(b"%PDF-1.4\n")
    offsets = []
    for number, obj in enumerate(objects, start=1):
        offsets.append(pdf.tell())
        pdf.write(f"{number} 0 obj\n".encode())
        pdf.write(obj)
        pdf.write(b"\nendobj\n")
    xref = pdf.tell()
    pdf.write(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets:
        pdf.write(f"{offset:010d} 00000 n \n".encode())
    pdf.write(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    return pdf.getvalue()


@router.get("/{entity}.{fmt}")
def export_report(entity: str, fmt: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    if entity not in EXPORTABLE:
        raise HTTPException(status_code=404, detail="Report not found")
    if fmt not in {"csv", "xlsx", "pdf"}:
        raise HTTPException(status_code=400, detail="Supported formats: csv, xlsx, pdf")

    rows, _total = list_records(db, entity, page=1, page_size=1000)
    data = [sanitize_export_row(model_to_dict(row)) for row in rows]

    if fmt == "csv":
        return Response(
            rows_to_csv(data),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{entity}.csv"'},
        )

    if fmt == "xlsx":
        return Response(
            build_xlsx(data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{entity}.xlsx"'},
        )

    return Response(
        build_pdf(f"{entity.title()} Report", data),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{entity}.pdf"'},
    )
