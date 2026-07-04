CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(30) NOT NULL CHECK (role IN ('Admin', 'SOC Analyst', 'Incident Manager', 'Viewer')),
    contact VARCHAR(150) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE systems (
    system_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45) NOT NULL UNIQUE,
    department VARCHAR(80) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('Online', 'Degraded', 'Offline')),
    criticality VARCHAR(20) NOT NULL CHECK (criticality IN ('Critical', 'High', 'Medium', 'Low'))
);

CREATE TABLE incidents (
    incident_id SERIAL PRIMARY KEY,
    date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    type VARCHAR(80) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    status VARCHAR(30) NOT NULL CHECK (status IN ('Open', 'Investigating', 'Contained', 'Resolved', 'Closed')),
    description TEXT,
    resolved_at TIMESTAMPTZ
);

CREATE TABLE logs (
    log_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event TEXT NOT NULL,
    source VARCHAR(80) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    system_id INTEGER REFERENCES systems(system_id) ON DELETE SET NULL
);

CREATE TABLE vulnerabilities (
    vuln_id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Critical', 'High', 'Medium', 'Low')),
    status VARCHAR(30) NOT NULL CHECK (status IN ('Open', 'In Progress', 'Fixed', 'Risk Accepted')),
    cve VARCHAR(32),
    affected_system VARCHAR(100)
);

CREATE TABLE responses (
    response_id SERIAL PRIMARY KEY,
    incident_id INTEGER NOT NULL REFERENCES incidents(incident_id) ON DELETE CASCADE,
    action_taken TEXT NOT NULL,
    responder VARCHAR(100) NOT NULL,
    time_taken INTEGER NOT NULL CHECK (time_taken >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_logs (
    audit_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    username VARCHAR(50) NOT NULL,
    action VARCHAR(30) NOT NULL,
    entity VARCHAR(80) NOT NULL,
    entity_id VARCHAR(80),
    before_value JSONB,
    after_value JSONB,
    ip_address VARCHAR(45),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE refresh_tokens (
    token_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash VARCHAR(128) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_systems_department ON systems(department);
CREATE INDEX ix_incidents_status_severity ON incidents(status, severity);
CREATE INDEX ix_incidents_date ON incidents(date);
CREATE INDEX ix_logs_timestamp_source ON logs(timestamp, source);
CREATE INDEX ix_vulnerabilities_status_severity ON vulnerabilities(status, severity);
CREATE INDEX ix_responses_incident_id ON responses(incident_id);
CREATE INDEX ix_audit_logs_timestamp_action ON audit_logs(timestamp, action);
CREATE INDEX ix_refresh_tokens_expires_at ON refresh_tokens(expires_at);
