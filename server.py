"""SightCount v1 server — Python standard library only, no pip installs.

Run:  python3 server.py [--port 8000]
Then open http://localhost:8000/ in a browser.

Endpoints:
  GET  /api/health      -> {"ok": true, "meta_api_key_set": bool}
  POST /api/interpret   -> JSON {count, groups, spread, mode, note}
                           returns the scene interpretation (Meta API if a
                           key is set, else the labelled local fallback).
  GET  /                -> the single-page app in static/
"""

import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meta_client import interpret  # noqa: E402


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "static"), **kwargs)

    def log_message(self, *args):
        pass  # keep the console clean; the UI event log is the record

    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/health":
            self._send_json({
                "ok": True,
                "meta_api_key_set": bool(os.environ.get("META_MODEL_API_KEY")),
            })
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != "/api/interpret":
            self._send_json({"error": "not found"}, status=404)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            scene = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            self._send_json({"error": "bad JSON"}, status=400)
            return
        scene = {
            "count": int(scene.get("count", 0)),
            "groups": int(scene.get("groups", 0)),
            "spread": str(scene.get("spread", "unknown")),
            "mode": str(scene.get("mode", "unknown")),
            "note": str(scene.get("note", ""))[:300],
        }
        self._send_json(interpret(scene))


def main():
    port = 8000
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"SightCount v1 running at http://127.0.0.1:{port}/")
    print("Meta API key set:", bool(os.environ.get("META_MODEL_API_KEY")),
          "(fallback mode if False)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
