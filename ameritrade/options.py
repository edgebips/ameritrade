"""Minor support for option-specific features.
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

from decimal import Decimal
import collections
import datetime
import re
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
    if '_' not in string:
        raise ValueError("Invalid Ameritrade symbol: '{}'".format(string))
    symbol, _, rest = string.partition('_')
    if not re.match(r'\d+$', rest[0:6]):
        raise ValueError("Invalid Ameritrade symbol: '{}'".format(string))
    expiration = datetime.datetime.strptime(rest[0:6], '%m%d%y').date()
    side = rest[6]
    if side not in {'C', 'P'}:
        raise ValueError("Invalid Ameritrade symbol: '{}'".format(string))
    if not re.match(r'[0-9\.]+$', rest[7:]):
        raise ValueError("Invalid Ameritrade symbol: '{}'".format(string))
    strike = Decimal(rest[7:])
    return Option(symbol, expiration, strike, side)


def MakeOptionSymbol(opt: Option) -> str:
    """Build an option symbol given an option."""
    return '{}_{:%m%d%y}{}{}'.format(opt.symbol,
                                     opt.expiration,
                                     opt.side[0].upper(),
                                     opt.strike)


_CALLS = [(chr(ord('A') + i), ('C', i+1)) for i in range(0, 12)]
_PUTS  = [(chr(ord('M') + i), ('P', i+1)) for i in range(0, 12)]
_MONTHSIDEMAP = dict(_CALLS + _PUTS)
_MONTHSIDEMAPINV = {key: value for value, key in _MONTHSIDEMAP.items()}

_DAYMAP = '_123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def ParseOptionCusip(string, yeartxn=None):
    """Given an Ameritrade CUSIP for an option, parse it into its components.

    The argument is a cusip like '0SPY..HH80290000' or '0HDV..BG80088000'.

    Args:
      string: The options CUSIP to parse.
      yeartxn: An optional integer of the year of transaction.
    """
    if len(string) != 16 or string[0] != '0':
        raise ValueError("Invalid CUSIP: '{}'".format(string))
    symbol = string[1:6].strip('.')

    # Compute month and side together
    side, month = _MONTHSIDEMAP[string[6]]

    # Compute day.
    day = _DAYMAP.index(string[7])

    # Compute year.
    if yeartxn is None:
        yeartxn = datetime.date.today().year
    else:
        assert isinstance(yeartxn, int)

    yearnow = yeartxn % 10
    yearbase = yeartxn // 10 * 10
    yearchar = int(string[8])
    if yearchar - yearnow < -5:  # Down to 20X5
        yearbase += 10
    year = yearbase + yearchar

    expiration = datetime.date(year, month, day)
    if string[9] != '0':
        raise ValueError("Invalid CUSIP: '{}'".format(string))

    if not re.match(r'\d+$', string[10:16]):
        raise ValueError("Invalid CUSIP: '{}'".format(string))
    strike = Decimal(string[10:16])/1000
    return Option(symbol, expiration, strike, side)


def MakeOptionCusip(opt: Option) -> str:
    """Build a CUSIP given an option."""
    key = (opt.side[0], opt.expiration.month)
    monthside_letter=  _MONTHSIDEMAPINV[key]
    day_letter = _DAYMAP[opt.expiration.day]
    year_char = opt.expiration.year % 10
    strike = int(opt.strike * 1000)
    return '0{:.<5}{}{}{}0{:06d}'.format(opt.symbol, monthside_letter, day_letter, year_char, strike)
