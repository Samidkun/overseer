import json
import time
import socket
import tempfile
import threading
import urllib.request
import urllib.error
from pathlib import Path
import pytest

from backend.server import make_server
from backend.telemetry import TelemetryManager

@pytest.fixture()
def srv():
    tmp_dir = tempfile.mkdtemp()
    mgr = TelemetryManager(watch_dir=tmp_dir)
    server = make_server(mgr, port=0, host="127.0.0.1")
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    yield base_url, mgr
    server.shutdown()

def req(url, method="GET", body=None, headers=None):
    h = headers or {}
    data = json.dumps(body).encode() if body is not None else None
    if body is not None and "Content-Type" not in h:
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=3) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read()
            is_json = "application/json" in content_type
            parsed = json.loads(raw.decode()) if is_json and raw else raw
            return resp.status, parsed, dict(resp.headers)
    except urllib.error.HTTPError as e:
        raw = e.read()
        content_type = e.headers.get("Content-Type", "")
        is_json = "application/json" in content_type
        parsed = json.loads(raw.decode()) if is_json and raw else raw
        return e.code, parsed, dict(e.headers)

# AC-1
def test_serve_frontend(srv):
    base, _ = srv
    s, b, h = req(f"{base}/")
    assert s == 200
    assert "text/html" in h.get("Content-Type", "")

# AC-2
def test_get_telemetry_snapshot(srv):
    base, mgr = srv
    s, data, _ = req(f"{base}/api/telemetry/snapshot")
    assert s == 200
    assert "supervisor" in data
    assert "subagents" in data
    assert "metrics" in data

# AC-3
def test_sse_stream_connect(srv):
    base, _ = srv
    # Direct socket request to verify header response without blocking on infinite stream
    host, port = base.replace("http://", "").split(":")
    sock = socket.create_connection((host, int(port)), timeout=3)
    req_raw = f"GET /api/telemetry/stream HTTP/1.1\r\nHost: {host}\r\nAccept: text/event-stream\r\n\r\n"
    sock.sendall(req_raw.encode())
    
    resp_header = b""
    while b"\r\n\r\n" not in resp_header:
        chunk = sock.recv(1024)
        if not chunk:
            break
        resp_header += chunk
    sock.close()

    header_text = resp_header.decode(errors="ignore")
    assert "200 OK" in header_text
    assert "text/event-stream" in header_text

# AC-6
def test_ingest_event_valid(srv):
    base, mgr = srv
    payload = {"type": "log", "data": {"message": "hello", "tag": "test"}}
    s, data, _ = req(f"{base}/api/telemetry/event", method="POST", body=payload)
    assert s == 200
    assert data == {"ok": True}

# AC-7
@pytest.mark.parametrize("bad_body", ["not json", {"no_data": 123}, []])
def test_ingest_event_malformed_400(srv, bad_body):
    base, _ = srv
    headers = {"Content-Type": "application/json"}
    raw = bad_body.encode() if isinstance(bad_body, str) else json.dumps(bad_body).encode()
    r = urllib.request.Request(f"{base}/api/telemetry/event", data=raw, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=3) as resp:
            status = resp.status
    except urllib.error.HTTPError as e:
        status = e.code
        err = json.loads(e.read().decode())
        assert "error" in err
    assert status == 400

# AC-8 (hazard #26 containment)
def test_path_traversal_blocked_404(srv):
    base, _ = srv
    s, _, _ = req(f"{base}/../../../../../../../../etc/passwd")
    assert s == 404

# AC-9
def test_security_headers_present(srv):
    base, _ = srv
    s, _, h = req(f"{base}/api/telemetry/snapshot")
    assert s == 200
    assert "Content-Security-Policy" in h
    assert "X-Frame-Options" in h
    assert "X-Content-Type-Options" in h
