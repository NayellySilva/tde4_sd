# ShopNow – Balanceador de Carga

Projeto da disciplina de Sistemas Distribuídos (TDE 4): uma loja virtual simples (**ShopNow**) rodando em 3 instâncias, com um **balanceador de carga** feito em Python na frente delas.

## Estrutura

```
app/        # Loja ShopNow (servidor HTTP em Python)
balancer/   # Balanceador de carga com health check e failover
scripts/    # Testes de carga, comparação de algoritmos e simulação de falha
docker-compose.yml
```

## Funcionalidades

- 3 instâncias da loja (`app1`, `app2`, `app3`), cada uma identificada pelo cabeçalho `X-Server`
- Algoritmos de balanceamento: `round_robin`, `least_connections`, `weighted_round_robin` e `random`
- Health check periódico (`/health`) e failover automático quando uma instância cai
- Painel web para acompanhar as instâncias e trocar o algoritmo em tempo real

## Como executar

Pré-requisito: Docker e Docker Compose.

```bash
docker compose up --build
```

Para escolher o algoritmo ao subir:

```bash
ALGORITHM=least_connections docker compose up --build
```

## Endereços

| URL | Descrição |
|-----|-----------|
| http://localhost:8080/ | Loja (passando pelo balanceador) |
| http://localhost:8080/lb/painel | Painel do balanceador |
| http://localhost:8080/lb/status | Status das instâncias (JSON) |
| http://localhost:8080/lb/algorithm?name=round_robin | Troca o algoritmo |

## Testes

```bash
# Teste de carga (Apache Benchmark): requisições, concorrência, rota
bash scripts/teste_carga.sh 5000 100 /

# Compara os 4 algoritmos
bash scripts/comparar_algoritmos.sh

# Mostra como as requisições foram distribuídas entre as instâncias
python3 scripts/distribuicao.py 30

# Derruba e religa uma instância durante o teste para mostrar o failover
python3 scripts/simular_falha.py shopnow-app2
```

## Configuração

Variáveis do balanceador no `docker-compose.yml`:

- `BACKENDS`: instâncias no formato `host:porta:peso`
- `ALGORITHM`: algoritmo inicial
- `HEALTH_INTERVAL`: intervalo do health check (segundos)
- `MAX_RETRIES`: tentativas em outra instância quando uma falha

## Autora

Nayelly Silva
