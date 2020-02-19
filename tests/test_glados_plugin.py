import pytest
from glados import GladosPlugin, RouteType, PluginImporter, BotImporter, GladosBot
from glados.plugin import PluginConfig
from glados.errors import GladosPathExistsError
import logging
from pathlib import Path
import os


PC_BASE_PATH = Path("tests", "plugins_config")
PC1 = Path(PC_BASE_PATH, "TestPlugin1.yaml")
PC2 = Path(PC_BASE_PATH, "TestPlugin2.yaml")
PC3 = Path(PC_BASE_PATH, "TestPlugin3.yaml")


@pytest.fixture
def MockGladosBot():
    return GladosBot("", "bot", "")


@pytest.fixture
def MockPluginConfig():
    return PluginConfig("test", "None")


@pytest.fixture
def MockGladosPlugin(MockGladosBot, MockPluginConfig):
    return GladosPlugin(MockPluginConfig, MockGladosBot)


def check_only_one_file():
    assert PC1.is_file() is True
    assert PC2.is_file() is False
    assert PC3.is_file() is False


def cleanup():
    os.remove(PC2)
    os.remove(PC3)
    check_only_one_file()


def test_cant_add_existing(MockGladosPlugin):
    def mock_function(request):
        return "something"

    MockGladosPlugin.add_route(RouteType.Webhook, "send_message", mock_function)

    assert len(MockGladosPlugin.routes) == 1

    with pytest.raises(GladosPathExistsError):
        MockGladosPlugin.add_route(RouteType.Webhook, "send_message", mock_function)


def test_add_route(MockGladosPlugin):
    assert MockGladosPlugin.routes == []

    MockGladosPlugin.add_route(RouteType.Webhook, "send_message", lambda request: True)

    assert len(MockGladosPlugin.routes) == 1

    route = MockGladosPlugin.routes[0]

    assert route.route == "bot_send_message"
    assert route.function(None)


def test_plugin_importer_discovery():
    pi = PluginImporter("tests/plugins", "tests/plugins_config")
    pi.discover_plugins()
    assert len(pi.config_files) == 3


def test_plugin_importer_load_configs():
    check_only_one_file()
    pi = PluginImporter("tests/plugins", "tests/plugins_config")
    pi.discover_plugins()
    pi.load_discovered_plugins_config()
    logging.info(pi.plugin_configs)

    assert len(pi.plugin_configs.keys()) == 3
    assert PC1.is_file() is True
    assert PC2.is_file() is True
    assert PC3.is_file() is True

    cleanup()


def test_plugin_importer_all():
    # Import all the bots
    check_only_one_file()
    bot_importer = BotImporter("tests/bots_config")
    bot_importer.import_bots()
    bots = bot_importer.bots.copy()

    # Now import all the plugins
    pi = PluginImporter("tests/plugins", "tests/plugins_config")
    pi.discover_plugins()
    pi.load_discovered_plugins_config()
    pi.import_discovered_plugins(bots)

    # Test that the plugin was installed
    assert pi.plugins["TestPlugin1"].test_function("TESTING") == "TESTING"

    # Make sure that only 1 plugin was installed
    # Plugin #2 should have been disabled
    assert len(pi.plugins) == 1
    assert pi.plugin_configs.get("TestPlugin2").enabled == False
    cleanup()
