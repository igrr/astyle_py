# Information for Contributors

Contributions in the form of pull requests, issue reports, and feature requests are welcome!

## Submitting a PR

Please do the following before submitting a PR:

- [ ] Install pre-commit hooks: `pip install pre-commit && pre-commit install`
- [ ] Create a virtual environment: `python3 -m venv .venv` and activate it: `. .venv/bin/activate`
- [ ] Install testing prerequisites: `pip install -e ".[dev]"`
- [ ] Run the tests: `pytest`

## Building Astyle

This Python package uses Astyle compiled into WebAssembly ([astyle_py/libastyle.wasm](astyle_py/libastyle.wasm)). To rebuild libastyle.wasm, run `build.sh` in the `builder/` directory.

Updating Astyle to a newer version might require tweaking the patch applied in [builder/build_inner.sh](builder/build_inner.sh).

## Tagging a new release

When tagging a new release, remember to update the package version in [astyle_py/__init__.py](astyle_py/__init__.py).

The release will be uploaded to PyPI automatically once the tag is pushed.
