import sys

from main import guess_graph
from twitter_helper import obtain_dm


if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = sys.argv[1]
        guess_graph(text)
    else:
        text = None

    todo = obtain_dm()

    for d in todo:
        guess_graph(text=d["text"], handle=d["handle"])

