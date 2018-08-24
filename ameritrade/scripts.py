"""Support for writing short scripts with defaults from environment.

Use this to build small convenient scripts and not have to repeat all the
configuration setup every time. (This is optional, just a convenience.)
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

from os import path
import os
import re

from ameritrade import api


def add_args(parser):
    """Add arguments to an argparse ArgumentParser instance."""

    CLIENT_ID = os.environ.get('AMERITRADE_CLIENT_ID', None)
    parser.add_argument('--ameritrade-client-id', action='store',
                        default=CLIENT_ID,
                        help='The client id OAuth username.')

    CONFIG_DIR = os.environ.get('AMERITRADE_CONFIG_DIR',
                                path.join(os.getenv("HOME"), '.ameritrade'))
    parser.add_argument('--ameritrade-config-dir', action='store',
                        default=CONFIG_DIR,
                        help='The directory where the config lives.')

    parser.add_argument('--ameritrade-cache', action='store_true',
                        help='True if we cache the result of calls.')
    DEFAULT_CACHE_DIR = path.join(os.getenv('HOME'), '.ameritrade/cache')
    parser.add_argument('--ameritrade-cache-dir', action='store',
                        default=DEFAULT_CACHE_DIR,
                        help=('The directory where the Ameritrade cache files are stored, '
                              'if enabled.'))

    parser.add_argument('--ameritrade-clear-cache', action='store_true',
                        help='Clear the cache before running.')

def open_with_args(args, readonly: bool = True):
    """Create the API with the script arguments."""

    # Optionally clear the cache before running.
    if args.ameritrade_cache and args.ameritrade_clear_cache and args.ameritrade_cache_dir:
        # Clear just the filenames that look like MD5 hashes.
        cache_dir = args.ameritrade_cache_dir
        for filename in os.listdir(cache_dir):
            if not re.match(r'[a-zA-F0-9]{32}$', filename):
                continue
            os.remove(path.join(cache_dir, filename))

    return api.open_with_dir(
        client_id=args.ameritrade_client_id,
        redirect_uri='https://localhost:8444',
        config_dir=args.ameritrade_config_dir,
        cache=args.ameritrade_cache_dir if args.ameritrade_cache else None,
        readonly=readonly)
