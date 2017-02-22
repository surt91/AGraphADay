import os
import time
import math
import random
import warnings
import inspect
from collections import defaultdict
from subprocess import call

import networkx as nx
import graph_tool as gt
import graph_tool.inference
import graph_tool.draw
import graph_tool.centrality
import numpy as np

from .nx2gt.nx2gt import nx2gt


def has_explicit_coordinates(G):
    # Guess if the graph has explicit coordinates
    try:
        float((G.nodes()[0][0]))
        graph_has_coordinates = True
    except:
        graph_has_coordinates = False
    return graph_has_coordinates


def draw_graph(G, basename, absdir, command="neato"):
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    from networkx.drawing.nx_agraph import graphviz_layout

    if has_explicit_coordinates(G):
        pos = {n: (n[0], n[1]) for n in G.nodes()}
        command = "explicit"
    else:
        pos = graphviz_layout(G, command)

    nx.draw(G, pos)
    plt.savefig(basename+".svg")
    plt.savefig(basename+".png")

    details = "style = {}, layout = {}".format("default", command)

    return basename+".png", details


def draw_graphviz(G, basename, absdir, command="dot", **kwargs):
    from networkx.drawing.nx_agraph import to_agraph, graphviz_layout
    A = to_agraph(G)
    A.write(basename+".dot")


class CyStyle:
    def __init__(self):
        # get all methods that generate graphs (convention: starts with 'style')
        members = inspect.getmembers(CyStyle)

        self.styles = [i[0][5:] for i in sorted(members) if "style" in i[0]]
        self.functions = [i[1] for i in sorted(members) if "style" in i[0]]
        self.names = {i[0][5:]: i[1] for i in sorted(members) if "style" in i[0]}

    def randomStyle(self):
        style = random.choice(self.functions)

        return style

    @staticmethod
    def styleSample3(cy):
        s = cy.style.create("Sample3")
        # the mappings=defaultdict(str) will assign empty strings to the nodes
        s.create_discrete_mapping(column="name",
                                  vp="NODE_LABEL",
                                  mappings=defaultdict(str))
        return s

    @staticmethod
    def styleCurved(cy):
        s = cy.style.create("Curved")
        s.create_discrete_mapping(column="name",
                                  vp="NODE_LABEL",
                                  mappings=defaultdict(str))
        s.update_defaults({"NETWORK_BACKGROUND_PAINT": "#404040",
                           "EDGE_TARGET_ARROW_SHAPE":  "NONE"})
        return s

    @staticmethod
    def styleRipple(cy):
        s = cy.style.create("Ripple")
        s.create_discrete_mapping(column="name",
                                  vp="NODE_LABEL",
                                  mappings=defaultdict(str))
        return s

    @staticmethod
    def styleDefaultBlack(cy):
        s = cy.style.create("default black")
        s.create_discrete_mapping(column="name",
                                  vp="NODE_LABEL",
                                  mappings=defaultdict(str))
        return s


class CyLayout:
    layouts = ["circular", "kamada-kawai", "force-directed",
               "hierarchical", "isom"]

    def randomLayout(self):
        layout = random.choice(self.layouts)

        return layout


def draw_cytoscape(G, basename, absdir, style, layout):
    from networkx.drawing.nx_agraph import graphviz_layout
    # igraph uses deprecated things
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        from py2cytoscape.data.cyrest_client import CyRestClient
        from py2cytoscape.data.util_network import NetworkUtil as util
        from py2cytoscape.data.style import StyleUtil as s_util

    # Create Client
    cy = CyRestClient()
    cy.session.delete()

    g_cy = cy.network.create_from_networkx(G)

    if style not in CyStyle().styles:
        style = CyStyle().randomStyle()

    # assign locations manual
    locations = []
    if has_explicit_coordinates(G):
        layout = "explicit"

        idmap = util.name2suid(g_cy)
        for v in G.nodes():
            locations.append([int(idmap[str(v)]), v[0]*1000, v[1]*1000])

    style = CyStyle().names[style](cy)

    details = "style = {}, layout = {}".format(style.get_name(), layout)

    # if there are explicit locations, use them
    if locations:
        cy.layout.apply_from_presets(g_cy, positions=locations)
    else:
        cy.layout.apply(network=g_cy, name=layout)

    cy.style.apply(style=style, network=g_cy)

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


class GtLayout:
    layouts = ["sfdp",
               "fruchterman_reingold",
               "arf",
               "radial_tree"]

    def randomLayout(self):
        layout = random.choice(self.layouts)

        return layout


# TODO methods take g and return a dict that can be splatted into draw_graph
class GtStyle:
    outsize = (4096, 4096)

    def __init__(self):
        # get all methods that generate graphs (convention: starts with 'style')
        members = inspect.getmembers(GtStyle)

        self.styles = [i[0][5:] for i in sorted(members) if "style" in i[0]]
        self.functions = [i[1] for i in sorted(members) if "style" in i[0]]
        self.names = {i[0][5:]: i[1] for i in sorted(members) if "style" in i[0]}

    def randomStyle(self):
        style = random.choice(self.styles)

        return style

    @staticmethod
    def styleDegree(g, pos):
        deg = g.degree_property_map("total")
        deg.a += 1  # nodes with value zero should be 5% of maximum
        deg.a = np.sqrt(deg.a) / np.sqrt(deg.a).max() * GtStyle.max_node_size(g, pos)
        style_dict = dict(vertex_size=deg,
                          vertex_fill_color=deg,
                          vorder=deg,
                          output_size=GtStyle.outsize,
                          bg_color=(1, 1, 1, 1))

        return style_dict

    @staticmethod
    def styleBetweenness(g, pos):
        deg = g.degree_property_map("total")
        vbet, ebet = gt.centrality.betweenness(g)
        vbet.a += vbet.a.max()*0.05  # nodes with value zero should be 5% of maximum
        vbet.a = np.sqrt(vbet.a)
        vbet.a /= vbet.a.max() / GtStyle.max_node_size(g, pos)
        ebet.a /= ebet.a.max() / 10.
        eorder = ebet.copy()
        eorder.a *= -1
        control = g.new_edge_property("vector<double>")
        for e in g.edges():
            d = math.sqrt(sum((pos[e.source()].a - pos[e.target()].a) ** 2)) / 5
            control[e] = [0.3, d, 0.7, d]
        bg_color = (0.25, 0.25, 0.25, 1.0)

        style_dict = dict(vertex_size=vbet, vertex_fill_color=deg, vorder=vbet,
                          edge_color=ebet, eorder=eorder, edge_pen_width=ebet,
                          edge_control_points=control,
                          output_size=GtStyle.outsize,
                          bg_color=bg_color)

        return style_dict

    @staticmethod
    def mean_distance_from_gt_pos(g, pos):
        ds = []
        max_d = 0
        for v in g.vertices():
            for w in v.out_neighbours():
                i = pos[v]
                j = pos[w]
                ds.append(math.sqrt((i[0] - j[0])**2 + (i[1] - j[1])**2))
        # d = sum(ds) / len(ds)
        short_edges = sorted(ds)[:max(1, len(ds)//20)]
        d = sum(short_edges) / len(short_edges)

        for v in g.vertices():
            for w in g.vertices():
                i = pos[v]
                j = pos[w]
                tmp = math.sqrt((i[0] - j[0])**2 + (i[1] - j[1])**2)
                max_d = max(tmp, max_d)

        return d, max_d

    @staticmethod
    def max_node_size(g, pos):
        # calculate the node size: a node should have a diameter of the mean
        # neighbor distance, but only for the 10% of nearest neighbors
        mean_d, max_d = GtStyle.mean_distance_from_gt_pos(g, pos)
        # since node size is given in pixel and or coordinates are arbitary,
        # we need to rescale
        # we multiply by >1 since the node size is diameter and not radius
        return 0.8 * mean_d / max_d * min(GtStyle.outsize)

def draw_graphtool(G, basename, absdir, style, layout):
    N = len(G.nodes())
    g = nx2gt(G)

    if style not in GtStyle().styles:
        print(style, "not valid, draw random style")
        style = GtStyle().randomStyle()

    deg = g.degree_property_map("total")

    # assign locations manual
    locations = []
    if has_explicit_coordinates(G):
        layout = "explicit"
        pos = g.new_vertex_property("vector<double>")
        for n, v in enumerate(G.nodes()):
            pos[g.vertex(n)] = [v[0]*1000, v[1]*1000]
    else:
        if layout == "sfdp":
            pos = gt.draw.sfdp_layout(g)
        elif layout == "fruchterman_reingold":
            pos = gt.draw.fruchterman_reingold_layout(g)
        elif layout == "arf":
            pos = gt.draw.arf_layout(g)
        elif layout == "radial_tree":
            # take the node with the highest degree as the root
            root_node = deg.a.argmax()
            pos = gt.draw.radial_tree_layout(g, root_node)
        else:
            pos = gt.draw.sfdp_layout(g)

    details = "style = {}, layout = {}".format(style, layout)

    infile = basename+"_raw.png"
    outfile = basename+".png"

    style_dict = GtStyle().names[style](g, pos)

    gt.draw.graph_draw(g, pos=pos, output=infile, **style_dict)

    call([os.path.join(absdir, "svg2png.sh"), infile, outfile])
    return outfile, details


def draw_blockmodel(G, basename, absdir, style, layout):
    g = nx2gt(G)
    state = gt.inference.minimize_nested_blockmodel_dl(g, deg_corr=True)

    details = "style = {}, layout = {}".format("blockmodel", "blockmodel")

    infile = basename+"_raw.png"
    outfile = basename+".png"

    gt.draw.draw_hierarchy(state,
                           bg_color=(0.25, 0.25, 0.25, 1.0),
                           output_size=(4096, 4096),
                           output=infile)
    call([os.path.join(absdir, "svg2png.sh"), infile, outfile])
    return outfile, details
