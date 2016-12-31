import random
import inspect

import networkx as nx
from networkx import generators as gen

from . import proximity_graphs


class RandomGraph:
    def __init__(self, seed=None):
        self.seed = seed
        random.seed(self.seed)

        # get all methods that generate graphs (convention: starts with 'generate')
        members = inspect.getmembers(RandomGraph)
        generators = [i[1] for i in sorted(members) if "generate" in i[0]]

        self.graphTypes = generators

    def randomGraph(self):
        gen = random.choice(self.graphTypes)

        return gen(self)

    def generateER(self, N=None, m=None):
        if N is None: N = random.randint(4, 400)
        if m is None: m = abs(int(random.gauss(N, N)))

        G = gen.gnm_random_graph(N, m)
        details = dict(name="Erdős-Rényi", N=N, m=m, seed=self.seed,
                       template="{name}, N = {N}, k = {k}, p = {p:.2f}, s = {s}")

        return G, details

    def generateNWS(self, N=None, k=None, p=None, s=None):
        if N is None: N = random.randint(4, 400)
        if k is None: k = random.randint(2, 5)
        if p is None: p = random.uniform(0, 0.2)
        if s is None: s = random.randint(0, 10**7)

        state = random.getstate()
        G = gen.newman_watts_strogatz_graph(N, k, p, s)
        random.setstate(state)
        details = dict(name="Newman-Watts-Strogatz", N=N, k=k, p=p, s=s, seed=self.seed,
                       template="{name}, N = {N}, k = {k}, p = {p:.2f}, s = {s}")

        return G, details

    def generateRR(self, N=None, d=None):
        if N is None: N = random.randint(4, 400)
        if d is None: d = random.randint(1, 5)

        # the product of N*d must be even, otherwise the regular graph does not exist
        if N*d % 2:
            N += 1

        G = gen.random_regular_graph(d, N)
        details = dict(name="Random Regular Graph", N=N, d=d, seed=self.seed,
                       template="{name}, N = {N}, d = {d}")

        return G, details

    def generateBA(self, N=None, m=None):
        if N is None: N = random.randint(4, 400)
        if m is None: m = random.randint(1, 5)

        G = gen.barabasi_albert_graph(N, m)
        details = dict(name="Barabási-Albert", N=N, m=m, seed=self.seed,
                       template="{name}, N = {N}, m = {m}")

        return G, details


    def generatePLC(self, N=None, m=None, p=None):
        if N is None: N = random.randint(4, 400)
        if m is None: m = random.randint(1, 5)
        if p is None: p = random.random()

        G = gen.powerlaw_cluster_graph(N, m, p)
        details = dict(name="Powerlaw Cluster Graph", N=N, m=m, p=p, seed=self.seed,
                       template="{name}, N = {N}, m = {m}, p = {p:.2f}")

        return G, details

    def generateDD(self, N=None, p=None, s=None):
        if N is None: N = random.randint(4, 400)
        if p is None: p = random.random()
        if s is None: s = random.randint(0, 10**7)

        state = random.getstate()
        G = gen.duplication_divergence_graph(N, p, s)
        random.setstate(state)
        details = dict(name="Duplication Divergence Graph", N=N, p=p, s=s, seed=self.seed,
                       template="{name}, N = {N}, p = {p:.2f}, s = {s}")

        return G, details

    def generateRL(self, N=None, p1=None, p2=None, s=None):
        if N is None: N = random.randint(4, 400),
        if p1 is None: p1 = random.uniform(0, 4),
        if p2 is None: p2 = random.uniform(0, 4),
        if s is None: s = random.randint(0, 10**7)

        state = random.getstate()
        G = gen.random_lobster(N, p1, p2)
        random.setstate(state)
        details = dict(name="Random Lobster Graph", N=N, p1=p1, p2=p2, s=s, seed=self.seed,
                       template="{name}, N = {N}, p1 = {p1:.2f}, p2 = {p2:.2f}, s = {s}")

        return G, details

    def generateSpec(self, idx=None):
        if idx is None: idx = random.randint(0, len(generators)-1)

        # special graphs, group under one, such that they are rare
        generators = [gen.karate_club_graph,
                      gen.davis_southern_women_graph,
                      gen.florentine_families_graph]
        label = ["Karate Club", "Davis Southern Women", "Florentine Families"]
        G = generators[idx]()
        details = dict(name=label[idx], N=len(G.nodes()), idx=idx, seed=self.seed,
                       template="{name}, N = {N}")

        return G, details

    def generateCaveman(self, l=None, k=None):
        if l is None: l=random.randint(1, 5),
        if k is None: k=random.randint(2, 9)

        G = nx.caveman_graph(l, k)
        details = dict(name="Caveman Graph", N=l*k, l=l, k=k, seed=self.seed,
                       template="{name}, N = {N}, l = {l}, k = {k}")

        return G, details

    def generateRelaxedCaveman(self, ):
        if l is None: l = random.randint(1, 5),
        if k is None: k = random.randint(2, 9),
        if p is None: p = random.uniform(0.05, 0.3),
        if s is None: s = random.randint(0, 10**7)

        state = random.getstate()
        G = nx.relaxed_caveman_graph(l, k, p)
        random.setstate(state)
        details = dict(name="Relaxed Caveman Graph", N=l*k, d=d, seed=self.seed,
                       template="{name}, N = {N}, l = {l}, k = {k}, p = {p:.2f}, s = {s}")

        return G, details

    def generateRNG(self, N=None):
        if N is None: N = random.randint(4, 400)

        state = random.getstate()
        G = proximity_graphs.relative_neighborhood_graph(N)
        random.setstate(state)
        details = dict(name="Relative Neighborhood Graph", N=N, seed=self.seed,
                       template="{name}, N = {N}")

        return G, details

    def generateGG(self, N=None):
        if N is None: N = random.randint(4, 400)

        state = random.getstate()
        G = proximity_graphs.gabriel_graph(N)
        random.setstate(state)
        details = dict(name="Gabriel Graph", N=N, seed=self.seed,
                       template="{name}, N = {N}")

        return G, details

