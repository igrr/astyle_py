#!/bin/bash

set -euo pipefail

ASTYLE_VERSION=3.1
ASTYLE_DIST_NAME=astyle_${ASTYLE_VERSION}_linux.tar.gz

if [ ! -f ${ASTYLE_DIST_NAME} ]; then
    wget -q -O ${ASTYLE_DIST_NAME} https://sourceforge.net/projects/astyle/files/astyle/astyle%20${ASTYLE_VERSION}/${ASTYLE_DIST_NAME}/download
fi

if [ ! -d astyle ]; then
    tar xf ${ASTYLE_DIST_NAME}
fi

cd astyle

# Add convenience function to libastyle, for easier invocation from WASM

if [ ! -f .main.patched ]; then
    cat << 'EOF' >> src/astyle_main.cpp
extern "C" void AStyleErrorHandler(int errorNumber, const char* errorMessage);
extern "C" EXPORT char* AStyleWrapper(const char* pSourceIn, const char* pOptions) {
    return AStyleMain(pSourceIn, pOptions, &AStyleErrorHandler, (fpAlloc) malloc);
}
EOF
    touch .main.patched
fi

cd build/gcc

# Small Makefile patches

if [ ! -f .Makefile.patched ]; then
    sed -i 's/CXX = g\+\+/CXX ?= g++/g' Makefile
    sed -i 's/ar crs/$(AR) crs/g' Makefile
    touch .Makefile.patched
fi


source ${EMSDK_PATH}/emsdk_env.sh

# build bin/libastyle.a
emmake make static

# link it as a wasm module
emcc -o bin/libastyle.wasm \
    -s EXPORTED_FUNCTIONS=["_AStyleGetVersion","_AStyleWrapper","_malloc","_free"] \
    -s STANDALONE_WASM=1 \
    --no-entry \
    bin/libastyle.a

ls -l bin/libastyle.wasm
sha256sum bin/libastyle.wasm
