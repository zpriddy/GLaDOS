from typing import Callable, Dict, Union
import yaml
import glob
import logging

import importlib

from glados import (
    GladosBot,
    RouteType,
    GladosRoute,
    BOT_ROUTES,
    GladosPathExistsError,
    GladosBotNotFoundError,
    GladosError,
    GladosRequest,
    VERIFY_ROUTES,
    EventRoutes,
)


class PluginImporter:
    def __init__(self, plugins_folder: str):
        self.plugins = dict()
        self.plugins_folder = plugins_folder
        self.config_files = list()
        self.plugin_configs = dict()

    def discover_plugins(self):
        """Discover all plugin config files in the plugins folder

        Returns
        -------
        list:
            list of all yaml config files
        """
        config_files = glob.glob(f"{self.plugins_folder}/**/*.yaml", recursive=True)
        self.config_files = config_files

    def load_discovered_plugins_config(self):
        """Load all the yaml configs for the plugins"""
        logging.debug("starting import of plugins")
        for config_file in self.config_files:
            with open(config_file) as file:
                c = yaml.load(file, yaml.FullLoader)
                logging.debug(c)
                if len(c.keys()) != 1:
                    logging.critical(
                        f"zero or more than one object in config file: {config_file}"
                    )
                    continue
                c[list(c.keys())[0]]["config_file"] = config_file
                self.plugin_configs.update(c)

    def import_discovered_plugins(self, bots: Dict[str, GladosBot]):
        """Import all discovered plugins and store them in self.plugins.

        Parameters
        ----------
        bots : Dict[str, GladosBot]
            dict of all the imported bots

        Returns
        -------
        None:
            the results are updated in self.plugins

        """
        for plugin_name, plugin_config in self.plugin_configs.items():
            if not plugin_config.get("enabled", False):
                logging.warning(f"plugin {plugin_name} is disabled")
                continue
            logging.info(f"importing plugin {plugin_name}")
            # Convert the config file path into the package
            package = plugin_config.get("config_file")
            package = package.replace("/", ".")
            package = package.replace(".config.yaml", "")
            logging.debug(package)
            module = importlib.import_module(package)

            # TODO(zpriddy): Do we want to allow bots to be setup in the plugin config?
            # Check if required bot is imported
            def get_required_bot(
                bot_name: str, bots: Dict[str, GladosBot]
            ) -> Union[None, GladosBot]:
                if not bot_name:
                    raise GladosError(f"no bot name set for plugin: {plugin_name}")
                bot = bots.get(bot_name)
                if not bot:
                    logging.error(
                        f"bot: {bot_name} is not found. disabling plugin: {plugin_name}"
                    )
                    raise GladosBotNotFoundError(
                        f"bot: {bot_name} is not found as required for {plugin_name}"
                    )
                return bot

            try:
                bot = get_required_bot(plugin_config.get("bot", {}).get("name"), bots)
            except GladosError as e:
                logging.error(f"{e} :: disabling plugin: {plugin_name}")
                self.plugin_configs[plugin_name]["enabled"] = False
                continue

            plugin = getattr(module, plugin_config.get("module"))(bot, plugin_name)
            self.plugins[plugin_name] = plugin


class GladosPlugin:
    """Parent class for a GLaDOS Plugin

    Parameters
    ----------
    name : str
        the name of the plugin
    bot : GladosBot
        the GLaDOS bot that this plugin will use
    """

    def __init__(self, name: str, bot: GladosBot, **kwargs):
        self.name = name
        self.bot = bot

        self._routes = dict()  # type: Dict[int, Dict[str, GladosRoute]]

        for route in RouteType._member_names_:
            self._routes[
                RouteType[route].value
            ] = dict()  # type: Dict[str, GladosRoute]

    def add_route(
        self, route_type: RouteType, route: Union[EventRoutes, str], function: Callable
    ):
        """Add a new route to the plugin

        Parameters
        ----------
        route_type : RouteType
            what type of route this is this
        route : Union[EventRoutes, str]
            what is the route to be added
        function : Callable
            the function to be executed when this route runs

        Returns
        -------

        """
        if type(route) is EventRoutes:
            route = route.name
        new_route = GladosRoute(route_type, route, function)
        if route_type in BOT_ROUTES:
            new_route.route = f"{self.bot.name}_{route}"
        if new_route.route in self._routes[new_route.route_type.value]:
            raise GladosPathExistsError(
                f"a route with the name of {new_route.route} already exists in the route type: {new_route.route_type.name}"
            )
        self._routes[new_route.route_type.value][new_route.route] = new_route

    def send_request(self, request: GladosRequest, **kwargs):
        """This is the function to be called when sending a request to a plugin.

        This function is responsible for validating the slack signature if needed. It also returns
        and empty string if the function called returns None.

        Parameters
        ----------
        request : GladosRequest
            the request object to be sent
        kwargs :

        Returns
        -------

        """
        if request.route_type in VERIFY_ROUTES:
            self.bot.validate_slack_signature(request)
        response = self._routes[request.route_type.value][request.route].function(
            request, **kwargs
        )
        if response is None:
            # TODO(zpriddy): add logging.
            return ""
        return response

    @property
    def routes(self):
        """List all routes for the plugin.

        Returns
        -------

        """
        routes = list()
        [
            routes.extend(route_object)
            for route_object in [
                list(route.values())
                for route in [route_type for route_type in self._routes.values()]
            ]
        ]
        return routes
