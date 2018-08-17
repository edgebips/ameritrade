"""Schema description for the Ameritrade API.
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

from typing import NamedTuple


Method = NamedTuple('Method', [
    ('name', str),
    ('description', str),
    ('http_method', str),
    ('path', str),
    ('fields', str),
])

Arg = NamedTuple('Arg', [
    ('name', str),
    ('required', str),
])


_METHODS = [
    # Accounts and Trading

    # Accounts and Trading > Orders.
    Method('CancelOrder',
           'Cancel a specific order for a specific account.',
           'DELETE', '/accounts/{accountId}/orders/{orderId}', [
               Arg('accountId', True),
               Arg('orderId', True),
           ]),
    Method('GetOrder',
           'Get a specific order for a specific account.',
           'GET', '/accounts/{accountId}/orders/{orderId}', [
               Arg('accountId', True),
               Arg('orderId', True),
           ]),
    Method('GetOrdersByPath',
           'Orders for a specific account.',
           'GET', '/accounts/{accountId}/orders', [
               Arg('accountId', True),
               Arg('orderId', True),
               Arg('maxResults', False),
               Arg('fromEnteredTime', False),
               Arg('toEnteredTime', False),
               Arg('status', False),
           ]),
    Method('GetOrdersByQuery',
           ("All orders for a specific account or, if account ID "
            "isn't specified, orders will be returned for all linked "
            "accounts"),
           'GET', '/orders', [
               Arg('accountId', False),
               Arg('maxResults', False),
               Arg('fromEnteredTime', False),
               Arg('toEnteredTime', False),
               Arg('status', False),
           ]),
    # Method('PlaceOrder',
    # Method('ReplaceOrder',
    ## FIXME: TODO

    # Accounts and Trading > Saved Orders.
    ## FIXME: TODO

    # Accounts and Trading > Accounts.
    Method('GetAccount',
           'Account balances, positions, and orders for a specific account.',
           'GET', '/accounts/{accountId}', [
               Arg('fields', False),
           ]),
    Method('GetAccounts',
           'Account balances, positions, and orders for all linked accounts.',
           'GET', '/accounts', [
               Arg('fields', False),
           ]),


    # Authentication
    ## FIXME: TODO

    # Instruments
    Method('SearchInstruments',
           'Search or retrieve instrument data, including fundamental data.',
           'GET', '/instruments', [
               Arg('symbol', True),
               Arg('projection', True),
           ]),
    Method('GetInstrument',
           'Get an instrument by CUSIP',
           'GET', '/instruments/{cusip}', [
               Arg('cusip', True),
           ]),

    # Market Hours
    Method('GetHoursSingleMarket',
           'Retrieve market hours for specified single market',
           'GET', '/marketdata/{market}/hours', [
               Arg('market', True),
               Arg('date', False),
           ]),

    Method('GetHoursMultipleMarkets',
           'Retrieve market hours for specified single market',
           'GET', '/marketdata/hours', [
               Arg('markets', False),
               Arg('date', False),
           ]),

    # Movers
    Method('GetMovers',
           'Top 10 (up or down) movers by value or percent for a particular market',
           'GET', '/marketdata/{index}/movers', [
               Arg('index', True),
               Arg('direction', False),
               Arg('change', False),
           ]),

    # Option Chains
    Method('GetOptionChain',
           'Get option chain for an optionable Symbol',
           'GET', '/marketdata/chains', [
               Arg('symbol', False),
               Arg('contractType', False),
               Arg('strikeCount', False),
               Arg('includeQuotes', False),
               Arg('strategy', False),
               Arg('interval', False),
               Arg('strike', False),
               Arg('range', False),
               Arg('fromDate', False),
               Arg('toDate', False),
               Arg('volatility', False),
               Arg('underlyingPrice', False),
               Arg('interestRate', False),
               Arg('daysToExpiration', False),
               Arg('expMonth', False),
               Arg('optionType', False),
           ]),

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

SCHEMA = {method.name: method for method in _METHODS}
