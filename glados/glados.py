from glados_bot import GladosBot
from glados_router import GladosRouter, GladosRoute, RouteType
from glados_plugin import GladosPlugin
from typing import List

class Glados(object):
    def __init__(self):
        self.router = GladosRouter()
        self.plugins = list() # type: List[GladosPlugin]

    def add_plugin(self, plugin: GladosPlugin):
        self.plugins.append(plugin)
        self.router.add_routes(plugin.routes)

    def request(self, route_type: RouteType, route, **kwargs):
        self.router.exec_route(route_type, route, **kwargs)
