const API = window.API_BASE || (
    ["localhost", "127.0.0.1"].includes(window.location.hostname)
        ? "http://127.0.0.1:8000"
        : "https://sentinelops-cybersecurity-incident.onrender.com"
);
const TOKEN_KEY = "sentinelops_access_token";
const REFRESH_KEY = "sentinelops_refresh_token";
const LEGACY_TOKEN_KEY = "access_token";
const LEGACY_REFRESH_KEY = "refresh_token";

const nav = [
    ["dashboard.html", "SOC Dashboard"],
    ["index.html", "Incidents"],
    ["systems.html", "Systems"],
    ["logs.html", "Logs"],
    ["vulnerabilities.html", "Vulnerabilities"],
    ["responses.html", "Responses"],
    ["users.html", "Users"],
];

const entityConfig = {
    incidents: {
        endpoint: "/incidents",
        id: "incident_id",
        title: "Incidents",
        fields: [
            ["date", "datetime-local", "Detected At"],
            ["type", "text", "Attack Type"],
            ["severity", "select", "Severity", ["Critical", "High", "Medium", "Low"]],
            ["status", "select", "Status", ["Open", "Investigating", "Contained", "Resolved", "Closed"]],
            ["description", "textarea", "Description"],
        ],
        columns: ["incident_id", "date", "type", "severity", "status", "description"],
        filters: [["severity", ["", "Critical", "High", "Medium", "Low"]], ["status", ["", "Open", "Investigating", "Contained", "Resolved", "Closed"]]],
        reports: true,
    },
    systems: {
        endpoint: "/systems",
        id: "system_id",
        title: "Systems",
        fields: [
            ["name", "text", "System Name"],
            ["ip_address", "text", "IP Address"],
            ["department", "text", "Department"],
            ["status", "select", "Health", ["Online", "Degraded", "Offline"]],
            ["criticality", "select", "Criticality", ["Critical", "High", "Medium", "Low"]],
        ],
        columns: ["system_id", "name", "ip_address", "department", "status", "criticality"],
        filters: [["status", ["", "Online", "Degraded", "Offline"]]],
        reports: false,
    },
    logs: {
        endpoint: "/logs",
        id: "log_id",
        title: "Security Events",
        fields: [
            ["timestamp", "datetime-local", "Timestamp"],
            ["event", "textarea", "Event"],
            ["source", "text", "Source"],
            ["severity", "select", "Severity", ["Critical", "High", "Medium", "Low"]],
            ["system_id", "number", "System ID"],
        ],
        columns: ["log_id", "timestamp", "event", "source", "severity", "system_id"],
        filters: [["severity", ["", "Critical", "High", "Medium", "Low"]]],
        reports: true,
    },
    vulnerabilities: {
        endpoint: "/vulnerabilities",
        id: "vuln_id",
        title: "Vulnerabilities",
        fields: [
            ["description", "textarea", "Description"],
            ["severity", "select", "Severity", ["Critical", "High", "Medium", "Low"]],
            ["status", "select", "Status", ["Open", "In Progress", "Fixed", "Risk Accepted"]],
            ["cve", "text", "CVE"],
            ["affected_system", "text", "Affected System"],
        ],
        columns: ["vuln_id", "description", "severity", "status", "cve", "affected_system"],
        filters: [["severity", ["", "Critical", "High", "Medium", "Low"]], ["status", ["", "Open", "In Progress", "Fixed", "Risk Accepted"]]],
        reports: true,
    },
    responses: {
        endpoint: "/responses",
        id: "response_id",
        title: "Incident Responses",
        fields: [
            ["incident_id", "number", "Incident ID"],
            ["action_taken", "textarea", "Action Taken"],
            ["responder", "text", "Responder"],
            ["time_taken", "number", "Time Taken Minutes"],
        ],
        columns: ["response_id", "incident_id", "action_taken", "responder", "time_taken", "created_at"],
        filters: [],
        reports: true,
    },
    users: {
        endpoint: "/users",
        id: "user_id",
        title: "Users",
        fields: [
            ["username", "text", "Username"],
            ["name", "text", "Full Name"],
            ["role", "select", "Role", ["Admin", "SOC Analyst", "Incident Manager", "Viewer"]],
            ["contact", "text", "Contact"],
            ["password", "password", "Password"],
            ["is_active", "select", "Active", ["true", "false"]],
        ],
        columns: ["user_id", "username", "name", "role", "contact", "is_active", "created_at"],
        filters: [["role", ["", "Admin", "SOC Analyst", "Incident Manager", "Viewer"]]],
        reports: false,
    },
};

const pageState = {};
const editState = {};

window.addEventListener("unhandledrejection", (event) => {
    event.preventDefault();
    toast(event.reason?.message || "Unexpected application error", true);
});

function shell(title, description) {
    const current = location.pathname.split("/").pop() || "dashboard.html";
    document.body.innerHTML = `
        <div class="shell">
            <aside class="sidebar">
                <div class="brand">Sentinel<span>Ops</span><sup>&trade;</sup></div>
                <div class="subtitle">Security Operations Center</div>
                <nav class="nav">${nav.map(([href, label]) => `<a class="${href === current ? "active" : ""}" href="${href}">${label}</a>`).join("")}</nav>
                <div class="creator-mark">N V AVINASH KRISHNA</div>
            </aside>
            <main class="main">
                <div class="topbar">
                    <div class="title"><h1>${title}</h1><p>${description}</p></div>
                    <div class="actions">
                        <input id="globalSearch" placeholder="Search telemetry, assets, incidents">
                        <button id="searchBtn" title="Run global search">Search</button>
                        <button id="logoutBtn" title="End current analyst session">Logout</button>
                    </div>
                </div>
                <div id="content"></div>
                <footer class="app-footer">SentinelOps &bull; Designed &amp; Developed by N V Avinash Krishna</footer>
            </main>
        </div>
        <div class="toast" id="toast"></div>
        <div class="login" id="loginOverlay">
            <form class="panel login-card" id="loginForm">
                <div class="brand large">Sentinel<span>Ops</span><sup>&trade;</sup></div>
                <h2>Analyst Sign In</h2>
                <p>Authenticate to view SOC telemetry, incidents, and audit activity.</p>
                <label>Username<input id="loginUsername" value="admin" required></label>
                <label>Password<input id="loginPassword" type="password" value="AdminPass123!" required></label>
                <button type="submit">Sign In</button>
                <small>Demo: admin / AdminPass123!</small>
            </form>
        </div>`;
    document.getElementById("logoutBtn").onclick = logout;
    document.getElementById("searchBtn").onclick = runGlobalSearch;
    document.getElementById("loginForm").onsubmit = login;
    if (!localStorage.getItem(TOKEN_KEY)) showLogin(true);
}

function showLogin(show) {
    document.getElementById("loginOverlay").style.display = show ? "grid" : "none";
}

function toast(message, isError = false) {
    const el = document.getElementById("toast");
    if (!el) {
        console.error(message);
        return;
    }
    el.textContent = message;
    el.style.borderColor = isError ? "rgba(251, 113, 133, .55)" : "rgba(52, 211, 153, .45)";
    el.style.display = "block";
    setTimeout(() => (el.style.display = "none"), 3600);
}

async function api(path, options = {}) {
    const headers = {"Content-Type": "application/json", ...(options.headers || {})};
    const token = localStorage.getItem(TOKEN_KEY) || localStorage.getItem(LEGACY_TOKEN_KEY);
    if (token) headers.Authorization = `Bearer ${token}`;
    let res;
    try {
        res = await fetch(`${API}${path}`, {...options, headers});
    } catch (err) {
        console.error(`API request failed: ${API}${path}`, err);
        throw new Error(`Network error: ${err.message}`);
    }
    if (res.status === 401) {
        showLogin(true);
        throw new Error("Session expired. Sign in again.");
    }
    if (!res.ok) {
        let detail = `Request failed (${res.status})`;
        try {
            const body = await res.json();
            detail = body.detail || detail;
        } catch (_) {}
        throw new Error(Array.isArray(detail) ? detail.map((d) => d.msg).join(", ") : detail);
    }
    if (res.headers.get("content-type")?.includes("application/json")) return res.json();
    return res.blob();
}

async function login(event) {
    event.preventDefault();
    try {
        const data = await api("/auth/login", {
            method: "POST",
            body: JSON.stringify({
                username: document.getElementById("loginUsername").value,
                password: document.getElementById("loginPassword").value,
            }),
        });
        localStorage.setItem(TOKEN_KEY, data.access_token);
        localStorage.setItem(REFRESH_KEY, data.refresh_token);
        localStorage.setItem(LEGACY_TOKEN_KEY, data.access_token);
        localStorage.setItem(LEGACY_REFRESH_KEY, data.refresh_token);
        showLogin(false);
        toast("Signed in");
        window.dispatchEvent(new Event("auth-ready"));
    } catch (err) {
        console.error("Login failed", err);
        toast(err.message, true);
    }
}

async function logout() {
    const refresh = localStorage.getItem(REFRESH_KEY) || localStorage.getItem(LEGACY_REFRESH_KEY);
    try {
        if (refresh) await api("/auth/logout", {method: "POST", body: JSON.stringify({refresh_token: refresh})});
    } catch (_) {}
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(LEGACY_TOKEN_KEY);
    localStorage.removeItem(LEGACY_REFRESH_KEY);
    showLogin(true);
}

async function runGlobalSearch() {
    const q = document.getElementById("globalSearch").value.trim();
    if (!q) return;
    try {
        const data = await api(`/search?q=${encodeURIComponent(q)}`);
        const summary = Object.entries(data).map(([key, value]) => `${key}: ${value.total}`).join(" | ");
        toast(summary || "No matches");
    } catch (err) {
        toast(err.message, true);
    }
}

function formatValue(value) {
    if (value === null || value === undefined || value === "") return "-";
    if (typeof value === "string" && value.includes("T")) return value.replace("T", " ").replace("Z", "");
    return value;
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function renderEntityPage(entity) {
    const cfg = entityConfig[entity];
    pageState[entity] = pageState[entity] || 1;
    shell(cfg.title, "Search, triage, update, export, and audit operational security records.");
    const content = document.getElementById("content");
    content.innerHTML = `
        <section class="panel">
            <form id="entityForm" class="grid form-grid">${cfg.fields.map(fieldInput).join("")}</form>
            <div class="actions">
                <button id="submitBtn" form="entityForm" type="submit">Create Record</button>
                <button id="cancelEditBtn" type="button" style="display:none">Cancel Edit</button>
            </div>
        </section>
        <section class="panel">
            <div class="toolbar">
                <label>Search<input id="entitySearch" placeholder="Search ${cfg.title.toLowerCase()}"></label>
                <label>Sort<select id="sortBy">${cfg.columns.map((c) => `<option value="${c}">${c}</option>`).join("")}</select></label>
                <label>Order<select id="sortOrder"><option value="desc">Desc</option><option value="asc">Asc</option></select></label>
                <div class="actions">
                    <button id="refreshBtn">Refresh</button>
                    ${cfg.reports ? '<button id="csvBtn">CSV</button><button id="xlsxBtn">Excel</button><button id="pdfBtn">PDF</button>' : ""}
                </div>
            </div>
            <div id="filterBar" class="actions">${cfg.filters.map(filterInput).join("")}</div>
            <table><thead><tr>${cfg.columns.map((c) => `<th>${c}</th>`).join("")}<th>Actions</th></tr></thead><tbody id="rows"></tbody></table>
            <div class="pagination">
                <button id="prevPage">Previous</button>
                <span id="pageLabel">Page 1</span>
                <button id="nextPage">Next</button>
            </div>
        </section>`;
    document.getElementById("entityForm").onsubmit = (event) => createEntity(event, entity);
    document.getElementById("cancelEditBtn").onclick = () => clearEdit(entity);
    document.getElementById("refreshBtn").onclick = () => loadEntity(entity);
    document.getElementById("entitySearch").oninput = debounce(() => resetAndLoad(entity), 300);
    document.getElementById("sortBy").onchange = () => resetAndLoad(entity);
    document.getElementById("sortOrder").onchange = () => resetAndLoad(entity);
    if (cfg.reports) {
        document.getElementById("csvBtn").onclick = () => downloadReport(entity, "csv");
        document.getElementById("xlsxBtn").onclick = () => downloadReport(entity, "xlsx");
        document.getElementById("pdfBtn").onclick = () => downloadReport(entity, "pdf");
    }
    document.getElementById("prevPage").onclick = () => changePage(entity, -1);
    document.getElementById("nextPage").onclick = () => changePage(entity, 1);
    document.querySelectorAll("[data-filter]").forEach((el) => (el.onchange = () => resetAndLoad(entity)));
    window.addEventListener("auth-ready", () => loadEntity(entity), {once: true});
    if (localStorage.getItem(TOKEN_KEY)) loadEntity(entity);
}

function fieldInput([name, type, label, options]) {
    if (type === "select") return `<label>${label}<select name="${name}" required>${options.map((o) => `<option value="${o}">${o}</option>`).join("")}</select></label>`;
    if (type === "textarea") return `<label>${label}<textarea name="${name}" required></textarea></label>`;
    return `<label>${label}<input name="${name}" type="${type}" required></label>`;
}

function filterInput([name, options]) {
    return `<label>${name}<select data-filter="${name}">${options.map((o) => `<option value="${o}">${o || "All"}</option>`).join("")}</select></label>`;
}

async function createEntity(event, entity) {
    event.preventDefault();
    const cfg = entityConfig[entity];
    const form = new FormData(event.target);
    const body = {};
    for (const [key, value] of form.entries()) {
        if (value === "") continue;
        body[key] = ["system_id", "incident_id", "time_taken"].includes(key) ? Number(value) : value;
        if (key === "is_active") body[key] = value === "true";
        if (key === "date" || key === "timestamp") body[key] = new Date(value).toISOString();
    }
    if (editState[entity] && body.password === "") delete body.password;
    try {
        const editId = editState[entity];
        await api(editId ? `${cfg.endpoint}/${editId}` : cfg.endpoint, {method: editId ? "PUT" : "POST", body: JSON.stringify(body)});
        clearEdit(entity);
        toast(`${cfg.title} record ${editId ? "updated" : "created"}`);
        loadEntity(entity);
    } catch (err) {
        toast(err.message, true);
    }
}

function resetAndLoad(entity) {
    pageState[entity] = 1;
    loadEntity(entity);
}

function changePage(entity, delta) {
    pageState[entity] = Math.max(1, (pageState[entity] || 1) + delta);
    loadEntity(entity);
}

async function loadEntity(entity) {
    const cfg = entityConfig[entity];
    const rowsEl = document.getElementById("rows");
    rowsEl.innerHTML = `<tr><td colspan="${cfg.columns.length + 1}"><div class="skeleton"></div><div class="skeleton short"></div></td></tr>`;
    const params = new URLSearchParams({
        search: document.getElementById("entitySearch").value,
        sort_by: document.getElementById("sortBy").value,
        sort_order: document.getElementById("sortOrder").value,
        page: String(pageState[entity] || 1),
        page_size: "10",
    });
    document.querySelectorAll("[data-filter]").forEach((el) => {
        if (el.value) params.set(el.dataset.filter, el.value);
    });
    try {
        const rows = await api(`${cfg.endpoint}?${params.toString()}`);
        document.getElementById("pageLabel").textContent = `Page ${pageState[entity] || 1}`;
        document.getElementById("prevPage").disabled = (pageState[entity] || 1) === 1;
        document.getElementById("nextPage").disabled = rows.length < 10;
        rowsEl.innerHTML = rows.length ? rows.map((row) => `
            <tr>
                ${cfg.columns.map((col) => `<td>${col.includes("severity") || col.includes("status") || col.includes("role") ? `<span class="badge">${escapeHtml(formatValue(row[col]))}</span>` : escapeHtml(formatValue(row[col]))}</td>`).join("")}
                <td>
                    <div class="row-actions">
                        <button data-edit="${row[cfg.id]}">Edit</button>
                        ${entity === "incidents" ? `<button data-ai="${row[cfg.id]}">AI</button><button data-timeline="${row[cfg.id]}">Timeline</button>` : ""}
                        <button class="danger" data-delete="${row[cfg.id]}">Delete</button>
                    </div>
                </td>
            </tr>`).join("") : `<tr><td colspan="${cfg.columns.length + 1}"><div class="empty-state">No ${cfg.title.toLowerCase()} match the current view.</div></td></tr>`;
        document.querySelectorAll("[data-delete]").forEach((btn) => {
            btn.onclick = () => deleteEntity(entity, btn.dataset.delete);
        });
        document.querySelectorAll("[data-edit]").forEach((btn) => {
            btn.onclick = () => startEdit(entity, rows.find((row) => String(row[cfg.id]) === btn.dataset.edit));
        });
        document.querySelectorAll("[data-ai]").forEach((btn) => {
            btn.onclick = () => showIncidentInsight(btn.dataset.ai);
        });
        document.querySelectorAll("[data-timeline]").forEach((btn) => {
            btn.onclick = () => showIncidentTimeline(btn.dataset.timeline);
        });
    } catch (err) {
        toast(err.message, true);
    }
}

function startEdit(entity, row) {
    const cfg = entityConfig[entity];
    editState[entity] = row[cfg.id];
    const form = document.getElementById("entityForm");
    cfg.fields.forEach(([name, type]) => {
        const input = form.elements[name];
        if (!input) return;
        if (name === "password") {
            input.required = false;
            input.value = "";
            input.placeholder = "Leave blank to keep current password";
            return;
        }
        const value = row[name];
        input.value = type === "datetime-local" && value ? value.slice(0, 16) : value ?? "";
    });
    document.getElementById("submitBtn").textContent = "Update Record";
    document.getElementById("cancelEditBtn").style.display = "inline-flex";
}

function clearEdit(entity) {
    editState[entity] = null;
    const form = document.getElementById("entityForm");
    if (form) {
        form.reset();
        const password = form.elements.password;
        if (password) {
            password.required = true;
            password.placeholder = "";
        }
    }
    document.getElementById("submitBtn").textContent = "Create Record";
    document.getElementById("cancelEditBtn").style.display = "none";
}

async function showIncidentInsight(incidentId) {
    try {
        const insight = await api(`/incidents/${incidentId}/ai-summary`);
        toast(`${insight.likely_category}: ${insight.summary}`);
    } catch (err) {
        toast(err.message, true);
    }
}

async function showIncidentTimeline(incidentId) {
    try {
        const timeline = await api(`/incidents/${incidentId}/timeline`);
        toast(timeline.events.map((event) => `${event.stage}: ${event.status}`).join(" | "));
    } catch (err) {
        toast(err.message, true);
    }
}

async function deleteEntity(entity, id) {
    const cfg = entityConfig[entity];
    try {
        await api(`${cfg.endpoint}/${id}`, {method: "DELETE"});
        toast(`${cfg.title} record deleted`);
        loadEntity(entity);
    } catch (err) {
        toast(err.message, true);
    }
}

async function downloadReport(entity, fmt) {
    try {
        const blob = await api(`/reports/${entity}.${fmt}`, {headers: {}});
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `${entity}.${fmt}`;
        link.click();
        setTimeout(() => URL.revokeObjectURL(url), 0);
    } catch (err) {
        toast(err.message, true);
    }
}

function debounce(fn, wait) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn(...args), wait);
    };
}

async function renderDashboard() {
    shell("SOC Command Dashboard", "Executive security posture, live incident telemetry, vulnerabilities, and audit activity.");
    document.getElementById("content").innerHTML = `
        <section class="grid soc-grid">
            <div class="panel hero-panel">
                <div class="metric-label">Organizational Risk Score</div>
                <div id="riskScore" class="risk-score">--</div>
                <p id="riskExplanation" class="subtitle"></p>
            </div>
            <div class="panel" id="socStatus"></div>
        </section>
        <section class="grid kpi-grid" id="kpis"></section>
        <section class="grid chart-grid">
            <div class="panel"><h2>Incident Severity</h2><canvas id="severityChart"></canvas></div>
            <div class="panel"><h2>Incident Trend</h2><canvas id="trendChart"></canvas></div>
            <div class="panel"><h2>Vulnerability Distribution</h2><canvas id="vulnChart"></canvas></div>
            <div class="panel"><h2>System Health</h2><canvas id="healthChart"></canvas></div>
            <div class="panel"><h2>Top Attack Types</h2><canvas id="attackChart"></canvas></div>
        </section>
        <section class="grid chart-grid">
            <div class="panel"><h2>Incident Timeline</h2><div class="timeline" id="incidentTimeline"></div></div>
            <div class="panel"><h2>Recent Security Events</h2><div class="timeline" id="events"></div></div>
            <div class="panel"><h2>Recent Activities</h2><div class="timeline" id="activities"></div></div>
        </section>`;
    window.addEventListener("auth-ready", loadDashboard, {once: true});
    if (localStorage.getItem(TOKEN_KEY)) loadDashboard();
}

async function loadDashboard() {
    try {
        const data = await api("/dashboard/metrics");
        const threatClass = data.threat_level === "Critical" ? "threat-critical" : data.threat_level === "Elevated" ? "threat-elevated" : "threat-normal";
        const cards = [
            ["Threat Level", data.threat_level, threatClass, "threat_level"],
            ["Critical Incidents", data.critical_incidents, "", "critical_incidents"],
            ["Open Incidents", data.open_incidents, "", "open_incidents"],
            ["Resolved", data.resolved_incidents, "", "resolved_incidents"],
            ["Avg Resolution", `${data.average_resolution_minutes}m`, "", "average_resolution_minutes"],
            ["Systems Protected", data.systems_protected, "", "systems_protected"],
        ];
        document.getElementById("riskScore").textContent = `${data.organizational_risk_score}/100 ${data.risk_level}`;
        document.getElementById("riskScore").className = `risk-score threat-${data.risk_level.toLowerCase()}`;
        document.getElementById("riskExplanation").textContent = data.risk_explanation;
        document.getElementById("socStatus").innerHTML = `
            <h2>SOC Status</h2>
            <div class="status-grid">
                <div><span>Threat Level</span><strong>${escapeHtml(data.threat_level)}</strong></div>
                <div><span>Alerts Today</span><strong>${data.security_alerts_today}</strong></div>
                <div><span>Analysts Online</span><strong>${data.analysts_online}</strong></div>
                <div><span>Systems Online</span><strong>${data.systems_online}</strong></div>
            </div>`;
        document.getElementById("kpis").innerHTML = cards.map(([label, value, cls = "", key]) => `<div class="card" data-metric="${key}"><div class="metric-label">${label}</div><div class="metric-value ${cls}">${value}</div></div>`).join("");
        chart("severityChart", "doughnut", data.incident_severity);
        chart("trendChart", "line", data.incident_trend);
        chart("vulnChart", "bar", data.vulnerability_distribution);
        chart("healthChart", "doughnut", data.system_health);
        chart("attackChart", "bar", data.top_attack_types);
        document.getElementById("incidentTimeline").innerHTML = data.incident_timeline.map((incident) => `
            <div class="timeline-item">
                <strong>#${incident.incident_id} ${escapeHtml(incident.type)}</strong>
                <div class="timeline-steps">${incident.events.map((event) => `<span class="${event.status === "Complete" ? "done" : ""}">${event.stage}</span>`).join("")}</div>
            </div>`).join("") || '<div class="empty-state">No incident timeline data yet.</div>';
        document.getElementById("events").innerHTML = data.recent_security_events.map((e) => `<div class="timeline-item"><strong>${escapeHtml(e.severity)}</strong> ${escapeHtml(e.event)}<br><span class="subtitle">${escapeHtml(e.source)} | ${escapeHtml(formatValue(e.timestamp))}</span></div>`).join("") || '<div class="empty-state">No recent security events.</div>';
        document.getElementById("activities").innerHTML = data.recent_activities.map((a) => `<div class="timeline-item"><strong>${escapeHtml(a.action)}</strong> ${escapeHtml(a.entity)}<br><span class="subtitle">${escapeHtml(a.username)} | ${escapeHtml(formatValue(a.timestamp))}</span></div>`).join("") || '<div class="empty-state">No recent activity.</div>';
    } catch (err) {
        toast(err.message, true);
    }
}

function chart(id, type, data) {
    if (!window.Chart) return;
    new Chart(document.getElementById(id), {
        type,
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                borderColor: "#D4AF37",
                backgroundColor: ["#D4AF37", "#E7C873", "#8c6f22", "#b94444", "#3f9f78"],
                tension: 0.35,
                borderWidth: 2,
                pointBackgroundColor: "#F1D98A",
                pointBorderColor: "#070707",
            }],
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                legend: {labels: {color: "#f7f4ec"}},
            },
            scales: {
                x: {
                    grid: {color: "rgba(247,244,236,0.08)"},
                    ticks: {color: "rgba(247,244,236,0.62)"},
                },
                y: {
                    grid: {color: "rgba(247,244,236,0.08)"},
                    ticks: {color: "rgba(247,244,236,0.62)"},
                },
            },
        },
    });
}
