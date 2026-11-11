N=${1:-3000}
C=${2:-50}
ROTA=${3:-/api/checkout}

for ALG in round_robin least_connections weighted_round_robin random; do
  curl -s "http://localhost:8080/lb/algorithm?name=$ALG" > /dev/null
  echo "--------------- $ALG ---------------"
  docker run --rm --network shopnow_default httpd:2.4-alpine \
    ab -q -n "$N" -c "$C" "http://loadbalancer:8080$ROTA" \
    | grep -E "Requests per second|Time per request:.*\(mean\)|Failed requests|  95%"
  python3 scripts/distribuicao.py 300 / 10 | tail -n 3
  echo
done
