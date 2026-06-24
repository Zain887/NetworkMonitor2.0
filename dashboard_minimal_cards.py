# dashboard_html_minimal.py
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Fleet Center</title>
    <style>
        :root {
            --bg-body: #0b0e14;
            --bg-card: #131722;
            --bg-inner: #1c2130;
            --text-main: #f0f3f8;
            --text-muted: #707e94;
            --status-green: #22c55e;
            --status-red: #ef4444;
            --status-orange: #f97316;
            --status-blue: #3b82f6;
            --border-subtle: #202637;
            --radius: 12px;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg-body); color: var(--text-main); padding: 24px; min-height: 100vh;
        }
        .dashboard-container { max-width: 1400px; margin: 0 auto; display: flex; flex-direction: column; gap: 24px; }
        header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
        header h1 { font-size: 24px; font-weight: 600; }
        header p { font-size: 14px; color: var(--text-muted); margin-top: 2px; }
        .metrics-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
        .metric-box { padding: 16px; background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius); display: flex; align-items: center; gap: 16px; }
        .metric-box .icon { font-size: 24px; width: 48px; height: 48px; background: var(--bg-inner); border-radius: 50%; display: flex; align-items: center; justify-content: center; }
        .metric-data .num { font-size: 28px; font-weight: 700; line-height: 1.2; }
        .metric-data .lbl { font-size: 12px; color: var(--text-muted); font-weight: 500; }
        .main-layout-grid { display: grid; grid-template-columns: 1fr 340px; gap: 24px; align-items: start; }
        @media (max-width: 1024px) { .main-layout-grid { grid-template-columns: 1fr; } }
        .card { background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius); padding: 20px; display: flex; flex-direction: column; gap: 16px; }
        .card-title { font-size: 14px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px; }
        .nodes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
        .node-unit { background: var(--bg-inner); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 14px; display: flex; justify-content: space-between; align-items: center; }
        .node-details { display: flex; flex-direction: column; gap: 4px; overflow: hidden; }
        .node-name { font-size: 14px; font-weight: 600; color: var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .node-ip { font-family: monospace; font-size: 12px; color: var(--text-muted); }
        .node-phone { font-size: 11px; color: var(--status-blue); margin-top: 2px; }
        .node-meta { text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
        .badge { font-size: 10px; font-weight: 700; padding: 4px 8px; border-radius: 4px; text-transform: uppercase; }
        .type-badge { background: rgba(255,255,255,0.05); color: var(--text-muted); }
        .dot-indicator { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
        .filter-tab-bar { display: flex; gap: 8px; border-bottom: 1px solid var(--border-subtle); padding-bottom: 12px; flex-wrap: wrap; }
        .tab-btn { background: transparent; border: none; color: var(--text-muted); padding: 6px 12px; font-size: 13px; font-weight: 600; cursor: pointer; border-radius: 6px; transition: 0.15s; white-space: nowrap; }
        .tab-btn:hover, .tab-btn.active { color: var(--text-main); background: var(--bg-inner); }
        .wa-info-row { display: flex; justify-content: space-between; font-size: 13px; padding-bottom: 8px; border-bottom: 1px solid var(--bg-inner); }
        .wa-log-box { background: var(--bg-inner); padding: 12px; border-radius: 6px; font-size: 12px; font-family: monospace; line-height: 1.4; color: var(--text-main); border-left: 3px solid var(--status-orange); word-break: break-all; }
        .diag-line { display: flex; justify-content: space-between; font-size: 13px; }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <header>
            <div>
                <h1>Network Fleet Center</h1>
                <p>Live health monitoring system status overview</p>
            </div>
        </header>
        <div class="metrics-strip">
            <div class="metric-box"><div class="icon" style="color: var(--status-blue);">📑</div><div class="metric-data"><div id="m-total" class="num">-</div><div class="lbl">Total Monitored Nodes</div></div></div>
            <div class="metric-box"><div class="icon" style="color: var(--status-green);">📡</div><div class="metric-data"><div id="m-online" class="num" style="color: var(--status-green);">-</div><div class="lbl">Active Online Systems</div></div></div>
            <div class="metric-box"><div class="icon" style="color: var(--status-red);">⚠️</div><div class="metric-data"><div id="m-offline" class="num" style="color: var(--status-red);">-</div><div class="lbl">Outage Flag Drops</div></div></div>
        </div>
        <div class="main-layout-grid">
            <div class="card">
                <div class="filter-tab-bar">
                    <button class="tab-btn active" onclick="setFilter('ALL')">All Devices</button>
                    <button class="tab-btn" onclick="setFilter('VOIP')">VoIP Subsystems</button>
                    <button class="tab-btn" onclick="setFilter('CAMERA')">Camera Nodes</button>
                    <button class="tab-btn" onclick="setFilter('OFFLINE')" style="color: var(--status-red);">Offline Terminals</button>
                </div>
                <div id="nodes-container-inject" class="nodes-grid"></div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 24px;">
                <div class="card">
                    <div class="card-title" style="color: var(--status-green);">💬 WhatsApp Alert Queue</div>
                    <div class="wa-info-row"><span style="color: var(--text-muted);">Queue Running:</span><span id="w-status" style="font-weight:600;">-</span></div>
                    <div class="wa-info-row"><span style="color: var(--text-muted);">Pending Alerts:</span><span id="w-pending" style="color: var(--status-orange); font-weight:700;">-</span></div>
                    <div class="wa-info-row"><span style="color: var(--text-muted);">Dispatched Counter:</span><span id="w-sent" style="font-weight:600;">-</span></div>
                    <div style="display: flex; flex-direction: column; gap: 6px; margin-top: 4px;">
                        <span style="font-size: 12px; font-weight:600; color: var(--text-muted);">Last Failure Target Notice:</span>
                        <div id="w-target" style="font-size: 12px; font-weight: 600; color: var(--status-blue);">-</div>
                        <div id="w-snippet" class="wa-log-box">-</div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">⚙️ Engine Variables</div>
                    <div class="diag-line"><span style="color:var(--text-muted);">Loop Runs:</span><span id="d-loops" style="font-weight:600;">-</span></div>
                    <div class="diag-line"><span style="color:var(--text-muted);">Latency Overhead:</span><span id="d-duration" style="font-weight:600;">-</span></div>
                    <div class="diag-line"><span style="color:var(--text-muted);">Main PBX Gateway:</span><span id="d-pbx" style="font-family:monospace; color:var(--status-blue);">-</span></div>
                    <div class="diag-line"><span style="color:var(--text-muted);">Refresh Ruleset:</span><span id="d-interval" style="font-weight:600;">-</span></div>
                </div>
            </div>
        </div>
    </div>
    <script>
        let activeFilter = 'ALL'; let cachedDevices = [];
        function setFilter(type) {
            activeFilter = type;
            document.querySelectorAll('.tab-btn').forEach(btn => {
                // Modified active state assignment logic to reliably match exact internal filter variables
                let matches = false;
                if (type === 'ALL' && btn.innerText.includes('All')) matches = true;
                else if (type === 'VOIP' && btn.innerText.includes('VoIP')) matches = true;
                else if (type === 'CAMERA' && btn.innerText.includes('Camera')) matches = true;
                else if (type === 'OFFLINE' && btn.innerText.includes('Offline')) matches = true;
                btn.classList.toggle('active', matches);
            });
            renderCards(cachedDevices);
        }
        function renderCards(devices) {
            let html = '';
            devices.forEach(d => {
                // Filter handling logic adjusted to cleanly filter by type rules OR specific offline status
                if (activeFilter === 'OFFLINE') {
                    if (d.status !== 'OFFLINE') return;
                } else if (activeFilter !== 'ALL' && d.type !== activeFilter) {
                    return;
                }
                
                let col = d.status === 'OFFLINE' ? 'var(--status-red)' : (d.status.startsWith('SIP') ? 'var(--status-orange)' : 'var(--status-green)');
                html += `<div class="node-unit" style="border-left: 3px solid ${col};">
                    <div class="node-details">
                        <div class="node-name">${d.name}</div>
                        <div class="node-ip">${d.ip}</div>
                        <div class="node-phone">${d.phone || '—'}</div>
                    </div>
                    <div class="node-meta">
                        <span class="dot-indicator" style="background: ${col}; box-shadow: 0 0 6px ${col};"></span>
                        <span class="badge type-badge">${d.type}</span>
                    </div>
                </div>`;
            });
            document.getElementById('nodes-container-inject').innerHTML = html || '<div style="padding:16px; color:var(--text-muted); font-size:13px;">No devices matching selection.</div>';
        }
        async function syncTelemetry() {
            try {
                const response = await fetch('/api/data'); const data = await response.json(); cachedDevices = data.devices;
                document.getElementById('m-total').innerText = data.stats.total;
                document.getElementById('m-online').innerText = data.stats.online;
                document.getElementById('m-offline').innerText = data.stats.offline;
                document.getElementById('d-loops').innerText = data.stats.loop_cycle_count;
                document.getElementById('d-duration').innerText = data.stats.scan_duration_ms + ' ms';
                document.getElementById('d-pbx').innerText = data.config.main_pbx_ip;
                document.getElementById('d-interval').innerText = data.config.check_interval + 's rule';
                document.getElementById('w-pending').innerText = data.whatsapp.pending_count;
                document.getElementById('w-sent').innerText = data.whatsapp.sent_count;
                document.getElementById('w-target').innerText = data.whatsapp.last_dispatched_to;
                document.getElementById('w-snippet').innerText = data.whatsapp.last_msg_snippet;
                const statusText = document.getElementById('w-status');
                if (data.whatsapp.pending_count > 0) { statusText.innerText = "TRANSMITTING FAILURE ALERT"; statusText.style.color = "var(--status-orange)"; }
                else { statusText.innerText = "STANDBY - ACTIVE LINK"; statusText.style.color = "var(--status-green)"; }
                renderCards(data.devices);
            } catch (error) { console.error("Sync error:", error); }
        }
        setInterval(syncTelemetry, 4000); syncTelemetry();
    </script>
</body>
</html>
"""