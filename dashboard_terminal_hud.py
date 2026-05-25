# dashboard_html_hud.py
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Matrix Terminal Fleet HUD</title>
    <style>
        :root {
            --term-bg: #03050a; --term-frame: #0a0f1d; --term-green: #00ff66; --term-amber: #ffb700;
            --term-red: #ff2a5f; --term-blue: #00e5ff; --term-dim: #415a77; --border-style: 1px dashed rgba(0, 255, 102, 0.2);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Consolas', monospace; background: var(--term-bg); color: #fff; padding: 20px; height: 100vh; display: flex; justify-content: center; align-items: center; overflow: hidden; }
        .terminal-hud { width: 100%; max-width: 1500px; height: 95vh; background: var(--term-frame); border: 1px solid var(--term-green); box-shadow: 0 0 15px rgba(0, 255, 102, 0.1); border-radius: 4px; display: flex; flex-direction: column; overflow: hidden; }
        .window-header { background: rgba(0, 255, 102, 0.04); border-bottom: 1px solid var(--term-green); padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: var(--term-green); }
        .hud-sys-banner { display: grid; grid-template-columns: repeat(4, 1fr); border-bottom: 1px solid var(--term-green); background: rgba(0,0,0,0.4); }
        .banner-stat { padding: 12px 20px; border-right: 1px dashed rgba(0, 255, 102, 0.15); font-size: 12px; }
        .banner-stat:last-child { border-right: none; }
        .stat-lbl { color: var(--term-dim); font-size: 10px; text-transform: uppercase; margin-bottom: 3px;}
        .stat-val { font-weight: bold; font-size: 18px; display: block; }
        .hud-body { flex: 1; display: grid; grid-template-rows: 1fr 180px; overflow: hidden; }
        .main-matrix-panel { padding: 20px; overflow-y: auto; display: flex; flex-direction: column; }
        .panel-controls { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px dashed rgba(0, 255, 102, 0.1); padding-bottom: 10px; }
        .panel-title { font-size: 13px; color: var(--term-blue); font-weight: bold; }
        .tab-group { display: flex; gap: 8px; }
        .tab-control { background: transparent; border: 1px solid var(--term-dim); color: var(--term-dim); padding: 4px 12px; font-size: 11px; cursor: pointer; }
        .tab-control.active, .tab-control:hover { border-color: var(--term-green); color: var(--term-green); background: rgba(0, 255, 102, 0.05); }
        .matrix-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 10px; }
        .matrix-node { background: #040712; border: var(--border-style); padding: 12px; display: flex; flex-direction: column; gap: 6px; position: relative; }
        .matrix-node::before { content: ""; position: absolute; top: 0; left: 0; width: 2px; height: 100%; background: currentColor; }
        .node-meta { display: flex; justify-content: space-between; font-size: 11px; color: var(--term-dim); }
        .node-head { font-size: 13px; font-weight: bold; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .node-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 4px; font-size: 11px; }
        .hud-footer-terminal { background: #020307; border-top: 1px solid var(--term-green); display: grid; grid-template-columns: 1fr 1fr; padding: 15px; gap: 20px; }
        .console-stream { display: flex; flex-direction: column; height: 100%; }
        .console-label { font-size: 11px; color: var(--term-blue); margin-bottom: 6px; text-transform: uppercase; }
        .console-box { flex: 1; border: 1px solid rgba(0, 255, 102, 0.05); background: rgba(0,0,0,0.3); padding: 10px; font-size: 11px; color: #cbd5e1; overflow-y: auto; }
        .c-row { display: flex; justify-content: space-between; margin-bottom: 4px; }
        .c-lbl { color: var(--term-dim); }
        .c-val { color: var(--term-green); font-weight: bold; }
    </style>
</head>
<body>
    <div class="terminal-hud">
        <div class="window-header"><span>CORE://STATION_FLEET_HUDS</span><span id="ui-heartbeat">SYS_TIME: --:--:--</span></div>
        <div class="hud-sys-banner">
            <div class="banner-stat" style="color: var(--term-blue);"><span class="stat-lbl">> CONF_TARGETS_LOADED</span><span id="m-total" class="stat-val">00</span></div>
            <div class="banner-stat" style="color: var(--term-green);"><span class="stat-lbl">> ICMP_PING_ONLINE</span><span id="m-online" class="stat-val">00</span></div>
            <div class="banner-stat" style="color: var(--term-red);"><span class="stat-lbl">> CRITICAL_DROPPED_NODES</span><span id="m-offline" class="stat-val">00</span></div>
            <div class="banner-stat" style="color: var(--term-amber);"><span class="stat-lbl">> SIP_REG_FAILURES</span><span id="m-sip-fail" class="stat-val">00</span></div>
        </div>
        <div class="hud-body">
            <div class="main-matrix-panel">
                <div class="panel-controls">
                    <div class="panel-title">> FLEET_ASSET_MATRIX</div>
                    <div class="tab-group">
                        <button class="tab-control active" onclick="setFilter('ALL')">ALL_CHANNELS</button>
                        <button class="tab-control" onclick="setFilter('VOIP')">VOIP_SUBNET</button>
                        <button class="tab-control" onclick="setFilter('CAMERA')">CAMERA_ARRAY</button>
                    </div>
                </div>
                <div id="nodes-container-inject" class="matrix-grid"></div>
            </div>
            <div class="hud-footer-terminal">
                <div class="console-stream">
                    <div class="console-label">LINK_BUFFER: WhatsApp Sender</div>
                    <div class="console-box">
                        <div class="c-row"><span class="c-lbl">DAEMON_STATE:</span><span id="w-status" class="c-val">—</span></div>
                        <div class="c-row"><span class="c-lbl">QUEUE_SIZE:</span><span id="w-pending" class="c-val" style="color: var(--term-amber)">0</span></div>
                        <div class="c-row"><span class="c-lbl">TOTAL_DISPATCHED:</span><span id="w-sent" class="c-val">—</span></div>
                        <div class="c-row"><span class="c-lbl">LAST_TARGET:</span><span id="w-target" class="c-val" style="color: var(--term-blue)">—</span></div>
                        <div style="font-size: 10px; color: var(--term-dim); margin-top: 6px;">BUFFER: <span id="w-snippet" style="color:#8a99ad;">—</span></div>
                    </div>
                </div>
                <div class="console-stream">
                    <div class="console-label">SYS_DAEMON: Micro-Engine Internals</div>
                    <div class="console-box">
                        <div class="c-row"><span class="c-lbl">LATENCY_OVERHEAD:</span><span id="d-duration" class="c-val">—</span></div>
                        <div class="c-row"><span class="c-lbl">ENGINE_LOOP_RUNS:</span><span id="d-loops" class="c-val">—</span></div>
                        <div class="c-row"><span class="c-lbl">TARGET_PBX_IP:</span><span id="d-pbx" class="c-val">—</span></div>
                        <div class="c-row"><span class="c-lbl">POLLING_FREQ:</span><span id="d-interval" class="c-val">—</span></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        let activeFilter = 'ALL'; let cachedDevices = [];
        function setFilter(type) {
            activeFilter = type;
            document.querySelectorAll('.tab-control').forEach(btn => {
                btn.classList.toggle('active', btn.innerText.includes(type) || (type === 'ALL' && btn.innerText.includes('ALL')));
            });
            renderCards(cachedDevices);
        }
        function renderCards(devices) {
            let html = '';
            devices.forEach(d => {
                if (activeFilter !== 'ALL' && d.type !== activeFilter) return;
                let stateColor = d.status === 'OFFLINE' ? 'var(--term-red)' : (d.status.startsWith('SIP') ? 'var(--term-amber)' : 'var(--term-green)');
                html += `<div class="matrix-node" style="color: ${stateColor}">
                    <div class="node-meta"><span>IP: ${d.ip}</span><span>${d.type}</span></div>
                    <div class="node-head" title="${d.name}"># ${d.name}</div>
                    <div class="node-foot"><span style="font-size:10px; color:var(--term-dim);">FLAG:</span><span style="font-weight:bold;">[${d.status}]</span></div>
                    <div style="font-size:10px; border-top:1px dashed rgba(255,255,255,0.03); padding-top:4px; display:flex; justify-content:space-between;">
                        <span style="color:var(--term-dim)">COMMS_MAP:</span><span style="color:var(--term-blue)">${d.phone || 'UNASSIGNED'}</span>
                    </div>
                </div>`;
            });
            document.getElementById('nodes-container-inject').innerHTML = html || '<div style="grid-column:1/-1; padding:20px; color:var(--term-dim);">// NO STREAM COINCIDENCE</div>';
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
                document.getElementById('d-interval').innerText = data.config.check_interval + 's cycle';
                document.getElementById('w-pending').innerText = data.whatsapp.pending_count;
                document.getElementById('w-sent').innerText = data.whatsapp.sent_count;
                document.getElementById('w-target').innerText = data.whatsapp.last_dispatched_to;
                document.getElementById('w-snippet').innerText = data.whatsapp.last_msg_snippet;
                const statusText = document.getElementById('w-status');
                statusText.innerText = data.whatsapp.pending_count > 0 ? "DISPATCHING_PAYLOAD" : "MONITOR_WAITING";
                statusText.style.color = data.whatsapp.pending_count > 0 ? "var(--term-amber)" : "var(--term-green)";
                document.getElementById('ui-heartbeat').innerText = "SYS_TIME: " + new Date().toLocaleTimeString();
                renderCards(data.devices);
            } catch (error) { console.error("HUD Sync error", error); }
        }
        setInterval(syncTelemetry, 3000); syncTelemetry();
    </script>
</body>
</html>
"""
