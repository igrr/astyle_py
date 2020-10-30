# astyle_py — Python wrapper around [astyle](http://astyle.sourceforge.net/)

[Artistic Style (astyle)](http://astyle.sourceforge.net/) is a source code indenter, formatter, and beautifier for the C, C++, C++/CLI, Objective‑C, C# and Java programming languages.

This project wraps `astyle` in a Python package, compatible with [pre-commit](https://pre-commit.com/) framework.
It allows you to fix source code formatting with a Git pre-commit hook.
The main motivation for using this Python wrapper, rather than native `astyle` binaries, is that users of all operating systems will be using exactly the same version of astyle. This prevents formatting differences which sometimes occur between different versions of astyle.

