from typing import List, Dict, TYPE_CHECKING, Optional
import yaml
import logging

from glados import (
    GladosPlugin,
    GladosRequest,
    GladosRouter,
    GladosBot,
    BotImporter,
    PluginImporter,
    read_config,
    DataStore,
)

if TYPE_CHECKING:
    from glados import GladosConfig


class Glados:
    """Glados is the core of the GLaDOS package."""

    def __init__(
        self,
        config_file=None,
        plugins_folder=None,
        bots_config_dir=None,
        plugins_config_dir=None,
    ):
        self.router = GladosRouter()
        self.plugins = list()  # type: List[GladosPlugin]
        self.bots = dict()  # type: Dict[str, GladosBot]

        self.config_file = config_file  # type: str
        self.plugins_folder = plugins_folder  # type: str
        self.bots_config_dir = bots_config_dir  # type: str
        self.plugins_config_dir = plugins_config_dir  # type: str
        self.logging_level = logging.getLevelName("DEBUG")
        self.logging_format = "%(asctime)s :: %(levelname)-8s :: [%(filename)s:%(lineno)s :: %(funcName)s() ] %(message)s"
        self.global_config = None
        self.enable_datastore = False
        self.datastore = None  # type: Optional[DataStore]

    def read_config(self, bot_name=None):
        # TODO: Fix logging setup
        if not self.config_file:
            logging.info("glados config file not set.")

        self.global_config = read_config(self.config_file)

        if "glados" not in self.global_config.sections:
            logging.info("did not import any config items")

        config = self.global_config.config.glados

        self.logging_level = config.get("logging_level", self.logging_level)
        self.logging_format = config.get("logging_format", self.logging_format)
        logging.basicConfig(
            level=self.logging_level,
            format=self.logging_format,
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        self.plugins_folder = config.get("plugins_folder")
        self.plugins_config_dir = config.get("plugins_config_folder")
        self.bots_config_dir = config.get("bots_config_folder")

        import_bots = config.get("import_bots")
        if import_bots:
            logging.info("auto-importing bots as set in glados config file")
            self.import_bots()

        import_plugins = config.get("import_plugins", True)
        if import_plugins is True:
            self.import_plugins()
        if import_plugins == "limited":
            self.import_plugins(bot_name=bot_name)

        # Config datastore
        if "datastore" in self.global_config.sections:
            ds_config = self.global_config.config.datastore
            ds_enabled = ds_config.get("enabled", False)
            ds_host = ds_config.get("host")
            ds_port = ds_config.get("port", 5432)
            ds_username = ds_config.get("username")
            ds_password = ds_config.get("password")
            ds_database = ds_config.get("database", "glados")
            ds_recreate = ds_config.get("recreate", False)
            if None in [
                ds_enabled,
                ds_host,
                ds_port,
                ds_username,
                ds_password,
                ds_database,
            ]:
                logging.warning(
                    "missing datastore config item(s) or datastore disabled. disabling datastore."
                )
                self.enable_datastore = False
            else:
                self.enable_datastore = ds_enabled
                if ds_enabled:
                    self.datastore = DataStore(
                        host=ds_host,
                        port=ds_port,
                        username=ds_username,
                        password=ds_password,
                        database=ds_database,
                    )
                    self.datastore.create_table(force=ds_recreate)
        else:
            logging.warning("datastore section not found in config file")
            self.enable_datastore = False

    def import_bots(self):
        """Import all discovered bots"""
        logging.info("importing bots...")
        importer = BotImporter(self.bots_config_dir)
        importer.import_bots()
        self.bots = importer.bots.copy()
        logging.info(f"successfully imported {len(self.bots)} bots")

    def import_plugins(self, bot_name=None):
        """Import all discovered plugins and add them to the plugin list."""
        logging.info("Importing plugins...")
        importer = PluginImporter(self.plugins_folder, self.plugins_config_dir)
        importer.discover_plugins()
        importer.load_discovered_plugins_config(False)

        # Remove unused bots if a bot name is provided.
        # This will cause a bunch of warnings of bots not existing. This is expected.
        # TODO(zpriddy): This should not remove the bots from the global bots.
        #  It should also check to see if plugins are already installed before
        #  installing them. This is key for AWS Lambda caching issues.

        if bot_name:
            bots = self.bots.copy()  #  type: dict
            for b_name, b_config in self.bots.items():
                if b_name != bot_name:
                    bots.pop(b_name)
            self.bots = bots.copy()

        importer.import_discovered_plugins(self.bots)
        for plugin in importer.plugins.values():
            self.add_plugin(plugin)
        logging.info(f"successfully imported {len(self.plugins)} plugins")

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

    def has_datastore(self):
        return (
            True
            if self.enable_datastore is True and self.datastore is not None
            else False
        )

    def request(self, request: GladosRequest):
        """Send a request to GLaDOS.

        This function will also set the datastore session for the request, try to find the interaction in the datastore and fetch it. This info is available in the request.

        Parameters
        ----------
        request : GladosRequest
            the request to be sent to GLaDOS

        Returns
        -------

        """
        # DataStore actions if enabled
        if self.has_datastore():
            request.set_datastore(self.datastore)
            request.set_interaction_from_datastore()

        response = self.router.exec_route(request)

        if self.has_datastore() and request.auto_link and request.new_interaction:
            try:
                request.link_interaction_to_message_response(
                    request.new_interaction, response
                )
            except Exception as e:
                logging.error(
                    f"error linking response to interaction: {e} response: {response}"
                )

        if self.has_datastore():
            request.close_session()

        return response
