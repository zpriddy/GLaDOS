from tests import SORTED_BOT_NAMES, GLADOS_CONFIG_FILE, GLADOS_CONFIG_FILE_LIMITED
from glados import Glados


def test_glados_import_bots(caplog):
    g = Glados(GLADOS_CONFIG_FILE)
    g.read_config()
    g.import_bots()
    assert len(g.bots) == len(SORTED_BOT_NAMES)
    assert sorted(list(g.bots.keys())) == SORTED_BOT_NAMES


def test_import_limited_bots_only(caplog):
    g = Glados(GLADOS_CONFIG_FILE_LIMITED)
    g.read_config(bot_name=SORTED_BOT_NAMES[0])
    assert len(g.plugins) == 1
