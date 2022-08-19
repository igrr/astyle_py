from collections import namedtuple

from .utils import get_lines_from_file

AstyleArgs = namedtuple(
    'AstyleArgs', ['options', 'files', 'exclude_list', 'fix_formatting', 'quiet']
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
    options_to_remove = []

    for o in options:
        o_trimmed = o[2:] if o.startswith('--') else o
        parts = o_trimmed.split('=')
        opt = parts[0]
        value = parts[1] if len(parts) > 1 else None

        def ensure_value():
            if not value:
                raise ValueError('Option {} requires a value'.format(opt))

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

    for o in options_to_remove:
        options.remove(o)

    return AstyleArgs(
        options=options,
        files=files,
        exclude_list=exclude_list,
        fix_formatting=fix_formatting,
        quiet=quiet,
    )
