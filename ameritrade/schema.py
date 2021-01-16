"""Schema description for the Ameritrade API.
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

from os import path
from pprint import pprint
from typing import NamedTuple, Set
import json
import re


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
    ('validator', object),
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

def _get_validator(name, validator):
    return (validator
            if validator is not None
            else _VALIDATORS_BY_NAME.get(name, None))

def M(name, description, http_method, path, *fields):
    return Method(name, description, http_method, path, fields)
def R(name, validator=None):
    return Arg(name, True, False, _get_validator(name, validator))
def O(name, validator=None):
    return Arg(name, False, False, _get_validator(name, validator))


def TypeValidator(typeobj):
    """Validate just the data type, not the values."""
    def validator(value):
        if not isinstance(value, typeobj):
            raise ValueError("Invalid type: {} should be of type {}".format(
                repr(value), typeobj))
    return validator







# FIXME: TODO - move all this to another module.

def JsonSchemaValidator(message_name):
    """Read a JSON schema as provide by the API docs and validate."""
    filename = path.join(_SCHEMA_DIR, '{}.json'.format(message_name))
    schemas = load_json_with_comments(filename)
    top_schema = {"type": "object",
                  "properties": schemas[message_name]}
    def validator(value):
        return validate_json_object(top_schema, value, schemas)
    return validator


def load_json_with_comments(filename):
    with open(filename) as schfile:
        contents = re.sub(r'//.*', '', schfile.read())
        #contents = re.sub('^[ \t]*\r?\n', '', contents, re.M)
        return json.loads(contents.strip())


def dispatch_validate(value_schema, value, schemas):
    value_type = value_schema['type']
    validfunc = _TYPE_VALIDATORS[value_type]
    return validfunc(value_schema, value, schemas)


def validate_json_object(schema, value, schemas):
    """Validate a JSON object."""
    assert set(schema.keys()) in ({'type', 'properties'},
                                  {'type', 'properties', 'discriminator'})
    properties = schema['properties']
    discriminator = schema.get('discriminator', None)
    if discriminator:
        disc_value = value[discriminator]
        disc_schema = properties[discriminator]
        assert disc_schema.keys() == {'type', 'enum'}
        validate_json_string(disc_schema, disc_value, schemas)
        schema_key = '{}_{}'.format(discriminator, disc_value)
        properties = schemas[schema_key]

    assert isinstance(properties, dict)
    for key, value in value.items():
        value_schema = properties[key]
        dispatch_validate(value_schema, value, schemas)


def validate_json_array(schema, value, schemas):
    """Validate a JSON array."""
    #print('validate_json_array', schema, value)
    assert set(schema.keys()) == {'type', 'items'}
    if not isinstance(value, list):
        raise TypeError("Invalid type for array: {}".foramt(value))
    item_schema = schema['items']
    for item in value:
        dispatch_validate(item_schema, item, schemas)


def validate_json_boolean(schema, value, schemas):
    """Validate a JSON boolean."""
    #print('validate_json_boolean')
    raise NotImplementedError


def validate_json_integer(schema, value, schemas):
    """Validate a JSON integer."""
    #print('validate_json_integer')
    raise NotImplementedError


def validate_json_number(schema, value, schemas):
    """Validate a JSON number."""
    #print('validate_json_number', schema, value)
    assert set(schema.keys()) == {'type', 'format'}
    if schema['format'] == 'double':
        if isinstance(value, (float, int)):
            pass
        elif isinstance(value, str):
            float(value)
        else:
            raise TypeError("Invalid format for {}: {}".format(value, schema['format']))
    else:
        raise ValueError("Invalid number format: {}".format(schema['format']))


def validate_json_string(schema, value, schemas):
    """Validate a JSON string."""
    #print('validate_json_string', schema, value)
    assert set(schema.keys()) in ({'type'}, {'type', 'enum'})
    enum = schema.get('enum', None)
    if enum:
        assert isinstance(enum, list)
        if value not in enum:
            raise ValueError("Invalid enumeration: {}".format(value))


_TYPE_VALIDATORS = {
    "array"   : validate_json_array,
    "boolean" : validate_json_boolean,
    "integer" : validate_json_integer,
    "number"  : validate_json_number,
    "object"  : validate_json_object,
    "string"  : validate_json_string,
}












_VALIDATORS_BY_NAME = {
    'accountId': TypeValidator(str)
}

_SCHEMA_DIR = path.join(path.dirname(__file__), 'schemas_old')


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
      R('accountId'),
      R('payload', JsonSchemaValidator('PlaceOrder'))),
    M('ReplaceOrder',
      ("Replace an existing order for an account. The existing order will be replaced by "
       "the new order. Once replaced, the old order will be canceled and a new order will "
       "be created."),
      'PUT', '/accounts/{accountId}/orders/{orderId}',
      R('accountId'),
      R('orderId'),
      R('payload', JsonSchemaValidator('ReplaceOrder'))),
    # Accounts and Trading > Saved Orders.
    M('CreateSavedOrder',
      'Save an order for a specific account.',
      'POST', '/accounts/{accountId}/savedorders',
      R('accountId'),
      R('payload', JsonSchemaValidator('CreateSavedOrder'))),
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
    M('ReplaceSavedOrder',
      ("Replace an existing saved order for an account. The existing saved order will "
       "be replaced by the new order."),
      'PUT', '/accounts/{accountId}/savedorders/{savedOrderId}',
      R('accountId'),
      R('savedOrderId'),
      R('payload', JsonSchemaValidator('ReplaceSavedOrder'))),

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
    M('DeleteWatchlist',
      "Delete watchlist for a specific account.",
      'DELETE', '/accounts/{accountId}/watchlists/{watchlistId}',
      R('accountId'),
      R('watchlistId')),  # INCOMPLETE
    M('GetWatchlist',
      "Specific watchlist for a specific account.",
      'GET', '/accounts/{accountId}/watchlists/{watchlistId}',
      R('accountId'),
      R('watchlistId')),  # INCOMPLETE
    M('GetWatchlistsForMultipleAccounts',
      "All watchlists for all of the user's linked accounts.",
      'GET', '/accounts/watchlists'),  # INCOMPLETE
    M('GetWatchlistsForSingleAccount',
      "All watchlists of an account.",
      'GET', '/accounts/{accountId}/watchlists',
      R('accountId')),  # INCOMPLETE
    M('ReplaceWatchlist',
      ("Replace watchlist for a specific account. This method does not verify that the "
       "symbol or asset type are valid."),
      'PUT', '/accounts/{accountId}/watchlists/{watchlistId}',
      R('accountId'),
      R('watchlistId')),  # INCOMPLETE
    M('UpdateWatchlist',
      ("Partially update watchlist for a specific account: change watchlist name, add to "
       "the beginning/end of a watchlist, update or delete items in a watchlist. This "
       "method does not verify that the symbol or asset type are valid."),
      'PATCH', '/accounts/{accountId}/watchlists/{watchlistId}',
      R('accountId'),
      R('watchlistId')),  # INCOMPLETE
]

SCHEMA = {method.name: prepare(method) for method in _METHODS}
