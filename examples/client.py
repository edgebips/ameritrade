#!/usr/bin/env python3
"""Test client program for the Ameritrade API.
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
from ameritrade import utils


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


def first(iterable):
    return next(iter(iterable))

def only(dictionary):
    assert len(dictionary) == 1
    return first(dictionary.values())


def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)-8s: %(message)s')
    parser = argparse.ArgumentParser(description=__doc__.strip())
    ameritrade.add_args(parser)
    args = parser.parse_args()
    config = ameritrade.config_from_args(args)
    api = ameritrade.open(config)

    accountId = utils.GetMainAccount(api)

    # prefs = api.GetPreferences(accountId=accountId)
    # pprint(prefs)

    # keys = api.GetStreamerSubscriptionKeys(accountIds=accountId)
    # pprint(keys)

    # up = api.GetUserPrincipals(fields='surrogateIds')
    # pprint(up)

    # txns = api.GetTransactions(accountId=accountId)
    # pprint(txns)

    # inst = api.GetInstrument(cusip='THCX_021921P13')
    # pprint(inst)

    # insts = api.SearchInstruments(symbol='THCX_021921P13', projection='symbol-search')
    # pprint(insts)

    # instruments = api.SearchInstruments(symbol='SPY', projection='symbol-search')
    # hours = api.GetHoursMultipleMarkets()
    # hours = api.GetHoursMultipleMarkets()
    # pprint.pprint(hours)

    # for o in get_options_values(api):
    #     print(o)

    # quotes = api.GetQuotes(symbol='VTI')
    # pprint(quotes)

    # hist = api.GetPriceHistory(symbol='VTI')
    # pprint(hist)


if __name__ == '__main__':
    main()
