import random

import networkx as nx


def generateRandomCoordinates(N=100):
    out = []
    for i in range(N):
        out.append((random.random(),random.random()))
    return out


def dist(n1, n2):
    return ((n1[0] - n2[0])**2 + (n1[1] - n2[1])**2)**0.5


def rng(G):
    for c1 in G.nodes():
        for c2 in G.nodes():
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
                    break
            else:
                G.add_edge(c1, c2)


def gg(G):
    for c1 in G.nodes():
        for c2 in G.nodes():
            if c1 == c2:
                continue
            mid = ((c1[0]+c2[0])/2, (c1[1]+c2[1])/2)
            r = dist(c1, c2)/2
            for possible_blocker in G.nodes():
                if c1 == possible_blocker or c2 == possible_blocker:
                    continue
                if dist(possible_blocker, mid) <= r:
                    # this node is in the lune and blocks
                    break
            else:
                G.add_edge(c1, c2)


def mr(G, r):
    for c1 in G.nodes():
        for c2 in G.nodes():
            if c1 == c2:
                continue
            if dist(c1, c2) < r:
                G.add_edge(c1, c2)


def relative_neighborhood_graph(N):
    coordinates = generateRandomCoordinates(N)

    G = nx.Graph()
    for x, y in coordinates:
        G.add_node((x, y), x=x, y=y)

    pos = {n: (n[0], n[1]) for n in G.nodes()} 

    rng(G)

    return G

def gabriel_graph(N):
    coordinates = generateRandomCoordinates(N)

    G = nx.Graph()
    for x, y in coordinates:
        G.add_node((x, y), x=x, y=y)

    pos = {n: (n[0], n[1]) for n in G.nodes()} 

    gg(G)

    return G

def minimum_radius(N, r):
    coordinates = generateRandomCoordinates(N)

    G = nx.Graph()
    for x, y in coordinates:
        G.add_node((x, y), x=x, y=y)

    pos = {n: (n[0], n[1]) for n in G.nodes()}

    mr(G, r)

    return G

