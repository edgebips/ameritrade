"""Main API code for the Ameritrade API wrappers.
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

from os import path
from typing import Tuple, Dict, NamedTuple
import logging
import os
import pprint
import re
import requests

from ameritrade import auth
from ameritrade import schema


def open(client_id: str,
         redirect_uri: str = 'https://localhost:8444',
         key_file: str = None,
         certificate_file: str = None,
         timeout: int = 300,
         secrets_file: str = None,
         readonly: bool = True):
    """Create an API endpoint. This is the main entry point."""
    config = Config(client_id,
                    redirect_uri,
                    key_file,
                    certificate_file,
                    timeout,
                    secrets_file,
                    readonly)
    return AmeritradeAPI(config)


def open_with_dir(client_id: str,
                  config_dir: str = os.getcwd(),
                  redirect_uri: str = 'https://localhost:8444',
                  timeout: int = 300,
                  readonly: bool = True):
    """Create an API endpoint with a config dfir. This is the main entry point."""
    config = Config(client_id,
                    redirect_uri,
                    path.join(config_dir, 'key.pem'),
                    path.join(config_dir, 'certificate.pem'),
                    timeout,
                    path.join(config_dir, 'secrets.json'),
                    readonly)
    return AmeritradeAPI(config)


# Configuration object. Create one of those and call AmeritradeAPI().
Config = NamedTuple('Config', [
    # The OAuth client id string, such as '<USERNAME>@AMER.OAUTHAP'.
    ('client_id', str),

    # A redirect URI, such as 'https://127.0.0.1:8444'. Note that this must
    # match that with which you created your app in the Ameritrade API
    # interface.
    ('redirect_uri', str),

    # The location of the key PEM file.
    ('key_file', str),

    # The location of the certificate PEM file.
    ('certificate_file', str),

    # Timeout (in seconds) to wait for OAuth token response.
    ('timeout', int),

    # The location of the JSON file to store the OAuth token in between
    # invocations.
    ('secrets_file', str),

    # Safe-mode that disallows any methods that modify state. Only allows
    # getters to read data from the account.
    ('readonly', bool),
    ])

# A dict of secrets. Contains the access token and Bearer type.
Secrets = Dict[str, str]


class AmeritradeAPI:
    """An Ameritrade endpoint, with credentials."""

    def __init__(self, config: Config, expire=False):
        """
        """
        self.config = config
        self.secrets = auth.read_or_create_secrets(config.secrets_file, config)

    def __getattribute__(self, key):
        method = schema.SCHEMA[key]
        # Disallow read-only methods.
        config = object.__getattribute__(self, 'config')
        if config.readonly and method.http_method != 'GET':
            raise NameError("Method {} is not allowed in safe read-only mode.".format(
                method.name))
        else:
            return CallableMethod(method, object.__getattribute__(self, 'secrets'))


class CallableMethod:
    """Callable method."""

    def __init__(self, method: schema.PreparedMethod, secrets: Secrets):
        self.method = method
        self.secrets = secrets

    def __call__(self, **kw):
        method = self.method

        # Check that all the required fields are being provided.
        provided_fields = set(kw.keys())
        uncovered_fields = method.required_fields - provided_fields
        if uncovered_fields:
            raise TypeError("Missing required fields: {}".format(uncovered_fields))

        # Check that there aren't any extra fields.
        invalid_fields = provided_fields - method.all_fields
        if invalid_fields:
            raise TypeError("Invalid fields: {}".format(invalid_fields))

        # Build the headers and URL path to call.
        headers = auth.get_headers(self.secrets)
        path_kw = {field: kw.pop(field) for field in method.url_fields}
        path = method.path.format(**path_kw)
        url = 'https://api.tdameritrade.com/v1{}'.format(path)
        logging.info("Opening URL: %s", url)

        # Call the resources with parameters.
        params = {key: str(value) for key, value in kw.items()}
        if self.method.http_method == 'GET':
            resp = requests.get(url, params=params, headers=headers)
        else:
            assert False, "Unsupported HTTP method for {}: {}".format(method.name,
                                                                      method.http_method)
        return resp.json()
