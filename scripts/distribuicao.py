import sys
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

LB_URL = "http://localhost:8080"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
PATH = sys.argv[2] if len(sys.argv) > 2 else "/"
CONCORRENCIA = int(sys.argv[3]) if len(sys.argv) > 3 else 1


def req(_):
    try:
        with urllib.request.urlopen(LB_URL + PATH, timeout=10) as r:
            return r.headers.get("X-Server", "?")
    except Exception as e:
        return f"ERRO ({type(e).__name__})"


with ThreadPoolExecutor(CONCORRENCIA) as pool:
    ordem = list(pool.map(req, range(N)))

with urllib.request.urlopen(LB_URL + "/lb/status") as r:
    import json
    algoritmo = json.load(r)["algorithm"]

print(f"Algoritmo: {algoritmo} | {N} requisições em {PATH} | concorrência {CONCORRENCIA}\n")
if N <= 30:
    print("Ordem:", " → ".join(ordem), "\n")
for servidor, qtd in sorted(Counter(ordem).items()):
    barra = "█" * round(qtd / N * 50)
    print(f"  {servidor:<8} {qtd:>5}  ({qtd / N:6.1%})  {barra}")
