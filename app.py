"""Consulta de proventos (brapi.dev).
Local: BRAPI_TOKEN=... python app.py -> http://localhost:8000
Vercel: usa a variável `app` (Flask) como entrypoint."""
import os
import re

import requests
from flask import Flask, jsonify, request, send_from_directory

API_URL = "https://brapi.dev/api/v2/stocks/dividends"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


@app.get("/")
def index():
    return send_from_directory(os.path.join(BASE_DIR, "public"), "index.html")


@app.get("/api/dividendos")
def dividendos():
    token = os.environ.get("BRAPI_TOKEN")
    if not token:
        return jsonify(erro="BRAPI_TOKEN não configurado no servidor."), 500

    symbol = request.args.get("symbol", "").strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{3,12}", symbol):
        return jsonify(erro="Código de ação inválido."), 400
    try:
        r = requests.get(API_URL, params={"symbols": symbol},
                         headers={"Authorization": token}, timeout=15)
    except requests.RequestException:
        return jsonify(erro="Não foi possível acessar a API da brapi."), 502
    if r.status_code in (400, 403, 404):
        return jsonify(erro=f"Ação {symbol} não encontrada."), 404
    if r.status_code != 200:
        return jsonify(erro=f"A brapi retornou erro {r.status_code}."), 502

    results = r.json().get("results") or []
    if not results or not results[0].get("data"):
        return jsonify(erro=f"Ação {symbol} não encontrada."), 404
    item = results[0]
    return jsonify(symbol=item.get("symbol", symbol),
                   cashDividends=item["data"].get("cashDividends", []))


if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 8000)))
