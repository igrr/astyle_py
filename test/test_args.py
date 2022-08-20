# SPDX-FileCopyrightText: 2022 Ivan Grokhotkov <ivan@igrr.me>
# SPDX-License-Identifier: MIT
import pathlib

import pytest
from test_files_iter import chdir_ctx

from astyle_py.args import parse_args


def test_args_default():
    args = parse_args([])
    assert not args.quiet
    assert args.fix_formatting


def test_args_simple():
    args = parse_args(['--quiet', '--dry-run', '--exclude=foo.c', 'bar.c', 'baz.c'])
    assert args.quiet
    assert not args.fix_formatting
    assert args.files == ['bar.c', 'baz.c']
    assert args.exclude_list == ['foo.c']


def test_option_requires_value():
    options = ['--exclude', '--exclude-list', '--options', '--rules']

    for option in options:
        with pytest.raises(ValueError) as exp:
            parse_args([option])
        assert f'Option {option} requires a value' in str(exp.value)


def test_options_from_file(tmp_path: pathlib.Path):
    excl_list_file = tmp_path / 'exclude.txt'
    exclude_list = ['# comment', '*.inc', '/sub/**/*.c']
    excl_list_file.write_text('\n'.join(exclude_list))

    options_list_file = tmp_path / 'options.txt'
    options_list = ['--style=otbs', '# comment 2', '--attach-namespace']
    options_list_file.write_text('\n'.join(options_list))

    with chdir_ctx(tmp_path):
        args = parse_args(
            [
                '--cmdline-arg=foo',
                '--exclude=bar.c',
                '--exclude-list=exclude.txt',
                '--options=options.txt',
            ]
        )

    assert args.exclude_list == ['bar.c', '*.inc', '/sub/**/*.c']
    assert args.options == ['--cmdline-arg=foo', '--style=otbs', '--attach-namespace']
