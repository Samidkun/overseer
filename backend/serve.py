"""Production entrypoint for Overseer daemon.
Usage:
  python -m backend.serve [--port 7788] [--host 127.0.0.1] [--watch-dir ~/.hermes/cache/delegation/live/]
"""
import os
import sys
import time
import argparse
import threading
from pathlib import Path

from .telemetry import TelemetryManager
from .server import make_server

def main():
    parser = argparse.ArgumentParser(description="Overseer: Agent Telemetry & Visualizer Daemon")
    default_watch = Path.home() / ".hermes" / "cache" / "delegation" / "live"
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "7788")), help="Port to bind (default 7788)")
    parser.add_argument("--host", type=str, default=os.environ.get("HOST", "127.0.0.1"), help="Host to bind (default 127.0.0.1)")
    parser.add_argument("--watch-dir", type=str, default=str(default_watch), help="Path to agent live log cache")
    args = parser.parse_args()

    watch_path = Path(args.watch_dir)
    watch_path.mkdir(parents=True, exist_ok=True)

    telemetry_mgr = TelemetryManager(watch_dir=str(watch_path))
    server = make_server(telemetry_mgr, port=args.port, host=args.host)
    actual_port = server.server_address[1]

    # Background log scanner & stuck detector thread
    def background_watcher():
        while True:
            try:
                telemetry_mgr.scan_log_files()
                telemetry_mgr.check_stuck_agents()
            except Exception:
                pass
            time.sleep(1.0)

    t = threading.Thread(target=background_watcher, daemon=True)
    t.start()

    print(f"============================================================")
    print(f"  OVERSEER // Real-Time Agent Mission Control")
    print(f"  Web Dashboard : http://{args.host}:{actual_port}")
    print(f"  Watching Logs : {watch_path}")
    print(f"============================================================", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Overseer daemon...")
        server.shutdown()

if __name__ == "__main__":
    main()
