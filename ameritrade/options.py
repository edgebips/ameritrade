"""Support for option-specific features.

The API involves at least three symbologies:
- One from the internal TOS platform that looks like this: "SPXW_012021P3520"
- Another one, visiblke in TOS, that looks like this: ".SPXW210120P3520"
- CUSIP (not sure using standard, see https://en.wikipedia.org/wiki/CUSIP)
There's also (but unspported):
- OCC terminology (https://help.yahoo.com/kb/SLN13884.html)
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
    The symbol name Used by TD Ameritrade API, 16 characters:

      Two parts: <name>_<expiration><side><strike>

    where

      <name> is the contract name or underlying.
      <expiration> is the expiration date in MMDDYY format.
      <side> is 'C' or 'P' for calls and puts, respectively.
      <strike> is the strike price, in whatever the smallest units
        of the contract are.

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


def ParseOptionCusip(cusip, yeartxn=None):
    """Given an Ameritrade CUSIP for an option, parse it into its components.

    The argument is a cusip like '0SPY..HH80290000' or '0HDV..BG80088000'.
    The CUSIP Format Used by TD Ameritrade API, 16 characters:

      0: always '0'
      1-5: symbol padded with '.'
      6: side and month; Calls: A-N is Jan-Dec, Puts: M-X is Jan Dec
      7: day mapped from '_123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
      8: year
      9-15: price * 1000, left padded with zeros.
      16: (optional) 'A' for AM options.

    Args:
      cusip: The options CUSIP to parse.
      yeartxn: An optional integer of the year of transaction.
    """
    if len(cusip) != 16 or cusip[0] != '0':
        raise ValueError("Invalid CUSIP: '{}'".format(cusip))
    symbol = cusip[1:6].strip('.')

    # Compute month and side together
    side, month = _MONTHSIDEMAP[cusip[6]]

    # Compute day.
    day = _DAYMAP.index(cusip[7])

    # Compute year.
    if yeartxn is None:
        yeartxn = datetime.date.today().year
    else:
        assert isinstance(yeartxn, int)

    yearnow = yeartxn % 10
    yearbase = yeartxn // 10 * 10
    yearchar = int(cusip[8])
    if yearchar - yearnow < -5:  # Down to 20X5
        yearbase += 10
    year = yearbase + yearchar
    expiration = datetime.date(year, month, day)

    # Parse AM/PM flag.
    if not ('0' <= cusip[15] <= '9'):
        tenk_multiplier = ord(cusip[15]) - ord('A') + 1
        tail = cusip[9:15] + '0'
    else:
        tenk_multiplier = 0
        tail = cusip[9:16]

    # Parse strike price.
    if not re.match(r'\d+$', tail):
        raise ValueError("Invalid CUSIP: '{}'".format(cusip))
    strike = tenk_multiplier * Decimal(10000) + Decimal(tail)/1000

    return Option(symbol, expiration, strike, side)


def MakeOptionCusip(opt: Option) -> str:
    """Build a CUSIP given an option."""
    key = (opt.side[0], opt.expiration.month)
    monthside_letter=  _MONTHSIDEMAPINV[key]
    day_letter = _DAYMAP[opt.expiration.day]
    year_char = opt.expiration.year % 10
    assert opt.strike < 100000
    if opt.strike >= 10000:
        tenk_num = int(opt.strike / 10000)
        letter = chr(tenk_num - 1 + ord('A'))
        strike = int(opt.strike % 10000 * 100)
        strike_str = '{:06d}{}'.format(strike, letter)
    else:
        strike = int(opt.strike * 1000)
        strike_str = '{:07d}'.format(strike)
    return '0{:.<5}{}{}{}{}'.format(
        opt.symbol, monthside_letter, day_letter, year_char, strike_str)
