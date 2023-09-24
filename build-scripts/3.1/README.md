Script to build WASM library for Astyle 3.1.

Run:

```bash
./build.sh
```

This should build the docker image with Emscripten SDK, download Astyle and build it with Emscripten. The resulting library will be copied to `astyle_py/lib/3.1/libastyle.wasm`.
