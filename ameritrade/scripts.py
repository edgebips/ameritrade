"""Support for writing short scripts with defaults from a single directory.

The default location of that directory is ~/.ameritrade. The AMERITRADE_DIR
environment variable can be used to override the default location of this
directory. This setup also defines command-line arguments to override this
directory and how the caching is intended to be used.

Use this to build small convenient scripts and not have to repeat all the
configuration setup every time. This is optional, just a convenience.

(Note: You should probably symlink ~/.ameritrade to an encrypted partition for
security purposes.)
"""
__author__ = 'Martin Blais <blais@furius.ca>'
__license__ = "GNU GPLv2"

from os import path
import os
import re
from typing import Optional

from ameritrade import api
from ameritrade import auth


def add_args(parser):
    """Add arguments to an argparse ArgumentParser instance."""

    parser.add_argument('--ameritrade-config', action='store',
                        default=api.DEFAULT_CONFIG_DIR,
                        help='The directory where the cache and config and secrets live.')

    parser.add_argument('--ameritrade-cache', action='store',
                        default=None,
                        help=("If set, a cache directory to update and read responses from "
                              "instead of hitting the servers. This sets the API to "
                              "connect to the servers lazily by default."))


def config_from_args(args, **kwargs):
    """Create the API with the script arguments."""
    return api.config_from_dir(config_dir=args.ameritrade_config,
                               cache_dir=args.ameritrade_cache,
                               lazy=bool(args.ameritrade_cache),
                               **kwargs)
