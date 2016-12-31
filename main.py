#!/usr/bin/env python3

import os
import sys
import random
import base64
from datetime import datetime

from twitter_helper import tweet_pic
from graphs import RandomGraph
from graphs import draw_cytoscape, draw_graph

absdir = os.path.abspath(os.path.dirname(__file__))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "test":
        seed = sys.argv[1]
    else:
        seed = base64.b64encode(os.urandom(8)).decode("ascii")

    print(seed)
    GraphGenerator = RandomGraph(seed)
    G, details = GraphGenerator.randomGraph()
    text = "{name} ({N} nodes)".format(**details)

    if not "test" in sys.argv:
        folder = os.path.join(absdir, "archive")
    else:
        folder = os.path.join(absdir, "test")

    os.makedirs(folder, exist_ok=True)
    basename = str(int(datetime.timestamp(datetime.now())))
    basename = os.path.join(folder, basename)

    try:
        path, style = draw_cytoscape(G, text, basename, absdir)
    except:
        path, style = draw_graph(G, text, basename, absdir, "neato")


    with open(basename+".txt", "w") as f:
        f.write(details["seed"])
        f.write("\n")
        f.write(details["template"].format(**details))
        f.write("\n")
        f.write(style)
        f.write("\n")

    if not "test" in sys.argv:
        tweet_pic(path, text)

