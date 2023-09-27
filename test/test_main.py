# SPDX-FileCopyrightText: 2023 Ivan Grokhotkov <ivan@igrr.me>
# SPDX-License-Identifier: MIT
import pathlib

import pytest
from test_files_iter import chdir_ctx

from astyle_py import __version__
from astyle_py.__main__ import astyle_py_main

# tmp_path: pathlib.Path


def test_main_version(capfd: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as e:
        astyle_py_main(['--version'])
    assert e.value.code == 0
    out, err = capfd.readouterr()
    assert out == f'astyle-py {__version__} with Astyle v3.1\n'
    assert err == ''


def test_main_specific_version(capfd: pytest.CaptureFixture[str]):
    ver = '3.4.7'
    with pytest.raises(SystemExit) as e:
        astyle_py_main([f'--astyle-version={ver}', '--version'])
    assert e.value.code == 0
    out, err = capfd.readouterr()
    assert out == f'astyle-py {__version__} with Astyle v{ver}\n'
    assert err == ''


def test_main_invalid_version(capfd: pytest.CaptureFixture[str]):
    ver = '1.2.3'
    with pytest.raises(SystemExit) as e:
        astyle_py_main([f'--astyle-version={ver}'])
    assert e.value.code == 1
    out, err = capfd.readouterr()
    assert out == ''
    assert f'Unsupported astyle version: {ver}. Available versions:' in err


def test_main_option_requires_value(capfd: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as e:
        astyle_py_main(['--exclude'])
    assert e.value.code == 1
    out, err = capfd.readouterr()
    assert out == ''
    assert 'Option --exclude requires a value' in err


def test_main_no_files(capfd: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as e:
        astyle_py_main([])
    assert e.value.code == 0
    out, err = capfd.readouterr()
    assert out == ''
    assert err == 'No files specified\n'


def test_main_formatting_error_invalid_arg(
    capfd: pytest.CaptureFixture[str], tmp_path: pathlib.Path
):
    base = str(tmp_path.absolute())
    (tmp_path / 'file_a.c').touch()

    with chdir_ctx(base):
        with pytest.raises(SystemExit) as e:
            astyle_py_main(['--invalid-arg', 'file_a.c'])
        assert e.value.code == 1
        out, err = capfd.readouterr()
        assert out == ''
        assert (
            'Error formatting file_a.c: error: Invalid Artistic Style options:\n\tinvalid-arg\n'
            in err
        )


def test_formatted_quiet(capfd: pytest.CaptureFixture[str], tmp_path: pathlib.Path):
    # Check in formatting mode (no --dry-run)
    base = str(tmp_path.absolute())
    (tmp_path / 'file_a.c').write_text('int main() { foo(); }\n')
    (tmp_path / 'file_b.c').write_text('int main()\n{\n    foo();\n}\n')

    with chdir_ctx(base):
        with pytest.raises(SystemExit) as e:
            astyle_py_main(['--style=otbs', '--quiet', 'file_a.c', 'file_b.c'])
        assert e.value.code == 0
        out, err = capfd.readouterr()
        assert out == ''
        assert err == ''

    # first file formatted, 2nd unchanged
    assert (tmp_path / 'file_a.c').read_text() == 'int main()\n{\n    foo();\n}\n'
    assert (tmp_path / 'file_b.c').read_text() == 'int main()\n{\n    foo();\n}\n'

    # Now check in --dry-run mode (no formatting)
    (tmp_path / 'file_a.c').write_text('int main() { foo(); }\n')
    (tmp_path / 'file_b.c').write_text('int main()\n{\n    foo();\n}\n')

    with chdir_ctx(base):
        with pytest.raises(SystemExit) as e:
            astyle_py_main(
                ['--style=otbs', '--quiet', '--dry-run', 'file_a.c', 'file_b.c']
            )
        assert e.value.code == 1
        out, err = capfd.readouterr()
        assert out == ''
        assert err == ''

    # Files should not be modified in dry-run mode
    assert (tmp_path / 'file_a.c').read_text() == 'int main() { foo(); }\n'
    assert (tmp_path / 'file_b.c').read_text() == 'int main()\n{\n    foo();\n}\n'


def test_formatted_verbose(capfd: pytest.CaptureFixture[str], tmp_path: pathlib.Path):
    base = str(tmp_path.absolute())
    (tmp_path / 'file_a.c').write_text('int main() { foo(); }\n')
    (tmp_path / 'file_b.c').write_text('int main()\n{\n    foo();\n}\n')

    with chdir_ctx(base):
        with pytest.raises(SystemExit) as e:
            astyle_py_main(['--style=otbs', 'file_a.c', 'file_b.c'])
        assert e.value.code == 0
        out, err = capfd.readouterr()
        assert out == ''
        assert 'Formatting file_a.c' in err
        assert 'Formatted 1 files' in err

    assert (tmp_path / 'file_a.c').read_text() == 'int main()\n{\n    foo();\n}\n'
    assert (tmp_path / 'file_b.c').read_text() == 'int main()\n{\n    foo();\n}\n'


def test_formatted_verbose_dry_run(
    capfd: pytest.CaptureFixture[str], tmp_path: pathlib.Path
):
    base = str(tmp_path.absolute())
    (tmp_path / 'file_a.c').write_text('int main() { foo(); }\n')
    (tmp_path / 'file_b.c').write_text('int main()\n{\n    foo();\n}\n')

    with chdir_ctx(base):
        with pytest.raises(SystemExit) as e:
            astyle_py_main(['--style=otbs', '--dry-run', 'file_a.c', 'file_b.c'])
        assert e.value.code == 1
        out, err = capfd.readouterr()
        assert out == ''
        assert 'Formatting error in file_a.c' in err
        assert 'Formatting errors found in 1 files' in err

    assert (tmp_path / 'file_a.c').read_text() == 'int main() { foo(); }\n'
    assert (tmp_path / 'file_b.c').read_text() == 'int main()\n{\n    foo();\n}\n'


def test_all_files_excluded_warning(
    capfd: pytest.CaptureFixture[str], tmp_path: pathlib.Path
):
    base = str(tmp_path.absolute())
    (tmp_path / 'file_a.c').touch()

    with chdir_ctx(base):
        with pytest.raises(SystemExit) as e:
            astyle_py_main(['--exclude=*.c', 'file_a.c'])
        assert e.value.code == 0
        out, err = capfd.readouterr()
        assert out == ''
        assert 'No files checked, excluded by --exclude/--exclude-list option' in err
