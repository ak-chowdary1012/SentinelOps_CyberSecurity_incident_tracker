INSERT INTO users (username, name, role, contact, hashed_password)
VALUES
('admin', 'SOC Administrator', 'Admin', 'soc-admin@example.com', 'generated-by-application'),
('analyst', 'Maya Rao', 'SOC Analyst', 'maya.rao@example.com', 'generated-by-application');

INSERT INTO systems (name, ip_address, department, status, criticality)
VALUES
('Identity Provider', '10.40.1.10', 'Security', 'Online', 'Critical'),
('Payment API', '10.20.3.15', 'Finance', 'Degraded', 'High'),
('Endpoint Fleet', '10.70.0.21', 'IT', 'Online', 'Medium');

INSERT INTO incidents (date, type, severity, status, description)
VALUES
(NOW() - INTERVAL '6 days', 'Malware', 'Critical', 'Investigating', 'Endpoint beaconing detected from finance subnet.'),
(NOW() - INTERVAL '4 days', 'Phishing', 'High', 'Contained', 'Credential harvesting campaign targeting executives.'),
(NOW() - INTERVAL '2 days', 'Unauthorized Access', 'Medium', 'Resolved', 'Suspicious admin login blocked.');

INSERT INTO logs (timestamp, event, source, severity, system_id)
VALUES
(NOW() - INTERVAL '5 hours', 'Multiple failed MFA challenges', 'identity', 'High', 1),
(NOW() - INTERVAL '3 hours', 'EDR isolated host FIN-022', 'edr', 'Critical', 2),
(NOW() - INTERVAL '1 hour', 'Firewall blocked outbound C2 traffic', 'firewall', 'High', 3);

INSERT INTO vulnerabilities (description, severity, status, cve, affected_system)
VALUES
('Outdated OpenSSL package on payment gateway', 'High', 'In Progress', 'CVE-2023-0286', 'Payment API'),
('Critical identity provider patch pending', 'Critical', 'Open', 'CVE-2024-3094', 'Identity Provider');
