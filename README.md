# ameritrade: Python API to the TD Ameritrade Developer REST API

## Overview

This is a thin Python wrapper for the TD Ameritrade broker API. The API is
homed at this page:  https://developer.tdameritrade.com/apis

## Usage

The API is a Python 3 library you can call in order to access the full API via
Python method calls. First you import the module:

   import argparse
   import ameritrade

Then you establish a connection at the top of your program:

   def main():
       parser = argparse.ArgumentParser(description=__doc__.strip())
       ameritrade.add_args(parser)
       args = parser.parse_args()
       config = ameritrade.config_from_args(args)
       api = ameritrade.open(config)

Finally, you make method calls to the API:

    instrument = api.GetInstrument("VTI")
    pprint.pprint(instrument)

See the [reference documentation](https://developer.tdameritrade.com/apis) for
the full list of available functionality. The API is actually pretty nice and
regular, with only some minor exceptions here and there.

## Enabling Your Account

You will have to first create an account and enable home apps at the developer
site: https://developer.tdameritrade.com

## Authentication & Configuration

Authentication proceeds via OAUTH. The server provides authentication tokens and
refresh tokens. Refresh tokens pretty much allow you to use the API without
having to reauthentication much (every 90 days). It works great.

In order to configure the API, you will need to provide only your customer key.
This is a string that looks like this:

    <USERNAME>@AMER.OAUTHAP

where `USERNAME` is your TD Ameritrade username all in caps.

This library will expect a file with only this value in it, in
`~/.ameritrade/client_id`. Not that you can override this default value by
providing a config dir in the Python library call to connect, or by setting an
environment variable:

    $ export AMERITRADE_DIR=/path/to/encrypted/directory

If necessary to authenticate (e.g. the first time your run or the credentails
have expired and need to get refreshed), the API will open a browser page at
Ameritrade to enter your login credentials. Note that this is not in any way
intercepted by this code (see ameitrade/auth.py), it's just directing your web
browser to a URL. On success, the Ameritrade page will redirect to a page on
your localhost providing it with the freshly created token. This token will be
cached for future use in `~/.ameritrade/secrets.json`.

However, This means that locally, the API has to temporarily serve an HTTPS
server to receive the fresh token. In order to do this, you must create an SSL
key your browser will trust. The easiest way to do this is to create a
self-signed certificate and key. The API expects those files as
`certificate.pem` and `key.pem` in the configuration directory by default. You
can create the files with the following command:

    $ cd ~/.ameritrade
    $ openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem

Make sure you set `localhost` or `127.0.0.1` in the common name field. The email
address doesn't matter (does not have to match your customer key).

If you only do that, when you get redirected your browser will moan about the
SSL certificate not being recognized or even invalid. Click on the menus to
continue, and "proceed to localhost".

**Mac Users** On macOS, Chrome won't even let you do that by default anymore.
You have to copy the `certificate.pem` somewhere the finder will let you
navigate to it (i.e., not under a . / hidden directory), open chrome://settings,
search or navigate to "Manage Certificates (Manage HTTPS/SSL certificates and
settings)", click on `Category >> Certificates` and then `+` to add a new one,
find the `certificate.pem` file and add it, then right-click on "Info" or
double-click on it to bring up the menu, and finally set "Secure Sockets Layer
(SSL)" to "Always Trust". When you get redirected, this won't remove the
annoying gray page, but at least will allow you to click open the bottom links
to "Proceed to localhost." You won't have to do this more than once, so it's not
that big a deal.

## Testing your Configuration & Connection

To test your configuration and connection from your ~/.ameritrade config, run
either of these commands::

    $ ./bin/td-config
    $ python3 -m ameritrade.check

## Schema Validation

This library scraped a copy of the API's schemas and we are in the process of
adding full local validation of the requests & responses. See files under
`ameritrade/schemas` if you're interested.

NOTE(2021-01-13): This is not completed yet. You can use the API today but you
will obtain JSON converted to Python back. It's still nice enough to use.
