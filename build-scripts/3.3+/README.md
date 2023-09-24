Build script for Astyle 3.3 and later.

Run:

```
./build.sh <version>
```

where `<version>` is the version of Astyle you want to build. For example, `3.4.7`.

The script will build a Docker image with Emscripten SDK, download the required version of Astyle and build it with Emscripten. Since Astyle >=3.3 has a CMake build system, everything is conveniently handled in CMakeLists.txt.

The resulting library will be copied to `astyle_py/lib/<version>/libastyle.wasm`.
