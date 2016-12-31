import os
import sys
import random
import base64
from datetime import datetime

from graphs import RandomGraph, synonyms
from graphs import draw_cytoscape, draw_graph
from parse import match

absdir = os.path.abspath(os.path.dirname(__file__))


if __name__ == "__main__":
    seed = base64.b64encode(os.urandom(8)).decode("ascii")

    GraphGenerator = RandomGraph(seed)

    if len(sys.argv) > 1:
        text = sys.argv[1]
        key, certainty = match(text, synonyms.keys())
        G, details = synonyms[key](GraphGenerator)
    else:
        G, details = GraphGenerator.randomGraph()
        certainty = 0

    name = details["name"]

    handle = "@someone"
    if certainty < 20:
        answer = "{handle} I am not sure what you mean, but I drew a {graph} for you"
    elif certainty < 70:
        answer = "{handle} I think you requested a {graph}, I drew it for you"
    else:
        answer = "{handle} here is the {graph} you requested"
    answer = answer.format(handle=handle, graph=name)

    print(answer)

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
