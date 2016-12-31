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
        text = "Erdős-Rényi, N = {}, m = {}".format(N, m)

        return G, text

    def generateNWS(self, N=None, k=None, p=None, s=None):
        if N is None: N = random.randint(4, 400)
        if k is None: k = random.randint(2, 5)
        if p is None: p = random.uniform(0, 0.2)
        if s is None: s = random.randint(0, 10**7)

        state = random.getstate()
        G = gen.newman_watts_strogatz_graph(N, k, p, s)
        random.setstate(state)
        text = "Newman-Watts-Strogatz, N = {}, k = {}, p = {:.2f}, s = {}".format(N, k, p, s)

        return G, text

    def generateRR(self, N=None, d=None):
        if N is None: N = random.randint(4, 400)
        if d is None: d = random.randint(1, 5)

        # the product of N*d must be even, otherwise the regular graph does not exist
        if N*d % 2:
            N += 1

        G = gen.random_regular_graph(d, N)
        text = "Random Regular, N = {}, d = {}".format(N, d)

        return G, text

    def generateBA(self, N=None, m=None):
        if N is None: N = random.randint(4, 400)
        if m is None: m = random.randint(1, 5)

        G = gen.barabasi_albert_graph(N, m)
        text = "Barabasi-Albert, N = {}, m = {}".format(N, m)

        return G, text


    def generatePLC(self, N=None, m=None, p=None):
        if N is None: N = random.randint(4, 400)
        if m is None: m = random.randint(1, 5)
        if p is None: p = random.random()

        G = gen.powerlaw_cluster_graph(N, m, p)
        text = "Powerlaw Cluster, N = {}, m = {}, p = {:.2f}".format(N, m, p)

        return G, text

    def generateDD(self, N=None, p=None, s=None):
        if N is None: N = random.randint(4, 400)
        if p is None: p = random.random()
        if s is None: s = random.randint(0, 10**7)

        state = random.getstate()
        G = gen.duplication_divergence_graph(N, p, s)
        random.setstate(state)
        text = "Duplication Divergence, N = {}, p = {:.2f}, s = {}".format(N, p, s)

        return G, text

    def generateRL(self, N=None, p1=None, p2=None, s=None):
        if N is None: N = random.randint(4, 400),
        if p1 is None: p1 = random.uniform(0, 4),
        if p2 is None: p2 = random.uniform(0, 4),
        if s is None: s = random.randint(0, 10**7)

        state = random.getstate()
        G = gen.random_lobster(N, p1, p2)
        random.setstate(state)
        text = "Random Lobster, N = {}, p1 = {:.2f}, p2 = {:.2f}, s = {}".format(N, p1, p2, s)

        return G, text

    def generateSpec(self, idx=None):
        if idx is None: idx = random.randint(0, len(generators)-1)

        # special graphs, group under one, such that they are rare
        generators = [gen.karate_club_graph,
                      gen.davis_southern_women_graph,
                      gen.florentine_families_graph]
        label = ["Karate Club", "Davis Southern Women", "Florentine Families"]
        G = generators[idx]()
        text = "{}, N = {}".format(label[idx], len(G.nodes()))

        return G, text

    def generateCaveman(self, l=None, k=None):
        if l is None: l=random.randint(1, 5),
        if k is None: k=random.randint(2, 9)

        G = nx.caveman_graph(l, k)
        text = "Caveman, N = {}, l = {}, k = {}".format(l*k, l, k)

        return G, text

    def generateRelaxedCaveman(self, ):
        if l is None: l = random.randint(1, 5),
        if k is None: k = random.randint(2, 9),
        if p is None: p = random.uniform(0.05, 0.3),
        if s is None: s = random.randint(0, 10**7)

        state = random.getstate()
        G = nx.relaxed_caveman_graph(l, k, p)
        random.setstate(state)
        text = "Relaxed Caveman, N = {}, l = {}, k = {}, p = {:.2f}, s = {}".format(l*k, l, k, p, s)

        return G, text

    def generateRNG(self, N=None):
        if N is None: N = random.randint(4, 400)

        state = random.getstate()
        G = proximity_graphs.relative_neighborhood_graph(N)
        random.setstate(state)
        text = "Relative Neighborhood Graph, N = {}".format(N)

        return G, text

    def generateGG(self, N=None):
        if N is None: N = random.randint(4, 400)

        state = random.getstate()
        G = proximity_graphs.gabriel_graph(N)
        random.setstate(state)
        text = "Gabriel Graph, N = {}".format(N)

        return G, text

