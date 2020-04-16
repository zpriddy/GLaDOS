import logging
from .utils import PyJSON, get_var, get_enc_var

from .db import DataStore, DataStoreInteraction
from .route_type import RouteType, EventRoutes, BOT_ROUTES, VERIFY_ROUTES
from .request import GladosRequest, SlackVerification
from .errors import (
    GladosPathExistsError,
    GladosRouteNotFoundError,
    GladosBotNotFoundError,
    GladosError,
)

from .bot import GladosBot, BotImporter
from .router import GladosRouter, GladosRoute
from .plugin import GladosPlugin, PluginImporter

from .configs import GladosConfig
from .utils import read_config


from .core import Glados

# LOGGING_FORMAT = "%(asctime)s :: %(levelname)-8s :: [%(filename)s:%(lineno)s :: %(funcName)s() ] %(message)s"
LOGGING_FORMAT = (
    "%(levelname)-8s :: [%(filename)s:%(lineno)s :: %(funcName)s() ] %(message)s"
)
logging.basicConfig(
    level=logging.DEBUG, format=LOGGING_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"
)


__all__ = [
    "Glados",
    "GladosBot",
    "GladosRequest",
    "RouteType",
    "EventRoutes",
    "GladosPlugin",
    "GladosConfig",
    "read_config",
]
