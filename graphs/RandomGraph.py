import random
import inspect
from functools import wraps

import networkx as nx
from networkx import generators as gen

from . import proximity_graphs
from .visualize import CyStyle, CyLayout, GtLayout


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


layouts_all = CyLayout.layouts + GtLayout.layouts + ["blockmodel"]
def layout(layout_list):
    def layout_decorator(func):
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            G, details = func(*args, **kwargs)
            details["allowed_layouts"] = layout_list
            return G, details
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
    @layout(["kamada-kawai", "force-directed", "sfdp", "fruchterman_reingold", "arf"])
    def generateErdosRenyi(self, N=None, m=None, **kwargs):
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
    @layout(["circular", "kamada-kawai", "force-directed", "sfdp", "fruchterman_reingold", "arf", "radial_tree"])
    def generateNewmanWattsStrogatz(self, N=None, k=None, p=None, s=None, **kwargs):
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
    @layout(["kamada-kawai", "force-directed", "sfdp", "fruchterman_reingold", "arf", "radial_tree"])
    def generateRandomRegular(self, N=None, d=None, **kwargs):
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
    @layout(["kamada-kawai", "force-directed", "sfdp", "fruchterman_reingold", "arf", "radial_tree"])
    def generateBarabasiAlbert(self, N=None, m=None, **kwargs):
        if N is None: N = random.randint(4, 400)
        if m is None: m = random.randint(1, 5)

        G = gen.barabasi_albert_graph(N, m)
        details = dict(name="Barabási-Albert Graph", N=N, m=m, seed=self.seed,
                       template="{name}, N = {N}, m = {m}")

        return G, details

    @synonym("power law cluster")
    @synonym("power law")
    @synonym("powerlaw")
    @synonym("powerlaw cluster")
    @style(styles_all)
    @layout(["kamada-kawai", "force-directed", "sfdp", "fruchterman_reingold", "arf", "radial_tree", "blockmodel"])
    def generatePowerLawCluster(self, N=None, m=None, p=None, **kwargs):
        if N is None: N = random.randint(4, 400)
        if m is None: m = random.randint(1, 5)
        if p is None: p = random.random()

        G = gen.powerlaw_cluster_graph(N, m, p)
        details = dict(name="Powerlaw Cluster Graph", N=N, m=m, p=p, seed=self.seed,
                       template="{name}, N = {N}, m = {m}, p = {p:.2f}")

        return G, details

    @synonym("duplication divergence")
    @style(styles_all)
    @layout(["kamada-kawai", "force-directed", "sfdp", "fruchterman_reingold", "arf", "radial_tree", "blockmodel"])
    def generateDuplicationDivergence(self, N=None, p=None, s=None, **kwargs):
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
    @layout(["kamada-kawai", "force-directed", "sfdp", "fruchterman_reingold", "arf", "radial_tree"])
    def generateRandomLobster(self, N=None, p1=None, p2=None, s=None, **kwargs):
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
    @layout(["kamada-kawai", "force-directed", "sfdp", "fruchterman_reingold", "arf", "blockmodel"])
    def generateSpecial(self, idx=None, **kwargs):
        # special graphs, group under one, such that they are rare
        generators = [gen.karate_club_graph,
                      gen.davis_southern_women_graph,
                      gen.florentine_families_graph]
        label = ["Zachary’s Karate Club",
                 "Davis Southern Women",
                 "Florentine Families"]

        if idx is None: idx = random.randint(0, len(generators)-1)
        G = generators[idx]()
        details = dict(name=label[idx], N=len(G.nodes()), idx=idx, seed=self.seed,
                       template="{name}, N = {N}")

        return G, details

    @synonym("Zachary’s Karate Club")
    def karate(self, **kwargs):
        return self.generateSpecial(0, **kwargs)

    @synonym("Davis Southern Women")
    def davis(self, **kwargs):
        return self.generateSpecial(1, **kwargs)

    @synonym("Florentine Families")
    def florentine(self, **kwargs):
        return self.generateSpecial(2, **kwargs)

    @synonym("real world network")
    @style(styles_all)
    @layout(["kamada-kawai", "force-directed", "sfdp", "fruchterman_reingold", "arf", "blockmodel"])
    def generateRealWorld(self, idx=None, **kwargs):
        files = ["adjnoun",
                 "celegansneural",
                 "dolphins",
                 "football",
                 "lesmis",
                 "polbooks"]
        label = ["word adjacencies in David Copperfield by Charles Dickens",
                 "neural network of c. elegans",
                 "a dolphin social network",
                 "American college football",
                 "Les Misérables",
                 "Amazon's copurchases of political books"]

        if idx is None: idx = random.randint(0, len(files)-1)

        G = nx.read_gml("graphs/networks/{}.gml".format(files[idx]))
        details = dict(name=label[idx],
                       N=len(G.nodes()),
                       idx=idx,
                       seed=self.seed,
                       template="{name}, N = {N}")

        return G, details

    @synonym("word adjacencies")
    @synonym("David Copperfield")
    def adjnoun(self, **kwargs):
        return self.generateRealWorld(0, **kwargs)

    @synonym("c. elegans")
    @synonym("neural network")
    def celegans(self, **kwargs):
        return self.generateRealWorld(1, **kwargs)

    @synonym("dolphins")
    def dolphins(self, **kwargs):
        return self.generateRealWorld(2, **kwargs)

    @synonym("american football")
    def football(self, **kwargs):
        return self.generateRealWorld(3, **kwargs)

    @synonym("Les Miserables")
    @synonym("book")
    def lesmis(self, **kwargs):
        return self.generateRealWorld(4, **kwargs)

    @synonym("political books")
    def polbooks(self, **kwargs):
        return self.generateRealWorld(5, **kwargs)

    @synonym("science")
    @synonym("citation")
    @style(styles_all)
    @layout(["kamada-kawai", "sfpd", "arf", "radial_tree"])
    def generateScience(self, idx=None, **kwargs):
        files = ["astro-ph",
                 "cond-mat",
                 "cond-mat-2003",
                 "cond-mat-2005",
                 "hep-th",
                 "netscience"]
        label = ["citations astrophysics (1995-2000)",
                 "citations condensed matter (1995-2000)",
                 "citations condensed matter (1995-2003)",
                 "citations condensed matter (1995-2005)",
                 "citations high energy physics (1995-2000)",
                 "citations network science (until 2006)"]

        if idx is None: idx = random.randint(0, len(files)-1)

        G = nx.read_gml("graphs/networks/{}.gml".format(files[idx]))
        details = dict(name=label[idx],
                       N=len(G.nodes()),
                       idx=idx,
                       seed=self.seed,
                       template="{name}, N = {N}")

        return G, details

    @synonym("astro physics")
    def astro(self, **kwargs):
        return self.generateScience(0, **kwargs)

    @synonym("condensed matter physics")
    def condmat(self, **kwargs):
        return self.generateScience(1, **kwargs)

    @synonym("high energy physics")
    def hep(self, **kwargs):
        return self.generateScience(4, **kwargs)

    @synonym("netscience")
    def netsci(self, **kwargs):
        return self.generateScience(5, **kwargs)

    @synonym("caveman")
    @synonym("clique")
    @style(styles_all)
    @layout(["kamada-kawai", "force-directed", "sfdp", "fruchterman_reingold", "arf", "radial_tree", "blockmodel"])
    def generateCaveman(self, N=None, l=None, k=None, **kwargs):
        if l is None: l = random.randint(1, 8)
        if k is None: k = random.randint(2, 14)

        if N is not None: k = N//l

        G = nx.caveman_graph(l, k)
        details = dict(name="Caveman Graph", N=l*k, l=l, k=k, seed=self.seed,
                       template="{name}, N = {N}, l = {l}, k = {k}")

        return G, details

    @synonym("relaxed caveman")
    @style(styles_all)
    @layout(["kamada-kawai", "force-directed", "sfdp", "fruchterman_reingold", "arf", "radial_tree", "blockmodel"])
    def generateRelaxedCaveman(self, N=None, l=None, k=None, p=None, s=None, **kwargs):
        if l is None: l = random.randint(1, 8)
        if k is None: k = random.randint(2, 14)
        if p is None: p = random.uniform(0.05, 0.3)
        if s is None: s = random.randint(0, 10**7)

        if N is not None: k = N//l

        state = random.getstate()
        G = nx.relaxed_caveman_graph(l, k, p)
        random.setstate(state)
        details = dict(name="Relaxed Caveman Graph", N=l*k, l=l, k=k, p=p, s=s, seed=self.seed,
                       template="{name}, N = {N}, l = {l}, k = {k}, p = {p:.2f}, s = {s}")

        return G, details

    @synonym("relative neighborhood")
    @style(styles_all)
    @layout(layouts_all)
    def generateRelativeNeighborhood(self, N=None, **kwargs):
        if N is None: N = random.randint(20, 800)

        state = random.getstate()
        G = proximity_graphs.relative_neighborhood_graph(N)
        random.setstate(state)
        details = dict(name="Relative Neighborhood Graph", N=N, seed=self.seed,
                       template="{name}, N = {N}")

        return G, details

    @synonym("gabriel")
    @style(styles_all)
    @layout(layouts_all)
    def generateGabriel(self, N=None, **kwargs):
        if N is None: N = random.randint(20, 800)

        state = random.getstate()
        G = proximity_graphs.gabriel_graph(N)
        random.setstate(state)
        details = dict(name="Gabriel Graph", N=N, seed=self.seed,
                       template="{name}, N = {N}")

        return G, details

    @synonym("barbell")
    @style(styles_all)
    @layout(["kamada-kawai", "force-directed", "sfdp", "fruchterman_reingold", "arf", "radial_tree", "blockmodel"])
    def generateBarbell(self, N=None, m1=None, m2=None, **kwargs):
        if m1 is None: m1 = random.randint(3, 20)
        if m2 is None: m2 = random.randint(1, 20)
        if N is not None:
            m1 = random.randint(3, N/2-2)
            m2 = N - 2*m1

        G = gen.barbell_graph(m1, m2)
        details = dict(name="Barbell Graph", N=len(G.nodes()), m1=m1, m2=m2, seed=self.seed,
                       template="{name}, N = {N}, m1 = {m1}, m2 = {m2}")

        return G, details

    @synonym("ladder")
    @style(styles_all)
    @layout(["kamada-kawai", "force-directed", "sfdp", "fruchterman_reingold", "arf", "radial_tree"])
    def generateCircularLadder(self, n=None, **kwargs):
        if n is None: n = random.randint(3, 400)

        G = gen.circular_ladder_graph(n)
        details = dict(name="Circular Ladder Graph", N=len(G.nodes()), n=n, seed=self.seed,
                       template="{name}, N = {N}, n = {n}")

        return G, details

    @synonym("Dorogovtsev Goltsev Mendes")
    @synonym("fractal")
    @style(styles_all)
    @layout(["kamada-kawai", "force-directed", "sfdp", "fruchterman_reingold", "arf", "radial_tree", "blockmodel"])
    def generateDorogovtsevGoltsevMendes(self, n=None, **kwargs):
        if n is None: n = random.randint(2, 7)

        G = gen.dorogovtsev_goltsev_mendes_graph(n)
        details = dict(name="Dorogovtsev-Goltsev-Mendes Graph", N=len(G.nodes()), n=n, seed=self.seed,
                       template="{name}, N = {N}, n = {n}")

        return G, details

    @synonym("partition")
    @style(styles_all)
    @layout(["kamada-kawai", "force-directed", "sfdp", "fruchterman_reingold", "arf", "radial_tree", "blockmodel"])
    def generateRandomPartition(self, sizes=None, p1=None, p2=None, s=None, **kwargs):
        if sizes is None: sizes = [random.randint(6, 120) for _ in range(random.randint(2, 3))]
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
    @layout(["kamada-kawai", "force-directed", "sfdp", "fruchterman_reingold", "arf", "radial_tree"])
    def generateRandomIntersection(self, n=None, m=None, p=None, s=None, **kwargs):
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
    @layout(layouts_all)
    def generateMinimumRadius(self, N=None, r=None, **kwargs):
        if N is None: N = random.randint(20, 800)
        if r is None: r = random.uniform(0.05, 0.3)

        state = random.getstate()
        G = proximity_graphs.minimum_radius(N, r)
        random.setstate(state)

        details = dict(name="Minimum Radius Graph", N=N, r=r, seed=self.seed,
                       template="{name}, N = {N}, r = {r}")

        return G, details
