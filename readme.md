# :art: A Graph A Day

<a href="https://twitter.com/randomGraphs/status/1342751042891624449" target="_blank"><img align="right" width="256" height="256" alt="Dorogovtsev-Goltsev-Mendes Graph" src="extra/example_graph.webp"></a>

This is a Twitter bot which tweets pictures of random graphs.

There is a short [blog article](https://blog.schawe.me/randomGraphs.html) about the tech and -- more importantly -- showing a few example pictures.

The bot can also listen for mentions and answers them with pictures of graphs
it detects in the tweet. The layout ans styles are also extracted from the
tweet if possible. If a number smaller than 1025 is detected, it is used as
the number of nodes.

## :hammer_and_wrench: Setup

Every time the program runs it will create a graph, save it as `png`
and its details in a `txt` named after the current Unix timestamp and tweets
it.

:key: **Important:** If you want to connect to Twitter, do not forget to put in valid keys and secrets in `keys_and_secrets.py`.

Also there is at least one submodule which should be loaded from GitHub,
therefore run `git submodule update --init --recursive` after cloning.

## :whale: Docker

You can also use a docker container:

```bash
# build it
docker build . -t graph
# run it
mkdir -p img test
docker run \
    -v $PWD/img:/AGraphADay/archive \
    -v $PWD/test:/AGraphADay/test \
    -v $PWD/keys_and_secrets.py:/AGraphADay/keys_and_secrets.py \
    graph test
# the generated graphs will be saved to the mounted volumes `img` or `test`
```

## :herb: Dependencies

* python packages:
  * networkx
  * matplotlib
  * scipy
  * pygraphviz
  * tweepy
  * fuzzywuzzy
  * graph-tool

* Imagemagick
* optipng


## :scroll: Selection of Recognized Keywords

If the bot is listening for mentions or the `test.py` script is called
the input text is searched fuzzily for keywords. Here is a selection of
recognized keywords.

### Graph Types

* Watts-Strogatz
* Barabási-Albert
* Powerlaw cluster graph
* Delaunay triangulation and some subgraphs
* Minimum Radius graph
* some real world networks (source: http://www-personal.umich.edu/~mejn/netdata/)
* Caveman graph

### Styles

* Betweenness
  * dark background
  * node color and size dependent on betweenness centrality
  * edge thickness dependent on betweenness centrality

* Degree
  * white background
  * node size and color dependent on their degree

* Blocky
  * dark background
  * square nodes
  * node color dependent on their eigenvector

* Curved
  * white background
  * curved edges
  * node size and color dependent on their HITS score assuming the graph
        is a citation network

### Layouts

* sfdp
* Fruchterman Reingold (spring based layout)
* ARF (attractive and repulsive forces, nodes inside a disk)
* radial tree
* blockmodel (stochastic blockmodel based hirachic layout)
* dot (from graphviz, a hierarchic layout)
* neato (from graphviz also known as Kamada-Kawai)
* circular (from graphviz, nodes on a circle)
* twopi (from graphviz, radial layout)