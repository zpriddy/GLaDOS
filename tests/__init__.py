import logging

GLADOS_CONFIG_FILE = "tests/glados.yaml"
GLADOS_CONFIG_FILE_LIMITED = "tests/glados_limited.yaml"
GLADOS_CONFIG_SECTIONS = sorted(["datastore", "glados", "my_other_config"])

LOGGING_FORMAT = (
    "%(levelname)-8s :: [%(filename)s:%(lineno)s :: %(funcName)s() ] %(message)s"
)
logging.basicConfig(
    level=logging.DEBUG, format=LOGGING_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"
)


SORTED_BOT_NAMES = sorted(["SecurityBot", "Bot1", "Bot2", "Bot3"])
