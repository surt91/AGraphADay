#A Graph A Day

This is a Twitter bot, which can tweet pictures of random graphs.
It also listens for mentions and answers them with pictures of graphs
it detects in the tweet. The layout ans styles are also extracted from the
tweet if possible. If a number smaller than 1025 is detected, it is used as
the number of nodes.

##Selection of Recognized Keywords

###Graph Types

    * Newman-Watts-Strogatz
    * Barabási-Albert
    * Powerlaw cluster graph
    * Relative Neighborhood graph
    * Minimum Radius graph
    * some social networks
    * Caveman graph

###Styles

    * Curved
        * dark background
        * orange nodes
        * curved, white edges

    * Sample3
        * dark background
        * blue nodes
        * white edges

    * default black
        * dark background
        * white nodes
        * green edges

    * default
        * white background
        * blue nodes
        * black edges

    * Ripple
        * white background
        * blue nodes
        * blue edges

###Layouts

    * circular
    * kamada-kawai
        also known as `neato`
    * force-directed
    * hierarchical
    * isom


##Setup

Install all dependencies, start Cytoscape as `cytoscape -R 1234`.
Every time the program runs it will create a graph, save it as `png` and `svg`
and its details in a `txt` named after the current unix timestamp and tweets
it. Do not forget to put in valid keys and secrets in `keys_and_secrets.py`.

##Dependencies

    * from PyPI
        * networkx
        * matplotlib
        * py2cytoscape
        * python-pygraphviz
        * tweepy
        * fuzzywuzzy

    * Cytoscape
        http://www.cytoscape.org/
        run with REST server on localhost at port 1234

    * Imagemagick
    * optipng
