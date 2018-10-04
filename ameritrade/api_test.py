
"""Unit tests for API."""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

from unittest import mock
import pytest

from ameritrade import schema
from ameritrade import api


def open_for_test():
    """Create an API endpoint. This is the main entry point."""
    return api.open(api.Config(client_id='TEST@AMER.OAUTHAP'))


def test_make_config():
    c = api.Config()
    assert isinstance(c, api.Config)
    c = api.Config(client_id='TEST@AMER.OAUTHAP')
    assert isinstance(c, api.Config)
    with pytest.raises(ValueError):
        c = api.Config(unknown='TEST@AMER.OAUTHAP')


@mock.patch('ameritrade.auth.get_headers')
@mock.patch('ameritrade.auth.read_or_create_secrets')
@mock.patch('requests.get')
def test_get(_, __, reqget):
    a = open_for_test()
    method = api.CallableMethod(schema.SCHEMA['GetMovers'], a, False)

    # Missing a required field.
    with pytest.raises(TypeError):
        method()

    # Just the required fields.
    result = method(index='$SPY.X')
    reqget.assert_called_once()
    reqget.reset_mock()

    # Required and optional fields.
    result = method(index='$SPY.X', direction='up')
    reqget.assert_called_once()

    # Required and invalid fields.
    with pytest.raises(TypeError):
        result = method(index='$SPY.X', impostor='up')

    # Just invalid fields.
    with pytest.raises(TypeError):
        result = method(impostor='up')


@mock.patch('ameritrade.auth.get_headers')
@mock.patch('ameritrade.auth.read_or_create_secrets')
@mock.patch('requests.get')
def test_readonly(_, __, ___):
    iapi = open_for_test()
    with pytest.raises(NameError):
        iapi.ReplaceSavedOrder(accountId='accountId',
                               savedOrderId='savedOrderId',
                               payload={})
