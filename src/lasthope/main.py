#!/usr/bin/env python3
"""Usage:
  lasthope run

Options:
  -h --help     Show this screen.
"""
import asyncio
import logging
import json
import os
from time import time

import daiquiri
import uvloop
from aiohttp import ClientSession
from aiohttp import web

from docopt import docopt

from pathlib import Path
from setproctitle import setproctitle  # noqa

import hoply as h
from hoply.leveldb import LevelDBConnexion

# from lasthope import settings


log = daiquiri.getLogger(__name__)


__version__ = (0, 0, 0)
VERSION = "v" + ".".join([str(x) for x in __version__])
HOMEPAGE = "https://lastho.pe"


# status


async def status(request):
    """Check that the app is properly working"""
    return web.json_response("OK")


# boot the app


async def init_database(app):
    log.debug("init database")
    cnx = LevelDBConnexion("/tmp/wt", logging=True)
    db = h.open(cnx, 'hoply', ('graph', 'subject', 'predicate'))
    app["db"] = db
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
    app["settings"] = None
    user_agent = "lasthope {} ({})".format(VERSION, HOMEPAGE)
    headers = {"User-Agent": user_agent}
    app["session"] = ClientSession(headers=headers)

    # api routes
    app.router.add_route("GET", "/api/status/", status)

    def pick(binding, keys):
        out = dict()
        for key in keys:
            out[key] = binding[key]
        return out

    async def projects(request):
        db = request.app["db"]
        query = h.compose(
            h.where(h.var("uid"), "type", "project"),
            h.where(h.var("uid"), "project/title", h.var("title")),
        )
        out = [pick(binding, ("uid", "title")) for binding in query(db)]
        return web.json_response(out)

    app.router.add_route("GET", "/api/projects/", projects)

    def now():
        # XXX: maybe replace with loop.time() trickry
        return int(time())

    async def project_new(request):
        data = await request.json()
        title = data["title"]
        description = data["description"]
        db = request.app["db"]
        with db.transaction():
            uid = h.uid().hex
            db.add(uid, "type", "project")
            db.add(uid, "project/title", title)
            # add description as first item
            item = h.uid().hex
            db.add(item, "type", "item")
            db.add(item, "item/project", uid)
            db.add(item, "item/type", "query")
            db.add(item, "item/value", json.dumps(description))
            db.add(item, "item/timestamp", now())
        return web.json_response(dict(uid=uid))

    app.router.add_route("POST", "/api/project/new/", project_new)

    async def project_get(request):
        uid = request.match_info["uid"]
        log.debug("Looking up project uid=%r", uid)
        out = dict(uid=uid)
        db = request.app["db"]
        # query project title
        query = h.compose(h.where(uid, "project/title", h.var("title")))
        out["title"] = list(query(db))[0]["title"]

        # query projet's items
        query = h.compose(
            h.where(h.var("uid"), "item/project", uid),
            # h.where(h.var('uid'), 'type', 'item'),
            h.where(h.var("uid"), "item/type", h.var("type")),
            h.where(h.var("uid"), "item/value", h.var("value")),
            h.where(h.var("uid"), "item/timestamp", h.var("timestamp")),
        )
        items = list()
        keys = ("uid", "type", "value", "timestamp")
        for binding in query(db):
            item = pick(binding, keys)
            item["value"] = json.loads(item["value"])
            items.append(item)
        items.sort(key=lambda x: x["timestamp"])
        out["items"] = items

        return web.json_response(out)

    app.router.add_route("GET", "/api/project/{uid}/", project_get)

    import yaml
    import searx.engines
    import searx.search

    settings = Path(__file__).parent.parent / "settings.yml"
    settings = yaml.load(settings.open())
    engines = searx.engines.load_engines(settings["engines"])

    async def search(query):
        params = searx.search.default_request_params()
        params["pageno"] = 1
        params["language"] = "en-US"
        params["time_range"] = None

        return searx.search.search_one_request(engines["google"], query, params)

    async def project_post(request):
        query = await request.json()
        query = query["query"]
        uid = request.match_info["uid"]
        db = request.app["db"]
        # add item to project
        with db.transaction():
            item = h.uid().hex
            db.add(item, "type", "item")
            db.add(item, "item/project", uid)
            db.add(item, "item/type", "query")
            db.add(item, "item/value", json.dumps(query))
            db.add(item, "item/timestamp", now())

            hits = await search(query)

            for hit in hits:
                hit_uid = h.uid().hex
                db.add(hit_uid, "type", "item")
                db.add(hit_uid, "item/project", uid)
                db.add(hit_uid, "item/type", "reply")
                db.add(hit_uid, "item/value", json.dumps(hit))
                db.add(hit_uid, "item/timestamp", now())

        return web.json_response()

    app.router.add_route("POST", "/api/project/{uid}/", project_post)

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
