# SPDX-FileCopyrightText: 2022 Ivan Grokhotkov <ivan@igrr.me>
# SPDX-License-Identifier: MIT
import sys

from . import __version__
from .args import parse_args
from .astyle_wrapper import ASTYLE_COMPAT_VERSION, Astyle
from .files_iter import iterate_files


def main():
    try:
        args = parse_args(sys.argv[1:])
    except ValueError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(1)

    if args.astyle_version:
        astyle_version = args.astyle_version
    else:
        astyle_version = ASTYLE_COMPAT_VERSION

    astyle = Astyle(version=astyle_version)

    if args.version:
        print('astyle-py {} with Astyle v{}'.format(__version__, astyle.version()))
        raise SystemExit(0)

    def diag(*args_):
        if not args.quiet:
            print(*args_, file=sys.stderr)

    files_with_errors = 0
    files_formatted = 0
    for file_item in iterate_files(args):
        fname = file_item.filename
        astyle.set_options(' '.join(file_item.astyle_options))
        with open(fname) as f:
            original = f.read()
        formatted = astyle.format(original)
        if formatted != original:
            if args.fix_formatting:
                diag('Formatting {}'.format(fname))
                with open(fname, 'w') as f:
                    f.write(formatted)
                files_formatted += 1
            else:
                diag('Formatting error in {}'.format(fname))
                files_with_errors += 1

    if args.fix_formatting:
        if files_formatted:
            diag('Formatted {} files'.format(files_formatted))
    else:
        if files_with_errors:
            diag('Formatting errors found in {} files'.format(files_with_errors))
            raise SystemExit(1)


if __name__ == '__main__':
    main()
