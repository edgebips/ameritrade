"""OAuth authentication and secrets code for the Ameritrade API."""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

from os import path
from typing import Dict
from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.parse import urlparse
import http.server
import json
import logging
import requests
import socketserver
import socket
import ssl
import threading
import webbrowser


DEFAULT_REDIRECT_URI = 'https://localhost:8444'


def read_or_create_secrets(secrets_file: str, config):
    """Initialize the secrets file."""
    # If no path to a secrets file is configured, just authenticate every time.
    if not secrets_file:
        secrets = authenticate(config)
    else:
        # Try to load the secrets file from disk.
        if path.exists(secrets_file):
            with open(secrets_file) as infile:
                secrets = json.load(infile)

            # Automatically re-authenticate if the token is expired.
            if test_secrets(secrets):
                return secrets
            else:
                logging.warning("Secrets expired or invalid; refreshing.")

                # Attempt to generate a refresh token.
                secrets = refresh_token(config.client_id, secrets["refresh_token"])
                if (isinstance(secrets, dict) and
                    'access_token' in secrets and
                    'refresh_token' in secrets):
                    # Success; Override the secrets and return.
                    with open(secrets_file, 'w') as outfile:
                        json.dump(secrets, outfile)
                    return secrets
                else:
                    logging.warning("Could not refresh access token; authenticating.")

        # We have to authenticate.
        secrets = authenticate(config)

        # Store the secrets to disk for the next time.
        with open(secrets_file, 'w') as outfile:
            json.dump(secrets, outfile)

    return secrets


def test_secrets(secrets) -> bool:
    """Return true if the secrets works."""
    headers = get_headers(secrets)
    resp = requests.get('https://api.tdameritrade.com/v1/instruments/SPY',
                        data={}, headers=headers)
    return resp.ok


def authenticate(config) -> Dict[str, str]:
    """Start an HTTP server and open a browser window to OAuth authenticate."""

    if not path.exists(config.key_file):
        raise OSError("FileNotFoundError: {}".format(config.key_file))
    if not path.exists(config.certificate_file):
        raise OSError("FileNotFoundError: {}".format(config.certificate_file))

    open_auth_browser(config)
    return gather_token(config)


def open_auth_browser(config):
    """Open browser tab for the user to type their password."""
    params = {
        'response_type': 'code',
        'redirect_uri': config.redirect_uri,
        'client_id': config.client_id,
    }
    auth_url = 'https://auth.tdameritrade.com/auth?{}'.format(urlencode(params))
    logging.info("Open to authenticate: %s", auth_url)
    webbrowser.open(auth_url, new=2)


def gather_token(config):
    """Create a server, run it in a thread, wait for handler, timeout."""

    # An event to signal a waiter thread that we've received the token.
    event = threading.Event()

    # Create an HTTPS server.
    pr = urlparse(config.redirect_uri)
    server = HTTPServer((pr.hostname, pr.port), TokenHandler,
                        config=config, event=event)

    # Wrap the socket in SSL.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=config.certificate_file,
                            keyfile=config.key_file)
    with context.wrap_socket(server.socket, server_side=True) as ssocket:
        server.socket = ssocket

        # Start server thread, wait for handler, timeout
        with server:
            thread = threading.Thread(target=server.serve_forever)
            thread.daemon = True
            thread.start()
            server.event.wait(timeout=300)
            server.shutdown()
            logging.info('Server: done')
            thread.join()

    return server.secrets


def refresh_token(client_id, token):
    """Attempt to refresh the token.

    Args:
      client_id: The client id.
      token: The refresh token.
    """
    # Post access token request.
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'refresh_token',
            'refresh_token': token,
            'access_type': 'offline',
            'client_id': client_id}
    resp = requests.post('https://api.tdameritrade.com/v1/oauth2/token',
                         data=data,
                         headers=headers)
    return resp.json()


class HTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Transient HTTP server used to process OAuth token response."""

    def __init__(self, *args, **kw):
        self.config = kw.pop('config')
        self.event = kw.pop('event')
        super(HTTPServer, self).__init__(*args, **kw)

        # Storage location for handler to return secrets via side-effect.
        self.secrets = None


class TokenHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        """Process OAuth token and store it into the server."""

        # Get the OAuth token code from the request.
        path, _, query_string = self.path.partition('?')
        qdict = parse_qs(query_string)

        # Ignore requests for other URLs, e.g., favicon.ico.
        if 'code' not in qdict:
            return
        code = qdict['code'][0]

        server = self.server
        config = server.config

        # Post access token request.
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'grant_type': 'authorization_code',
                'access_type': 'offline',
                'code': code,
                'client_id': config.client_id,
                'redirect_uri': config.redirect_uri}
        resp = requests.post('https://api.tdameritrade.com/v1/oauth2/token',
                             data=data,
                             headers=headers)

        # Return response.
        if resp.ok:
            # Send response headers.
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            # Stash the response contents into the server.
            server.secrets = resp.json()
            server.event.set()

            self.wfile.write(b'OK.')
        else:
            self.send_response(resp.status_code)
            self.end_headers()

        logging.info("Handler: done")


def get_headers(secrets) -> Dict[str, str]:
    """Get the token headers to include."""
    auth = '{} {}'.format(secrets['token_type'],
                          secrets['access_token'])
    return {'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': auth}
