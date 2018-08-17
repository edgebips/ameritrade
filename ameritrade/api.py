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
         secrets_file: str = None):
    config = Config(client_id,
                    redirect_uri,
                    key_file,
                    certificate_file,
                    timeout,
                    secrets_file)
    return AmeritradeAPI(config)


def open_with_dir(client_id: str,
                  config_dir: str = os.getcwd(),
                  redirect_uri: str = 'https://localhost:8444',
                  timeout: int = 300):
    config = Config(client_id,
                    redirect_uri,
                    path.join(config_dir, 'key.pem'),
                    path.join(config_dir, 'certificate.pem'),
                    timeout,
                    path.join(config_dir, 'secrets.json'))
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
        return CallableMethod(key, object.__getattribute__(self, 'secrets'))


class CallableMethod:
    """Callable method."""

    def __init__(self, function: str, secrets: Secrets):
        self.function = function
        self.secrets = secrets
        self.method = schema.SCHEMA[function]

    def __call__(self, **kw):
        provided_fields = set(kw.keys())
        required_fields = [field.name
                           for field in self.method.fields
                           if field.required]
        uncovered_fields = set(required_fields) - provided_fields
        if uncovered_fields:
            raise ValueError("Missing required fields: {}".format(uncovered_fields))

        all_fields = [field.name for field in self.method.fields]
        invalid_fields = provided_fields - set(all_fields)
        if invalid_fields:
            raise ValueError("Invalid fields: {}".format(invalid_fields))

        path_fields = [match.group(1)
                       for match in re.finditer(r"{(.*)}", self.method.path)]
        path_kw = {field: kw.pop(field) for field in path_fields}


        method = self.method

        headers = auth.get_headers(self.secrets)
        path = method.path.format(**path_kw)
        logging.info("Opening URL: %s", path)
        url = 'https://api.tdameritrade.com/v1/{}'.format(path)
        params = {key: str(value) for key, value in kw.items()}
        if self.method.http_method == 'GET':
            resp = requests.get(url, params=params, headers=headers)
        else:
            assert False, "No method for {}".format(self.function)
        return resp.json()
