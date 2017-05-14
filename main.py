#!/usr/bin/env python3

import os
import sys
import random
import base64
from datetime import datetime
from time import sleep

from twitter import tweet_pic, answerMentions
from graphs import RandomGraph, synonyms, layouts_all, styles_all
from graphs import draw_graph, draw_graphtool, draw_blockmodel
from graphs.visualize import GtLayout
from parse import match

absdir = os.path.abspath(os.path.dirname(__file__))


def createPlot(graphGenerator, folder, seed,
               comment="no comment", style=None, layout=None):
    G, details = graphGenerator()

    os.makedirs(folder, exist_ok=True)
    basename = "{:.0f}_{}".format(datetime.timestamp(datetime.now()),
                                  seed.replace("/", "-"))
    basename = os.path.join(folder, basename)

    if style is None:
        style = random.choice(details["allowed_styles"])

    if layout is None:
        layout = random.choice(details["allowed_layouts"])

    # TODO I need to make this pretty
    try:
        if layout in GtLayout.layouts or layout == "explicit":
            path, style_detail = draw_graphtool(G, basename, absdir, style, layout)
        elif layout == "blockmodel":
            path, style_detail = draw_blockmodel(G, basename, absdir, "None", layout)
        else:
            raise
    except:
        from traceback import print_exc
        # print("unexpected error:", sys.exc_info())
        print_exc()
        path, style = draw_graph(G, basename, absdir, "neato")

    with open(basename + ".txt", "w") as f:
        f.write(details["seed"])
        f.write("\n")
        f.write(comment)
        f.write("\n")
        f.write(details["template"].format(**details))
        f.write("\n")
        f.write(style_detail)
        f.write("\n")

    return path, details


def guess_graph(text=None, handle=""):
    seed = base64.b64encode(os.urandom(8)).decode("ascii")

    GraphGenerator = RandomGraph(seed)
    style = None
    layout = None

    if text:
        numbers = [int(s) for s in text.split() if s.isdigit() and int(s) < 1024]
        if numbers:
            N = random.choice(numbers)
            print(f"recognized {N} nodes")
        else:
            N = None

        key, certainty = match(text, synonyms.keys())
        gen = lambda: synonyms[key](GraphGenerator, N=N)

        styleKey, styleCertainty = match(text, styles_all)

        if styleCertainty >= 80:
            print(f"regocnized style: {styleKey} ({styleCertainty})")
            style = styleKey

        layoutKey, layoutCertainty = match(text, layouts_all)

        if layoutCertainty >= 80:
            print(f"recognized layout: {layoutKey} ({layoutCertainty})")
            layout = layoutKey

    if not text or certainty < 20:
        gen = GraphGenerator.randomGraph
        certainty = 0
        key = "n/a"

    folder = os.path.join(absdir, "answers")
    path, details = createPlot(gen, folder, seed,
                               comment="'{text}' -> {key} ({certainty}%)",
                               style=style,
                               layout=layout)

    print(key, "({}%)".format(certainty))

    print(details["template"].format(**details))

    name = details["name"]
    if handle and handle[0] != "@":
        handle = "@" + handle

    if certainty < 50:
        answer = "{handle} I am not sure what you mean, but I drew a {graph} for you! ({N} nodes)"
    elif certainty < 80:
        answer = "{handle} I think you mentioned a {graph}, I drew it for you. ({N} nodes)"
    else:
        answer = "{handle} here is a picture of the {graph} you're interested in! ({N} nodes)"
    answer = answer.format(handle=handle, graph=name, N=details["N"]).strip()

    return path, answer


if __name__ == "__main__":
    if len(sys.argv) > 1 and "mentions" in sys.argv:
        while True:
            try:
                answerMentions(guess_graph)
            except KeyboardInterrupt:
                print("closed by KeyboardInterrupt")
                sys.exit()
            except:
                print("some strange exception:", sys.exc_info())
                sleep(60)

    if len(sys.argv) > 1 and sys.argv[1] != "test":
        seed = sys.argv[1]
    else:
        seed = base64.b64encode(os.urandom(8)).decode("ascii")

    if "test" not in sys.argv:
        folder = os.path.join(absdir, "archive")
    else:
        folder = os.path.join(absdir, "test")

    GraphGenerator = RandomGraph(seed)
    path, details = createPlot(GraphGenerator.randomGraph, folder, seed)

    text = "{name} ({N} nodes)".format(**details)

    if "test" not in sys.argv:
        tweet_pic(path, text)
