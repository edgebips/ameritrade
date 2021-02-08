"""Main API code for the Ameritrade API wrappers.
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

from decimal import Decimal
from os import path
from typing import Tuple, Dict, Optional, NamedTuple,Optional
import builtins
import hashlib
import logging
import os
import pickle
import re
import requests
import time

# We need use_decimal.
# TODO(blais): Remove this when the default JSON gets updated to 2.1 and above.
try:
    import simplejson as json
except ImportError:
    import json

from ameritrade import auth
from ameritrade import schema


DEFAULT_CONFIG_DIR = os.environ.get(
    'AMERITRADE_DIR', path.join(os.getenv('HOME'), '.ameritrade'))


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

    # Cache directory; if this is set, requests matching a historical request
    # will be fetched from the cache instead of being sent to the server
    # upstream. This is an easy way to avoid hitting the servers too often
    # during development and after the cache is filled, returns instantly. By
    # default this is not set, so all requests are sent to the server and you
    # don't need this otherwise.
    ('cache_dir', Optional[str]),

    # Authenticate or refresh secrets lazily, upon first attribute access.
    ('lazy', bool),

    # Enable debug traces.
    ('debug', bool),
    ])


_ConfigDefaults = {
    'redirect_uri': auth.DEFAULT_REDIRECT_URI,
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


def config_from_dir(config_dir: Optional[str] = None, **kwargs) -> Config:
    """Create an API endpoint with a config dfir. This is the main entry point."""

    # Set defaults from same default dir used in scripts.add_args().
    newargs = dict(kwargs)
    if config_dir is None:
        config_dir = DEFAULT_CONFIG_DIR

    # Set filenames from dir if not set.
    if newargs.get('key_file', None) is None:
        newargs['key_file'] = path.join(config_dir, 'key.pem')
    if newargs.get('certificate_file', None) is None:
        newargs['certificate_file'] = path.join(config_dir, 'certificate.pem')
    if newargs.get('secrets_file', None) is None:
        newargs['secrets_file'] = path.join(config_dir, 'secrets.json')

    # Read the client id from the 'config/client_id' file.
    if newargs.get('client_id', None) is None:
        client_id_file = path.join(config_dir, 'client_id')
        with builtins.open(client_id_file) as clifile:
            newargs['client_id'] = clifile.read().strip()

    return Config(**newargs)


class JsonWrapper(dict):
    """A convenience wrapper for JSON dicts with attribute access."""

    def __getattr__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError as exc:
            raise AttributeError from exc


# TODO(blais): Make these configurable.
JSON_KWARGS = dict(object_hook=JsonWrapper, use_decimal=True)


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
            self.secrets = auth.read_or_create_secrets(self.config)
        return self.secrets

    def refresh_secrets(self):
        if self.secrets is None:
            return self.get_secrets()
        else:
            self.secrets = auth.refresh_secrets(self.config, self.secrets)
        return self.secrets

    def __getattr__(self, key):
        method = schema.SCHEMA[key]
        config = self.config

        # Disallow read-only methods.
        if config.readonly and method.http_method != 'GET':
            raise NameError("Method {} is not allowed in read-only mode.".format(
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
            # TODO(blais): Remove this, this isn't working. Convert schemas
            # instead of using validators.
            exc = field.validator(value)
            if exc:
                raise exc

        # Build the headers and URL path to call.
        path_kw = {field: kw.pop(field) for field in method.url_fields}
        path = method.path.format(**path_kw)
        url = 'https://api.tdameritrade.com/v1{}'.format(path)
        logging.info("Opening URL: %s", url)

        # Call the resources with parameters.
        # TODO(blais): Clean this up with methods.
        params = {key: str(value) for key, value in kw.items()}
        extra_headers = {}
        if self.method.http_method == 'GET':
            # Those methods have query params (something none of them), never a
            # payload, but always a JSON response.
            call = lambda hdrs: requests.get(url, params=params, headers=hdrs)
            retvalue = lambda r: r.json(**JSON_KWARGS) if r.text else None

        elif self.method.http_method == 'DELETE':
            # Those methods only have the URL, no query params nor payload.
            # Never a response body.
            call = lambda hdrs: requests.delete(url, params=params, headers=hdrs)
            retvalue = lambda r: r.json(**JSON_KWARGS) if r.text else None

        elif self.method.http_method in {'POST', 'PUT', 'PATCH'}:
            # These methods never have query params but all have a payload.
            # Never a response body.
            extra_headers['Content-Type'] = 'application/json'
            method = getattr(requests, self.method.http_method.lower())
            call = lambda hdrs: method(url, json=kw['payload'], headers=hdrs)
            retvalue = lambda r: r.json(**JSON_KWARGS) if r.text else None

        else:
            # TODO(blais): Implement the other methods along with their schemas.
            assert False, "Unsupported HTTP method for {}: {}".format(method.name,
                                                                      method.http_method)

        # Make the first attempt to call the method.
        secrets = self.api.get_secrets()
        headers = auth.get_headers(secrets)
        headers.update(extra_headers)
        resp = call(headers)
        if resp.status_code == requests.codes['unauthorized']:  # HTTP error 401
            # If the token is expired, refresh the token automatically and retry
            # once, maybe even a few times, if we need some resilience for a job
            # that needs to run all week (e.g., a monitoring job).
            num_retries = 1  # TODO(blais): Add configuration.
            for _ in range(num_retries):
                secrets = self.api.refresh_secrets()
                headers = auth.get_headers(secrets)
                resp = call(headers)
                if resp.status_code == requests.codes.ok:
                    break
                time.sleep(0.3)  # TODO(blais): Add configuration.
            else:
                # Oh well, still failed. Bail out.
                raise IOError("HTTP Error {}: {} ({})".format(
                    resp.status_code, resp.reason, resp.text))

        # Return either JSON or text, depending on method.
        return retvalue(resp)



class CachedMethod:
    """A caching proxy for any callable methods."""

    def __init__(self, cache_dir, method_name, method, debug):
        self.cache_dir = cache_dir
        self.method_name = method_name
        self.method = method
        self.debug = debug
        assert cache_dir

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
        cache_path = path.join(self.cache_dir, "{}.json".format(digest))
        if path.exists(cache_path):
            # Cache hit.
            logging.info("{%s} Cache hit for call to %s", digest, self.method_name)
            with builtins.open(cache_path, 'r') as infile:
                return json.load(infile, **JSON_KWARGS)
        else:
            # Cache miss.
            logging.info("{%s} Cache miss for call to %s", digest, self.method_name)
            response = self.method(**kw)
            logging.info("{%s} Updating cache for call to %s", digest, self.method_name)
            with builtins.open(cache_path, 'w') as infile:
                json.dump(response, infile, sort_keys=True, indent=4, use_decimal=True)
            return response
