#!/usr/bin/env python3

import os
import sys
import random
import base64
from datetime import datetime

import tweepy

from twitter_helper import tweet_pic, obtain_dm, api
from graphs import RandomGraph, synonyms
from graphs import draw_cytoscape, draw_graph
from parse import match

absdir = os.path.abspath(os.path.dirname(__file__))
my_handle = "randomGraphs"


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

    print(key, "({}%)".format(certainty))

    name = details["name"]
    if handle and handle[0] != "@":
        handle = "@"+handle

    if certainty < 20:
        answer = "{handle} I am not sure what you mean, but I drew a {graph} for you!"
    elif certainty < 70:
        answer = "{handle} I think you mentioned a {graph}, I drew it for you."
    else:
        answer = "{handle} here is a picture of the {graph} you're interested in!"
    answer = answer.format(handle=handle, graph=name).strip()

    folder = os.path.join(absdir, "answers")

    os.makedirs(folder, exist_ok=True)
    basename = str(int(datetime.timestamp(datetime.now()))) + "_" + seed.replace("/", "-")
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


class MyStreamListener(tweepy.StreamListener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            with open("last_id.dat", "r") as f:
                self.last_id = int(f.read().strip())
        except:
            self.last_id = 0

    def on_status(self, status):
        print(status.text)
        print("@" + status.user.screen_name, ":", status.text)
        # make sure that we are actually mentioned
        mentioned = False
        for i in status.entities["user_mentions"]:
            if i["screen_name"] == my_handle:
                mentioned = True
        if mentioned:
            print(status.text)
            text = status.text.replace(my_handle, "")
            path, answer = guess_graph(text=text, handle=status.user.screen_name)
            tweet_pic(path, answer, status.id)

            self.last_id = status.id
            with open("last_id.dat", "w") as f:
                f.write(str(self.last_id))


def answerMentions():
    # are there new mentions while we were not listening?
    todo = obtain_dm()
    print(len(todo), "new messages")
    for d in todo:
        text = d["text"].replace(my_handle, "")
        path, answer = guess_graph(text=d["text"], handle=d["handle"])
        tweet_pic(path, answer, d["id"])

    # listen for new mentions
    print("listening for mentions")
    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
    myStream.filter(track=['randomGraphs'])


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
    basename = str(int(datetime.timestamp(datetime.now()))) + "_" + seed.replace("/", "-")
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

