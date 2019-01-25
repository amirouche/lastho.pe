#!/usr/bin/env python3
"""Usage:
  lasthope run

Options:
  -h --help     Show this screen.
"""
import asyncio
import logging
import os
from uuid import UUID

import daiquiri
import uvloop
from aiohttp import ClientSession
from aiohttp import web
from argon2 import PasswordHasher

from docopt import docopt
from itsdangerous import BadSignature
from itsdangerous import SignatureExpired
from itsdangerous import TimestampSigner

from pathlib import Path
from setproctitle import setproctitle  # pylint: disable=no-name-in-module

from lasthope import settings
from lasthope import feed


log = daiquiri.getLogger(__name__)


__version__ = (0, 0, 0)
VERSION = "v" + ".".join([str(x) for x in __version__])
HOMEPAGE = "https://bit.ly/2D2fT5Q"


# middleware


async def middleware_check_auth(app, handler):
    """Check that the request has a valid token.

    Raise HTTPForbidden when the token is not valid.

    `handler` can be marked to ignore token. This is useful for pages like
    account login, account creation and password retrieval

    """

    async def middleware_handler(request):
        if getattr(handler, "no_auth", False):
            response = await handler(request)
            return response
        else:
            try:
                token = request.cookies["token"]
            except KeyError:
                log.debug("No auth token found")
                raise web.HTTPFound(location="/")
            else:
                max_age = app["settings"].TOKEN_MAX_AGE
                try:
                    uid = app["signer"].unsign(token, max_age=max_age)
                except SignatureExpired:
                    log.debug("Token expired")
                    raise web.HTTPFound(location="/")
                except BadSignature:
                    log.debug("Bad signature")
                    raise web.HTTPFound(location="/")
                else:
                    uid = uid.decode("utf-8")
                    uid = UUID(hex=uid)
                    actor = await user.user_by_uid(
                        request.app["db"], request.app["sparky"], uid
                    )
                    if actor is None:
                        redirect = web.HTTPSeeOther(location="/")
                        redirect.del_cookie("token")
                        return redirect
                    log.debug("User authenticated as '%s'", actor["name"])
                    request.user = actor
                    response = await handler(request)
                    return response

    return middleware_handler


# status


async def status(request):
    """Check that the app is properly working"""
    return web.json_response("OK")


# boot the app


async def init_database(app):
    log.debug("init database")
    return app


def create_app(loop):
    """Starts the aiohttp process to serve the REST API"""
    # setup logging
    level_name = os.environ.get("DEBUG", "INFO")
    level = getattr(logging, level_name)
    daiquiri.setup(level=level, outputs=("stderr",))

    setproctitle("lasthope")

    log.info("init lasthope %s", VERSION)

    # init app
    app = web.Application()  # pylint: disable=invalid-name
    # others
    app.on_startup.append(init_database)
    app["settings"] = settings
    app["hasher"] = PasswordHasher()
    app["signer"] = TimestampSigner(settings.SECRET)
    user_agent = "lasthope {} ({})".format(VERSION, HOMEPAGE)
    headers = {"User-Agent": user_agent}
    app["session"] = ClientSession(headers=headers)

    # api route
    app.router.add_route("GET", "/api/status", status)

    # index and static
    def index(request):
        index = Path(__file__).parent / "index.html"
        with index.open("rb") as f:
            out = f.read()
        return web.Response(body=out, content_type="text/html")

    app.router.add_route("GET", "/", index)
    app.add_routes([web.static("/static", Path(__file__).parent / "static")])

    return app


def main():
    args = docopt(__doc__)
    setproctitle("lasthope")

    if args.get("run"):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()
        app = create_app(loop)
        log.info("running webserver on http://0.0.0.0:8000")
        web.run_app(app, host="0.0.0.0", port=8000)  # nosec
    else:
        print("Use --help to know more")


if __name__ == "__main__":
    main()
