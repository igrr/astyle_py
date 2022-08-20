# SPDX-FileCopyrightText: 2022 Ivan Grokhotkov <ivan@igrr.me>
# SPDX-License-Identifier: MIT
from astyle_py import Astyle


def test_version():
    obj = Astyle()
    assert obj.version() == '3.1'
