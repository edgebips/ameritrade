#!/usr/bin/env python3
"""Test client program for the Ameritrade API.

Set AMERITRADE_API_DIR to a private directory where your secrets will be stored.
Also, generate the required SSL certificates there.
"""
__author__ = 'Martin Blais <blais@furius.ca>'

from os import path
import argparse
import logging
import os
from pprint import pprint
from typing import NamedTuple
from decimal import Decimal

import ameritrade

# Set these values before calling this.
CLIENT_ID = os.environ['AMERITRADE_CLIENT_ID']
CONFIG_DIR = os.environ['AMERITRADE_CONFIG_DIR']


Option = NamedTuple('Option', [
    ('symbol', str),
    ('quantity', Decimal),
    ('marketValue', Decimal),
])


def get_options_values(api):
    """Gather and return the list and current market values of options positions."""
    options = []
    for account in api.GetAccounts(fields='positions'):
        _, account = next(iter(account.items()))
        positions = account.get('positions', None)
        if not positions:
            continue
        for pos in positions:
            #pprint(pos)
            if pos['instrument']['assetType'] != 'OPTION':
                continue
            quantity = Decimal(pos['longQuantity']) - Decimal(pos['shortQuantity'])
            options.append(Option(pos['instrument']['symbol'],
                                  quantity,
                                  Decimal(pos['marketValue'])))
    return options


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('-c', '--client_id', action='store',
                        default=CLIENT_ID,
                        help='The client id OAuth username')
    parser.add_argument('-x', '--expire', action='store_true',
                        help="Expire OAuth token explicitly")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    api = ameritrade.open_with_dir(client_id=args.client_id,
                                   redirect_uri='https://localhost:8444',
                                   config_dir=CONFIG_DIR)

    instruments = api.SearchInstruments(symbol='SPY', projection='symbol-search')
    hours = api.GetHoursMultipleMarkets()
    hours = api.GetHoursMultipleMarkets()
    pprint.pprint(hours)

    for o in get_options_values(api):
        print(o)


if __name__ == '__main__':
    main()
