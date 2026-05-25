# dashboard_html_soc.py
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOC Cyber Threat & Fleet Operations Center</title>
    <style>
        :root {
            --soc-bg: #04060a; --soc-panel: #090d16; --soc-surface: #0e1424;
            --border-heavy: 1px solid #1e293b; --text-primary: #f8fafc; --text-secondary: #94a3b8;
            --soc-neon-blue: #38bdf8; --soc-neon-green: #22c55e; --soc-neon-orange: #f97316; --soc-neon-red: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: var(--soc-bg); 
            color: var(--text-primary); padding: 16px; height: 100vh; display: flex; flex-direction: column; gap: 16px; overflow: hidden;
        }
        .soc-header-ticker { display: grid; grid-template-columns: 300px 1fr; align-items: center; background: var(--soc-panel); border: var(--border-heavy); padding: 12px 20px; }
        .soc-title h1 { font-size: 14px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; }
        .soc-title p { font-size: 11px; color: var(--soc-neon-blue); font-family: monospace; }
        .soc-ticker-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; padding-left: 20px; border-left: 2px solid var(--border-heavy); }
        .ticker-item { display: flex; align-items: center; justify-content: space-between; font-size: 12px; }
        .ticker-lbl { color: var(--text-secondary); text-transform: uppercase; font-size: 10px; font-weight: 700; }
        .ticker-val { font-family: monospace; font-weight: bold; font-size: 16px; }
        .soc-workspace-grid { flex: 1; display: grid; grid-template-columns: 1fr 340px 380px; gap: 16px; overflow: hidden; }
        @media (max-width: 1400px) { .soc-workspace-grid { grid-template-columns: 1fr 300px; } }
        .soc-panel { background: var(--soc-panel); border: var(--border-heavy); display: flex; flex-direction: column; overflow: hidden; }
        .soc-panel-header { background: rgba(255,255,255,0.02); padding: 12px 16px; border-bottom: var(--border-heavy); display: flex; justify-content: space-between; align-items: center; }
        .soc-panel-title { font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); }
        .soc-panel-body { flex: 1; padding: 16px; overflow-y: auto; }
        .soc-filter-group { display: flex; gap: 4px; }
        .soc-btn { background: var(--soc-surface); border: var(--border-heavy); color: var(--text-secondary); padding: 4px 10px; font-size: 11px; text-transform: uppercase; cursor: pointer; }
        .soc-btn.active { background: rgba(56, 189, 248, 0.1); border-color: var(--soc-neon-blue); color: #fff; }
        .soc-table { width: 100%; border-collapse: collapse; font-size: 12px; }
        .soc-table th { text-align: left; padding: 10px; color: var(--text-secondary); font-size: 10px; text-transform: uppercase; border-bottom: var(--border-heavy); }
        .soc-table td { padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.02); }
        .soc-pill { display: inline-flex; align-items: center; gap: 6px; padding: 2px 8px; font-size: 10px; font-weight: 700; font-family: monospace; border-radius: 2px; }
        .pill-online { background: rgba(34, 197, 94, 0.1); color: var(--soc-neon-green); }
        .pill-offline { background: rgba(239, 68, 68, 0.1); color: var(--soc-neon-red); border: 1px solid rgba(239, 68, 68, 0.2); }
        .pill-sip { background: rgba(249, 115, 22, 0.1); color: var(--soc-neon-orange); }
        .soc-kv-list { display: flex; flex-direction: column; gap: 10px; }
        .soc-kv-row { display: flex; justify-content: space-between; align-items: center; background: var(--soc-surface); padding: 10px 14px; border: 1px solid rgba(255,255,255,0.02); }
        .soc-kv-lbl { font-size: 11px; color: var(--text-secondary); text-transform: uppercase; }
        .soc-kv-val { font-size: 12px; font-family: monospace; font-weight: 600; }
        .soc-log-terminal { background: #020305; border: var(--border-heavy); padding: 10px; font-family: monospace; font-size: 11px; color: #a1a1aa; height: 120px; overflow-y: auto; word-break: break-all; margin-top: 8px; }
    </style>
</head>
<body>
    <header class="soc-header-ticker">
        <div class="soc-title"><h1>SOC Global Threat Wall</h1><p id="ui-heartbeat">Console Live Synchronization</p></div>
        <div class="soc-ticker-grid">
            <div class="ticker-item" style="color: var(--soc-neon-blue);"><span class="ticker-lbl">Monitored Items</span><span id="m-total" class="ticker-val">00</span></div>
            <div class="ticker-item" style="color: var(--soc-neon-green);"><span class="ticker-lbl">Ping Handshakes</span><span id="m-online" class="ticker-val">00</span></div>
            <div class="ticker-item" style="color: var(--soc-neon-red);"><span class="ticker-lbl">Active Outages</span><span id="m-offline" class="ticker-val">00</span></div>
            <div class="ticker-item" style="color: var(--soc-neon-orange);"><span class="ticker-lbl">SIP Transport Drops</span><span id="m-sip-fail" class="ticker-val">00</span></div>
        </div>
    </header>
    <div class="soc-workspace-grid">
        <section class="soc-panel">
            <div class="soc-panel-header">
                <span class="soc-panel-title">Asset Deployment Subnets</span>
                <div class="soc-filter-group">
                    <button class="soc-btn active" onclick="setFilter('ALL')">All Subnets</button>
                    <button class="soc-btn" onclick="setFilter('VOIP')">VoIP Channels</button>
                    <button class="soc-btn" onclick="setFilter('CAMERA')">Surveillance</button>
                </div>
            </div>
            <div class="soc-panel-body" style="padding: 0;"><table class="soc-table"><thead><tr><th>Node Description</th><th>IP Address</th><th>Classification</th><th>Triage Severity</th></tr></thead><tbody id="nodes-container-inject"></tbody></table></div>
        </section>
        <section class="soc-panel">
            <div class="soc-panel-header"><span class="soc-panel-title">Daemon Cycle Parameters</span></div>
            <div class="soc-panel-body">
                <div class="soc-kv-list">
                    <div class="soc-kv-row"><span class="soc-kv-lbl">Thread Engine Status</span><span class="soc-kv-val" style="color: var(--soc-neon-green)">ONLINE ACTIVE</span></div>
                    <div class="soc-kv-row"><span class="soc-kv-lbl">Completed Sweeps</span><span id="d-loops" class="soc-kv-val">—</span></div>
                    <div class="soc-kv-row"><span class="soc-kv-lbl">Cycle Duration</span><span id="d-duration" class="soc-kv-val" style="color: var(--soc-neon-blue)">—</span></div>
                    <div class="soc-kv-row"><span class="soc-kv-lbl">Main Gateway PBX</span><span id="d-pbx" class="soc-kv-val">—</span></div>
                    <div class="soc-kv-row"><span class="soc-kv-lbl">Sync Interval</span><span id="d-interval" class="soc-kv-val">—</span></div>
                </div>
            </div>
        </section>
        <section class="soc-panel">
            <div class="soc-panel-header"><span class="soc-panel-title">Incident Alert Dispatcher</span></div>
            <div class="soc-panel-body">
                <div class="soc-kv-list">
                    <div class="soc-kv-row"><span class="soc-kv-lbl">WhatsApp Daemon</span><span id="w-status" class="soc-kv-val">—</span></div>
                    <div class="soc-kv-row"><span class="soc-kv-lbl">Buffered Queue Size</span><span id="w-pending" class="soc-kv-val" style="color: var(--soc-neon-orange)">0</span></div>
                    <div class="soc-kv-row"><span class="soc-kv-lbl">Total Dispatches</span><span id="w-sent" class="soc-kv-val">—</span></div>
                </div>
                <div style="margin-top: 16px;">
                    <span class="soc-panel-title" style="font-size: 10px;">Buffer Output Stream Log</span>
                    <div id="w-target" style="font-family: monospace; font-size:11px; font-weight:bold; color: var(--soc-neon-blue); margin-bottom:4px;">—</div>
                    <div id="w-snippet" class="soc-log-terminal">—</div>
                </div>
                <div style="margin-top: 20px; border-top: 1px dashed rgba(255,255,255,0.05); padding-top: 16px;">
                    <div style="display:flex; justify-content: space-between; font-size:11px;">
                        <div>VoIP Allocation: <span id="d-voip-count" style="color:var(--soc-neon-blue); font-weight:bold;">0</span></div>
                        <div>CCTV Channels: <span id="d-cam-count" style="color:var(--soc-neon-blue); font-weight:bold;">0</span></div>
                    </div>
                </div>
            </div>
        </section>
    </div>
    <script>
        let activeFilter = 'ALL'; let cachedDevices = [];
        function setFilter(type) {
            activeFilter = type;
            document.querySelectorAll('.soc-btn').forEach(btn => {
                btn.classList.toggle('active', btn.innerText.toUpperCase().includes(type) || (type === 'ALL' && btn.innerText.includes('Subnets')));
            });
            renderCards(cachedDevices);
        }
        function renderCards(devices) {
            let html = '';
            devices.forEach(d => {
                if (activeFilter !== 'ALL' && d.type !== activeFilter) return;
                let badge = '<span class="soc-pill pill-online">CRIT_OK // ONLINE</span>';
                if (d.status === 'OFFLINE') badge = '<span class="soc-pill pill-offline">CRIT_ERR // DROPPED</span>';
                else if (d.status.startsWith('SIP')) badge = `<span class="soc-pill pill-sip">PORT_FAIL // ${d.status}</span>`;
                html += `<tr><td style="font-weight: 600; color: #fff;">${d.name}</td><td style="font-family: monospace; color: var(--soc-neon-blue);">${d.ip}</td><td style="color: var(--text-secondary); font-size: 11px; font-weight: bold;">${d.type}</td><td>${badge}</td></tr>`;
            });
            document.getElementById('nodes-container-inject').innerHTML = html || '<tr><td colspan="4" style="text-align:center; color:var(--text-secondary);">No anomalies detected.</td></tr>';
        }
        async function syncTelemetry() {
            try {
                const response = await fetch('/api/data'); const data = await response.json(); cachedDevices = data.devices;
                document.getElementById('m-total').innerText = data.stats.total.toString().padStart(2, '0');
                document.getElementById('m-online').innerText = data.stats.online.toString().padStart(2, '0');
                document.getElementById('m-offline').innerText = data.stats.offline.toString().padStart(2, '0');
                document.getElementById('m-sip-fail').innerText = (data.stats.sip_failures || 0).toString().padStart(2, '0');
                document.getElementById('d-loops').innerText = data.stats.loop_cycle_count;
                document.getElementById('d-duration').innerText = data.stats.scan_duration_ms + ' ms';
                document.getElementById('d-pbx').innerText = data.config.main_pbx_ip;
                document.getElementById('d-interval').innerText = data.config.check_interval + 's';
                document.getElementById('d-voip-count').innerText = data.stats.voip_count;
                document.getElementById('d-cam-count').innerText = data.stats.camera_count;
                document.getElementById('w-pending').innerText = data.whatsapp.pending_count;
                document.getElementById('w-sent').innerText = data.whatsapp.sent_count;
                document.getElementById('w-target').innerText = data.whatsapp.last_dispatched_to || 'WAIT_IDLE';
                document.getElementById('w-snippet').innerText = data.whatsapp.last_msg_snippet;
                const statusText = document.getElementById('w-status');
                statusText.innerText = data.whatsapp.pending_count > 0 ? "FIRING_ALERTS" : "LISTENING_PORT";
                statusText.style.color = data.whatsapp.pending_count > 0 ? "var(--soc-neon-orange)" : "var(--soc-neon-green)";
                document.getElementById('ui-heartbeat').innerText = "SOC LIVE SYNC // TIME: " + new Date().toLocaleTimeString();
                renderCards(data.devices);
            } catch (error) { console.error("SOC crash", error); }
        }
        setInterval(syncTelemetry, 3000); syncTelemetry();
    </script>
</body>
</html>
"""
