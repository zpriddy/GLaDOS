from tests import SORTED_BOT_NAMES, GLADOS_CONFIG_FILE
from glados import Glados


def test_glados_import_bots(caplog):
    g = Glados(GLADOS_CONFIG_FILE)
    g.read_config()
    g.import_bots()
    assert len(g.bots) == len(SORTED_BOT_NAMES)
    assert sorted(list(g.bots.keys())) == SORTED_BOT_NAMES
