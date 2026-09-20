"""HTTP daemon, static file server, and SSE telemetry broadcaster.
Zero-dependency, stdlib Python only.
"""
import json
import queue
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse
from typing import Any

from .telemetry import TelemetryManager

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self'"
    ),
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
}

class TelemetryServer(ThreadingHTTPServer):
    def __init__(self, server_address, RequestHandlerClass, telemetry_mgr: TelemetryManager):
        self.telemetry_mgr = telemetry_mgr
        super().__init__(server_address, RequestHandlerClass)

class OverseerHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "Overseer"
    sys_version = ""

    def _send(self, status: int, payload: Any = None, content_type: str = "application/json", raw: bytes | None = None):
        if raw is not None:
            body = raw
        elif payload is not None:
            body = json.dumps(payload).encode("utf-8")
        else:
            body = b""

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for k, v in SECURITY_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _error(self, code: str, message: str, status: int = 400):
        self._send(status, {"error": {"code": code, "message": message}})

    def _drain_body(self):
        """Hazard #28: Always consume unread request body to avoid socket desync."""
        if getattr(self, "_body_read", False):
            return
        self._body_read = True
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
            if length > 0:
                self.rfile.read(length)
        except (ValueError, TypeError):
            self.close_connection = True

    def _read_body_json(self) -> Any:
        self._body_read = True
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
        except (ValueError, TypeError):
            raise ValueError("Invalid Content-Length")
        if length <= 0:
            raise ValueError("Empty body")
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ValueError("Malformed JSON payload") from e

    def do_GET(self):
        try:
            self._route_get()
        finally:
            self._drain_body()

    def do_POST(self):
        try:
            self._route_post()
        finally:
            self._drain_body()

    def _route_get(self):
        path = urlparse(self.path).path
        mgr = self.server.telemetry_mgr

        if path == "/api/telemetry/snapshot":
            return self._send(200, mgr.get_snapshot())

        if path == "/api/telemetry/stream":
            return self._handle_sse_stream()

        # Static file serving with strict containment (hazard #26)
        if path == "/":
            path = "/index.html"

        rel_path = unquote(path).lstrip("/")
        target = (FRONTEND_DIR / rel_path).resolve()
        try:
            target.relative_to(FRONTEND_DIR)
        except ValueError:
            return self._error("not_found", "File not found", 404)

        if not target.is_file():
            return self._error("not_found", "File not found", 404)

        ctype = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".json": "application/json",
            ".svg": "image/svg+xml",
            ".png": "image/png"
        }.get(target.suffix, "application/octet-stream")

        self._send(200, content_type=ctype, raw=target.read_bytes())

    def _route_post(self):
        path = urlparse(self.path).path
        mgr = self.server.telemetry_mgr

        if path == "/api/telemetry/event":
            try:
                data = self._read_body_json()
            except ValueError as e:
                return self._error("validation_error", str(e), 400)

            if not isinstance(data, dict) or "type" not in data or "data" not in data:
                return self._error("validation_error", "Event must be an object with 'type' and 'data'", 400)

            event_type = str(data["type"])
            payload = data.get("data")
            if not isinstance(payload, dict):
                return self._error("validation_error", "'data' must be an object", 400)

            mgr.broadcast(event_type, payload)
            return self._send(200, {"ok": True})

        return self._error("not_found", "Endpoint not found", 404)

    def _handle_sse_stream(self):
        """Server-Sent Events streaming handler."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        for k, v in SECURITY_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()

        mgr = self.server.telemetry_mgr
        event_q = queue.Queue(maxsize=100)

        def subscriber(event_type: str, data: dict):
            try:
                event_q.put_nowait((event_type, data))
            except queue.Full:
                pass

        mgr.add_subscriber(subscriber)

        # Initial snapshot
        try:
            snap = mgr.get_snapshot()
            init_msg = f"event: snapshot\ndata: {json.dumps(snap)}\n\n"
            self.wfile.write(init_msg.encode("utf-8"))
            self.wfile.flush()

            while True:
                try:
                    event_type, data = event_q.get(timeout=15.0)
                    msg = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
                    self.wfile.write(msg.encode("utf-8"))
                    self.wfile.flush()
                except queue.Empty:
                    # Heartbeat comment to keep SSE stream alive
                    self.wfile.write(b": heartbeat\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            mgr.remove_subscriber(subscriber)

    def log_message(self, format, *args):
        pass  # Keep stderr clean

def make_server(telemetry_mgr: TelemetryManager, port: int = 7788, host: str = "127.0.0.1") -> TelemetryServer:
    """Create TelemetryServer with port fallback support."""
    # Ensure frontend directory exists
    FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
    
    if port == 0:
        return TelemetryServer((host, 0), OverseerHandler, telemetry_mgr)

    current_port = port
    for attempt in range(10):
        try:
            server = TelemetryServer((host, current_port), OverseerHandler, telemetry_mgr)
            return server
        except OSError as e:
            if "Address already in use" in str(e) or e.errno == 98:
                current_port += 1
                continue
            raise

    raise RuntimeError(f"Could not bind to ports {port}-{current_port}")
