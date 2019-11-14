from typing import List

from glados import GladosPlugin, GladosRequest, GladosRouter
#from glados_router import GladosRouter


class Glados(object):
    def __init__(self):
        self.router = GladosRouter()
        self.plugins = list()  # type: List[GladosPlugin]

    def add_plugin(self, plugin: GladosPlugin):
        self.plugins.append(plugin)
        self.router.add_routes(plugin.routes)

    def request(self, request: GladosRequest):
        return self.router.exec_route(request)
