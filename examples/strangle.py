#!/usr/bin/env python3
"""Quotes for simple daily short strangle options strategy.

Note: For a similar free source of data, you could also use this:
https://query1.finance.yahoo.com/v7/finance/options/SPY
"""
__author__ = 'Martin Blais <blais@furius.ca>'

from pprint import pprint
import argparse
import datetime
import logging
import math
import re

import numpy

import ameritrade
from baskets.table import Table


def first(iterable):
    return next(iter(iterable))


def get_chain_table(dateMap):
    columns = sorted(first(first(dateMap.values()).values())[0].keys())
    rows = []
    for dateDays, priceMap in sorted(dateMap.items()):
        _, __, days = dateDays.partition(':')
        for price, optionlist in sorted(priceMap.items()):
            for option in optionlist:
                rows.append([option[col] for col in columns])
    return Table(columns, [str] * len(columns), rows)


def get_candidates(chain, args):
    """Produce a table of candidates OTM calls to sell."""

    # Convert options to a table.
    dateMap = chain['callExpDateMap']
    tbl = get_chain_table(dateMap)

    # Remove ITM strikes.
    tbl = (tbl
           .filter(lambda row: not row.inthemoney)
           .delete(['inthemoney']))

    # Compute median bid and ask sizes and filter to instruments with at least
    # this size.
    median_bidsize = numpy.median(tbl.array('bidsize'))
    median_asksize = numpy.median(tbl.array('asksize'))
    tbl = (tbl
           .filter(lambda row: (row.bidsize > median_bidsize and
                                row.asksize > median_asksize)))

    # Compute a rough estimate of volatility or use that which is given.
    if args.volatility:
        volatility = args.volatility
    else:
        vol_values = tbl.array('volatility')
        volatility = numpy.mean(vol_values)

    # Trim down the columns.
    tbl = tbl.select(['symbol', 'description', 'bid', 'ask', 'timevalue',
                      'bidsize', 'asksize',
                      'daystoexpiration', 'strikeprice', 'volatility'])

    # Filter on rough probability estimate.
    underlying = chain['underlyingPrice']
    tbl = (tbl
           .create('expi_vol',
                   lambda row: volatility * math.sqrt(row.daystoexpiration/365.))
           .filter(lambda row: row.strikeprice >= (underlying + args.pvalue * row.expi_vol)))

    # Mark options that are too close to the underlying price.
    tbl = tbl.create('pctaway',
                     lambda row: 100*abs(1 - row.strikeprice / underlying))

    if args.near_margin:
        frac_margin = args.near_margin/100
        tbl = tbl.filter(lambda row: abs(1 - row.strikeprice / underlying) >= frac_margin)

    # Sort to exhibit most interesting by some criteria.
    tbl = tbl.order(
        lambda row: (-row.daystoexpiration, row.pctaway, row.bid, row.bidsize + row.asksize),
        asc=False)

    return tbl


def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)-8s: %(message)s')
    parser = argparse.ArgumentParser(description=__doc__.strip())
    ameritrade.add_script_args(parser)

    parser.add_argument('-s', '--underlying', '--stock', action='store',
                        default='$XSP.X',  # E-mini S&P 500 Futures
                        help="Name of the underlying to use.")

    parser.add_argument('-v', '--volatility', '--vol', action='store', type=float,
                        help=("Volatility assumption (if not present, use single estimate "
                              "of implied vol)."))

    parser.add_argument('-p', '--pvalue', action='store', type=float,
                        default=2.0,  # 95%
                        help="Minimum p-value to use.")

    parser.add_argument('-m', '--near-margin', action='store', type=float,
                        help=("Fixed (over time) minimum margin (in pct) away from "
                              "the underlying."))

    parser.add_argument('-f', '--filter', action='store',
                        help="Filter on the description field (for Weekly or Monthly)")

    args = parser.parse_args()
    config = ameritrade.config_from_args(args)
    api = ameritrade.open(config)

    # Fetch call chain.
    fromDate = datetime.date.today() + datetime.timedelta(days=5)
    toDate = datetime.date.today() + datetime.timedelta(days=45)
    chain = api.GetOptionChain(symbol=args.underlying, strategy='SINGLE', contractType='CALL',
                               range='SAK',
                               fromDate=fromDate, toDate=toDate)
    if chain['status'] != 'SUCCESS':
        logging.error(chain)
        return

    tbl = get_candidates(chain, args)
    if args.filter:
        tbl = tbl.filter(lambda row: re.search(args.filter, row.description))

    print('Options for {}: {}'.format(chain['symbol'], chain['underlyingPrice']))
    print(tbl)


if __name__ == '__main__':
    main()


# == Columns ==
# ask
# asksize
# bid
# bidsize
# closeprice
# daystoexpiration
# deliverablenote
# delta
# description
# exchangename
# expirationdate
# expirationtype
# gamma
# highprice
# inthemoney
# isindexoption
# last
# lastsize
# lasttradingday
# lowprice
# mark
# markchange
# markpercentchange
# mini
# multiplier
# netchange
# nonstandard
# openinterest
# openprice
# optiondeliverableslist
# percentchange
# putcall
# quotetimeinlong
# rho
# settlementtype
# strikeprice
# symbol
# theoreticaloptionvalue
# theoreticalvolatility
# theta
# timevalue
# totalvolume
# tradedate
# tradetimeinlong
# vega
# volatility
