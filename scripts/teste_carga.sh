set -e

if [ "$1" = "wrk" ]; then
  docker run --rm --network shopnow_default williamyeh/wrk \
    -t4 -c200 -d20s --latency http://loadbalancer:8080/
  exit 0
fi

N=${1:-5000}
C=${2:-100}
ROTA=${3:-/}

echo "== Apache Benchmark: $N requisições, $C simultâneas, rota $ROTA =="
docker run --rm --network shopnow_default httpd:2.4-alpine \
  ab -n "$N" -c "$C" "http://loadbalancer:8080$ROTA"

echo
echo "== Distribuição registrada pelo balanceador =="
curl -s http://localhost:8080/lb/status
