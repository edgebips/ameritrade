#!/usr/bin/env python3
"""Quotes for simple daily short strangle options strategy.
"""
__author__ = 'Martin Blais <blais@furius.ca>'

from pprint import pprint
import argparse
import datetime
import logging
import math

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
    margin_price = underlying * (1. + args.near_margin/100)
    tbl = tbl.create('tooclose',
                     lambda row: '*' if row.strikeprice < margin_price else '')

    # Sort to exhibit most interesting by some criteria.
    tbl = tbl.order(
        lambda row: (-row.daystoexpiration, row.bidsize + row.asksize, row.bid),
        asc=False)

    return tbl


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip())
    ameritrade.add_script_args(parser)

    parser.add_argument('-s', '--underlying', '--stock', action='store',
                        default='$SPX.X',
                        help="Name of the underlying to use.")

    parser.add_argument('-v', '--volatility', '--vol', action='store', type=float,
                        help=("Volatility assumption (if not present, use single estimate "
                              "of implied vol)."))

    parser.add_argument('-p', '--pvalue', action='store', type=float,
                        default=2.0,  # 95%
                        help="Minimum p-value to use.")

    parser.add_argument('-m', '--near-margin', action='store', type=float,
                        default=3.0,
                        help=("Fixed (over time) minimum margin (in pct) away from "
                              "the underlying."))

    args = parser.parse_args()
    api = ameritrade.open_with_args(args)

    # Fetch call chain.
    fromDate = datetime.date.today() + datetime.timedelta(days=5)
    toDate = datetime.date.today() + datetime.timedelta(days=45)
    chain = api.GetOptionChain(symbol=args.underlying, strategy='SINGLE', contractType='CALL',
                               strikeCount='20', range='SAK', interval='2',
                               fromDate=fromDate, toDate=toDate)
    if chain['status'] != 'SUCCESS':
        logging.error(chain)
        return

    tbl = get_candidates(chain, args)
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
