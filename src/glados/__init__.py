import logging as RootLogging

from .bot import BotImporter, GladosBot
from .configs import GladosConfig, read_config
from .core import Glados
from .errors import (
    GladosBotNotFoundError,
    GladosError,
    GladosPathExistsError,
    GladosRouteNotFoundError,
)
from .plugin import GladosPlugin, PluginImporter
from .request import GladosRequest, SlackVerification
from .route_type import BOT_ROUTES, VERIFY_ROUTES, EventRoutes, RouteType
from .router import GladosRoute, GladosRouter
from .utils import PyJSON, check_for_env_vars, get_enc_var, get_var

LOGGING_FORMAT = "%(levelname)-8s :: [ %(module)s.%(funcName)s:%(lineno)s ] %(message)s"
LOGGING_LEVEL = "WARNING"
RootLogging.basicConfig(
    level=RootLogging.DEBUG, format=LOGGING_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"
)

# This is for AWS
logger = RootLogging.getLogger()
logger.setLevel("DEBUG")

# This is the logger that GLaDOS will use.
# logging = RootLogging.getLogger(__name__)  # type: Logger


# LOGGING_FORMAT = (
#     "%(levelname)-8s :: [%(filename)s:%(lineno)s :: %(funcName)s() ] %(message)s"
# )
# logging.basicConfig(
#     level=logging.DEBUG, format=LOGGING_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"
# )

__all__ = [
    "Glados",
    "GladosBot",
    "GladosRequest",
    "RouteType",
    "EventRoutes",
    "GladosPlugin",
    "GladosConfig",
    "read_config",
    "check_for_env_vars",
]
