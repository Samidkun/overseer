import json
import time
import tempfile
import threading
import urllib.request
from pathlib import Path

from backend.server import make_server
from backend.telemetry import TelemetryManager

def test_full_e2e_lifecycle():
    tmp_dir = tempfile.mkdtemp()
    mgr = TelemetryManager(watch_dir=tmp_dir)
    server = make_server(mgr, port=0, host="127.0.0.1")
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"

    try:
        # 1. Frontend serves cleanly
        with urllib.request.urlopen(f"{base}/", timeout=3) as resp:
            assert resp.status == 200
            html = resp.read().decode()
            assert "OVERSEER" in html
            assert "topologyCanvas" in html

        # 2. Static CSS & JS serve cleanly
        with urllib.request.urlopen(f"{base}/styles.css", timeout=3) as resp:
            assert resp.status == 200
            assert "css" in resp.headers.get("Content-Type", "")

        with urllib.request.urlopen(f"{base}/app.js", timeout=3) as resp:
            assert resp.status == 200
            assert "javascript" in resp.headers.get("Content-Type", "")

        # 3. Snapshot endpoint
        with urllib.request.urlopen(f"{base}/api/telemetry/snapshot", timeout=3) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode())
            assert "supervisor" in data
            assert "subagents" in data

        # 4. Ingest event from agent
        req = urllib.request.Request(
            f"{base}/api/telemetry/event",
            data=json.dumps({"type": "log", "data": {"tag": "tool", "message": "e2e-tool-run"}}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            assert resp.status == 200
            res = json.loads(resp.read().decode())
            assert res == {"ok": True}

        # 5. Security headers on responses
        with urllib.request.urlopen(f"{base}/api/telemetry/snapshot", timeout=3) as resp:
            h = dict(resp.headers)
            assert "Content-Security-Policy" in h
            assert "X-Frame-Options" in h
            assert "X-Content-Type-Options" in h

    finally:
        server.shutdown()
