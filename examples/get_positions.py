#!/usr/bin/env python3
"""Get the current list of options positions.
"""
__author__ = 'Martin Blais <blais@furius.ca>'

import argparse
import collections
import logging
import math
import pprint

import pandas as pd

import ameritrade


def GetPositions(accounts) -> pd.DataFrame:
    """Parse the list of positions out of an accounts definition."""
    rows = []
    for account in accounts:
        for subtype, subaccount in account.items():
            assert subtype == 'securitiesAccount'
            if 'positions' not in subaccount:
                continue
            positions = subaccount['positions']
            for pos in positions:
                inst = pos['instrument']
                if inst['assetType'] != 'OPTION':
                    continue
                quantity = pos['longQuantity'] - pos['shortQuantity']
                maintenance = pos['maintenanceRequirement']
                row = [quantity,
                       inst['underlyingSymbol'],
                       inst['cusip'],
                       inst['symbol'],
                       inst['description'],
                       maintenance]
                pprint.pprint(pos)
                rows.append(row)
    return pd.DataFrame(
        rows, columns=['quantity', 'underlying', 'cusip', 'symbol', 'description', 'maint'])


def main():
    """Compute various vol estimates."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)-8s: %(message)s')
    parser = argparse.ArgumentParser(description=__doc__.strip())
    ameritrade.add_args(parser)
    args = parser.parse_args()
    config = ameritrade.config_from_args(args)
    api = ameritrade.open(config)

    # Fetch account information.
    #
    # This does appear not suffer time to settlement or delays, so could be used
    # to build monitoring UI.
    accounts = api.GetAccounts(fields='positions')

    dfpos = GetPositions(accounts)
    print(dfpos.to_string())

    # TODO(blais): Compute beta-weighted portfolio delta.


if __name__ == '__main__':
    main()
