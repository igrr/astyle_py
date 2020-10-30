# astyle_py — Python wrapper around [astyle](http://astyle.sourceforge.net/)

[Artistic Style (astyle)](http://astyle.sourceforge.net/) is a source code indenter, formatter, and beautifier for the C, C++, C++/CLI, Objective‑C, C# and Java programming languages.

This project wraps `astyle` in a Python package, compatible with [pre-commit](https://pre-commit.com/) framework.
It allows you to fix source code formatting with a Git pre-commit hook.
The main motivation for using this Python wrapper, rather than native `astyle` binaries, is that users of all operating systems will be using exactly the same version of astyle. This prevents formatting differences which sometimes occur between different versions of astyle.

To simplify distribution of astyle, it is compiled to WebAssembly ([astyle_py/libastyle.wasm](astyle_py/libastyle.wasm)) and executed using wasmtime runtime via its Python bindings. This package should work on all operating systems supported by wasmtime — at the time of writing these are the x86_64 versions of Windows, Linux, macOS, and aarch64 Linux.

## Usage

By default, `astyle_py` formats the files specified, according to the given options.

### With pre-commit

1. Set up pre-commit for your project as described in https://pre-commit.com/#install.
2. Add `astyle_py` to your `.pre-commit-config.yaml` file:
   ```yaml
   repos:
   -   repo: https://github.com/igrr/astyle_py.git
       rev: master
       hooks:
       -   id: astyle_py
           args: [--style=linux]
   ```

   Place the required astyle formatting options to the `args` array. See the next section for details.

   If necessary, add `verbose: true` to see the output.

   Use `files:` option to configure the regex pattern used to match the files to be formatted. Default is `'^.*\.(c|cpp|cxx|h|hpp|inc)$'`.

### From command line

There is no PyPI release yet, but you can install the package directly from Github:
```
pip install git+https://github.com/igrr/astyle_py.git
```

Usage:
```
astyle_py [options] <files>
```

`<files>` — list of files to process

`[options]` — astyle formatting options, see http://astyle.sourceforge.net/astyle.html for reference.

Note that __only a few__ of the options in ["Other options"](http://astyle.sourceforge.net/astyle.html#_Other_Options) and ["Command Line Only"](http://astyle.sourceforge.net/astyle.html#_Command_Line_Only) are supported, namely:

* `--options=<file>` — read more options from the specified file. Empty lines and lines starting with `#` are ignored.
* `--dry-run` — don't format the files, return non-zero exit code if any file would change after formatting.
* `--exclude=<pattern>` — skip files matching the given pattern. Note that patterns use the syntax of [Gitlab CODEOWNERS files](https://docs.gitlab.com/ee/user/project/code_owners.html#the-syntax-of-code-owners-files).
* `--exclude-list=<file>` — skip files matching the list of patterns specified in a file.
* `--version` — print the version and exit.
* `--quiet` — don't print diagnostic messages; by default the files containing errors or files which are formatted are listed in stderr.

