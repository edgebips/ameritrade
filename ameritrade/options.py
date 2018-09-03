"""Minor support for option-specific features.
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

from decimal import Decimal
import collections
import datetime
import typing


# A representation of an option.
# The side is represented by the letter 'C' or 'P'.
Option = typing.NamedTuple('Option', [
    ('symbol', str),
    ('expiration', datetime.date),
    ('strike', Decimal),
    ('side', str),
    ])


def ParseOptionSymbol(string: str) -> Option:
    """Given an Ameritrade symbol for an option, parse it into its components.

    The argument is a symbol like 'SPY_081718C290' or 'HDV_021618C88'.
    """
    symbol, _, rest = string.partition('_')
    expiration = datetime.datetime.strptime(rest[0:6], '%m%d%y').date()
    side = rest[6]
    strike = Decimal(rest[7:])
    return Option(symbol, expiration, strike, side)


_CALLS = [(chr(ord('A') + i), ('C', i+1)) for i in range(0, 12)]
_PUTS  = [(chr(ord('M') + i), ('P', i+1)) for i in range(0, 12)]
_MONTHSIDEMAP = dict(_CALLS + _PUTS)

_DAYMAP = '_123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def ParseOptionCusip(string):
    """Given an Ameritrade CUSIP for an option, parse it into its components.

    The argument is a cusip like '0SPY..HH80290000' or '0HDV..BG80088000'.
    """
    assert len(string) == 16
    assert string[0] == '0'
    symbol = string[1:6].strip('.')

    # Compute month and side together
    side, month = _MONTHSIDEMAP[string[6]]

    # Compute day.
    day = _DAYMAP.index(string[7])

    # Compute year.
    today = datetime.date.today()
    yearnow = today.year % 10
    yearbase = today.year // 10 * 10
    yearchar = int(string[8])
    if yearchar - yearnow < 0:
        yearbase += 10
    year = yearbase + yearchar

    expiration = datetime.date(year, month, day)
    assert string[9] == '0'

    strike = Decimal(string[10:16])/1000
    return Option(symbol, expiration, strike, side)
