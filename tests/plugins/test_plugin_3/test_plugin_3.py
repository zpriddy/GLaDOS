from glados import GladosBot, GladosPlugin
from glados.plugin import PluginConfig
import logging


class TestPlugin3(GladosPlugin):
    def __init__(self, config: PluginConfig, bot: GladosBot, **kwargs):
        super().__init__(config, bot, **kwargs)
        logging.info(f"plugin {self.name} imported")

    def test_function(self, echo, **kwargs):
        return echo
