import subprocess
import sys
import threading
import time
import urllib.request
from collections import Counter

LB_URL = "http://localhost:8080/"
ALVO = sys.argv[1] if len(sys.argv) > 1 else "shopnow-app2"
DURACAO = 24          
DERRUBAR_EM = 8       
RELIGAR_EM = 13      
THREADS = 6

contagem = Counter()
lock = threading.Lock()
rodando = True


def cliente():
    while rodando:
        try:
            with urllib.request.urlopen(LB_URL, timeout=5) as r:
                chave = r.headers.get("X-Server", "?")
        except Exception:
            chave = "ERRO"
        with lock:
            contagem[chave] += 1


def docker(acao):
    print(f"\n>>> docker {acao} {ALVO}\n", flush=True)
    subprocess.run(["docker", acao, ALVO], capture_output=True)


threads = [threading.Thread(target=cliente, daemon=True) for _ in range(THREADS)]
for t in threads:
    t.start()

print(f"Teste de falha: {DURACAO}s, derrubando {ALVO} em t={DERRUBAR_EM}s "
      f"e religando em t={RELIGAR_EM}s\n")
print(f"{'t(s)':>4} | {'app1':>6} {'app2':>6} {'app3':>6} | {'ERROS':>5}")
print("-" * 40)

total = Counter()
for seg in range(1, DURACAO + 1):
    if seg == DERRUBAR_EM:
        threading.Thread(target=docker, args=("stop",)).start()
    if seg == RELIGAR_EM:
        threading.Thread(target=docker, args=("start",)).start()
    time.sleep(1)
    with lock:
        snap = dict(contagem)
        contagem.clear()
    total.update(snap)
    print(f"{seg:>4} | {snap.get('app1', 0):>6} {snap.get('app2', 0):>6} "
          f"{snap.get('app3', 0):>6} | {snap.get('ERRO', 0):>5}", flush=True)

rodando = False
soma = sum(total.values())
print("-" * 40)
print(f"Total: {soma} requisições | erros vistos pelo cliente: {total.get('ERRO', 0)}")
