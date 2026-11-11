import http.client
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from algorithms import ALGORITMOS, get_algorithm

PORT = int(os.getenv("PORT", "8080"))
HEALTH_INTERVAL = float(os.getenv("HEALTH_INTERVAL", "2"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
BACKEND_TIMEOUT = float(os.getenv("BACKEND_TIMEOUT", "2"))

HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade",
}


def log(msg):
    print(f"[LB {time.strftime('%H:%M:%S')}] {msg}", flush=True)


class Backend:
    def __init__(self, host, port, weight=1):
        self.host = host
        self.port = port
        self.weight = weight
        self.name = f"{host}:{port}"
        self.healthy = True
        self.active_connections = 0
        self.total_requests = 0
        self.failures = 0
        self.lock = threading.Lock()

    def mark(self, healthy: bool, motivo: str = ""):
        with self.lock:
            mudou = self.healthy != healthy
            self.healthy = healthy
        if mudou:
            estado = "VOLTOU" if healthy else "CAIU"
            log(f"{self.name} {estado} {motivo}")

    def to_dict(self):
        return {
            "name": self.name,
            "weight": self.weight,
            "healthy": self.healthy,
            "active_connections": self.active_connections,
            "total_requests": self.total_requests,
            "failures": self.failures,
        }


def parse_backends(raw: str):
    backends = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        partes = item.split(":")
        host, port = partes[0], int(partes[1])
        weight = int(partes[2]) if len(partes) > 2 else 1
        backends.append(Backend(host, port, weight))
    return backends


class LoadBalancer:
    def __init__(self, backends, algorithm_name):
        self.backends = backends
        self.algorithm = get_algorithm(algorithm_name)
        self.started_at = time.time()
        self.total_requests = 0
        self.total_errors = 0
        self.stats_lock = threading.Lock()

    def healthy_backends(self):
        return [b for b in self.backends if b.healthy]

    def pick(self, excluir):
        candidatos = [b for b in self.healthy_backends() if b not in excluir]
        if not candidatos:
            return None
        return self.algorithm.choose(candidatos)

    def set_algorithm(self, name):
        self.algorithm = get_algorithm(name)
        log(f"Algoritmo alterado para {name}")

    def health_check_loop(self):
        while True:
            for b in self.backends:
                try:
                    conn = http.client.HTTPConnection(b.host, b.port, timeout=1.5)
                    conn.request("GET", "/health")
                    resp = conn.getresponse()
                    resp.read()
                    conn.close()
                    b.mark(resp.status == 200, f"(health check HTTP {resp.status})")
                except Exception as e:
                    b.mark(False, f"(health check: {type(e).__name__})")
            time.sleep(HEALTH_INTERVAL)

    def status(self):
        return {
            "algorithm": self.algorithm.name,
            "available_algorithms": list(ALGORITMOS),
            "uptime_s": round(time.time() - self.started_at, 1),
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "healthy": len(self.healthy_backends()),
            "backends": [b.to_dict() for b in self.backends],
        }


LB: LoadBalancer = None 


class ProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _reply(self, status, body: dict):
        data = json.dumps(body, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def handle_admin(self, url):
        if url.path == "/lb/status":
            return self._reply(200, LB.status())
        if url.path == "/lb/algorithm":
            nome = parse_qs(url.query).get("name", [None])[0]
            try:
                LB.set_algorithm(nome)
                return self._reply(200, {"algorithm": nome})
            except ValueError as e:
                return self._reply(400, {"erro": str(e)})
        return self._reply(404, {"erro": "endpoint do LB não encontrado"})

    def proxy(self):
        url = urlparse(self.path)
        if url.path.startswith("/lb/"):
            return self.handle_admin(url)

        with LB.stats_lock:
            LB.total_requests += 1

        length = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(length) if length else None
        headers = {
            k: v for k, v in self.headers.items() if k.lower() not in HOP_BY_HOP
        }
        headers["X-Forwarded-For"] = self.client_address[0]

        tentados = []
        for _ in range(MAX_RETRIES):
            backend = LB.pick(excluir=tentados)
            if backend is None:
                break
            tentados.append(backend)

            with backend.lock:
                backend.active_connections += 1
                backend.total_requests += 1
            try:
                conn = http.client.HTTPConnection(
                    backend.host, backend.port, timeout=BACKEND_TIMEOUT
                )
                conn.request(self.command, self.path, body=body, headers=headers)
                resp = conn.getresponse()
                data = resp.read()
                conn.close()
            except Exception as e:
                with backend.lock:
                    backend.failures += 1
                backend.mark(False, f"(erro na requisição: {type(e).__name__})")
                continue
            finally:
                with backend.lock:
                    backend.active_connections -= 1

            self.send_response(resp.status)
            for k, v in resp.getheaders():
                if k.lower() not in HOP_BY_HOP and k.lower() != "content-length":
                    self.send_header(k, v)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("X-Backend", backend.name)
            self.send_header("X-LB-Algorithm", LB.algorithm.name)
            self.end_headers()
            self.wfile.write(data)
            return

        with LB.stats_lock:
            LB.total_errors += 1
        self._reply(503, {"erro": "Nenhum servidor disponível no momento"})

    do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = proxy

    def log_message(self, fmt, *args):
        pass


def main():
    global LB
    backends = parse_backends(
        os.getenv("BACKENDS", "localhost:5001,localhost:5002,localhost:5003")
    )
    LB = LoadBalancer(backends, os.getenv("ALGORITHM", "round_robin"))

    threading.Thread(target=LB.health_check_loop, daemon=True).start()

    ThreadingHTTPServer.daemon_threads = True
    ThreadingHTTPServer.request_queue_size = 1024
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), ProxyHandler)
    log(f"Balanceador na porta {PORT} | algoritmo: {LB.algorithm.name}")
    log("Backends: " + ", ".join(f"{b.name} (peso {b.weight})" for b in backends))
    httpd.serve_forever()


if __name__ == "__main__":
    main()
