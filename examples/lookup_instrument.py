#!/usr/bin/env python3
"""Produce instrument detail.
"""
__author__ = 'Martin Blais <blais@furius.ca>'

import argparse
import logging
import pprint
import json

import ameritrade


def main():
    """Compute various vol estimates."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)-8s: %(message)s')
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('symbol', action='store',
                        help="TD symbol or CUSIP symbol to look up.")
    ameritrade.add_args(parser)
    args = parser.parse_args()
    config = ameritrade.config_from_args(args)
    api = ameritrade.open(config)

    resp = api.GetInstrument(cusip=args.symbol)
    pprint.pprint(resp)


if __name__ == '__main__':
    main()
