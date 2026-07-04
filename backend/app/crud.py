from typing import Any, Type

from fastapi import HTTPException, status
from sqlalchemy import String, asc, cast, desc, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.services import model_to_dict, write_audit


MODEL_CONFIG = {
    "systems": {
        "model": models.System,
        "id": "system_id",
        "search": ["name", "ip_address", "department"],
        "sort": ["system_id", "name", "department", "status", "criticality"],
    },
    "users": {
        "model": models.User,
        "id": "user_id",
        "search": ["username", "name", "contact", "role"],
        "sort": ["user_id", "username", "name", "role", "created_at"],
    },
    "incidents": {
        "model": models.Incident,
        "id": "incident_id",
        "search": ["type", "severity", "status", "description"],
        "sort": ["incident_id", "date", "type", "severity", "status"],
    },
    "logs": {
        "model": models.Log,
        "id": "log_id",
        "search": ["event", "source", "severity"],
        "sort": ["log_id", "timestamp", "source", "severity"],
    },
    "vulnerabilities": {
        "model": models.Vulnerability,
        "id": "vuln_id",
        "search": ["description", "severity", "status", "cve", "affected_system"],
        "sort": ["vuln_id", "severity", "status", "cve"],
    },
    "responses": {
        "model": models.Response,
        "id": "response_id",
        "search": ["action_taken", "responder"],
        "sort": ["response_id", "incident_id", "responder", "time_taken", "created_at"],
    },
}


def get_config(entity: str) -> dict[str, Any]:
    return MODEL_CONFIG[entity]


def list_records(
    db: Session,
    entity: str,
    *,
    search: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
    page: int = 1,
    page_size: int = 25,
    filters: dict[str, Any] | None = None,
) -> tuple[list[Any], int]:
    config = get_config(entity)
    model: Type = config["model"]
    query = db.query(model)

    if search:
        clauses = [cast(getattr(model, field), String).ilike(f"%{search}%") for field in config["search"] if hasattr(model, field)]
        if clauses:
            query = query.filter(or_(*clauses))

    for field, value in (filters or {}).items():
        if value not in (None, "") and hasattr(model, field):
            column = getattr(model, field)
            enum_class = getattr(getattr(column, "type", None), "enum_class", None)
            if enum_class:
                value = next(
                    (
                        member
                        for member in enum_class
                        if value in {member.value, member.name}
                    ),
                    value,
                )
            query = query.filter(column == value)

    total = query.count()
    sort_field = sort_by if sort_by in config["sort"] else config["id"]
    sort_column = getattr(model, sort_field)
    query = query.order_by(desc(sort_column) if sort_order.lower() == "desc" else asc(sort_column))
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    return rows, total


def get_record(db: Session, entity: str, record_id: int) -> Any:
    config = get_config(entity)
    model: Type = config["model"]
    row = db.get(model, record_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity[:-1].title()} not found")
    return row


def create_record(db: Session, entity: str, data: dict[str, Any], *, user, ip_address: str | None) -> Any:
    config = get_config(entity)
    model: Type = config["model"]
    row = model(**data)
    try:
        db.add(row)
        db.flush()
        record_id = getattr(row, config["id"])
        write_audit(db, user=user, action="CREATE", entity=entity, entity_id=record_id, after=model_to_dict(row), ip_address=ip_address)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{entity[:-1].title()} conflicts with an existing record") from exc
    db.refresh(row)
    return row


def update_record(db: Session, entity: str, record_id: int, data: dict[str, Any], *, user, ip_address: str | None) -> Any:
    row = get_record(db, entity, record_id)
    before = model_to_dict(row)
    for key, value in data.items():
        setattr(row, key, value)
    try:
        db.flush()
        write_audit(
            db,
            user=user,
            action="UPDATE",
            entity=entity,
            entity_id=record_id,
            before=before,
            after=model_to_dict(row),
            ip_address=ip_address,
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{entity[:-1].title()} conflicts with an existing record") from exc
    db.refresh(row)
    return row


def delete_record(db: Session, entity: str, record_id: int, *, user, ip_address: str | None) -> None:
    row = get_record(db, entity, record_id)
    before = model_to_dict(row)
    db.delete(row)
    write_audit(db, user=user, action="DELETE", entity=entity, entity_id=record_id, before=before, ip_address=ip_address)
    db.commit()
