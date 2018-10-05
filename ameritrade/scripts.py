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

from ameritrade import api


def add_args(parser):
    """Add arguments to an argparse ArgumentParser instance."""

    # Establish a single directory to store all the configuration and cache
    # files.
    default_dir = path.join(os.getenv('HOME'), '.ameritrade')
    program_dir = os.environ.get('AMERITRADE_DIR', default_dir)
    parser.add_argument('--ameritrade-dir', action='store',
                        default=program_dir,
                        help='The directory where the cache and config and secrets live.')

    # Cache control. This kind of control is very useful during development.
    parser.set_defaults(ameritrade_cache={'read': False, 'write': False})
    cache_group = parser.add_mutually_exclusive_group()
    cache_group.add_argument('--ameritrade-cache', dest='ameritrade_cache',
                             action='store_const', const={'read': True, 'write': True},
                             help='Read and write from the request cache.')
    cache_group.add_argument('--ameritrade-read-cache', dest='ameritrade_cache',
                             action='store_const', const={'read': True, 'write': False},
                             help='Read from the cache, but do not update it.')
    cache_group.add_argument('--ameritrade-write-cache', dest='ameritrade_cache',
                             action='store_const', const={'read': False, 'write': True},
                             help='Do not read from the cache, but update it always.')

    # Clear the cache before running.
    parser.add_argument('--ameritrade-clear-cache', action='store_true',
                        help='Clear the cache before running.')


def clear_cache(cache_dir: str):
    """Remove all the cached filenames."""
    for filename in os.listdir(cache_dir):
        if not re.match(r'[a-zA-F0-9]{32}$', filename):
            continue
        os.remove(path.join(cache_dir, filename))


def config_from_args(args,
                     readonly: bool = True,
                     lazy: bool = False,
                     debug: bool = False):
    """Create the API with the script arguments."""

    # Optionally clear the cache before running.
    if args.ameritrade_clear_cache and args.ameritrade_cache_dir:
        # Clear just the filenames that look like MD5 hashes.
        clear_cache(args.ameritrade_cache_dir)

    # The config dir contains the certificate.pem and key.pem files, the
    # secrets.json file, and a client_id file.
    config_dir = path.join(args.ameritrade_dir, 'config')

    # The cache dir contains past responses for API queries.
    cache_dir = path.join(args.ameritrade_dir, 'cache')

    # Cache settings.
    read_cache = args.ameritrade_cache.get('read', False)
    write_cache = args.ameritrade_cache.get('write', False)

    return api.config_from_dir(
        config_dir=config_dir,
        redirect_uri='https://localhost:8444',
        read_cache=read_cache,
        write_cache=write_cache,
        cache_dir=cache_dir if read_cache or write_cache else None,
        readonly=readonly,
        lazy=lazy,
        debug=debug)
