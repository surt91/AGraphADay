#!/bin/bash

# will generate a graph every 24 hours +- 6 hours
# will also timeout the generation after 2h and restart

while true; do
    sleep $(echo "18*3600 + ( ($RANDOM / 32767) * (12*3600) )" | bc -l)s
    until timeout 7200 python3 main.py; do
        echo "killed ... retry"
        sleep 300
    done
done
