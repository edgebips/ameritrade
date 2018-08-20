"""Support for writing short scripts with defaults from environment.

Use this to build small convenient scripts and not have to repeat all the
configuration setup every time. (This is optional, just a convenience.)
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

from os import path
import os

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


def open_with_args(args):
    """Create the API with the script arguments."""
    return api.open_with_dir(client_id=args.ameritrade_client_id,
                             redirect_uri='https://localhost:8444',
                             config_dir=args.ameritrade_config_dir)
