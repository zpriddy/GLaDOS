from typing import List, Dict

from glados import GladosPlugin, GladosRequest, GladosRouter, GladosBot


class Glados:
    """Glados is the core of the GLaDOS package."""

    def __init__(self):
        self.router = GladosRouter()
        self.plugins = list()  # type: List[GladosPlugin]
        self.bots = dict()  # type: Dict[str, GladosBot]

    def add_plugin(self, plugin: GladosPlugin):
        """Add a plugin to GLaDOS

        Parameters
        ----------
        plugin : GladosPlugin
            the plugin to be added to GLaDOS

        Returns
        -------

        """
        self.plugins.append(plugin)
        self.router.add_routes(plugin.routes)

    def add_bot(self, bot: GladosBot):
        """Add a new bot to GLaDOS.

        Parameters
        ----------
        bot : GladosBot
            the bot to be added to GLaDOS

        Returns
        -------

        """
        self.bots[bot.name] = bot

    def request(self, request: GladosRequest):
        """Send a request to GLaDOS.

        Parameters
        ----------
        request : GladosRequest
            the request to be sent to GLaDOS

        Returns
        -------

        """
        return self.router.exec_route(request)
