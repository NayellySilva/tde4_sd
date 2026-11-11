import random
import threading


class Algoritmos:
    name = "base"

    def __init__(self):
        self.lock = threading.Lock()

    def choose(self, backends):
        raise NotImplementedError


class RoundRobin(Algoritmos):
    name = "round_robin"

    def __init__(self):
        super().__init__()
        self.counter = 0

    def choose(self, backends):
        with self.lock:
            backend = backends[self.counter % len(backends)]
            self.counter += 1
            return backend


class LeastConnections(Algoritmos):

    name = "least_connections"

    def choose(self, backends):
        with self.lock:
            menor = min(b.active_connections for b in backends)
            candidatos = [b for b in backends if b.active_connections == menor]
            return random.choice(candidatos)


class WeightedRoundRobin(Algoritmos):

    name = "weighted_round_robin"

    def __init__(self):
        super().__init__()
        self.current = {}

    def choose(self, backends):
        with self.lock:
            total = 0
            melhor = None
            for b in backends:
                self.current[b.name] = self.current.get(b.name, 0) + b.weight
                total += b.weight
                if melhor is None or self.current[b.name] > self.current[melhor.name]:
                    melhor = b
            self.current[melhor.name] -= total
            return melhor


class RandomChoice(Algoritmos):

    name = "random"

    def choose(self, backends):
        return random.choice(backends)


ALGORITMOS = {
    cls.name: cls
    for cls in (RoundRobin, LeastConnections, WeightedRoundRobin, RandomChoice)
}


def get_algorithm(name: str) -> Algoritmos:
    if name not in ALGORITMOS:
        raise ValueError(
            f"Algoritmo '{name}' inválido. Opções: {', '.join(ALGORITMOS)}"
        )
    return ALGORITMOS[name]()
