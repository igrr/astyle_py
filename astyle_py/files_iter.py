# SPDX-FileCopyrightText: 2022 Ivan Grokhotkov <ivan@igrr.me>
# SPDX-License-Identifier: MIT
import os
import re
from collections import namedtuple
from typing import Generator, List, Pattern

import yaml

from .args import AstyleArgs
from .utils import pattern_to_regex

FileItem = namedtuple('FileItem', ['filename', 'astyle_options'])
Rule = namedtuple('Rule', ['check', 'include', 'options'])


def file_matches_patterns(fname: str, patterns: List[Pattern]) -> bool:
    # Normalize the path (remove any '..').
    fname_norm = os.path.normpath(fname)
    # Regex patterns are written with forward slashes in mind,
    # convert the file path to use forward slashes as well.
    fname_fwdslash = fname_norm.replace(os.path.sep, '/')
    # Make the path 'absolute', with root being the root
    # of the project (where this tool is invoked)
    fname_match = f'/{fname_fwdslash}'

    return any((re.search(regex, fname_match) for regex in patterns))


def iterate_files(args: AstyleArgs) -> Generator[FileItem, None, None]:
    if args.rules is None:
        yield from iterate_files_simple(args.files, args.exclude_list, args.options)
    else:
        yield from iterate_files_rules(args.files, args.rules)


def iterate_files_simple(
    files: List[str], exclude_list: List[str], options: List[str]
) -> Generator[FileItem, None, None]:
    exclude_regexes = [re.compile(pattern_to_regex(p)) for p in exclude_list]

    for fname in files:
        if file_matches_patterns(fname, exclude_regexes):
            continue
        yield FileItem(filename=fname, astyle_options=options)


def iterate_files_rules(
    files: List[str], rules_file: str
) -> Generator[FileItem, None, None]:
    with open(rules_file, 'r', encoding='utf-8') as rf:
        rules_dict = yaml.safe_load(rf)

    # set the default rule
    default_rule = Rule(check=True, include=[pattern_to_regex('*')], options=[])

    # if 'DEFAULT' key is in the YAML file, use it to update the default rule
    default_rule_dict = rules_dict.get('DEFAULT')
    if default_rule_dict:
        default_rule = get_rule_from_dict('DEFAULT', default_rule_dict, default_rule)

    # load the rest of the rules
    rules = []  # type: List[Rule]
    for rule_name, rule_dict in rules_dict.items():
        if rule_name == 'DEFAULT':
            continue
        r = get_rule_from_dict(rule_name, rule_dict, default_rule)
        rules.append(r)

    # now process the files
    for fname in files:
        # search for a rule for this file
        yield from process_rules_for_file(fname, rules, default_rule)


def get_rule_from_dict(rule_name: str, rule_dict, defaults: Rule) -> Rule:
    options = defaults.options
    check = defaults.check
    include = defaults.include

    for k, v in rule_dict.items():
        if k == 'options':
            if not isinstance(v, str):
                raise ValueError(
                    f'Unexpected value of \'options\' in rule {rule_name}, expected a string, found {v}'
                )
            options = v.split(' ')
        elif k == 'check':
            if not isinstance(v, bool):
                raise ValueError(
                    f'Unexpected value of \'check\' in rule {rule_name}, expected a boolean, found {v}'
                )
            check = v
        elif k == 'include':
            if not isinstance(v, list) or not all((isinstance(x, str) for x in v)):
                raise ValueError(
                    f'Unexpected value of \'include\' in rule {rule_name}, expected a list of strings, found {v}'
                )
            include = [re.compile(pattern_to_regex(x)) for x in v]
        else:
            raise ValueError(
                f'Unexpected key \'{k}\' in rule {rule_name}, expected one of: options, check, include'
            )

    return Rule(check, include, options)


def process_rules_for_file(
    fname: str, rules: List[Rule], default_rule: Rule
) -> Generator[FileItem, None, None]:
    selected_rule = default_rule
    for rule in rules:
        if file_matches_patterns(fname, rule.include):
            selected_rule = rule
    if selected_rule.check:
        yield FileItem(filename=fname, astyle_options=selected_rule.options)
