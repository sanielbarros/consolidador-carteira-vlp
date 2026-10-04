"""Servidor local para testes: BRAPI_TOKEN=... python servidor_local.py -> http://localhost:8000
Em produção (Vercel) quem atende é public/index.html + api/dividendos.py."""
import os
from http.server import ThreadingHTTPServer

from api.dividendos import handler as ApiHandler

PORT = int(os.environ.get("PORT", 8000))


class Local(ApiHandler):
    def do_GET(self):
        if self.path.startswith("/api/dividendos"):
            return super().do_GET()
        with open("public/index.html", "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    print(f"Servidor em http://localhost:{PORT}")
    ThreadingHTTPServer(("", PORT), Local).serve_forever()
