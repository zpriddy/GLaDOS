from typing import List, Dict
import yaml
import logging

from glados import GladosPlugin, GladosRequest, GladosRouter, GladosBot, BotImporter


class Glados:
    """Glados is the core of the GLaDOS package."""

    def __init__(self, config_file=None, plugins_folder=None, bots_config_dir=None):
        self.router = GladosRouter()
        self.plugins = list()  # type: List[GladosPlugin]
        self.bots = dict()  # type: Dict[str, GladosBot]

        self.config_file = config_file  # type: str
        self.plugins_folder = plugins_folder  # type: str
        self.bots_config_dir = bots_config_dir  # type: str
        self.logging_level = logging.getLevelName("WARN")
        self.logging_format = "%(asctime)s :: %(levelname)-8s :: [%(filename)s:%(lineno)s :: %(funcName)s() ] %(message)s"

    def read_config(self):
        # TODO: Fix logging setup
        if not self.config_file:
            logging.info("glados config file not set.")

        config = dict()

        try:
            with open(self.config_file) as file:
                config = yaml.load(file, Loader=yaml.FullLoader).copy()
                logging.debug(f"glados config: {config}")
        except FileNotFoundError:
            logging.error("glados config file not found")
            exit(1)

        if not config:
            logging.info("did not import any config items")

        self.logging_level = config.get("logging_level", self.logging_level)
        self.logging_format = config.get("logging_format", self.logging_format)
        logging.basicConfig(
            level=self.logging_level,
            format=self.logging_format,
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        self.plugins_folder = config.get("plugins_folder")
        self.bots_config_dir = config.get("bots_config_folder")

        import_bots = config.get("import_bots")
        if import_bots:
            logging.info("auto-importing bots as set in glados config file")
            self.import_bots()

    def import_bots(self):
        logging.info("importing bots...")
        importer = BotImporter(self.bots_config_dir)
        importer.import_bots()
        self.bots = importer.bots.copy()
        logging.info(f"successfully imported {len(self.bots)} bots")

    def add_plugin(self, plugin: GladosPlugin):
        """Add a plugin to GLaDOS

        Parameters
        ----------
        plugin : GladosPlugin
            the plugin to be added to GLaDOS

        Returns
        -------

        """
        logging.debug(f"installing plugin: {plugin.name}")
        self.plugins.append(plugin)
        self.router.add_routes(plugin)

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
