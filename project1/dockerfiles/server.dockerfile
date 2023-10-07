FROM asmital/dslab1:base

MAINTAINER Asmita <asmita@utexas.edu> version: 0.1

USER root

WORKDIR $KVS_HOME

COPY server.py .

CMD python3 server.py -i $SERVER_ID
