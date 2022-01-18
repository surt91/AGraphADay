#!/bin/bash

# will also timeout the generation after 1h and restart

# before usage build with 
# docker build . -t graph

timeout 3600 docker run \
    -v $PWD/img:/AGraphADay/archive \
    -v $PWD/test:/AGraphADay/test \
    -v $PWD/keys_and_secrets.py:/AGraphADay/keys_and_secrets.py \
    graph
