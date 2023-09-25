# SPDX-FileCopyrightText: 2022 Ivan Grokhotkov <ivan@igrr.me>
# SPDX-License-Identifier: MIT
import os
import pathlib
import textwrap
from contextlib import contextmanager

from astyle_py.files_iter import FileItem, iterate_files_rules, iterate_files_simple


@contextmanager
def chdir_ctx(path):
    cwd = os.getcwd()
    try:
        yield os.chdir(path)
    finally:
        os.chdir(cwd)


def test_iter_simple(tmp_path: pathlib.Path):
    base = str(tmp_path.absolute())
    (tmp_path / 'file_a.c').touch()
    (tmp_path / 'file_b.c').touch()
    (tmp_path / 'sub').mkdir()
    (tmp_path / 'sub' / 'file_c.c').touch()
    (tmp_path / 'sub' / 'sub2').mkdir()
    (tmp_path / 'sub' / 'sub2' / 'file_d.c').touch()

    all_files = sorted(str(p.relative_to(base)) for p in tmp_path.glob('**/*.c'))
    assert len(all_files) == 4

    options = ['--opta', '--optb=2']

    with chdir_ctx(base):
        # no excludes
        items = list(iterate_files_simple(all_files, [], options))
        assert sorted([it.filename for it in items]) == all_files
        assert all(it.astyle_options == options for it in items)

        # exclude all
        items = list(iterate_files_simple(all_files, ['/**/*.c'], options))
        assert items == []

        # exclude all another way
        items = list(iterate_files_simple(all_files, ['*.c'], options))
        assert items == []

        # exclude sub2
        items = list(iterate_files_simple(all_files, ['sub2/'], options))
        assert sorted([it.filename for it in items]) == [
            'file_a.c',
            'file_b.c',
            os.path.join('sub', 'file_c.c'),
        ]

        # exclude sub*
        items = list(iterate_files_simple(all_files, ['sub*/'], options))
        assert sorted([it.filename for it in items]) == ['file_a.c', 'file_b.c']

        # exclude one file form sub
        items = list(iterate_files_simple(all_files, ['sub/file_?.c'], options))
        assert sorted([it.filename for it in items]) == [
            'file_a.c',
            'file_b.c',
            os.path.join('sub', 'sub2', 'file_d.c'),
        ]


def test_iter_rules(tmp_path: pathlib.Path):
    base = str(tmp_path.absolute())
    (tmp_path / 'file_a.c').touch()
    (tmp_path / 'file_b.c').touch()
    (tmp_path / 'sub').mkdir()
    (tmp_path / 'sub' / 'file_c.c').touch()
    (tmp_path / 'sub' / 'sub2').mkdir()
    (tmp_path / 'sub' / 'sub2' / 'file_d.c').touch()

    all_files = sorted(str(p.relative_to(base)) for p in tmp_path.glob('**/*.c'))
    assert len(all_files) == 4

    rules_str = textwrap.dedent(
        """
        DEFAULT:
            options: "--opt1 --opt2=foo"
            check: true

        rule_1:
            include:
                - "*_b.c"
            options: "--opt3 --opt4=bar"

        rule_2:
            include:
                - "/sub/"
            check: false

        rule_3:
            include:
                - "/**/sub2/"
            options: "--opt7 --opt8=ffs"
    """
    )
    rules_file = tmp_path / 'rules'
    rules_file.write_text(rules_str)

    items = list(iterate_files_rules(all_files, str(rules_file)))
    assert len(items) == 3
    assert FileItem('file_a.c', ['--opt1', '--opt2=foo']) in items
    assert FileItem('file_b.c', ['--opt3', '--opt4=bar']) in items
