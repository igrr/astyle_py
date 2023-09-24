#!/bin/bash
set -euo pipefail

# argument is the version number
if [ $# -ne 1 ]; then
    echo "Usage: $0 <astyle_version>"
    exit 1
fi

ASTYLE_VERSION=$1

DOCKER_DIR=${PWD}/../docker
docker build -t emsdk ${DOCKER_DIR}

TMP_DIR=${PWD}/../tmp/${ASTYLE_VERSION}
mkdir -p ${TMP_DIR}
DST_DIR=${PWD}/../../astyle_py/lib/${ASTYLE_VERSION}
mkdir -p ${DST_DIR}

docker run --rm -v ${PWD}:/src -v ${TMP_DIR}:/build emsdk bash -c "cmake -S /src -B /build -DASTYLE_VER=${ASTYLE_VERSION} && cmake --build /build"
cp ${TMP_DIR}/astyle-wasm.wasm ${DST_DIR}/libastyle.wasm
