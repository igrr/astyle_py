# SPDX-FileCopyrightText: 2022 Ivan Grokhotkov <ivan@igrr.me>
# SPDX-License-Identifier: MIT
from .astyle_wrapper import Astyle, AstyleError
from .version import __version__

__all__ = ['Astyle', 'AstyleError', '__version__']
