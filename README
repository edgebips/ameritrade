============================================================
   ameritrade: Python API to the TD Ameritrade REST API
============================================================

Introduction
--------------------

This is a thin Python wrapper for the TD Ameritrade broker API.

The API is documnented at this page:
https://developer.tdameritrade.com/apis


Usage
--------------------

https://developer.tdameritrade.com/content/web-server-authentication-python-3

   $ export AMERITRADE_DIR=/path/to/encrypted/directory

<USERNAME>@AMER.OAUTHAP'

   $ cd /path/to/encrypted/directory
   $ openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem

Then from Python::

   import argparse
   import ameritrade

   def main():
     parser = argparse.ArgumentParser(description=__doc__.strip())
     ameritrade.add_script_args(parser)
     args = parser.parse_args()
     config = ameritrade.config_from_args(args)
     api = ameritrade.open(config)
     ...

See `examples/minimal.py` for an example.

To test your configuration and connection from your ~/.ameritrade config, run this::

   python3 -m ameritrade.check
