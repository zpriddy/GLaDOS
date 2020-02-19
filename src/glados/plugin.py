from typing import Callable, Dict, Union
import yaml
import glob
import logging
import requests

from pathlib import Path

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
    PyJSON,
)

from slack.web.classes.messages import Message
from slack.web.classes.objects import MarkdownTextObject, TextObject, PlainTextObject

SLACK_MESSAGE_TYPES = [Message, MarkdownTextObject, TextObject, PlainTextObject]


class PluginBotConfig:
    def __init__(self, name="NOT SET"):
        self.name = name

    def to_dict(self):
        return dict(name=self.name)


# TODO
# Read the plugin config
# read the user config
# running_config = plugin_config.update(user_config
class PluginConfig:
    def __init__(
        self, name, config_file, module=None, enabled=False, bot=None, **kwargs
    ):
        if not bot:
            bot = dict()
        self.name = name
        self.module = module
        self.enabled = enabled
        self.bot = PluginBotConfig(**bot)
        self.config_file = config_file
        self.config = PyJSON(kwargs)

        package = config_file.replace("/", ".")
        package = package.replace(".config.yaml", "")
        self.package = package

    def update(self, config: "PluginConfig", use_base_module: bool = True):
        """Update a config object using the default values from the config object passed in.

        Parameters
        ----------
        config : PluginConfig
            the config object to use as the base. By default the module property will be set from
            the base config object only
        use_base_module: bool
            if set true use the value of module and package from the base config object only.

        Returns
        -------

        """
        config = config.__dict__.copy()
        self_config = self.__dict__
        if use_base_module:
            self_config.pop("module")
            self_config.pop("package")
        config.update(self_config)
        self.__dict__ = config

    def to_dict(self, user_config_only=True):
        config = dict(enabled=self.enabled, bot=self.bot.to_dict())
        if not user_config_only:
            config["module"] = self.module
        return {self.name: config}

    def to_yaml(self, user_config_only=True):
        return yaml.dump(self.to_dict(user_config_only))


class PluginImporter:
    def __init__(self, plugins_folder: str, plugins_config_folder: str):
        self.plugins = dict()
        self.plugins_folder = plugins_folder
        self.plugins_config_folder = plugins_config_folder
        self.config_files = list()
        self.plugin_configs = dict()  # type: Dict[str, PluginConfig]

    def discover_plugins(self):
        """Discover all plugin config files in the plugins folder

        Returns
        -------
        list:
            list of all yaml config files
        """
        config_files = glob.glob(f"{self.plugins_folder}/**/*.yaml", recursive=True)
        self.config_files = config_files

    def load_discovered_plugins_config(self, write_to_user_config=True):
        """Load all the yaml configs for the plugins"""
        plugin_package_config = None
        plugin_user_config = None

        logging.debug("starting import of plugins")
        for config_file in self.config_files:
            # Read the plugin package config
            plugin_name = None
            with open(config_file) as file:
                c = yaml.load(file, yaml.FullLoader)
                if len(c.keys()) != 1:
                    logging.critical(
                        f"zero or more than one object in config file: {config_file}"
                    )
                    continue
                plugin_name = list(c.keys())[0]
                c[plugin_name]["config_file"] = config_file
                plugin_package_config = PluginConfig(plugin_name, **c[plugin_name])

            if plugin_name is None:
                logging.critical(
                    f"invalid or missing plugin name. config file: {config_file}"
                )
                continue

            user_config_path = Path(self.plugins_config_folder, f"{plugin_name}.yaml")

            # Write defaults to user file
            if not user_config_path.is_file() and write_to_user_config:
                with open(user_config_path, "w") as file:
                    plugin_package_config.enabled = False
                    yaml.dump(plugin_package_config.to_dict(), file)

            elif not user_config_path.is_file() and not write_to_user_config:
                logging.warning(f"no user plugin config for {plugin_name}. skipping.")
                continue

            with open(user_config_path) as file:
                c = yaml.load(file, yaml.FullLoader)

                if len(c.keys()) != 1:
                    logging.critical(
                        f"zero or more than one object in config file: {config_file}"
                    )
                    continue

                c[plugin_name]["config_file"] = str(user_config_path)
                plugin_user_config = PluginConfig(plugin_name, **c[plugin_name])
                plugin_user_config.update(plugin_package_config)
            self.plugin_configs[plugin_name] = plugin_user_config

    # TODO(zpriddy): Filter out warnings and errors if importing plugins in a limited way.

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
            if not plugin_config.enabled:
                logging.warning(f"plugin {plugin_name} is disabled")
                continue
            plugin_config.name = plugin_name
            logging.info(f"importing plugin: {plugin_name}")
            module = importlib.import_module(plugin_config.package)

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
                bot = get_required_bot(plugin_config.bot.name, bots)
            except GladosError as e:
                logging.error(f"{e} :: disabling plugin: {plugin_name}")
                self.plugin_configs[plugin_name].enabled = False
                continue

            plugin = getattr(module, plugin_config.module)(plugin_config, bot)
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

    def __init__(self, config: PluginConfig, bot: GladosBot, **kwargs):
        self.name = config.name
        self._config = config
        self.config = config.config
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

        if request.route_type is RouteType.Interaction and request.response_url:
            if type(response) is str:
                self.respond_to_url(request, response)
            if type(response) in SLACK_MESSAGE_TYPES:
                response = response.to_dict()
            if type(response) is dict:
                self.respond_to_url(request, **response)

        return response

    def respond_to_url(self, request: GladosRequest, text: str, **kwargs):
        if not request.response_url:
            logging.error("no response_url provided in request.")
            return
        kwargs["text"] = text
        r = requests.post(request.response_url, json=kwargs)
        logging.info(f"slack response: {r}")

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
