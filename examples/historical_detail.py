#!/usr/bin/env python3
"""Exploring how much detail can be fetched over historical periods.
"""
__author__ = 'Martin Blais <blais@furius.ca>'

import argparse
import collections
import datetime
import logging
import math
from decimal import Decimal

import numpy
from scipy.stats import norm
import petl
petl.config.look_style = 'minimal'
petl.compat.numeric_types = petl.compat.numeric_types + (Decimal,)
petl.config.failonerror = True
from matplotlib import pyplot
import tzlocal

import ameritrade
import petl


class Candle(collections.namedtuple('Candle', 'datetime open low high close volume')):

    def __len__(self):
        return len(self.datetime)

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


# def historical_volatility(datetime, close):
#     """Compute historical volatility."""
#     num_days = (datetime[-1] - datetime[0]) / (24*60*60)
#     return numpy.std(close)/math.sqrt(num_days/365.)


# def historical_volatility_dist(datetime, close, days):
#     """Compute the distribution of volatility estimates."""
#     assert datetime is not None
#     assert datetime.shape == close.shape
#     num = datetime.shape[0]
#     ann = math.sqrt(365./days)
#     vols = []
#     voldates = []
#     for firstday in range(0, num-days):
#         lastday = firstday + days
#         vol = numpy.std(close[firstday:lastday])*ann
#         vols.append(vol)
#         voldates.append(datetime[lastday])
#     return numpy.array(voldates), numpy.array(vols)


"""
day (1,2,3,4,5,10)
  minute (1,5,10,15,30)
month (1,2,3,6)
  daily (1)
  weekly (1)
year (1,2,3,5,10,15,20)
  daily (1)
  weekly (1)
  monthly (1)
ytd (1)
  daily (1)
  weekly (1)
"""


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
    tz = tzlocal.get_localzone()
    get_ts = lambda *args: int(datetime.datetime(*args, tzinfo=tz).timestamp()) * 1000
    # start = get_ts(2021, 8, 20, 9, 30, 0)
    # end = start + 2 * 60 * 60 * 1000
    start = None
    end = get_ts(2021, 4, 20, 15, 00, 0)

    # hist = api.GetPriceHistory(symbol=args.symbol,
    #                            period=1, periodType='day',
    #                            frequency=1, frequencyType='minute',
    #                            startDate=start, endDate=end)
    hist = api.GetPriceHistory(symbol=args.symbol,
                               period=1, periodType='day',
                               frequency=5, frequencyType='minute',
                               startDate=start, endDate=end)
    if 'error' in hist:
        logging.error(f"Error: {hist}")
        return
    if hist.get('empty', False):
        logging.error(f"Error: {hist}")
        return

    candle = price_history_to_arrays(hist)
    print(len(candle))
    # pyplot.plot(candle.datetime, candle.close)
    # pyplot.show()


if __name__ == '__main__':
    main()
