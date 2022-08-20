# SPDX-FileCopyrightText: 2022 Ivan Grokhotkov <ivan@igrr.me>
# SPDX-License-Identifier: MIT
import re
from collections import namedtuple
from typing import Generator, List

from .args import AstyleArgs
from .utils import pattern_to_regex

FileItem = namedtuple('FileItem', ['filename', 'astyle_options'])


def iterate_files(args: AstyleArgs) -> Generator[FileItem, None, None]:
    if args.rules is None:
        yield from iterate_files_simple(args.files, args.exclude_list, args.options)
    else:
        raise NotImplementedError('args.rules not implemented yet')


def iterate_files_simple(
    files: List[str], exclude_list: List[str], options: List[str]
) -> Generator[FileItem, None, None]:
    exclude_regexes = [re.compile(pattern_to_regex(p)) for p in exclude_list]

    for fname in files:
        if any((re.search(regex, f'/{fname}') for regex in exclude_regexes)):
            continue
        yield FileItem(filename=fname, astyle_options=options)
