from typing import List, Dict

from glados import GladosPlugin, GladosRequest, GladosRouter, GladosBot


class Glados():
    def __init__(self):
        self.router = GladosRouter()
        self.plugins = list()  # type: List[GladosPlugin]
        self.bots = dict()  # type: Dict[str, GladosBot]

    def add_plugin(self, plugin: GladosPlugin):
        self.plugins.append(plugin)
        self.router.add_routes(plugin.routes)

    def add_bot(self, bot: GladosBot):
        self.bots[bot.name] = bot

    def request(self, request: GladosRequest):
        return self.router.exec_route(request)
