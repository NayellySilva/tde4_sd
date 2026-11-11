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


CORES = {"app1": "#2563eb", "app2": "#16a34a", "app3": "#ea580c"}
ICONES = {"Celular": "📱", "Ração": "🐶", "Fralda": "👶", "TV": "📺", "Sofa": "🛋️"}


def preco_br(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render_home() -> str:
    cor = CORES.get(SERVER_NAME, "#7c3aed")
    cards = "".join(
        f"""<div class="card">
              <div class="icone">{ICONES.get(p['nome'], '🛍️')}</div>
              <span class="desconto">-30%</span>
              <h3>{p['nome']}</h3>
              <p class="de">{preco_br(p['preco'] / 0.7)}</p>
              <p class="por">{preco_br(p['preco'])}</p>
              <button onclick="comprar(this)">Comprar</button>
            </div>"""
        for p in PRODUCTS
    )
    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ShopNow • Black Friday</title>
<style>
  * {{ box-sizing: border-box; margin: 0; }}
  body {{ font-family: "Segoe UI", system-ui, sans-serif; background: #f4f4f5; color: #18181b; }}
  header {{ background: #09090b; color: #fff; padding: 18px 32px; display: flex;
           justify-content: space-between; align-items: center; }}
  .logo {{ font-size: 24px; font-weight: 800; }}
  .logo span {{ color: #facc15; }}
  .servidor {{ background: {cor}; padding: 8px 16px; border-radius: 999px;
              font-weight: 700; font-size: 14px; }}
  .banner {{ background: linear-gradient(90deg, #09090b, #3f3f46); color: #facc15;
            text-align: center; padding: 36px 16px; }}
  .banner h1 {{ font-size: 42px; letter-spacing: 2px; }}
  .banner p {{ color: #e4e4e7; margin-top: 8px; }}
  main {{ max-width: 1100px; margin: 32px auto; padding: 0 16px; display: grid;
         grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 20px; }}
  .card {{ background: #fff; border-radius: 14px; padding: 20px; position: relative;
          box-shadow: 0 2px 8px rgba(0,0,0,.06); text-align: center; transition: transform .15s; }}
  .card:hover {{ transform: translateY(-4px); }}
  .icone {{ font-size: 64px; margin: 8px 0 12px; }}
  .desconto {{ position: absolute; top: 12px; left: 12px; background: #dc2626; color: #fff;
              font-size: 12px; font-weight: 700; padding: 3px 8px; border-radius: 6px; }}
  .de {{ color: #a1a1aa; text-decoration: line-through; font-size: 13px; margin-top: 6px; }}
  .por {{ color: #16a34a; font-size: 22px; font-weight: 800; margin: 2px 0 14px; }}
  button {{ width: 100%; padding: 10px; border: 0; border-radius: 8px; background: #09090b;
           color: #fff; font-weight: 700; cursor: pointer; }}
  button:hover {{ background: {cor}; }}
  footer {{ text-align: center; color: #71717a; padding: 24px; font-size: 14px; }}
  footer b {{ color: {cor}; }}
  #toast {{ position: fixed; bottom: 24px; right: 24px; background: #09090b; color: #fff;
           padding: 14px 20px; border-radius: 10px; display: none; }}
</style>
</head>
<body>
  <header>
    <div class="logo">🛒 Shop<span>Now</span></div>
    <div class="servidor">🖥️ Atendido por: {SERVER_NAME.upper()}</div>
  </header>
  <section class="banner">
    <h1>BLACK FRIDAY</h1>
    <p>Até 30% de desconto em todos os produtos</p>
  </section>
  <main>{cards}</main>
  <footer>Página gerada pela instância <b>{SERVER_NAME}</b> — aperte F5 e veja o balanceador trocar de servidor</footer>
  <div id="toast"></div>
<script>
  async function comprar(btn) {{
    btn.disabled = true; btn.textContent = "Processando...";
    const toast = document.getElementById("toast");
    try {{
      const r = await fetch("/api/checkout");
      const d = await r.json();
      toast.textContent = "✅ " + d.status + " (processado por " + d.server + ")";
    }} catch (e) {{
      toast.textContent = "❌ Erro ao finalizar compra";
    }}
    toast.style.display = "block";
    setTimeout(() => toast.style.display = "none", 3000);
    btn.disabled = false; btn.textContent = "Comprar";
  }}
</script>
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
