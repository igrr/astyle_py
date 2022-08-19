import re
import typing


def get_lines_from_file(fname: str) -> typing.List[str]:
    with open(fname) as f:
        return [
            line.strip()
            for line in f
            if not line.startswith('#') and len(line.strip()) > 0
        ]


def pattern_to_regex(pattern: str) -> str:
    """
    Convert the CODEOWNERS-style path pattern into a regular expression string
    """
    orig_pattern = pattern  # for printing errors later

    # Replicates the logic from normalize_pattern function in Gitlab ee/lib/gitlab/code_owners/file.rb:
    if not pattern.startswith('/'):
        pattern = '/**/' + pattern
    if pattern.endswith('/'):
        pattern = pattern + '**/*'

    # Convert the glob pattern into a regular expression:
    # first into intermediate tokens
    pattern = (
        pattern.replace('**/', ':REGLOB:')
        .replace('**', ':INVALID:')
        .replace('*', ':GLOB:')
        .replace('.', ':DOT:')
        .replace('?', ':ANY:')
    )

    if pattern.find(':INVALID:') >= 0:
        raise ValueError(
            "Likely invalid pattern '{}': '**' should be followed by '/'".format(
                orig_pattern
            )
        )

    # then into the final regex pattern:
    re_pattern = (
        pattern.replace(':REGLOB:', '(?:.*/)?')
        .replace(':GLOB:', '[^/]*')
        .replace(':DOT:', '[.]')
        .replace(':ANY:', '.')
        + '$'
    )
    if re_pattern.startswith('/'):
        re_pattern = '^' + re_pattern

    return re_pattern


def file_excluded(
    fname: str, exclude_regexes: typing.Iterable[typing.Pattern[str]]
) -> bool:
    for regex in exclude_regexes:
        if re.search(regex, '/' + fname):
            return True
    return False
