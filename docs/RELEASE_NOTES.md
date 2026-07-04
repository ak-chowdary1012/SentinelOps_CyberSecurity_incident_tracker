# Release Notes

## SentinelOps 2.1.0
This release focuses on portfolio polish and enterprise realism.

Highlights:
- Organizational risk score engine.
- SOC status widget.
- Incident timeline.
- Lightweight AI incident summary.
- Users frontend workflow.
- Improved UI states: skeleton loaders, empty states, update mode, pagination, improved login, polished dashboard cards.
- Expanded verification and documentation set.

Compatibility:
- Existing CRUD, auth, RBAC, reports, dashboard, and audit features remain intact.

Verification:
```text
python -m pytest -q -> 4 passed
node --check frontend/pages/app.js -> passed
```
