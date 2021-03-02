#!/usr/bin/env python3
"""Replace TD ameritrade links.
"""

import re
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('filenames', help='Filenames')
    args = parser.parse_args()

    for line in open(args.filenames):
        sys.stdout.write(re.sub(r"\^(\d{9,11})\b", r"^td-\1", line))


if __name__ == '__main__':
    main()
