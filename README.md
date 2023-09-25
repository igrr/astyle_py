# astyle_py — Python wrapper around [astyle](http://astyle.sourceforge.net/)

![PyPI - Version](https://img.shields.io/pypi/v/astyle-py?labelColor=383838)
 [![CI](https://github.com/igrr/astyle_py/actions/workflows/main.yml/badge.svg)](https://github.com/igrr/astyle_py/actions/workflows/main.yml) ![Python](https://img.shields.io/badge/dynamic/yaml?url=https://raw.githubusercontent.com/igrr/astyle_py/main/.github/workflows/main.yml&query=$.jobs['test'].strategy.matrix['python-version']&label=Python&logo=python&color=3366ff&logoColor=ffcc00&labelColor=383838)

[Artistic Style (astyle)](http://astyle.sourceforge.net/) is a source code indenter, formatter, and beautifier for the C, C++, C++/CLI, Objective‑C, C# and Java programming languages.

This project wraps `astyle` in a Python package. The package can be used:
- [as a pre-commit hook](#using-with-pre-commit) compatible with the [pre-commit](https://pre-commit.com/) framework,
- [as a console program](#using-from-the-command-line),
- [as a library](#using-as-a-library), from other Python packages.

The main reason to use this Python wrapper, rather than native `astyle` binaries, is that makes it easy for developers working on a project to have exactly the same version of astyle, regardless of their operating system. This prevents formatting differences which sometimes occur between different versions of astyle.

## Using with `pre-commit`

1. Set up `pre-commit` for your project as described in https://pre-commit.com/#install.
2. Add `astyle_py` to your `.pre-commit-config.yaml` file as follows. **Note: avoid using `main` as the revision.**
   ```yaml
   repos:
   -   repo: https://github.com/igrr/astyle_py.git
       rev: v1.0.1
       hooks:
       -   id: astyle_py
           args: [--astyle-version=3.4.7 --style=linux]
   ```

Place the required astyle formatting options to the `args` array. See the next section for details.

Use `--dry-run` argument if you only want the pre-commit hook to report the formatting errors, and not fix them automatically.

If necessary, add `verbose: true` option to see the output.

Use `files:` option to configure the regex pattern used to match the files to be formatted. The default pattern is `'^.*\.(c|cpp|cxx|h|hpp|inc)$'`. You can exclude certain files via additional arguments, as described in the next section.

## Using from the command line

Install the package from PyPI:
```
pip install astyle-py
```

Usage:
```
astyle_py [options] <files to format>
```

* `<files>` — list of files to process. By default, `astyle_py` formats the files, modifying them in-place.
* `[options]` — can be any of the [formatting options](#formatting-options), plus the following options are accepted:

### Common options

* `--version` — print the version and exit.
* `--astyle-version=<VER>` — choose the version of Astyle to use.
* `--quiet` — don't print diagnostic messages; by default, the list of files which are formatted is printed to `stderr`.
* `--dry-run` — don't format the files, only check the formatting. Returns non-zero exit code if any file would change after formatting.

### Specifying additional options and excluded files

* `--options=<file>` — read more formatting options from the specified file. Empty lines and lines starting with `#` are ignored.
* `--exclude=<pattern>` — skip files matching the given pattern. Note that patterns use the syntax of [Gitlab CODEOWNERS files](https://docs.gitlab.com/ee/user/project/code_owners.html#the-syntax-of-code-owners-files).
* `--exclude-list=<file>` — skip files matching the list of patterns specified in a file. Empty lines and lines starting with `#` are ignored.

### Specifying the rules file

* `--rules=<file>` — read the formatting rules from the specified rules file. See [Rules files](#rules-files) section for details. This option is incompatible with `--options`, `--exclude`, `--exclude-list`.

## Using as a library

This package can be used as a library to implement custom formatting tools. See [sample.py](sample.py) for an example.

## Formatting options

See http://astyle.sourceforge.net/astyle.html for the details on Astyle formatting options.

Note that this wrapper doesn't implement the options from ["Other options"](http://astyle.sourceforge.net/astyle.html#_Other_Options) and ["Command Line Only"](http://astyle.sourceforge.net/astyle.html#_Command_Line_Only) categories, except for those listed [above](#using-from-the-command-line).

## Rules files

Option `--rules=<file>` allows loading the formatting options from a _rules file_ in YAML format. The rules file can specify different formatting rules for different parts of the project. This can be useful for monorepos which contain libraries written with different formatting conventions.

The rules file consists of sections (rules). For each section the following keywords may be specified:
- `version:` Version of Astyle to use
- `include:` List of files name patterns to include in this rule. Pattern syntax of [Gitlab CODEOWNERS files](https://docs.gitlab.com/ee/user/project/code_owners.html#the-syntax-of-code-owners-files) is used. Required.
- `check:` If set to `false`, the files covered by this rule will be ignored and not checked/formatted. Optional, default is `true`.
- `options:` A string specifying the [formatting options](#formatting-options) for files covered by this rule.

If the file path matches multiple rules, the latest rule is applied. If the file path doesn't match any rule, the options from the special `DEFAULT` rule are used.

Here is an example of a rules file:
```yml

DEFAULT:
    # These formatting options will be used by default
    options: "--style=otbs --indent=spaces=4 --convert-tabs"

thirdparty_lib_1:   # The section name is arbitrary
    # Override formatting rules for the files in a certain directory
    options: "--style=linux"
    include:
        - "/thirdparty/lib1/"

code_to_ignore_for_now:
    # Ignore files in some other directories
    check: false
    include:
        - "/src/component1/"
        - "/src/component2/"
        - "tests/"     # matches a subdirectory 'tests' anywhere in the source tree
```

## Supported Astyle versions

This python wrapper bundles multiple copies of Astyle, you can choose which one to use:
- In the CLI: via `--astyle-version=VERSION` argument
- When using astyle_py as a library: by passing the version to `Astyle()` constructor

The following versions are supported:

- 3.1 — used by default, unless a different version is specified
- 3.4.7

## Implementation notes

To simplify distribution of astyle, it is compiled to WebAssembly ([astyle_py/libastyle.wasm](astyle_py/libastyle.wasm)) and executed using [wasmtime runtime](https://github.com/bytecodealliance/wasmtime) via its [Python bindings](https://github.com/bytecodealliance/wasmtime-py). This package should work on all operating systems supported by wasmtime — at the time of writing these are:
- x86_64 (amd64) Windows, Linux, macOS
- aarch64 (arm64) Linux and macOS

Other project which wraps astyle into a Python package include:
- https://github.com/timonwong/pyastyle — unmaintained at the time of writing, uses native Astyle binaries
- https://github.com/Freed-Wu/astyle-wheel/ — actively maintained, uses native Astyle binaries

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Copyright and License

* The source code in this repository is Copyright (c) 2020-2022 Ivan Grokhotkov and licensed under the [MIT license](LICENSE).
* `libastyle.wasm` binaries bundled under [astyle_py/lib](astyle_py/lib) directory are built from [Artistic Style project](https://gitlab.com/saalen/astyle), Copyright (c) 2018 by Jim Pattee <jimp03@email.com>, also licensed under the MIT license. See http://astyle.sourceforge.net/ for details.

Thanks to André Simon for maintaining Astyle project!
