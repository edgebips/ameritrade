"""Print configuration and attempt to connect, to validate that it works.
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

import argparse
import logging
import pprint

from ameritrade import scripts
from ameritrade import api


def check():
    parser = argparse.ArgumentParser(description=__doc__.strip())
    scripts.add_args(parser)
    args = parser.parse_args()

    # Print the configuration.
    config = scripts.config_from_args(args, lazy=False)
    pprint.pprint(dict(config._asdict()))

    # Attempt to connect (non-lazy open).
    try:
        api_ = api.open(config)
    except Exception as exc:
        print("Failure connecting: {}".format(exc))
    else:
        print("Success connecting: {}".format(api_))


if __name__ == '__main__':
    check()
