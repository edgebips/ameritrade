#!/usr/bin/env python3
"""Compute various vol estimates.
"""
__author__ = 'Martin Blais <blais@furius.ca>'

import argparse
import collections
import logging
import math
from decimal import Decimal

import numpy
from scipy.stats import norm
import petl
petl.config.look_style = 'minimal'
petl.compat.numeric_types = petl.compat.numeric_types + (Decimal,)
petl.config.failonerror = True

import ameritrade
import petl


Candle = collections.namedtuple('Candle', 'datetime open low high close volume')
Q = Decimal('0.01')


def price_history_to_arrays(history):
    """Convert response from GetPriceHistory to NumPy arrays."""
    candles = history['candles']
    num = len(candles)
    convert = lambda fname, dtype: numpy.fromiter((candle[fname] for candle in candles),
                                                  dtype=dtype, count=num)
    return Candle(convert('datetime', int)/1000,
                  convert('open', float),
                  convert('low', float),
                  convert('high', float),
                  convert('close', float),
                  convert('volume', int))


def historical_volatility(datetime, close):
    """Compute historical volatility."""
    num_days = (datetime[-1] - datetime[0]) / (24*60*60)
    return numpy.std(close)/math.sqrt(num_days/365.)


def historical_volatility_dist(datetime, close, days):
    """Compute the distribution of volatility estimates."""
    assert datetime is not None
    assert datetime.shape == close.shape
    num = datetime.shape[0]
    ann = math.sqrt(365./days)
    vols = []
    voldates = []
    for firstday in range(0, num-days):
        lastday = firstday + days
        vol = numpy.std(close[firstday:lastday])*ann
        vols.append(vol)
        voldates.append(datetime[lastday])
    return numpy.array(voldates), numpy.array(vols)


def main():
    """Compute various vol estimates."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)-8s: %(message)s')
    parser = argparse.ArgumentParser(description=__doc__.strip())
    ameritrade.add_args(parser)
    parser.add_argument('-s', '--symbol', action='store', default='SPY',
                        help="Symbol to compute on")
    args = parser.parse_args()
    config = ameritrade.config_from_args(args)
    api = ameritrade.open(config)

    # Fetch call chain for underlying.
    hist = api.GetPriceHistory(symbol=args.symbol,
                               frequency=1, frequencyType='daily',
                               period=2, periodType='year')
    candle = price_history_to_arrays(hist)

    # Compute historical volatility estimates and centile of vol distribution of
    # underlying over various time periods.
    header = ['windays', 'annual_vol', 'iv_percentile', 'mean', 'std']
    rows = [header]
    for days in [7, 15, 20, 30, 60, 90, 120, 180, 365, None]:
        centiles = True
        if days is None:
            centiles = False
            days = candle.datetime.shape[0]
        vol = historical_volatility(candle.datetime[-days:], candle.close[-days:])

        if centiles:
            _, vols = historical_volatility_dist(candle.datetime, candle.close, days)
            assert len(vols) > 0
            meanvol = numpy.mean(vols)
            stdvol = numpy.std(vols)
            centile = norm.cdf(vol, meanvol, stdvol)
            rows.append([days, vol, centile, meanvol, stdvol])
            # print("Vol over {:3} days: {:8.2f}"
            #       "  (IVpct: {:5.1%}; mean/std: {:.1f}~{:.1f})".format(
            #           days, vol, centile, meanvol, stdvol))
        else:
            #print("Vol over {:3} days: {:8.2f}".format(days, vol))
            rows.append([days, vol, '', '', ''])
    convert = lambda v: Decimal(v).quantize(Q) if v else ''
    table = (petl.wrap(rows)
             .convert('annual_vol', convert)
             .convert('iv_percentile', convert)
             .convert('mean', convert)
             .convert('std', convert)
             .cut('windays', 'mean', 'std', 'annual_vol', 'iv_percentile'))
    print(table.lookallstr())


if __name__ == '__main__':
    main()
