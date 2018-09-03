"""Unit tests for API."""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

from unittest import mock
import pytest

from ameritrade import schema
from ameritrade import api

@mock.patch('ameritrade.auth.get_headers')
@mock.patch('requests.get')
def test_get(_, reqget):
    method = api.CallableMethod(schema.SCHEMA['GetMovers'], object())

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
@mock.patch('requests.get')
def test_readonly(_, reqget):
    method = api.CallableMethod(schema.SCHEMA['CancelOrder'], object())

    with pytest.raises(NameError):
        method(accountId='accountId', orderId='orderId')
