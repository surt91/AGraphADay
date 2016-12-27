import os
import sys
import random
import base64

from datetime import datetime

import networkx as nx
from networkx import generators as gen

import twitter


def tweet_pic(path):
    api = twitter.Api(**keys_and_secrets)
    api.PostMedia("", path)


def draw_graph(G, text, basename, command="neato"):
    from matplotlib import pyplot as plt
    from networkx.drawing.nx_agraph import to_agraph, graphviz_layout
    
    pos = graphviz_layout(G, command)
    nx.draw(G, pos)
    ax = plt.gca()
    plt.text(0.99, 0.01, text,
            verticalalignment='bottom', horizontalalignment='right',
            transform=ax.transAxes,
            fontsize=10)
    plt.savefig(basename+".svg")


def draw_graphviz(G, text, basename, command="dot"):
    from networkx.drawing.nx_agraph import to_agraph, graphviz_layout
    A = to_agraph(G)
    A.write(basename+".dot")


def draw_cytoscape(G, text, basename):
    from py2cytoscape.data.cyrest_client import CyRestClient
    from py2cytoscape.data.util_network import NetworkUtil as util
    from py2cytoscape.data.style import StyleUtil as s_util

    # fixme should be asked from the server
    styles = ["Sample3", "Sample3", "Curved", 
              "Ripple", "Sample2", "default black", "Minimal"]
    # http://localhost:1234/v1/apply/layouts/
    layouts = ["stacked-node-layout", "degree-circle", 
                "circular", "kamada-kawai", "force-directed",
                "grid", "hierarchical", "fruchterman-rheingold", "isom"]

    style = random.choice(styles)
    layout = random.choice(layouts)

    details = "style = {}, layout = {}".format(style, layout)

    # Create Client
    cy = CyRestClient()
    # Clear current session
    cy.session.delete()
    
    g_cy = cy.network.create_from_networkx(G)

    cy.layout.apply(network=g_cy, name=layout)
    style_s3 = cy.style.create(style)
    # do not show numbers at the nodes
    style_s3.create_discrete_mapping(column="name", vp="NODE_LABEL", mappings={g: "" for g in G})

    cy.style.apply(style=style_s3, network=g_cy)

    png = g_cy.get_png(height=2000)
    with open(basename+".png", "wb") as f:
        f.write(png)

    svg = g_cy.get_svg()
    with open(basename+".svg", "wb") as f:
        f.write(svg)

    return basename+".png", details


def get_random_graph(seed):
    random.seed(seed)
    total = 5
    
    idx = random.randint(1, total)
    N = random.randint(4, 100)

    if idx == 1:
        m = -1
        while m < 0:
            m = int(random.gauss(N, N))
        G = gen.gnm_random_graph(N, m)
        text = "Erdős-Rényi, N = {}, m = {}, ({})".format(N, m, seed)

    elif idx == 2:
        k = random.randint(2, 5)
        p = random.uniform(0, 0.2)
        s = random.randint(0, 10**7)
        G = gen.newman_watts_strogatz_graph(N, k, p, s)
        text = "Newman-Watts-Strogatz, N = {}, k = {}, p = {:.2f}, s = {}, ({})".format(N, k, p, s, seed)

    elif idx == 3:
        d = random.randint(1, 5)
        if N*d % 2:
            N += 1
        G = gen.random_regular_graph(d, N)
        text = "Random Regular, N = {}, d = {}, ({})".format(N, d, seed)

    elif idx == 4:
        m = random.randint(1, 5)
        G = gen.barabasi_albert_graph(N, m)
        text = "Barabasi-Albert, N = {}, m = {}, ({})".format(N, m, seed)

    elif idx == 5:
        m = random.randint(1, 5)
        p = random.random()
        G = gen.powerlaw_cluster_graph(N, m, p)
        text = "Powerlaw Cluster, N = {}, m = {}, p = {:.2f} ({})".format(N, m, p, seed)

    return G, text


if __name__ == "__main__":
    if len(sys.argv) > 1:
        seed = sys.argv[1]
    else:
        seed = base64.b64encode(os.urandom(8)).decode("ascii")

    print(seed)
    G, text = get_random_graph(seed)
#    draw_graph(G, text, "test", "neato")
#    draw_graphviz(G, text, "test")

    basename = str(int(datetime.timestamp(datetime.now())))
    path, details = draw_cytoscape(G, text, basename)

    with open(basename+".txt", w) as f:
        f.write(text)
        f.write("\n")
        f.write(details)
        f.write("\n")

    tweet_pic(path)

