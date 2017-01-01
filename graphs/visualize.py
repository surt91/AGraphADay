import os
import time
import random
import warnings
from subprocess import call

import networkx as nx

def has_explicit_coordinates(G):
    # Guess if the graph has explicit coordinates
    try:
        float((G.nodes()[0][0]))
        graph_has_coordinates = True
    except:
        graph_has_coordinates = False
    return graph_has_coordinates


def draw_graph(G, text, basename, absdir, command="neato"):
    from matplotlib import pyplot as plt
    from networkx.drawing.nx_agraph import graphviz_layout

    if has_explicit_coordinates(G):
        pos = {n: (n[0], n[1]) for n in G.nodes()}
        command = "explicit"
    else:
        pos = graphviz_layout(G, command)

    nx.draw(G, pos)
#    ax = plt.gca()
#    plt.text(0.99, 0.01, text,
#            verticalalignment='bottom',
#            horizontalalignment='right',
#            transform=ax.transAxes,
#            fontsize=10)
    plt.savefig(basename+".svg")
    plt.savefig(basename+".png")

    details = "style = {}, layout = {}".format("default", command)

    return basename+".png", details


def draw_graphviz(G, text, basename, absdir, command="dot"):
    from networkx.drawing.nx_agraph import to_agraph, graphviz_layout
    A = to_agraph(G)
    A.write(basename+".dot")


def draw_cytoscape(G, text, basename, absdir):
    from networkx.drawing.nx_agraph import graphviz_layout
    # igraph uses deprecated things
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore",category=DeprecationWarning)
        from py2cytoscape.data.cyrest_client import CyRestClient
        from py2cytoscape.data.util_network import NetworkUtil as util
        from py2cytoscape.data.style import StyleUtil as s_util

    # fixme should be asked from the server
    styles = ["Sample3", "Sample3", "Curved", 
              "Ripple", "Sample2", "default black"]
    # http://localhost:1234/v1/apply/layouts/
    layouts = [ "circular", "kamada-kawai", "force-directed",
                "hierarchical", "isom"]

    graphviz = ["neato", "dot", "circo", "twopi", "fdp"]

    # only use for small graphs
    if len(G) < 60:
        styles += ["Minimal"]
        layouts += ["stacked-node-layout"]
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

    infile = basename+".svg"
    outfile = basename+".png"

    svg = g_cy.get_svg()
    with open(infile, "wb") as f:
        f.write(svg)

    # postprocessing using imagemagick and conversion to png
    call([os.path.join(absdir, "svg2png.sh"), infile, outfile])

    return outfile, details

