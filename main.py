#!/usr/bin/env python3

import os
import sys
import random
import base64
from datetime import datetime

from twitter_helper import tweet_pic, obtain_dm
from graphs import RandomGraph, synonyms
from graphs import draw_cytoscape, draw_graph
from parse import match

absdir = os.path.abspath(os.path.dirname(__file__))


def guess_graph(text=None, handle=""):
    seed = base64.b64encode(os.urandom(8)).decode("ascii")

    GraphGenerator = RandomGraph(seed)

    if text:
        key, certainty = match(text, synonyms.keys())
        G, details = synonyms[key](GraphGenerator)

    if not text or certainty < 20:
        G, details = GraphGenerator.randomGraph()
        certainty = 0
        key = "n/a"

    name = details["name"]
    if handle and handle[0] != "@":
        handle = "@"+handle

    if certainty < 20:
        answer = "{handle} I am not sure what you mean, but I drew a {graph} for you"
    elif certainty < 70:
        answer = "{handle} I think you requested a {graph}, I drew it for you"
    else:
        answer = "{handle} here is the {graph} you requested"
    answer = answer.format(handle=handle, graph=name).strip()

    folder = os.path.join(absdir, "answers")

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
        f.write("'{}' -> {} ({}%)".format(text, key, certainty))
        f.write("\n")
        f.write("'{}'".format(answer))
        f.write("\n")
        f.write(details["template"].format(**details))
        f.write("\n")
        f.write(style)
        f.write("\n")

    return path, answer


def answerMentions():
    todo = obtain_dm()

    for d in todo:
        path, answer = guess_graph(text=d["text"], handle=d["handle"])
        tweet_pic(path, answer)


if __name__ == "__main__":
    if len(sys.argv) > 1 and "mentions" in sys.argv:
        answerMentions()
        sys.exit()

    if len(sys.argv) > 1 and sys.argv[1] != "test":
        seed = sys.argv[1]
    else:
        seed = base64.b64encode(os.urandom(8)).decode("ascii")

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

