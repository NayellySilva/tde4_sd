import json
import os
import random
import socket
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SERVER_NAME = os.getenv("SERVER_NAME", socket.gethostname())
PORT = int(os.getenv("PORT", "5000"))
DELAY_MS = int(os.getenv("DELAY_MS", "0"))

PRODUCTS = [
    {"id": 1, "nome": "Celular", "preco": 8586.90},
    {"id": 2, "nome": "Ração", "preco": 650.00},
    {"id": 3, "nome": "Fralda", "preco": 300.00},
    {"id": 4, "nome": "TV", "preco": 9999.99},
    {"id": 5, "nome": "Sofa", "preco": 3000.00},
]

STARTED_AT = time.time()
request_count = 0


def render_home() -> str:
    itens = "".join(
        f"<li>{p['nome']} — <b>R$ {p['preco']:.2f}</b></li>" for p in PRODUCTS
    )
    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head><meta charset="utf-8"><title>ShopNow</title></head>
<body style="font-family: sans-serif; max-width: 640px; margin: 40px auto;">
  <h1>🛒 ShopNow — Black Friday</h1>
  <p>Atendido por: <b>{SERVER_NAME}</b></p>
  <ul>{itens}</ul>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, status: int, body: str, content_type: str):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Server", SERVER_NAME)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        global request_count
        request_count += 1

        if DELAY_MS:
            time.sleep(DELAY_MS / 1000)

        path = self.path.split("?")[0]

        if path == "/":
            self._send(200, render_home(), "text/html; charset=utf-8")
        elif path == "/api/products":
            body = {"server": SERVER_NAME, "products": PRODUCTS}
            self._send(200, json.dumps(body, ensure_ascii=False), "application/json")
        elif path == "/api/checkout":
            time.sleep(random.uniform(0.1, 0.3))
            body = {"server": SERVER_NAME, "status": "pedido confirmado"}
            self._send(200, json.dumps(body, ensure_ascii=False), "application/json")
        elif path == "/health":
            body = {
                "status": "ok",
                "server": SERVER_NAME,
                "uptime_s": round(time.time() - STARTED_AT, 1),
                "requests": request_count,
            }
            self._send(200, json.dumps(body), "application/json")
        else:
            self._send(404, json.dumps({"erro": "não encontrado"}), "application/json")

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer.daemon_threads = True
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[{SERVER_NAME}] ShopNow rodando na porta {PORT}", flush=True)
    httpd.serve_forever()
