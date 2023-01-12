#!/usr/bin/env python3
"""Compute betas and beta-weighted deltas for the positions in my account.
"""

from decimal import Decimal
import argparse
import logging
from typing import Tuple

import numpy
import petl
petl.config.look_style = 'minimal'
from matplotlib import pyplot

import ameritrade
from ameritrade import AmeritradeAPI
from ameritrade import JSON
from ameritrade import utils


Array = numpy.ndarray
Q = Decimal('0.001')
PERIOD_TYPES = ['daily1yr', 'weekly3yr', 'monthly3yr', 'experimental']


def GetReturns(api: AmeritradeAPI, symbol: str, periodType: str) -> Tuple[Array, Array]:
    """Get a series of returns for a particular period type."""
    if periodType == 'daily1yr':
        kwargs = dict(period=1,
                      periodType='year',
                      frequency=1,
                      frequencyType='daily')
    elif periodType == 'weekly3yr':
        kwargs = dict(period=3,
                      periodType='year',
                      frequency=1,
                      frequencyType='weekly')
    elif periodType == 'monthly3yr':
        kwargs = dict(period=3,
                      periodType='year',
                      frequency=1,
                      frequencyType='monthly')
    elif periodType == 'experimental':
        # Just searching around for parameters that would reproduce one of the
        # four betas found in the UI.
        kwargs = dict(period=3,
                      periodType='year',
                      frequency=1,
                      frequencyType='weekly')
    elif periodType == 'recent':
        kwargs = dict(period=5,
                      periodType='day',
                      frequency=1,
                      frequencyType='minute')
    else:
        raise ValueError("Invalid periodType: {}".format(periodType))

    hist = api.GetPriceHistory(symbol=symbol, **kwargs)
    if 'candles' not in hist:
        print(hist, symbol, kwargs)
    candles = hist.candles

    time = numpy.fromiter((bar.datetime for bar in candles), dtype=int)
    open = numpy.fromiter((bar.open for bar in candles), dtype=float)
    close = numpy.fromiter((bar.close for bar in candles), dtype=float)
    time = time[1:]
    returns = (close[1:] - close[:-1]) / close[:-1]
    #returns2 = (close - open) / open
    return time, returns


def GetBeta(api: AmeritradeAPI, symbol: str) -> float:
    """Get beta provided by portfolio fundamentals."""
    inst = api.SearchInstruments(symbol=symbol, projection='fundamental')
    value = next(iter(inst.values()))
    return value.fundamental.beta


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip())

    parser.add_argument('--betasym', default='SPY',
                        help='Symbol to use as reference for beta')

    ameritrade.add_args(parser)
    args = parser.parse_args()
    config = ameritrade.config_from_args(args)
    api = ameritrade.open(config)

    accountId = utils.GetMainAccount(api)

    # Get the account's portfolio stock positions.
    all_positions = utils.GetPositions(api, accountId)
    positions = [(pos.instrument.symbol, pos.longQuantity - pos.shortQuantity)
                 for pos in all_positions
                 if pos.instrument.assetType == 'EQUITY']
    positions.append(('$SPX.X', Decimal('1')))
    positions.append(('SPY', Decimal('1')))
    positions = [list(x) for x in sorted(positions)]

    # Get betas from the API.
    for row in positions:
        symbol = row[0]
        api_beta = GetBeta(api, symbol)
        row.append(api_beta.quantize(Q))

    # Get time series for the benchmark.
    for periodType in PERIOD_TYPES:
        # Get benchmark returns for that period type.
        time, bench_returns = GetReturns(api, args.betasym, periodType)

        # Get price time series for all symbols.
        for row in positions:
            symbol = row[0]
            ptime, returns = GetReturns(api, symbol, periodType)
            if time.shape != ptime.shape:
                print((time.shape, ptime.shape, row))
                pyplot.plot(time, bench_returns)
                pyplot.plot(ptime, returns)
                pyplot.show()
                computed_beta = Decimal('-100')
            else:
                assert list(time) == list(ptime)
                cov = numpy.cov(returns, bench_returns)
                computed_beta = cov[0,1]/cov[1,1]
            row.append(Decimal(computed_beta).quantize(Q))

    header = ['symbol', 'quantity', 'api_beta'] + PERIOD_TYPES
    positions.insert(0, header)
    table = (petl.wrap(positions)
             .cutout('quantity'))
    print(table.lookallstr())


if __name__ == '__main__':
    main()
