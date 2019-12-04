from tests import SORTED_BOT_NAMES
from glados import Glados


def test_glados_import_bots(caplog):
    g = Glados("tests/glados.yaml")
    g.read_config()
    assert len(g.bots) == 3
    assert sorted(list(g.bots.keys())) == SORTED_BOT_NAMES
