#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2022 Ivan Grokhotkov <ivan@igrr.me>
# SPDX-License-Identifier: Unlicense OR CC0-1.0
import textwrap

from astyle_py import Astyle


def main():
    # Create the formatter
    formatter = Astyle()

    # Get the version of Astyle
    version: str = formatter.version()
    print(f'Formatted with Astyle v{version}:')

    # Set formatting options
    formatter.set_options('--style=mozilla --mode=c')

    # Original source to format
    source = textwrap.dedent(
        '''
        int main(int argc, char** argv) {
          if (argc == 0) {
            return 1;
          }
          return 0;
        }
        '''
    ).strip()

    # Format!
    result: str = formatter.format(source)
    print(result)

    # This should be the result
    expected = textwrap.dedent(
        '''
        int main(int argc, char** argv)
        {
            if (argc == 0) {
                return 1;
            }
            return 0;
        }
        '''
    ).strip()
    assert result == expected


if __name__ == '__main__':
    main()
