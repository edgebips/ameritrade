"""Print configuration and attempt to connect, to validate that it works.
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

import argparse
import logging

from ameritrade import scripts


def check():
    parser = argparse.ArgumentParser(description=__doc__.strip())
    scripts.add_script_args(parser)
    args = parser.parse_args()
    api = scripts.open_with_args(args)


if __name__ == '__main__':
    check()
