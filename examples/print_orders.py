#!/usr/bin/env python3
"""Print active orders (for debugging).
"""
__author__ = 'Martin Blais <blais@furius.ca>'

import argparse
import collections
import datetime
import logging
import math
import itertools
import pprint
import re
import time
from typing import Any, Optional, Tuple

import ameritrade as td
from ameritrade import utils


def main():
    """Compute various vol estimates."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)-8s: %(message)s')
    parser = argparse.ArgumentParser(description=__doc__.strip())
    td.add_args(parser)
    args = parser.parse_args()
    config = td.config_from_args(args)
    config = config._replace(readonly=False)
    api = td.open(config)
    account_id = utils.GetMainAccount(api)

    orders = api.GetOrdersByPath(accountId=account_id)
    for order in orders:
        if order['status'] in utils.ACTIVE_STATUS:
            pprint.pprint(order)


if __name__ == '__main__':
    main()
