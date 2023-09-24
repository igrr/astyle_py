FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y \
    git \
    make \
    python3 \
    wget \
    xz-utils \
    bzip2 \
    cmake \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/*

ARG EMSDK_VER=3.1.46

RUN cd /opt \
  && git clone -b ${EMSDK_VER} https://github.com/emscripten-core/emsdk.git \
  && cd emsdk \
  && ./emsdk install ${EMSDK_VER} \
  && ./emsdk activate ${EMSDK_VER} \
  && rm -rf zips

ENV EMSDK_PATH=/opt/emsdk
