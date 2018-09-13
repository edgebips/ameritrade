"""Main API code for the Ameritrade API wrappers.
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

from os import path
from typing import Tuple, Dict, NamedTuple
import builtins
import hashlib
import json
import logging
import os
import pickle
from pprint import pprint
import re
import requests

from ameritrade import auth
from ameritrade import schema


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

    # Cache: If non-null, all calls are cached to files and the cache is
    # consulted and returned if present before making new calls. This is
    # intended to be used during development of scripts in order to avoid
    # hitting the API so much while iterating over code. The cache is indexed by
    # method name and set of arguments. Don't use this normally, just when
    # developing or debugging, to minimize API calls and reduce turnaround time.
    # Cache hit/misses are logged to INFO level.
    ('cache', str),

    # Enable debug traces.
    ('debug', bool),
    ])


def open(client_id: str,
         redirect_uri: str = 'https://localhost:8444',
         key_file: str = None,
         certificate_file: str = None,
         timeout: int = 300,
         secrets_file: str = None,
         readonly: bool = True,
         cache: str = None,
         debug: bool = False):
    """Create an API endpoint. This is the main entry point."""
    config = Config(client_id,
                    redirect_uri,
                    key_file,
                    certificate_file,
                    timeout,
                    secrets_file,
                    readonly,
                    cache,
                    debug)
    return AmeritradeAPI(config)


def open_with_dir(client_id: str,
                  config_dir: str = os.getcwd(),
                  redirect_uri: str = 'https://localhost:8444',
                  timeout: int = 300,
                  readonly: bool = True,
                  cache: str = None,
                  debug: bool = False):
    """Create an API endpoint with a config dfir. This is the main entry point."""
    config = Config(client_id,
                    redirect_uri,
                    path.join(config_dir, 'key.pem'),
                    path.join(config_dir, 'certificate.pem'),
                    timeout,
                    path.join(config_dir, 'secrets.json'),
                    readonly,
                    cache,
                    debug)
    return AmeritradeAPI(config)


# A dict of secrets. Contains the access token and Bearer type.
Secrets = Dict[str, str]


class AmeritradeAPI:
    """An Ameritrade endpoint, with credentials."""

    def __init__(self, config: Config):
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
            method = CallableMethod(method,
                                    object.__getattribute__(self, 'secrets'),
                                    config.debug)
            if config.cache:
                method = CachedMethod(config.cache, key, method, config.debug)
            return method


class CallableMethod:
    """Callable method."""

    def __init__(self, method: schema.PreparedMethod, secrets: Secrets, debug: bool):
        self.method = method
        self.secrets = secrets
        self.debug = debug

    def __call__(self, **kw):
        method = self.method

        # Remove values which are None.
        kw = {key: value for key, value in kw.items() if value is not None}

        # Check that all the required fields are being provided.
        provided_fields = set(kw.keys())
        uncovered_fields = method.required_fields - provided_fields
        if uncovered_fields:
            raise TypeError("Missing required fields: {}".format(uncovered_fields))

        # Check that there aren't any extra fields.
        invalid_fields = provided_fields - method.all_fields
        if invalid_fields:
            raise TypeError("Invalid fields: {}".format(invalid_fields))

        # Run the validations if there are any.
        fieldmap = {field.name: field for field in method.fields}
        for fname, value in kw.items():
            field = fieldmap[fname]
            if field.validator is None:
                continue
            exc = field.validator(value)
            if exc:
                raise exc

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
            return resp.json()
        elif self.method.http_method == 'DELETE':
            resp = requests.delete(url, params=params, headers=headers)
            return resp.text
        elif self.method.http_method == 'POST':
            headers['Content-Type'] = 'application/json'
            resp = requests.post(url, json=kw['payload'], headers=headers)
            return resp.text
        else:
            assert False, "Unsupported HTTP method for {}: {}".format(method.name,
                                                                      method.http_method)


class CachedMethod:
    """A caching proxy for any callable methods."""

    def __init__(self, cache_dir, method_name, method, debug):
        self.cache_dir = cache_dir
        self.method_name = method_name
        self.method = method
        self.debug = debug

    def __call__(self, **kw):
        # Ensure the cache directory exists the first time a method is called.
        if not path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        # Remove values which are None.
        kw = {key: value for key, value in kw.items() if value is not None}

        # Compute unique method call hash.
        md5 = hashlib.md5()
        keyobj = (self.method_name, sorted(kw.items()))
        md5.update(pickle.dumps(keyobj))
        digest = md5.hexdigest()

        # Test the cache.
        cache_path = path.join(self.cache_dir, digest)
        if path.exists(cache_path):
            # Cache hit.
            logging.info("Cache hit for call to %s", self.method_name)
            with builtins.open(cache_path, 'r') as infile:
                return json.load(infile)
        else:
            # Cache miss.
            logging.info("Cache miss for call to %s", self.method_name)
            response = self.method(**kw)
            with builtins.open(cache_path, 'w') as infile:
                json.dump(response, infile)
            return response
