from glados import GladosBot, GladosPlugin
import logging


class TestPlugin3(GladosPlugin):
    def __init__(self, bot: GladosBot, name, **kwargs):
        super().__init__(name, bot, **kwargs)
        logging.info(f"plugin {self.name} imported")

    def test_function(self, echo, **kwargs):
        return echo