import random
import inspect
from functools import wraps

import networkx as nx
from networkx import generators as gen

from . import proximity_graphs
from .visualize import CyStyle


# decorator to add synonyms of the graph types
# this enables us to do a fuzzy matching
synonyms = {}
def synonym(synonym_name):
    def synonym_decorator(func):
        synonyms[synonym_name] = func

        @wraps(func)
        def func_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return func_wrapper
    return synonym_decorator



styles_all = CyStyle().styles
def style(style_list):
    def style_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            G, details = func(*args, **kwargs)
            details["allowed_styles"] = style_list
            return G, details
        return func_wrapper
    return style_decorator


layouts_all = ["circular", "kamada-kawai", "force-directed", "hierarchical", "isom"]
layouts= {}
def layout(layout_name):
    def layout_decorator(func):
        layout[func.__name__] = layout_name

        @wraps(func)
        def func_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return func_wrapper
    return layout_decorator


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

    @synonym("Erdos Renyi")
    @synonym("Erdős-Rényi")
    @style(styles_all)
    def generateErdosRenyi(self, N=None, m=None):
        if N is None: N = random.randint(4, 400)
        if m is None: m = abs(int(random.gauss(N, N)))

        G = gen.gnm_random_graph(N, m)
        details = dict(name="Erdős-Rényi Graph", N=N, m=m, seed=self.seed,
                       template="{name}, N = {N}, m = {m}")

        return G, details

    @synonym("Watts Strogatz")
    @synonym("Newman Watts Strogatz")
    @synonym("small world")
    @style(styles_all)
    def generateNewmanWattsStrogatz(self, N=None, k=None, p=None, s=None):
        if N is None: N = random.randint(4, 400)
        if k is None: k = random.randint(2, 5)
        if p is None: p = random.uniform(0, 0.2)
        if s is None: s = random.randint(0, 10**7)

        state = random.getstate()
        G = gen.newman_watts_strogatz_graph(N, k, p, s)
        random.setstate(state)
        details = dict(name="Newman-Watts-Strogatz Graph", N=N, k=k, p=p, s=s, seed=self.seed,
                       template="{name}, N = {N}, k = {k}, p = {p:.2f}, s = {s}")

        return G, details

    @synonym("Random Regular")
    @style(styles_all)
    def generateRandomRegular(self, N=None, d=None):
        if N is None: N = random.randint(4, 400)
        if d is None: d = random.randint(1, 5)

        # the product of N*d must be even, otherwise the regular graph does not exist
        if N*d % 2:
            N += 1

        G = gen.random_regular_graph(d, N)
        details = dict(name="Random Regular Graph", N=N, d=d, seed=self.seed,
                       template="{name}, N = {N}, d = {d}")

        return G, details

    @synonym("Barabasi Albert")
    @synonym("preferential attachment")
    @style(styles_all)
    def generateBarabasiAlbert(self, N=None, m=None):
        if N is None: N = random.randint(4, 400)
        if m is None: m = random.randint(1, 5)

        G = gen.barabasi_albert_graph(N, m)
        details = dict(name="Barabási-Albert Graph", N=N, m=m, seed=self.seed,
                       template="{name}, N = {N}, m = {m}")

        return G, details

    @synonym("power law cluster")
    @synonym("power law")
    @style(styles_all)
    def generatePowerLawCluster(self, N=None, m=None, p=None):
        if N is None: N = random.randint(4, 400)
        if m is None: m = random.randint(1, 5)
        if p is None: p = random.random()

        G = gen.powerlaw_cluster_graph(N, m, p)
        details = dict(name="Powerlaw Cluster Graph", N=N, m=m, p=p, seed=self.seed,
                       template="{name}, N = {N}, m = {m}, p = {p:.2f}")

        return G, details

    @synonym("duplication divergence")
    @style(styles_all)
    def generateDuplicationDivergence(self, N=None, p=None, s=None):
        if N is None: N = random.randint(4, 400)
        if p is None: p = random.random()
        if s is None: s = random.randint(0, 10**7)

        state = random.getstate()
        G = gen.duplication_divergence_graph(N, p, s)
        random.setstate(state)
        details = dict(name="Duplication Divergence Graph", N=N, p=p, s=s, seed=self.seed,
                       template="{name}, N = {N}, p = {p:.2f}, s = {s}")

        return G, details

    @synonym("lobster")
    @style(styles_all)
    def generateRandomLobster(self, N=None, p1=None, p2=None, s=None):
        if N is None: N = random.randint(4, 400)
        if p1 is None: p1 = random.uniform(0, 4)
        if p2 is None: p2 = random.uniform(0, 4)
        if s is None: s = random.randint(0, 10**7)

        state = random.getstate()
        G = gen.random_lobster(N, p1, p2)
        random.setstate(state)
        details = dict(name="Random Lobster Graph", N=N, p1=p1, p2=p2, s=s, seed=self.seed,
                       template="{name}, N = {N}, p1 = {p1:.2f}, p2 = {p2:.2f}, s = {s}")

        return G, details

    @synonym("social network")
    @style(styles_all)
    def generateSpecial(self, idx=None):
        if idx is None: idx = random.randint(0, len(generators)-1)

        # special graphs, group under one, such that they are rare
        generators = [gen.karate_club_graph,
                      gen.davis_southern_women_graph,
                      gen.florentine_families_graph]
        label = ["Zachary’s Karate Club", "Davis Southern Women", "Florentine Families"]
        G = generators[idx]()
        details = dict(name=label[idx], N=len(G.nodes()), idx=idx, seed=self.seed,
                       template="{name}, N = {N}")

        return G, details

    @synonym("caveman")
    @synonym("clique")
    @style(styles_all)
    def generateCaveman(self, l=None, k=None):
        if l is None: l = random.randint(1, 5)
        if k is None: k = random.randint(2, 9)

        G = nx.caveman_graph(l, k)
        details = dict(name="Caveman Graph", N=l*k, l=l, k=k, seed=self.seed,
                       template="{name}, N = {N}, l = {l}, k = {k}")

        return G, details

    @synonym("relaxed caveman")
    @style(styles_all)
    def generateRelaxedCaveman(self, l=None, k=None, p=None, s=None):
        if l is None: l = random.randint(1, 5)
        if k is None: k = random.randint(2, 9)
        if p is None: p = random.uniform(0.05, 0.3)
        if s is None: s = random.randint(0, 10**7)

        state = random.getstate()
        G = nx.relaxed_caveman_graph(l, k, p)
        random.setstate(state)
        details = dict(name="Relaxed Caveman Graph", N=l*k, l=l, k=k, p=p, s=s, seed=self.seed,
                       template="{name}, N = {N}, l = {l}, k = {k}, p = {p:.2f}, s = {s}")

        return G, details

    @synonym("relative neighborhood")
    @style(styles_all)
    def generateRelativeNeighborhood(self, N=None):
        if N is None: N = random.randint(20, 400)

        state = random.getstate()
        G = proximity_graphs.relative_neighborhood_graph(N)
        random.setstate(state)
        details = dict(name="Relative Neighborhood Graph", N=N, seed=self.seed,
                       template="{name}, N = {N}")

        return G, details

    @synonym("gabriel")
    @style(styles_all)
    def generateGabriel(self, N=None):
        if N is None: N = random.randint(20, 400)

        state = random.getstate()
        G = proximity_graphs.gabriel_graph(N)
        random.setstate(state)
        details = dict(name="Gabriel Graph", N=N, seed=self.seed,
                       template="{name}, N = {N}")

        return G, details

    @synonym("barbell")
    @style(styles_all)
    def generateBarbell(self, m1=None, m2=None):
        if m1 is None: m1 = random.randint(3, 20)
        if m2 is None: m2 = random.randint(1, 20)

        G = gen.barbell_graph(m1, m2)
        details = dict(name="Barbell Graph", N=len(G.nodes()), m1=m1, m2=m2, seed=self.seed,
                       template="{name}, N = {N}, m1 = {m1}, m2 = {m2}")

        return G, details

    @synonym("circular ladder")
    @style(styles_all)
    def generateCircularLadder(self, n=None):
        if n is None: n = random.randint(3, 200)

        G = gen.circular_ladder_graph(n)
        details = dict(name="Circular Ladder Graph", N=len(G.nodes()), n=n, seed=self.seed,
                       template="{name}, N = {N}, n = {n}")

        return G, details

    @synonym("Dorogovtsev Goltsev Mendes")
    @synonym("fractal")
    @style(styles_all)
    def generateDorogovtsevGoltsevMendes(self, n=None):
        if n is None: n = random.randint(2, 7)

        G = gen.dorogovtsev_goltsev_mendes_graph(n)
        details = dict(name="Dorogovtsev-Goltsev-Mendes Graph", N=len(G.nodes()), n=n, seed=self.seed,
                       template="{name}, N = {N}, n = {n}")

        return G, details

    @synonym("partition")
    @style(styles_all)
    def generateRandomPartition(self, sizes=None, p1=None, p2=None, s=None):
        if sizes is None: sizes = [random.randint(6, 20) for _ in range(random.randint(2, 3))]
        if p1 is None: p1 = random.uniform(0.2, 0.8)
        if p2 is None: p2 = random.uniform(0.0, 0.1)
        if s is None: s = random.randint(0, 10**7)

        state = random.getstate()
        G = gen.random_partition_graph(sizes, p1, p2, s)
        random.setstate(state)
        details = dict(name="Random Partition Graph", N=len(G.nodes()), sizes=sizes, p1=p1, p2=p2, s=s, seed=self.seed,
                       template="{name}, N = {N}, sizes = {sizes}, p1 = {p1:.2f}, p2 = {p2:.2f}, s = {s}")

        return G, details

    @synonym("bipartite")
    @synonym("random intersection")
    @style(styles_all)
    def generateRandomIntersection(self, n=None, m=None, p=None, s=None):
        if n is None: n = random.randint(3, 100)
        if m is None: m = random.randint(3, 100)
        if p is None: p = random.random()
        if s is None: s = random.randint(0, 10**7)

        state = random.getstate()
        G = gen.uniform_random_intersection_graph(n, m, p, s)
        random.setstate(state)

        details = dict(name="Random Intersection Graph", N=len(G.nodes()), n=n, m=m, p=p, s=s, seed=self.seed,
                       template="{name}, N = {N}, n = {n}, m = {m}, p = {p:.2f}, s = {s}")

        return G, details

    @synonym("geometric graph")
    @synonym("minimum radius")
    @style(styles_all)
    def generateMinimumRadius(self, N=None, r=None):
        if N is None: N = random.randint(20, 400)
        if r is None: r = random.uniform(0.05, 0.3)

        state = random.getstate()
        G = proximity_graphs.minimum_radius(N, r)
        random.setstate(state)

        details = dict(name="Minimum Radius Graph", N=N, r=r, seed=self.seed,
                       template="{name}, N = {N}, r = {r}")

        return G, details

