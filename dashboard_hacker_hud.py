# dashboard_html_hacker.py
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Network Fleet Operations Center</title>
    <style>
        :root {
            --bg-body: #050811; --bg-card: #0a0f24; --bg-inner: #0f1736;
            --text-main: #e2e8f0; --text-muted: #475569; --text-labels: #38bdf8;
            --status-green: #00ff9d; --status-red: #ff3b69; --status-orange: #ff9f1c; --status-blue: #00d2ff;
            --border-subtle: rgba(56, 189, 248, 0.15); --border-glow: rgba(56, 189, 248, 0.3);
            --radius-lg: 4px; --radius-md: 2px;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Courier New', Courier, monospace; background: var(--bg-body); 
            background-image: linear-gradient(rgba(10, 15, 36, 0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(10, 15, 36, 0.3) 1px, transparent 1px);
            background-size: 20px 20px; color: var(--text-main); padding: 24px; min-height: 100vh; position: relative;
        }
        body::before {
            content: " "; display: block; position: fixed; top: 0; left: 0; bottom: 0; right: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%);
            z-index: 9999; background-size: 100% 4px; pointer-events: none;
        }
        .dashboard-container { max-width: 1600px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--border-subtle); padding-bottom: 16px; }
        header h1 { font-size: 24px; font-weight: 900; text-transform: uppercase; letter-spacing: 2px; text-shadow: 0 0 10px rgba(56, 189, 248, 0.6); }
        header p { font-size: 12px; color: var(--text-labels); text-transform: uppercase; }
        .timestamp-badge { background: rgba(0, 210, 255, 0.1); padding: 6px 12px; border-radius: var(--radius-md); font-size: 12px; border: 1px solid var(--status-blue); color: var(--status-blue); box-shadow: 0 0 8px rgba(0, 210, 255, 0.2); }
        .metrics-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }
        .metric-box { padding: 20px; background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); display: flex; align-items: center; gap: 16px; position: relative; }
        .metric-box::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: currentColor; }
        .metric-data .num { font-size: 32px; font-weight: 900; }
        .metric-data .lbl { font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: bold; margin-top: 4px; }
        .main-layout-grid { display: grid; grid-template-columns: 1fr 400px; gap: 20px; align-items: start; }
        @media (max-width: 1200px) { .main-layout-grid { grid-template-columns: 1fr; } }
        .card { background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: 20px; display: flex; flex-direction: column; gap: 16px; position: relative; }
        .card::after { content: ''; position: absolute; top: -1px; right: -1px; width: 10px; height: 10px; border-top: 2px solid var(--text-labels); border-right: 2px solid var(--text-labels); }
        .card-header-group { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-subtle); padding-bottom: 12px; }
        .card-title { font-size: 12px; font-weight: 700; color: #fff; text-transform: uppercase; letter-spacing: 1px; }
        .nodes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); gap: 12px; }
        .node-unit { background: var(--bg-inner); border: 1px solid rgba(255,255,255,0.05); border-radius: var(--radius-md); padding: 14px; display: flex; flex-direction: column; gap: 10px; transition: all 0.2s ease; }
        .node-unit:hover { transform: translateY(-2px); border-color: var(--border-glow); }
        .node-row-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;}
        .node-name { font-size: 14px; font-weight: bold; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .node-ip { font-size: 12px; color: var(--text-labels); }
        .node-details-list { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; background: rgba(0, 0, 0, 0.3); padding: 8px; border-radius: var(--radius-md); font-size: 11px; }
        .nd-item { display: flex; flex-direction: column; }
        .nd-lbl { color: var(--text-muted); font-size: 9px; text-transform: uppercase; }
        .nd-val { font-weight: 500; margin-top: 2px; }
        .badge { font-size: 9px; font-weight: bold; padding: 2px 6px; border-radius: var(--radius-md); text-transform: uppercase; }
        .type-badge { border: 1px solid var(--text-muted); color: var(--text-main); }
        .status-txt-badge { padding: 2px 6px; border-radius: var(--radius-md); font-size: 10px; font-weight: bold; }
        .st-online-b { background: rgba(0, 255, 157, 0.1); color: var(--status-green); border: 1px solid rgba(0, 255, 157, 0.3); }
        .st-offline-b { background: rgba(255, 59, 105, 0.1); color: var(--status-red); border: 1px solid rgba(255, 59, 105, 0.3); animation: pulse 1.5s infinite; }
        .st-sip-b { background: rgba(255, 159, 28, 0.1); color: var(--status-orange); border: 1px solid rgba(255, 159, 28, 0.3); }
        .dot-indicator { width: 10px; height: 10px; border-radius: 50%; display: inline-block; position: relative; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .filter-tab-bar { display: flex; gap: 6px; }
        .tab-btn { background: transparent; border: 1px solid var(--border-subtle); color: var(--text-labels); padding: 6px 14px; font-size: 11px; font-weight: bold; cursor: pointer; text-transform: uppercase; }
        .tab-btn:hover, .tab-btn.active { color: #000; background: var(--status-blue); border-color: var(--status-blue); box-shadow: 0 0 10px rgba(0, 210, 255, 0.4); }
        .data-list-group { display: flex; flex-direction: column; gap: 8px; }
        .info-row { display: flex; justify-content: space-between; align-items: center; font-size: 12px; padding: 8px 4px; border-bottom: 1px dashed rgba(56, 189, 248, 0.1); }
        .info-lbl { color: var(--text-main); font-size: 11px; text-transform: uppercase; opacity: 0.8; }
        .info-val { font-weight: 600; color: var(--status-blue); }
        .wa-log-box { background: #04060e; padding: 12px; border-radius: var(--radius-md); font-size: 11px; line-height: 1.4; color: #a1a1aa; border-left: 4px solid var(--status-orange); word-break: break-all; }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <header>
            <div><h1>Infrastructure Fleet Monitor</h1><p>> System Core Telemetry Node Pipeline View // Matrix Active</p></div>
            <div class="timestamp-badge" id="ui-heartbeat">SYS_SYNC_TIMESTAMP: --:--:--</div>
        </header>
        <div class="metrics-strip">
            <div class="metric-box" style="color: var(--status-blue);"><div class="metric-data"><div id="m-total" class="num">-</div><div class="lbl">Configuration Arrays</div></div></div>
            <div class="metric-box" style="color: var(--status-green);"><div class="metric-data"><div id="m-online" class="num" style="color: var(--status-green);">-</div><div class="lbl">Ping Online Matrix</div></div></div>
            <div class="metric-box" style="color: var(--status-red);"><div class="metric-data"><div id="m-offline" class="num" style="color: var(--status-red);">-</div><div class="lbl">Outage Flag Drops</div></div></div>
            <div class="metric-box" style="color: var(--status-orange);"><div class="metric-data"><div id="m-sip-fail" class="num" style="color: var(--status-orange);">-</div><div class="lbl">SIP Port Reg Dropped</div></div></div>
        </div>
        <div class="main-layout-grid">
            <div class="card">
                <div class="card-header-group">
                    <div class="card-title">// Main Node Core Interface Grid</div>
                    <div class="filter-tab-bar">
                        <button class="tab-btn active" onclick="setFilter('ALL')">All Fleet</button>
                        <button class="tab-btn" onclick="setFilter('VOIP')">VoIP Matrix</button>
                        <button class="tab-btn" onclick="setFilter('CAMERA')">IP Camera Stream</button>
                    </div>
                </div>
                <div id="nodes-container-inject" class="nodes-grid"></div>
            </div>
            <div class="sidebar-stack" style="display: flex; flex-direction: column; gap: 20px;">
                <div class="card">
                    <div class="card-title" style="color: var(--status-orange);">// WhatsApp Automation Node Link</div>
                    <div class="data-list-group">
                        <div class="info-row"><span class="info-lbl">Automation Engine:</span><span id="w-status" class="info-val">—</span></div>
                        <div class="info-row"><span class="info-lbl">Queued Payload Buffers:</span><span id="w-pending" class="info-val" style="color: var(--status-orange);">0</span></div>
                        <div class="info-row"><span class="info-lbl">Total Outage Logs Sent:</span><span id="w-sent" class="info-val">—</span></div>
                        <div style="display: flex; flex-direction: column; gap: 4px; margin-top: 4px;">
                            <span style="font-size: 10px; color: var(--text-muted); text-transform: uppercase;">Raw Message Buffer payload:</span>
                            <div id="w-target" style="font-size:11px; font-weight:700; color:var(--status-blue); font-family:monospace;">—</div>
                            <div id="w-snippet" class="wa-log-box">—</div>
                        </div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">// Thread Runtime Diagnostic Analytics</div>
                    <div class="data-list-group">
                        <div class="info-row"><span class="info-lbl">Executed Processing Loops:</span><span id="d-loops" class="info-val">—</span></div>
                        <div class="info-row"><span class="info-lbl">Calculated Loop Latency:</span><span id="d-duration" class="info-val">—</span></div>
                        <div class="info-row"><span class="info-lbl">Target Main PBX IP Map:</span><span id="d-pbx" class="info-val">—</span></div>
                        <div class="info-row"><span class="info-lbl">Polling File Sync:</span><span id="d-interval" class="info-val">—</span></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        let activeFilter = 'ALL'; let cachedDevices = [];
        function setFilter(type) {
            activeFilter = type;
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.toggle('active', btn.innerText.toUpperCase().includes(type) || (type === 'ALL' && btn.innerText.includes('All')));
            });
            renderCards(cachedDevices);
        }
        function renderCards(devices) {
            let html = '';
            devices.forEach(d => {
                if (activeFilter !== 'ALL' && d.type !== activeFilter) return;
                let ind = d.status === 'OFFLINE' ? 'var(--status-red)' : (d.status.startsWith('SIP') ? 'var(--status-orange)' : 'var(--status-green)');
                let cls = d.status === 'OFFLINE' ? 'st-offline-b' : (d.status.startsWith('SIP') ? 'st-sip-b' : 'st-online-b');
                html += `<div class="node-unit">
                    <div class="node-row-top">
                        <div><div class="node-name">> ${d.name}</div><div class="node-ip">${d.ip}</div></div>
                        <span class="dot-indicator" style="background: ${ind}; box-shadow: 0 0 10px ${ind}; flex-shrink:0;"></span>
                    </div>
                    <div class="node-details-list">
                        <div class="nd-item"><span class="nd-lbl">Device Type</span><span class="nd-val"><span class="badge type-badge">${d.type}</span></span></div>
                        <div class="nd-item"><span class="nd-lbl">Protocol Layer</span><span class="nd-val"><span class="status-txt-badge ${cls}">${d.status}</span></span></div>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px; border-top:1px dashed rgba(56, 189, 248, 0.1); padding-top:8px;">
                        <span style="color:var(--text-muted); font-size:10px; text-transform:uppercase;">[Sec_Comms_Num]:</span>
                        <span style="color:var(--status-blue); font-weight:600;">${d.phone || 'NO_LINK_FLAGGED'}</span>
                    </div>
                </div>`;
            });
            document.getElementById('nodes-container-inject').innerHTML = html || '<div style="padding:20px; color:var(--text-muted); font-size:12px;">// CRITICAL: No matrix entries.</div>';
        }
        async function syncTelemetry() {
            try {
                const response = await fetch('/api/data'); const data = await response.json(); cachedDevices = data.devices;
                document.getElementById('m-total').innerText = data.stats.total;
                document.getElementById('m-online').innerText = data.stats.online;
                document.getElementById('m-offline').innerText = data.stats.offline;
                document.getElementById('m-sip-fail').innerText = data.stats.sip_failures || 0;
                document.getElementById('d-loops').innerText = '#_CYCLES: ' + data.stats.loop_cycle_count;
                document.getElementById('d-duration').innerText = data.stats.scan_duration_ms + ' ms';
                document.getElementById('d-pbx').innerText = data.config.main_pbx_ip;
                document.getElementById('d-interval').innerText = data.config.check_interval + 's rule';
                document.getElementById('w-pending').innerText = data.whatsapp.pending_count;
                document.getElementById('w-sent').innerText = data.whatsapp.sent_count;
                document.getElementById('w-target').innerText = '>> ' + data.whatsapp.last_dispatched_to;
                document.getElementById('w-snippet').innerText = data.whatsapp.last_msg_snippet;
                const statusText = document.getElementById('w-status');
                if (data.whatsapp.pending_count > 0) { statusText.innerText = "● DISPATCHING PAYLOAD"; statusText.style.color = "var(--status-orange)"; }
                else { statusText.innerText = "● STATUS_IDLE"; statusText.style.color = "var(--status-green)"; }
                document.getElementById('ui-heartbeat').innerText = "SYS_SYNC_TIMESTAMP: " + new Date().toLocaleTimeString();
                renderCards(data.devices);
            } catch (error) { console.error("Sync failure", error); }
        }
        setInterval(syncTelemetry, 3000); syncTelemetry();
    </script>
</body>
</html>
"""
