import random

import networkx as nx
import scipy.spatial


def generateRandomCoordinates(N=100):
    out = []
    for i in range(N):
        out.append((random.random(), random.random()))
    return out


def dist(n1, n2):
    return ((n1[0] - n2[0])**2 + (n1[1] - n2[1])**2)**0.5


def dt(G):
    points = list(G.nodes())
    delaunay = scipy.spatial.Delaunay(points, qhull_options="QJ")

    # create a set for edges that are indexes of the points
    edges = set()
    # for each Delaunay triangle
    for n in range(delaunay.nsimplex):
        # iterate over the 3 vertices of the simplex
        for i, j in [(0, 1), (1, 2), (2, 0)]:
            # sorting since edges may appear multiple times,
            # if they are always sorted, the set will kill duplicates
            u, v = sorted((delaunay.vertices[n, i], delaunay.vertices[n, j]))
            edges.add((points[u], points[v]))

    G.add_edges_from(edges)

    return G


def rng(G):
    G = dt(G)
    to_remove = set()
    for c1, c2 in G.edges():
        if c1 == c2:
            continue
        d = dist(c1, c2)
        for possible_blocker in G.nodes():
            if c1 == possible_blocker or c2 == possible_blocker:
                continue
            distToC1 = dist(possible_blocker, c1)
            distToC2 = dist(possible_blocker, c2)
            if distToC1 < d and distToC2 < d:
                # this node is in the lune and blocks
                to_remove.add((c1, c2))
    G.remove_edges_from(to_remove)
    return G


def gg(G):
    G = dt(G)
    to_remove = set()
    for c1, c2 in G.edges():
        mid = ((c1[0] + c2[0]) / 2, (c1[1] + c2[1]) / 2)
        r = dist(c1, c2) / 2
        for possible_blocker in G.nodes():
            if c1 == possible_blocker or c2 == possible_blocker:
                continue
            if dist(possible_blocker, mid) <= r:
                # this node is in the lune and blocks
                to_remove.add((c1, c2))
    G.remove_edges_from(to_remove)
    return G


def mst(G):
    candidates = G.copy()
    dt(candidates)
    for u, v, d in candidates.edges(data=True):
        d['weight'] = dist(u, v)
    G = nx.minimum_spanning_tree(candidates)
    return G


def mr(G, r=None):
    # radius: minimum radius such that the graph is connected
    # -> longest edge of the minimum spanning tree half
    tmp = mst(G.copy())
    if r is None:
        r = max(e[2]["weight"] for e in tmp.edges(data=True))

    for c1 in G.nodes():
        for c2 in G.nodes():
            if c1 == c2:
                continue
            if dist(c1, c2) <= r:
                G.add_edge(c1, c2)
    return G


def random_points(N):
    coordinates = generateRandomCoordinates(N)

    G = nx.Graph()
    for x, y in coordinates:
        G.add_node((x, y), x=x, y=y)
    return G


def delaunay(N):
    G = random_points(N)

    G = dt(G)

    return G


def relative_neighborhood_graph(N):
    G = random_points(N)

    G = rng(G)

    return G


def gabriel_graph(N):
    G = random_points(N)

    G = gg(G)

    return G


def minimum_radius(N, r=None):
    G = random_points(N)

    G = mr(G, r)

    return G


def minimum_spanning_tree(N):
    G = random_points(N)

    G = mst(G)

    return G
