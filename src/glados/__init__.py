import logging as RootLogging
from logging import Logger
from pkg_resources import get_distribution

__version__ = get_distribution("glados").version

LOGGING_FORMAT = "%(levelname)-8s :: [ %(module)s.%(funcName)s:%(lineno)s ] %(message)s"
LOGGING_LEVEL = "WARNING"
RootLogging.basicConfig(
    level=RootLogging.DEBUG, format=LOGGING_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"
)

# This is for AWS
logger = RootLogging.getLogger()
logger.setLevel("DEBUG")

# This is the logger that GLaDOS will use.
logging = RootLogging.getLogger(__name__)  # type: Logger


def set_logging(level: str = None, format: str = None):
    """Set the logging format

    Parameters
    ----------
    level
        Level to set logging to
    format
        Logging format to set
    """
    if not format:
        try:
            format = logging.handlers[0].formatter._fmt
        except Exception as e:
            logging.error(f"error setting logging: {e}")
            format = LOGGING_FORMAT
    if not level:
        level = logging.level

    RootLogging.basicConfig(format=format, level=level)


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

from .configs import GladosConfig
from .utils import read_config, check_for_env_vars

from .bot import GladosBot, BotImporter
from .router import GladosRouter, GladosRoute
from .plugin import GladosPlugin, PluginImporter


from .core import Glados

# LOGGING_FORMAT = "%(asctime)s :: %(levelname)-8s :: [%(filename)s:%(lineno)s :: %(funcName)s() ] %(message)s"


__all__ = [
    "Glados",
    "GladosBot",
    "GladosRequest",
    "RouteType",
    "EventRoutes",
    "GladosPlugin",
    "GladosConfig",
    "read_config",
    "logging",
    "set_logging",
    "check_for_env_vars",
]
