from tests import GLADOS_CONFIG_FILE, GLADOS_CONFIG_SECTIONS, POSTGRES_HOST
from glados import GladosConfig

from os import environ

environ["POSTGRES_HOST"] = POSTGRES_HOST


def test_bad_config_file_path():
    gc = GladosConfig("blah.yaml")
    try:
        gc.read_config()
    except Exception as e:
        assert type(e) is FileNotFoundError


def test_reading_glados_config():
    gc = GladosConfig(GLADOS_CONFIG_FILE)
    gc.read_config()

    assert gc.sections == GLADOS_CONFIG_SECTIONS
    assert gc.config.glados.import_bots is True


def test_reading_glados_config_datastore():

    gc = GladosConfig(GLADOS_CONFIG_FILE)
    gc.read_config()

    assert gc.config.datastore.host == POSTGRES_HOST

    assert gc.sections == GLADOS_CONFIG_SECTIONS
    assert gc.config.glados.import_bots is True
