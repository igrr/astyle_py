# SPDX-FileCopyrightText: 2022 Ivan Grokhotkov <ivan@igrr.me>
# SPDX-License-Identifier: MIT
import pytest

from astyle_py import Astyle, AstyleError


def test_version():
    obj = Astyle()
    assert obj.version() == '3.1'

    obj = Astyle(version='3.4.7')
    assert obj.version() == '3.4.7'

    with pytest.raises(ValueError):
        Astyle(version='1.2.3')


def test_astyle_invalid_option():
    obj = Astyle()
    obj.set_options('--invalid-option')
    with pytest.raises(AstyleError):
        obj.format('int main() {}')
