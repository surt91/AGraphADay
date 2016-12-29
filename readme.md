Setup
-----

Install all dependencies, start Cytoscape as `cytoscape -R 1234`.
Every time the program runs it will create a graph, save it as `png` and `svg`
and its details in a `txt` named after the current unix timestamp and tweets
it. Do not forget to put in valid keys and secrets in `keys_and_secrets.py`.

Dependencies
------------

* from PyPI
    * networkx
    * matplotlib
    * py2cytoscape
    * python-twitter

* Cytoscape
    http://www.cytoscape.org/
    run with REST server on localhost at port 1234

* Imagemagick
