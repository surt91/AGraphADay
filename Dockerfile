FROM debian:bullseye-slim
RUN apt-get update && apt-get install -y python3 python3-pip python3-networkx python3-matplotlib python3-scipy python3-pygraphviz  python3-tweepy python3-fuzzywuzzy python3-cairo python3-gi imagemagick optipng gnupg git
RUN echo "deb [ arch=amd64 ] https://downloads.skewed.de/apt bullseye main" >> /etc/apt/sources.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-key 612DEFB798507F25
RUN apt-get update && apt-get install -y python3-graph-tool && rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN git clone --depth=1 https://github.com/surt91/AGraphADay.git
WORKDIR /AGraphADay
RUN git submodule update --init --recursive
ENTRYPOINT ["python3", "main.py"]
