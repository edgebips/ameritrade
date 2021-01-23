# Python Bindings for TD Ameritrade Developer API

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

where `<USERNAME>` is your TD Ameritrade username all in caps.

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

## Development Assistance & Debugging

When you're writing a script that fetches data from the API, it can be expensive
to connect regularly to fetch the same data time after time. A common technique
to reduce the iteration time and the number of server connections is to cache
the last fetched data and to simply replay it back. Normally this is done in the
client program, but this API supports a `cache' mode that does just this:

    my_program.py --ameritrade-cache=/tmp/tdapi_cache

This is intended only to ease development. The cache never gets cleared or
updated. It's up to you to delete the files. You can also use this to find a
copy of all the responses returned from the server.

## Schema Validation

This library scraped a copy of the API's schemas and we are in the process of
adding full local validation of the requests & responses. See files under
`ameritrade/schemas` if you're interested.

NOTE(2021-01-13): This is not completed yet. You can use the API today but you
will obtain JSON converted to Python back. It's still nice enough to use.

## Differences with Other Projects

There are probably 50 other Git repositories with similar bindings out there.
Probably the best of them is [Alex Golec's
TDA-API](https://github.com/alexgolec/tda-api), which seems to have a growing
community building up around it.

This particular API distinguishes itself from those projects in a few ways:

- It does not coerce the usage of threading or of async/await primitves. The API
  runs in immediate, blocking mode. You can choose to use coroutines or even
  threads at the level of your own program, wrapping this API.

- It does not rely on Selenium. Refresh token for this API work for a very long
  time (in the order of months) and it's the rare occasion where a browser
  window needs to be brought up to perform authentication. For those times where
  it's needed, I'd rather the API never even have to see your password and just
  trigger opening a vanilla browser to the right URL and process the response
  token with a local server. This also removes another dependency of this
  library (it does not require your password stored anywhere; I never like
  putting in passwords in files myself, and neither should you have to).

- It cleanly separates the communication portion of the API (JSON in and out)
  with the schema and potential wrapper and validator objects. I believe that
  these two aspects can be easily factored from each other and this results in a
  much smaller library (a very small one actually), easier to maintain.

  What's more, is that the schema generation is (well, will be) completely
  automated. A script scrapes down all the schemas from the TD website and
  untangles and deduplicates the data types as much as possible. The hope is
  that a schema validator can be implemented with automatic code-generation to
  produce a very regular API, log files that can be parsed in other computer
  langauges, good up-to-date request validators and perhaps even a generated API
  for more convenient bindings.

- It should eventually support logging

Overall my goals is to keep this API as simple and lean as possible for
long-term maintainability. My goals are not to build the ultimate library for
everyone, but rather, something stable robust, up-to-date and stable that I can
use for the long term.

## Status

This project is functional, but in active development as of January 2021.
You can except some more changes during in H1 2021.
