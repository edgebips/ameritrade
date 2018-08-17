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
    """Cache attributes for method calls."""
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
    return Method(name, description, http_method, path, fields)
def R(name): return Arg(name, True, False)
def O(name): return Arg(name, False, False)


_METHODS = [
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
    M('PlaceOrder',
      'Place an order for a specific account.',
      'POST', '/accounts/{accountId}/orders',
      R('accountId')),  # INCOMPLETE
    M('ReplaceOrder',
      ("Replace an existing order for an account. The existing order will be replaced by "
       "the new order. Once replaced, the old order will be canceled and a new order will "
       "be created."),
      'PUT', '/accounts/{accountId}/orders/{orderId}',
      R('accountId'),
      R('orderId')),  # INCOMPLETE

    # Accounts and Trading > Saved Orders.
    M('CreateSavedOrder',
      'Save an order for a specific account.',
      'POST', '/accounts/{accountId}/savedorders',
      R('accountId')),  # INCOMPLETE
    M('DeleteSavedOrder',
      'Delete a specific saved order for a specific account.',
      'DELETE', '/accounts/{accountId}/savedorders/{savedOrderId}',
      R('accountId'),
      R('savedOrderId')),  # INCOMPLETE
    M('GetSavedOrder',
      'Specific saved order by its ID, for a specific account.',
      'GET', '/accounts/{accountId}/savedorders/{savedOrderId}',
      R('accountId'),
      R('savedOrderId')),  # INCOMPLETE
    M('GetSavedOrdersByPath',
      'Saved orders for a specific account.',
      'GET', '/accounts/{accountId}/savedorders',
      R('accountId')),  # INCOMPLETE
    M('Replace Saved Order',
      ("Replace an existing saved order for an account. The existing saved order will "
       "be replaced by the new order."),
      'PUT', '/accounts/{accountId}/savedorders/{savedOrderId}',
      R('accountId'),
      R('savedOrderId')),  # INCOMPLETE

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
    M('PostAccessToken',
      'The token endpoint returns an access token along with an optional refresh token.',
      'POST', '/oauth2/token'),  # INCOMPLETE

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
    M('GetPriceHistory',
      'Get price history for a symbol',
      'GET', '/marketdata/{symbol}/pricehistory',
      R('symbol'),
      O('periodType'),
      O('period'),
      O('frequencyType'),
      O('frequency'),
      O('endDate'),
      O('startDate'),
      O('needExtendedHoursData')),

    # Quotes
    M('GetQuotes',
      'Get quote for one or more symbols.',
      'GET', '/marketdata/quotes',
      R('symbol')),
    M('GetQuote',
      'Get quote for a symbol',
      'GET', '/marketdata/{symbol}/quotes',
      R('symbol')),

    # Transaction History
    M('GetTransaction',
      'Transaction for a specific account.',
      'GET', '/accounts/{accountId}/transactions/{transactionId}',
      R('accountId'),
      R('transactionId')),
    M('GetTransactions',
      'Transactions for a specific account.',
      'GET', '/accounts/{accountId}/transactions',
      R('accountId'),
      O('type'),
      O('symbol'),
      O('startDate'),
      O('endDate')),

    # User Info and Preferences
    M('GetPreferences',
      'Preferences for a specific account.',
      'GET', '/accounts/{accountId}/preferences',
      R('accountId')),
    M('GetStreamerSubscriptionKeys',
      'SubscriptionKey for provided accounts or default accounts.',
      'GET', '/userprincipals/streamersubscriptionkeys',
      O('accountIds')),
    M('GetUserPrincipals',
      'User Principal details.',
      'GET', '/userprincipals',
      O('fields')),
    M('UpdatePreferences',
      ("Update preferences for a specific account. Please note that the "
       "directOptionsRouting and directEquityRouting values cannot be modified via "
       "this operation."),
      'PUT', '/accounts/{accountId}/preferences',
      R('accountId')),  # INCOMPLETE

    # Watchlist
    M('CreateWatchlist',
      ("Create watchlist for specific account.This method does not verify that the symbol "
       "or asset type are valid."),
      'POST', '/accounts/{accountId}/watchlists',
      R('accountId')),  # INCOMPLETE
    M('Delete Watchlist',
      "Delete watchlist for a specific account.",
      'DELETE', '/accounts/{accountId}/watchlists/{watchlistId}',
      R('accountId'),
      R('watchlistId')),  # INCOMPLETE
    M('Get Watchlist',
      "Specific watchlist for a specific account.",
      'GET', '/accounts/{accountId}/watchlists/{watchlistId}',
      R('accountId'),
      R('watchlistId')),  # INCOMPLETE
    M('Get Watchlists for Multiple Accounts',
      "All watchlists for all of the user's linked accounts.",
      'GET', '/accounts/watchlists'),  # INCOMPLETE
    M('Get Watchlists for Single Account',
      "All watchlists of an account.",
      'GET', '/accounts/{accountId}/watchlists',
      R('accountId')),  # INCOMPLETE
    M('Replace Watchlist',
      ("Replace watchlist for a specific account. This method does not verify that the "
       "symbol or asset type are valid."),
      'PUT', '/accounts/{accountId}/watchlists/{watchlistId}',
      R('accountId'),
      R('watchlistId')),  # INCOMPLETE
    M('Update Watchlist',
      ("Partially update watchlist for a specific account: change watchlist name, add to "
       "the beginning/end of a watchlist, update or delete items in a watchlist. This "
       "method does not verify that the symbol or asset type are valid."),
      'PATCH', '/accounts/{accountId}/watchlists/{watchlistId}',
      R('accountId'),
      R('watchlistId')),  # INCOMPLETE

]

SCHEMA = {method.name: prepare(method) for method in _METHODS}
