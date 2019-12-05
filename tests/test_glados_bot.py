import pytest
from tests import SORTED_BOT_NAMES
from glados import BotImporter


def test_import_bots():
    bot_importer = BotImporter("tests/bots_config")
    bot_importer.import_bots()
    assert sorted(list(bot_importer.bots.keys())) == SORTED_BOT_NAMES
    assert bot_importer.bots["SecurityBot"].token == "my-bot-api-token"
    assert bot_importer.bots["SecurityBot"].signing_secret == "test_signing_secret"
    assert bot_importer.bots["Bot1"].token == "bot-1-api-token"
    assert bot_importer.bots["Bot2"].signing_secret == "bot_2_signing_secret"
