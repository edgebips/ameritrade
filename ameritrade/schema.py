"""Schema description for the Ameritrade API.
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

import re
from typing import NamedTuple, Set


Method = NamedTuple('Method', [
    ('name', str),
    ('description', str),
    ('http_method', str),
    ('path', str),
    ('fields', str),
])

PreparedMethod = NamedTuple('PreparedMethod', [
    ('name', str),
    ('http_method', str),
    ('path', str),
    ('fields', str),
    ('all_fields', Set[str]),
    ('url_fields', Set[str]),
    ('required_fields', Set[str]),
])


Arg = NamedTuple('Arg', [
    ('name', str),
    ('required', bool),
    ('urlarg', bool),
])

def prepare(method):
    from ameritrade import api
    all_fields = set(field.name for field in method.fields)
    required_fields = set(field.name
                          for field in method.fields
                          if field.required)
    url_fields = set(match.group(1)
                     for match in re.finditer(r"{([a-zA-Z]*)}", method.path))
    assert not (url_fields - required_fields), (url_fields, required_fields)
    return PreparedMethod(method.name,
                          method.http_method,
                          method.path,
                          method.fields,
                          all_fields,
                          url_fields,
                          required_fields)

def M(name, description, http_method, path, *fields):
    "Create method."
    return Method(name, description, http_method, path, fields)

def R(name): return Arg(name, True, False)
def O(name): return Arg(name, False, False)


_METHODS = [
    # Accounts and Trading

    # Accounts and Trading > Orders.
    M('CancelOrder',
      'Cancel a specific order for a specific account.',
      'DELETE', '/accounts/{accountId}/orders/{orderId}',
      R('accountId'),
      R('orderId')),
    M('GetOrder',
      'Get a specific order for a specific account.',
      'GET', '/accounts/{accountId}/orders/{orderId}',
      R('accountId'),
      R('orderId')),
    M('GetOrdersByPath',
      'Orders for a specific account.',
      'GET', '/accounts/{accountId}/orders',
      R('accountId'),
      R('orderId'),
      O('maxResults'),
      O('fromEnteredTime'),
      O('toEnteredTime'),
      O('status')),
    M('GetOrdersByQuery',
      ("All orders for a specific account or, if account ID "
       "isn't specified, orders will be returned for all linked "
       "accounts"),
      'GET', '/orders',
      O('accountId'),
      O('maxResults'),
      O('fromEnteredTime'),
      O('toEnteredTime'),
      O('status')),
    # M('PlaceOrder',
    # M('ReplaceOrder',
    ## FIXME: TODO

    # Accounts and Trading > Saved Orders.
    ## FIXME: TODO

    # Accounts and Trading > Accounts.
    M('GetAccount',
      'Account balances, positions, and orders for a specific account.',
      'GET', '/accounts/{accountId}',
      R('accountId'),
      O('fields')),
    M('GetAccounts',
      'Account balances, positions, and orders for all linked accounts.',
      'GET', '/accounts',
      O('fields')),


    # Authentication
    ## FIXME: TODO

    # Instruments
    M('SearchInstruments',
      'Search or retrieve instrument data, including fundamental data.',
      'GET', '/instruments',
      R('symbol'),
      R('projection')),
    M('GetInstrument',
      'Get an instrument by CUSIP',
      'GET', '/instruments/{cusip}',
      R('cusip')),

    # Market Hours
    M('GetHoursSingleMarket',
      'Retrieve market hours for specified single market',
      'GET', '/marketdata/{market}/hours',
      R('market'),
      O('date')),

    M('GetHoursMultipleMarkets',
      'Retrieve market hours for specified single market',
      'GET', '/marketdata/hours',
      O('markets'),
      O('date')),

    # Movers
    M('GetMovers',
      'Top 10 (up or down) movers by value or percent for a particular market',
      'GET', '/marketdata/{index}/movers',
      R('index'),
      O('direction'),
      O('change')),

    # Option Chains
    M('GetOptionChain',
      'Get option chain for an optionable Symbol',
      'GET', '/marketdata/chains',
      O('symbol'),
      O('contractType'),
      O('strikeCount'),
      O('includeQuotes'),
      O('strategy'),
      O('interval'),
      O('strike'),
      O('range'),
      O('fromDate'),
      O('toDate'),
      O('volatility'),
      O('underlyingPrice'),
      O('interestRate'),
      O('daysToExpiration'),
      O('expMonth'),
      O('optionType')),

    # Price History
    ## FIXME: TODO

    # Quotes
    ## FIXME: TODO

    # Transaction History
    ## FIXME: TODO

    # User Info and Preferences
    ## FIXME: TODO

    # Watchlist
    ## FIXME: TODO
]

SCHEMA = {method.name: prepare(method) for method in _METHODS}
