# dashboard_html_tactical.py
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tactical Network Operations Center</title>
    <style>
        :root {
            --bg-body: #020408; --bg-sidebar: #050812; --bg-terminal: #080c1d;
            --text-main: #00ff9d; --text-dim: #008f5d; --text-alert: #ff3b69; --text-cmd: #38bdf8;
            --border-glow: 0 0 10px rgba(0, 255, 157, 0.2); --border-line: 1px solid rgba(0, 255, 157, 0.1);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Consolas', 'Monaco', monospace; background: var(--bg-body); color: var(--text-main); 
            height: 100vh; display: flex; flex-direction: column; overflow: hidden; position: relative;
        }
        body::before {
            content: ""; position: absolute; width: 100%; height: 100%;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.2) 50%), linear-gradient(90deg, rgba(0, 255, 0, 0.03) 1px, transparent 1px), linear-gradient(rgba(0, 255, 0, 0.03) 1px, transparent 1px);
            background-size: 100% 2px, 25px 25px, 25px 25px; pointer-events: none; z-index: 5;
        }
        header { height: 50px; background: var(--bg-sidebar); border-bottom: 2px solid var(--text-main); display: flex; align-items: center; padding: 0 20px; justify-content: space-between; z-index: 10; }
        header h1 { font-size: 16px; letter-spacing: 3px; font-weight: 900; }
        .sys-path { color: var(--text-cmd); font-size: 12px; }
        .main-wrapper { flex: 1; display: flex; overflow: hidden; z-index: 2; }
        .triage-sidebar { width: 260px; background: var(--bg-sidebar); border-right: var(--border-line); display: flex; flex-direction: column; padding: 15px; gap: 15px; }
        .metric-v-box { padding: 15px; border: 1px solid rgba(0, 255, 157, 0.1); background: rgba(0,0,0,0.3); position: relative; }
        .metric-v-box::before { content: "[ STATUS ]"; position: absolute; top: -8px; left: 10px; background: var(--bg-sidebar); font-size: 9px; padding: 0 5px; color: var(--text-dim); }
        .metric-v-box .num { font-size: 28px; font-weight: bold; display: block; margin-top: 5px; }
        .metric-v-box .lbl { font-size: 10px; color: var(--text-dim); text-transform: uppercase; }
        .ops-center { flex: 1; display: flex; flex-direction: column; background: rgba(0,0,0,0.4); padding: 20px; overflow-y: auto; }
        .filter-bar { display: flex; gap: 10px; margin-bottom: 20px; }
        .filter-btn { background: transparent; border: 1px solid var(--text-dim); color: var(--text-dim); padding: 5px 15px; cursor: pointer; font-size: 11px; text-transform: uppercase; }
        .filter-btn.active { border-color: var(--text-main); color: var(--text-main); box-shadow: var(--border-glow); }
        .node-row { display: grid; grid-template-columns: 40px 1fr 150px 150px 150px; align-items: center; padding: 10px; border-bottom: 1px solid rgba(0, 255, 157, 0.05); font-size: 12px; }
        .node-row:hover { background: rgba(0, 255, 157, 0.05); }
        .node-row.header-row { color: var(--text-cmd); font-weight: bold; border-bottom: 1px solid var(--text-cmd); }
        .st-indicator { width: 8px; height: 8px; border-radius: 2px; }
        .pulse { animation: terminalPulse 2s infinite; }
        @keyframes terminalPulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
        .footer-terminal { height: 220px; background: var(--bg-terminal); border-top: 2px solid var(--text-main); display: grid; grid-template-columns: 1fr 1fr; padding: 15px; gap: 20px; z-index: 10; }
        .terminal-block { display: flex; flex-direction: column; overflow: hidden; }
        .term-title { font-size: 11px; color: var(--text-cmd); margin-bottom: 8px; border-bottom: 1px solid rgba(56, 189, 248, 0.2); padding-bottom: 4px; }
        .term-out { font-size: 11px; color: #a1a1aa; line-height: 1.6; overflow-y: auto; flex: 1; }
        .log-entry { margin-bottom: 5px; }
        .log-ts { color: var(--text-dim); margin-right: 10px; }
    </style>
</head>
<body>
    <header><h1>>> INFRASTRUCTURE_OMNIVIEW_V2.0</h1><div class="sys-path" id="ui-heartbeat">SYS_TIME: --:--:--</div></header>
    <div class="main-wrapper">
        <aside class="triage-sidebar">
            <div class="metric-v-box" style="color: var(--text-cmd)"><span class="lbl">Total Setup</span><span id="m-total" class="num">00</span></div>
            <div class="metric-v-box" style="color: var(--text-main)"><span class="lbl">Network Online</span><span id="m-online" class="num">00</span></div>
            <div class="metric-v-box" style="color: var(--text-alert)"><span class="lbl">Terminal Drops</span><span id="m-offline" class="num">00</span></div>
            <div class="metric-v-box" style="color: #ff9f1c"><span class="lbl">SIP Port Fail</span><span id="m-sip-fail" class="num">00</span></div>
        </aside>
        <main class="ops-center">
            <div class="filter-bar">
                <button class="filter-btn active" onclick="setFilter('ALL')">All_Nodes</button>
                <button class="filter-btn" onclick="setFilter('VOIP')">Voip_Subnet</button>
                <button class="filter-btn" onclick="setFilter('CAMERA')">Cam_Stream</button>
            </div>
            <div class="node-row header-row"><span></span><span>NODE_IDENTIFIER</span><span>INTERFACE_IP</span><span>CLASSIFICATION</span><span>STATUS_FLAG</span></div>
            <div id="nodes-container-inject"></div>
        </main>
    </div>
    <footer class="footer-terminal">
        <div class="terminal-block">
            <div class="term-title">COMM_LOGS: WHATSAPP_DISPATCH_QUEUE</div>
            <div class="term-out">
                <div class="log-entry"><span class="log-ts">[ STATE ]</span> Automation: <span id="w-status">STANDBY</span></div>
                <div class="log-entry"><span class="log-ts">[ QUEUE ]</span> Pending_Buffers: <span id="w-pending" style="color:var(--text-alert)">0</span></div>
                <div class="log-entry"><span class="log-ts">[ SENT  ]</span> Total_Dispatches: <span id="w-sent">0</span></div>
                <div class="log-entry"><span class="log-ts">[ TARGET]</span> Last_Recipient: <span id="w-target" style="color:var(--text-cmd)">None</span></div>
                <div class="log-entry" style="margin-top:10px;"><div class="log-ts">RAW_PAYLOAD_SNIPPET:</div><div id="w-snippet" style="color:#64748b; padding-left:10px; border-left:1px solid #333;">...</div></div>
            </div>
        </div>
        <div class="terminal-block">
            <div class="term-title">ENGINE_DIAGNOSTICS: THREAD_RUNTIME</div>
            <div class="term-out">
                <div class="log-entry"><span class="log-ts">[ SCAN_LOAD ]</span> <span id="d-duration">0ms</span></div>
                <div class="log-entry"><span class="log-ts">[ CYCLES    ]</span> <span id="d-loops">0</span></div>
                <div class="log-entry"><span class="log-ts">[ PBX_GATE  ]</span> <span id="d-pbx">0.0.0.0</span></div>
                <div class="log-entry"><span class="log-ts">[ POLLING   ]</span> <span id="d-interval">0s</span></div>
            </div>
        </div>
    </footer>
    <script>
        let activeFilter = 'ALL'; let cachedDevices = [];
        function setFilter(type) {
            activeFilter = type;
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.toggle('active', btn.innerText.toUpperCase().includes(type) || (type === 'ALL' && btn.innerText.includes('All')));
            });
            renderCards(cachedDevices);
        }
        function renderCards(devices) {
            let html = '';
            devices.forEach(d => {
                if (activeFilter !== 'ALL' && d.type !== activeFilter) return;
                let color = d.status === 'OFFLINE' ? '#ff3b69' : (d.status.startsWith('SIP') ? '#ff9f1c' : '#00ff9d');
                html += `<div class="node-row">
                    <div class="st-indicator ${d.online ? '' : 'pulse'}" style="background: ${color}; box-shadow: 0 0 5px ${color}"></div>
                    <div class="node-name">${d.name}</div>
                    <div class="node-ip">${d.ip}</div>
                    <div style="color:var(--text-dim)">${d.type}</div>
                    <div style="color:${color}; font-weight:bold;">${d.status}</div>
                </div>`;
            });
            document.getElementById('nodes-container-inject').innerHTML = html;
        }
        async function syncTelemetry() {
            try {
                const response = await fetch('/api/data'); const data = await response.json(); cachedDevices = data.devices;
                document.getElementById('m-total').innerText = data.stats.total.toString().padStart(2, '0');
                document.getElementById('m-online').innerText = data.stats.online.toString().padStart(2, '0');
                document.getElementById('m-offline').innerText = data.stats.offline.toString().padStart(2, '0');
                document.getElementById('m-sip-fail').innerText = (data.stats.sip_failures || 0).toString().padStart(2, '0');
                document.getElementById('d-loops').innerText = data.stats.loop_cycle_count;
                document.getElementById('d-duration').innerText = data.stats.scan_duration_ms + 'ms';
                document.getElementById('d-pbx').innerText = data.config.main_pbx_ip;
                document.getElementById('d-interval').innerText = data.config.check_interval + 's';
                document.getElementById('w-pending').innerText = data.whatsapp.pending_count;
                document.getElementById('w-sent').innerText = data.whatsapp.sent_count;
                document.getElementById('w-target').innerText = data.whatsapp.last_dispatched_to;
                document.getElementById('w-snippet').innerText = data.whatsapp.last_msg_snippet;
                const statusText = document.getElementById('w-status');
                statusText.innerText = data.whatsapp.pending_count > 0 ? "TRANSMITTING..." : "IDLE_LISTENING";
                statusText.style.color = data.whatsapp.pending_count > 0 ? "var(--text-alert)" : "var(--text-main)";
                document.getElementById('ui-heartbeat').innerText = "SYS_TIME: " + new Date().toLocaleTimeString();
                renderCards(data.devices);
            } catch (error) { console.error("Sync Error", error); }
        }
        setInterval(syncTelemetry, 3000); syncTelemetry();
    </script>
</body>
</html>
"""
