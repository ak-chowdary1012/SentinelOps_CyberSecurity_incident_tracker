# API Reference

Base URL: `http://127.0.0.1:8000`

## Authentication
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`

## Users
- `GET /users`
- `GET /users/me`
- `GET /users/{user_id}`
- `POST /users`
- `PUT /users/{user_id}`
- `DELETE /users/{user_id}`

## Systems
- `GET /systems`
- `GET /systems/{system_id}`
- `POST /systems`
- `PUT /systems/{system_id}`
- `DELETE /systems/{system_id}`

## Incidents
- `GET /incidents`
- `GET /incidents/{incident_id}`
- `GET /incidents/{incident_id}/timeline`
- `GET /incidents/{incident_id}/ai-summary`
- `POST /incidents`
- `PUT /incidents/{incident_id}`
- `DELETE /incidents/{incident_id}`

## Logs
- `GET /logs`
- `GET /logs/{log_id}`
- `POST /logs`
- `PUT /logs/{log_id}`
- `DELETE /logs/{log_id}`

## Vulnerabilities
- `GET /vulnerabilities`
- `GET /vulnerabilities/{vuln_id}`
- `POST /vulnerabilities`
- `PUT /vulnerabilities/{vuln_id}`
- `DELETE /vulnerabilities/{vuln_id}`

## Responses
- `GET /responses`
- `GET /responses/{response_id}`
- `POST /responses`
- `PUT /responses/{response_id}`
- `DELETE /responses/{response_id}`

## SOC Operations
- `GET /dashboard/metrics`
- `GET /audit-logs`
- `GET /search?q=<term>`
- `GET /reports/{incidents|logs|vulnerabilities|responses}.{csv|xlsx|pdf}`

## Common Query Parameters
- `search`
- `sort_by`
- `sort_order=asc|desc`
- `page`
- `page_size`
- Entity filters such as `severity`, `status`, `department`, `source`, or `role`.
