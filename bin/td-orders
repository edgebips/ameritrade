#!/usr/bin/env python3
"""Print all active orders (for debugging).
"""
__author__ = 'Martin Blais <blais@furius.ca>'

import argparse
import pprint

import ameritrade as td
from ameritrade import utils


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip())
    td.add_args(parser)
    args = parser.parse_args()
    api = td.open(td.config_from_args(args))
    account_id = utils.GetMainAccount(api)

    orders = api.GetOrdersByPath(accountId=account_id)
    for order in orders:
        if order['status'] in utils.ACTIVE_STATUS:
            pprint.pprint(order)


if __name__ == '__main__':
    main()
