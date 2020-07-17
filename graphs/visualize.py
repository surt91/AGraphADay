import os
import math
import random
import inspect
from subprocess import call

import networkx as nx
import numpy as np

# hack to suppress "Unable to init server: Could not connect: Connection refused"
# errors on stderr, if not launched from an X session
os.environ["DISPLAY"] = ":0"
import graph_tool as gt
import graph_tool.inference
import graph_tool.draw
import graph_tool.centrality
import cairo

from .nx2gt.nx2gt import nx2gt


class RetryableError(Exception):
    pass


def has_explicit_coordinates(G):
    # Guess if the graph has explicit coordinates
    try:
        if isinstance(list(G.nodes())[0], str):
            raise TypeError
        float(list(G.nodes())[0][0])
        # we can only use d=2
        if len(list(G.nodes())[0]) != 2:
            raise
        graph_has_coordinates = True
    except IndexError:
        # if we can not get enough elements, it can not be coordinates
        graph_has_coordinates = False
    except TypeError:
        # if we can not get the zeroths element, it can not be coordinates
        graph_has_coordinates = False
    except ValueError:
        # if we can not convert it to float, it can not be coordinates
        graph_has_coordinates = False
    except:
        # otherwise: panic!
        print(list(G.nodes()))
        raise
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
    plt.savefig(f"{basename}.svg")
    plt.savefig(f"{basename}.png")

    details = "style = {}, layout = {}".format("default", command)

    return f"{basename}.png", details


def draw_graphviz(G, basename, absdir, command="dot", **kwargs):
    from networkx.drawing.nx_agraph import to_agraph
    A = to_agraph(G)
    A.write(f"{basename}.dot")


class NxLayout:
    def __init__(self):
        members = inspect.getmembers(NxLayout)

        self.layouts = [i[0][6:] for i in sorted(members) if "layout" in i[0]]
        self.names = {i[0][6:]: i[1] for i in sorted(members) if "layout" in i[0]}

    @staticmethod
    def layoutKamadaKawai(G):
        return NxLayout.layoutNeato(G)

    @staticmethod
    def layoutCircular(G):
        return nx.circular_layout(G)

    @staticmethod
    def layoutShell(G):
        return nx.shell_layout(G)

    @staticmethod
    def layoutSpectral(G):
        return nx.spectral_layout(G)


class GvLayout:
    def __init__(self):
        members = inspect.getmembers(GvLayout)

        self.layouts = [i[0][6:] for i in sorted(members) if "layout" in i[0]]
        self.names = {i[0][6:]: i[1] for i in sorted(members) if "layout" in i[0]}

    @staticmethod
    def layoutDot(G):
        return nx.nx_pydot.graphviz_layout(G, prog="dot")

    @staticmethod
    def layoutNeato(G):
        return nx.nx_pydot.graphviz_layout(G, prog="neato")

    @staticmethod
    def layoutTwoPi(G):
        return nx.nx_pydot.graphviz_layout(G, prog="twopi")


class GtLayout:
    def __init__(self):
        members = inspect.getmembers(GtLayout)

        self.layouts = [i[0][6:] for i in sorted(members) if "layout" in i[0]]
        self.names = {i[0][6:]: i[1] for i in sorted(members) if "layout" in i[0]}

    @staticmethod
    def layoutSFDP(g):
        return gt.draw.sfdp_layout(g)

    @staticmethod
    def layoutFruchtermanReingold(g):
        return gt.draw.fruchterman_reingold_layout(g)

    @staticmethod
    def layoutARF(g):
        return gt.draw.arf_layout(g)

    @staticmethod
    def layoutRadialTree(g):
        # take the node with the highest degree as the root
        deg = g.degree_property_map("total")
        root_node = deg.a.argmax()
        return gt.draw.radial_tree_layout(g, root_node)


class GtStyle:
    outsize = (4096, 4096)
    # outsize = (2046, 1022)

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
    def styleDegree(g, pos, fixed=False):
        deg = g.degree_property_map("total")
        deg.a += 1  # nodes with value zero should be 5% of maximum
        deg.a = np.sqrt(deg.a) / np.sqrt(deg.a).max() * GtStyle.max_node_size(g, pos, fixed)
        style_dict = dict(vertex_size=deg,
                          vertex_fill_color=deg,
                          vorder=deg,
                          output_size=GtStyle.outsize,
                          bg_color=(1, 1, 1, 1))

        return style_dict

    @staticmethod
    def styleBetweenness(g, pos, fixed=False):
        deg = g.degree_property_map("total")
        vbet, ebet = gt.centrality.betweenness(g)
        # nodes with value zero should be 5% of maximum
        vbet.a += max(vbet.a.max(), 1) * 0.05
        vbet.a = np.sqrt(vbet.a)
        vbet.a /= vbet.a.max() / GtStyle.max_node_size(g, pos, fixed)
        ebet.a += 0.05 * ebet.a.max()
        ebet.a /= ebet.a.max() / 10.
        eorder = ebet.copy()
        eorder.a *= -1
        bg_color = (0.25, 0.25, 0.25, 1.0)

        style_dict = dict(vertex_size=vbet, vertex_fill_color=deg, vorder=vbet,
                          edge_color=ebet, eorder=eorder, edge_pen_width=ebet,
                          output_size=GtStyle.outsize,
                          bg_color=bg_color)

        return style_dict

    @staticmethod
    def styleCurved(g, pos, fixed=False):
        eig, auth, hub = graph_tool.centrality.hits(g)

        auth.a += 1  # nodes with value zero should be 5% of maximum
        auth.a = auth.a**2 / (auth.a**2).max() * GtStyle.max_node_size(g, pos, fixed)

        bg_color = (1, 1, 1, 1)
        # curvature: see http://main-discussion-list-for-the-graph-tool-project.982480.n3.nabble.com/Clarifications-in-docs-about-graph-draw-edge-control-points-and-splines-td4026216.html
        control = g.new_edge_property("vector<double>")
        for e in g.edges():
            d = math.sqrt(sum((pos[e.source()].a - pos[e.target()].a)**2)) / 5
            control[e] = [0.0, 0.0, 0.3, d, 0.7, d, 1.0, 0.0]

        style_dict = dict(vertex_fill_color=auth, vertex_size=auth,
                          edge_control_points=control,
                          output_size=GtStyle.outsize,
                          bg_color=bg_color)

        return style_dict

    @staticmethod
    def styleBlocky(g, pos, fixed=False):
        lambda1, eig = graph_tool.centrality.eigenvector(g)

        eig.a += 1  # nodes with value zero should be 5% of maximum
        eig.a = np.sqrt(eig.a) / np.sqrt(eig.a).max() * GtStyle.max_node_size(g, pos, fixed)

        ecol = g.new_edge_property("double")
        for e in g.edges():
            ecol[e] = max(eig[e.source()], eig[e.target()])

        bg_color = (0.25, 0.25, 0.25, 1.0)

        style_dict = dict(vertex_fill_color=eig, vertex_size=eig,
                          vertex_shape="square",
                          edge_color=ecol,
                          output_size=GtStyle.outsize,
                          bg_color=bg_color)

        return style_dict

    @staticmethod
    def mean_distance_from_gt_pos(g, pos, fixed=False):
        ds = []
        max_d = 0
        for v in g.vertices():
            for w in v.out_neighbours():
                i = pos[v]
                j = pos[w]
                try:
                    ds.append(math.sqrt((i[0] - j[0])**2 + (i[1] - j[1])**2))
                except IndexError:
                    print(v, w, i, j)
                    raise RetryableError
        if fixed:
            # fixed nodes -> Geometric graph, take shortest 20% of edges
            short_edges = sorted(ds)[:max(1, len(ds) // 5)]
        else:
            # not fixed -> take shortes 5% of egdes
            short_edges = sorted(ds)[:max(1, len(ds) // 20)]
        d = sum(short_edges) / len(short_edges)

        for v in g.vertices():
            for w in g.vertices():
                i = pos[v]
                j = pos[w]
                try:
                    tmp = math.sqrt((i[0] - j[0])**2 + (i[1] - j[1])**2)
                except IndexError:
                    print(v, w, i, j)
                    raise RetryableError
                max_d = max(tmp, max_d)

        return d, max_d

    @staticmethod
    def max_node_size(g, pos, fixed=False):
        # calculate the node size: a node should have a diameter of the mean
        # neighbor distance, but only for the 10% of nearest neighbors
        mean_d, max_d = GtStyle.mean_distance_from_gt_pos(g, pos, fixed)
        # since node size is given in pixel and or coordinates are arbitary,
        # we need to rescale
        # we multiply by >1 since the node size is diameter and not radius
        return 0.8 * mean_d / max_d * min(GtStyle.outsize)


def draw_graphtool(G, basename, absdir, style, layout):
    """Draw the graph G using graph-tool.

    basename    -- filename
    absdir      -- output path
    style       -- style to use
    layout      -- layout to use
    """
    g = nx2gt(G)

    if style not in GtStyle().styles:
        print(style, "not valid, draw random style")
        style = GtStyle().randomStyle()

    if has_explicit_coordinates(G):
        layout = "explicit"
        pos = g.new_vertex_property("vector<double>")
        for n, v in enumerate(G.nodes()):
            pos[g.vertex(n)] = [v[0] * 1000, v[1] * 1000]
    elif layout in NxLayout().layouts:
        pos = g.new_vertex_property("vector<double>")
        fixed_positions = NxLayout().names[layout](G)
        for n, v in enumerate(G.nodes()):
            pos[g.vertex(n)] = fixed_positions[v]
    elif layout in GtLayout().layouts:
        pos = GtLayout().names[layout](g)
    else:
        pos = gt.draw.sfdp_layout(g)

    details = "style = {}, layout = {}".format(style, layout)

    infile = f"{basename}_raw.png"
    outfile = f"{basename}.png"

    style_dict = GtStyle().names[style](g, pos, fixed=layout == "explicit")

    try:
        gt.draw.graph_draw(g, pos=pos, output=infile, **style_dict)
    except cairo.Error:
        print("some cairo error")
        raise RetryableError

    call([os.path.join(absdir, "svg2png.sh"), infile, outfile])

    # test if the file is smaller than 60 kB, in that case something went wrong
    # or it is probably too boring
    if os.path.getsize(outfile) < 60e3:
        print("apparently the output is empty, try again")
        raise RetryableError
    return outfile, details


def draw_blockmodel(G, basename, absdir, style, layout):
    g = nx2gt(G)
    state = gt.inference.minimize_nested_blockmodel_dl(g, deg_corr=True)

    details = "style = {}, layout = {}".format("Blockmodel", "Blockmodel")

    infile = f"{basename}_raw.png"
    outfile = f"{basename}.png"

    gt.draw.draw_hierarchy(state,
                           bg_color=(0.25, 0.25, 0.25, 1.0),
                           output_size=(4096, 4096),
                           output=infile)
    call([os.path.join(absdir, "svg2png.sh"), infile, outfile])
    return outfile, details
