# SPDX-FileCopyrightText: 2022 Ivan Grokhotkov <ivan@igrr.me>
# SPDX-License-Identifier: MIT
from collections import namedtuple

from .utils import get_lines_from_file

AstyleArgs = namedtuple(
    'AstyleArgs',
    ['rules', 'options', 'files', 'exclude_list', 'fix_formatting', 'quiet'],
)


def parse_args(args) -> AstyleArgs:
    i = 0
    for i, arg in enumerate(args):
        if not arg.startswith('--'):
            break
    else:
        i = len(args)

    options = args[:i]
    files = args[i:]
    exclude_list = []
    fix_formatting = True
    quiet = False
    rules = None
    options_to_remove = []

    for o in options:
        o_trimmed = o[2:] if o.startswith('--') else o
        parts = o_trimmed.split('=')
        opt = parts[0]
        value = parts[1] if len(parts) > 1 else None

        def ensure_value():
            if not value:
                raise ValueError('Option --{} requires a value'.format(opt))

        if opt == 'dry-run':
            options_to_remove.append(o)
            fix_formatting = False

        elif opt == 'options':
            options_to_remove.append(o)
            ensure_value()
            options += get_lines_from_file(value)

        elif opt == 'exclude':
            options_to_remove.append(o)
            ensure_value()
            exclude_list.append(value)

        elif opt == 'exclude-list':
            options_to_remove.append(o)
            ensure_value()
            exclude_list += get_lines_from_file(value)

        elif opt == 'quiet':
            options_to_remove.append(o)
            quiet = True

        elif opt == 'rules':
            options_to_remove.append(o)
            ensure_value()
            rules = value

    for o in options_to_remove:
        options.remove(o)

    has_rules = rules is not None
    has_options_or_exclude_list = options or exclude_list
    if has_rules and has_options_or_exclude_list:
        raise ValueError(
            '--options, --exclude, --exclude-list can\'t be used together with --rules'
        )

    return AstyleArgs(
        rules=rules,
        options=options,
        files=files,
        exclude_list=exclude_list,
        fix_formatting=fix_formatting,
        quiet=quiet,
    )
