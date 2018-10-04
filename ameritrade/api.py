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


_Config = NamedTuple('_Config', [
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

    # The location of the JSON file to store the OAuth token in between
    # invocations.
    ('secrets_file', str),

    # Timeout (in seconds) to wait for OAuth token response.
    ('timeout', int),

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
    ('cache_dir', str),

    # Authenticate or refresh secrets lazily, upon first attribute access.
    ('lazy', bool),

    # Enable debug traces.
    ('debug', bool),
    ])


_ConfigDefaults = {
    'redirect_uri': 'https://localhost:8444',
    'timeout': 300,
    'readonly': True,
    'lazy': False,
    'debug': False,
}

class Config(_Config):
    """Configuration object. Create one of those and call AmeritradeAPI()."""

    def __new__(cls, *args, **kwargs):
        """Create a Config instance using the kwargs."""
        cpargs = dict(kwargs)
        args += tuple(cpargs.pop(key, _ConfigDefaults.get(key, None))
                      for key in Config._fields[len(args):])
        if cpargs:
            raise ValueError("Invalid arguments: {}".format(','.join(cpargs.keys())))
        return _Config.__new__(cls, *args)


def config_from_dir(config_dir: str = os.getcwd(), **kwargs) -> Config:
    """Create an API endpoint with a config dfir. This is the main entry point."""

    # Set filenames from dir if not set.
    newargs = dict(kwargs)
    if newargs.get('key_file', None) is None:
        newargs['key_file'] = path.join(config_dir, 'key.pem')
    if newargs.get('certificate_file', None) is None:
        newargs['certificate_file'] = path.join(config_dir, 'certificate.pem')
    if newargs.get('secrets_file', None) is None:
        newargs['secrets_file'] = path.join(config_dir, 'secrets.json')

    # Read the client id from the 'config/client_id' file.
    if newargs.get('client_id', None) is None:
        newargs['client_id']
        client_id_file = path.join(config_dir, 'client_id')
        with builtins.open(client_id_file) as clifile:
            client_id = clifile.read().strip()

    return Config(**newargs)


# A dict of secrets. Contains the access token and Bearer type.
Secrets = Dict[str, str]


class AmeritradeAPI:
    """An Ameritrade endpoint, with credentials."""

    def __init__(self, config: Config):
        self.config = config
        self.secrets = None
        if not config.lazy:
            self.get_secrets()

    def get_secrets(self):
        if self.secrets is None:
            logging.info("Authenticating")
            self.secrets = auth.read_or_create_secrets(self.config.secrets_file,
                                                       self.config)
        return self.secrets

    def __getattr__(self, key):
        method = schema.SCHEMA[key]
        config = self.config

        # Disallow read-only methods.
        if config.readonly and method.http_method != 'GET':
            raise NameError("Method {} is not allowed in safe read-only mode.".format(
                method.name))
        else:
            # Create a method, with caching or not.
            method = CallableMethod(method, self, config.debug)
            if config.cache_dir:
                method = CachedMethod(config.cache_dir, key, method, config.debug)
            return method


def open(config: Config) -> AmeritradeAPI:
    """Create an API endpoint. This is the main entry point."""
    return AmeritradeAPI(config)


class CallableMethod:
    """Callable method."""

    def __init__(self, method: schema.PreparedMethod, api: AmeritradeAPI, debug: bool):
        self.method = method
        self.api = api
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
        api = self.api.get_secrets()
        headers = auth.get_headers(api)
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
