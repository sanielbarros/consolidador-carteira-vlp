import json
import os
import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import requests

API_URL = "https://brapi.dev/api/v2/stocks/dividends"


class handler(BaseHTTPRequestHandler):
    def _json(self, status, obj):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        token = os.environ.get("BRAPI_TOKEN")
        if not token:
            return self._json(500, {"erro": "BRAPI_TOKEN não configurado no servidor."})

        symbol = parse_qs(urlparse(self.path).query).get("symbol", [""])[0].strip().upper()
        if not re.fullmatch(r"[A-Z0-9]{3,12}", symbol):
            return self._json(400, {"erro": "Código de ação inválido."})
        try:
            r = requests.get(API_URL, params={"symbols": symbol},
                             headers={"Authorization": token}, timeout=15)
        except requests.RequestException:
            return self._json(502, {"erro": "Não foi possível acessar a API da brapi."})
        if r.status_code in (400, 403, 404):
            return self._json(404, {"erro": f"Ação {symbol} não encontrada."})
        if r.status_code != 200:
            return self._json(502, {"erro": f"A brapi retornou erro {r.status_code}."})

        results = r.json().get("results") or []
        if not results or not results[0].get("data"):
            return self._json(404, {"erro": f"Ação {symbol} não encontrada."})
        item = results[0]
        self._json(200, {"symbol": item.get("symbol", symbol),
                         "cashDividends": item["data"].get("cashDividends", [])})
