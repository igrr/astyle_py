FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y \
    git \
    make \
    python3 \
    wget \
    xz-utils \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/*

ARG EMSDK_VER=2.0.8

RUN cd /opt \
  && git clone -b ${EMSDK_VER} https://github.com/emscripten-core/emsdk.git \
  && cd emsdk \
  && ./emsdk install ${EMSDK_VER} \
  && ./emsdk activate ${EMSDK_VER} \
  && rm -rf zips

ENV EMSDK_PATH=/opt/emsdk
