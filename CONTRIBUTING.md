# Information for Contributors

Contributions in the form of pull requests, issue reports, and feature requests are welcome!

## Submitting a PR

Please do the following before submitting a PR:

- [ ] Create a virtual environment: `python3 -m venv .venv` and activate it: `. .venv/bin/activate`
- [ ] Install testing prerequisites: `pip install -e ".[dev]"`
- [ ] Install pre-commit hooks: `pre-commit install`
- [ ] Run the tests: `pytest`

## Building Astyle

This Python package uses Astyle compiled into WebAssembly (`astyle_py/lib/<VERSION>/libastyle.wasm`). To build libastyle.wasm for a new Astyle version, run `build.sh <VERSION>` in the `build-scripts/3.3+` directory. For example, to build the library for Astyle 3.4.7:

```bash
cd build-scripts/3.3+
./build.sh 3.4.7
```

You need Docker installed to do the build.

A build script for the older Astyle 3.1 is also provided in `build-scripts/3.1`.

## Tagging a new release

When tagging a new release, remember to update the package version in:
- [`astyle_py/__init__.py`](astyle_py/__init__.py)
- [`README.md`](README.md)

The release will be uploaded to PyPI automatically once the tag is pushed.
