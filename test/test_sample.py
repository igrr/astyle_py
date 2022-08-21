# SPDX-FileCopyrightText: 2022 Ivan Grokhotkov <ivan@igrr.me>
# SPDX-License-Identifier: MIT
import os
import subprocess
import sys


def test_sample():
    subprocess.check_call(
        [sys.executable, os.path.join(os.path.dirname(__file__), '..', 'sample.py')]
    )
