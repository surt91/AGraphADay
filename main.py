#!/usr/bin/env python3

import os
import sys
import time
import random
import base64
import warnings
from datetime import datetime

import networkx as nx
from networkx import generators as gen

from twitter_helper import tweet_pic
from proximity_graphs import relative_neighborhood_graph, gabriel_graph

absdir = os.path.abspath(os.path.dirname(__file__))


def has_explicit_coordinates(G):
    # Guess if the graph has explicit coordinates
    try:
        float((G.nodes()[0][0]))
        graph_has_coordinates = True
    except:
        graph_has_coordinates = False
    return graph_has_coordinates


def draw_graph(G, text, basename, command="neato"):
    from matplotlib import pyplot as plt
    from networkx.drawing.nx_agraph import graphviz_layout

    if has_explicit_coordinates(G):
        pos = {n: (n[0], n[1]) for n in G.nodes()}
        command = "explicit"
    else:
        pos = graphviz_layout(G, command)

    nx.draw(G, pos)
    ax = plt.gca()
    plt.text(0.99, 0.01, text,
            verticalalignment='bottom', 
            horizontalalignment='right',
            transform=ax.transAxes,
            fontsize=10)
    plt.savefig(basename+".svg")
    plt.savefig(basename+".png")

    details = "style = {}, layout = {}".format("default", command)

    return basename+".png", details


def draw_graphviz(G, text, basename, command="dot"):
    from networkx.drawing.nx_agraph import to_agraph, graphviz_layout
    A = to_agraph(G)
    A.write(basename+".dot")


def draw_cytoscape(G, text, basename):
    from networkx.drawing.nx_agraph import graphviz_layout
    # igraph uses deprecated things
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore",category=DeprecationWarning)
        from py2cytoscape.data.cyrest_client import CyRestClient
        from py2cytoscape.data.util_network import NetworkUtil as util
        from py2cytoscape.data.style import StyleUtil as s_util

    # fixme should be asked from the server
    styles = ["Sample3", "Sample3", "Curved", 
              "Ripple", "Sample2", "default black", "Minimal"]
    # http://localhost:1234/v1/apply/layouts/
    layouts = [ "stacked-node-layout",
                "circular", "kamada-kawai", "force-directed",
                "hierarchical", "isom"]

    graphviz = ["neato", "dot", "circo", "twopi", "fdp"]

    # only use for small graphs
    if len(G) < 60:
        layouts += graphviz

    style = random.choice(styles)
    layout = random.choice(layouts)

    # Create Client
    cy = CyRestClient()
    cy.session.delete()

    g_cy = cy.network.create_from_networkx(G)

    # assign lacations manual
    locations = []
    if has_explicit_coordinates(G):
        layout = "explicit"

        idmap = util.name2suid(g_cy)
        for v in G.nodes():
            locations.append([int(idmap[str(v)]), v[0]*1000, v[1]*1000])

    elif layout in graphviz:
        pos = graphviz_layout(G, layout)

        idmap = util.name2suid(g_cy)

        for k in pos.keys():
            v = pos[k]
            locations.append([int(idmap[k]), v[0] , v[1]])

    details = "style = {}, layout = {}".format(style, layout)

    # if there are explicit locations, use them
    if locations:
        cy.layout.apply_from_presets(g_cy, positions=locations)
    else:
        cy.layout.apply(network=g_cy, name=layout)

    style_s3 = cy.style.create(style)

    # do not show numbers at the nodes
    style_s3.create_discrete_mapping(column="name", vp="NODE_LABEL", mappings={g: "" for g in G})

    cy.style.apply(style=style_s3, network=g_cy)

    cy.layout.fit(g_cy)
    # cytoscape needs some time to rescale the graphic
    time.sleep(5)

    svg = g_cy.get_svg()
    with open(basename+".svg", "wb") as f:
        f.write(svg)

    png = g_cy.get_png(height=2000)
    with open(basename+".png", "wb") as f:
        f.write(png)

    return basename+".png", details


def get_random_graph(seed):
    random.seed(seed)
    total = 12

    idx = random.randint(1, total)
    N = random.randint(4, 400)

    if idx == 1:
        m = -1
        while m < 0:
            m = int(random.gauss(N, N))
        G = gen.gnm_random_graph(N, m)
        text = "Erdős-Rényi, N = {}, m = {} ({})".format(N, m, seed)

    elif idx == 2:
        k = random.randint(2, 5)
        p = random.uniform(0, 0.2)
        s = random.randint(0, 10**7)
        G = gen.newman_watts_strogatz_graph(N, k, p, s)
        text = "Newman-Watts-Strogatz, N = {}, k = {}, p = {:.2f}, s = {} ({})".format(N, k, p, s, seed)

    elif idx == 3:
        d = random.randint(1, 5)
        if N*d % 2:
            N += 1
        G = gen.random_regular_graph(d, N)
        text = "Random Regular, N = {}, d = {} ({})".format(N, d, seed)

    elif idx == 4:
        m = random.randint(1, 5)
        G = gen.barabasi_albert_graph(N, m)
        text = "Barabasi-Albert, N = {}, m = {} ({})".format(N, m, seed)

    elif idx == 5:
        m = random.randint(1, 5)
        p = random.random()
        G = gen.powerlaw_cluster_graph(N, m, p)
        text = "Powerlaw Cluster, N = {}, m = {}, p = {:.2f} ({})".format(N, m, p, seed)

    elif idx == 6:
        p = random.random()
        s = random.randint(0, 10**7)
        G = gen.duplication_divergence_graph(N, p, s)
        text = "Duplication Divergence, N = {}, p = {:.2f}, s = {} ({})".format(N, p, s, seed)

    elif idx == 7:
        p1 = random.uniform(0, 4)
        p2 = random.uniform(0, 4)
        G = gen.random_lobster(N, p1, p2)
        text = "Random Lobster, N = {}, p1 = {:.2f}, p2 = {:.2f} ({})".format(N, p1, p2, seed)

    elif idx == 8:
        # special graphs, group under one, such that they are rare
        generators = [gen.karate_club_graph,
                      gen.davis_southern_women_graph,
                      gen.florentine_families_graph]
        label = ["Karate Club", "Davis Southern Women", "Florentine Families"]
        j = random.randint(0, len(generators)-1)
        G = generators[j]()
        text = "{} ({})".format(label[j], seed)

    elif idx == 9:
        l = random.randint(2, 10)
        k = random.randint(1, 5)
        G = nx.caveman_graph(l, k)
        text = "Caveman, l = {}, k = {} ({})".format(l, k, seed)

    elif idx == 10:
        p = random.uniform(0.05, 0.3)
        l = random.randint(1, 5)
        k = random.randint(1, 5)
        G = nx.relaxed_caveman_graph(l, k, p)
        text = "Relaxed Caveman, l = {}, k = {}, p = {:.2f} ({})".format(l, k, p, seed)

    elif idx == 11:
        G = relative_neighborhood_graph(N)
        text = "Relative Neighborhood Graph, N = {}".format(N)

    elif idx == 12:
        G = gabriel_graph(N)
        text = "Gabriel Graph, N = {}".format(N)

    return G, text


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "test":
        seed = sys.argv[1]
    else:
        seed = base64.b64encode(os.urandom(8)).decode("ascii")

    print(seed)
    G, text = get_random_graph(seed)
    print(text)

    folder = os.path.join(absdir, "archive")
    os.makedirs(folder, exist_ok=True)
    basename = str(int(datetime.timestamp(datetime.now())))
    basename = os.path.join(folder, basename)

    try:
        path, details = draw_cytoscape(G, text, basename)
    except:
        path, details = draw_graph(G, text, basename, "neato")

    print(details)

    with open(basename+".txt", "w") as f:
        f.write(text)
        f.write("\n")
        f.write(details)
        f.write("\n")

    if not "test" in sys.argv:
        tweet_pic(path)

