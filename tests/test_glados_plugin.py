import pytest
from glados import GladosPlugin, RouteType, PluginImporter, BotImporter
from glados.errors import GladosPathExistsError
import logging


@pytest.fixture
def MockGladosPlugin():
    return GladosPlugin("mock", None)


def test_cant_add_existing(MockGladosPlugin):
    def mock_function(request):
        return "something"

    MockGladosPlugin.add_route(RouteType.SendMessage, "send_message", mock_function)

    assert len(MockGladosPlugin.routes) == 1

    with pytest.raises(GladosPathExistsError):
        MockGladosPlugin.add_route(RouteType.SendMessage, "send_message", mock_function)


def test_add_route(MockGladosPlugin):
    assert MockGladosPlugin.routes == []

    MockGladosPlugin.add_route(
        RouteType.SendMessage, "send_message", lambda request: True
    )

    assert len(MockGladosPlugin.routes) == 1

    route = MockGladosPlugin.routes[0]

    assert route.route == "send_message"
    assert route.function(None)


def test_plugin_importer_discovery():
    pi = PluginImporter("tests/plugins")
    pi.discover_plugins()
    assert len(pi.config_files) == 3


def test_plugin_importer_load_configs():
    pi = PluginImporter("tests/plugins")
    pi.discover_plugins()
    pi.load_discovered_plugins_config()
    logging.info(pi.plugin_configs)
    assert len(pi.plugin_configs.keys()) == 3


def test_plugin_importer_all():
    # Import all the bots
    bot_importer = BotImporter("tests/bots_config")
    bot_importer.import_bots()
    bots = bot_importer.bots.copy()

    # Now import all the plugins
    pi = PluginImporter("tests/plugins")
    pi.discover_plugins()
    pi.load_discovered_plugins_config()
    pi.import_discovered_plugins(bots)

    # Test that the plugin was installed
    assert pi.plugins["TestPlugin1"].test_function("TESTING") == "TESTING"

    # Make sure that only 1 plugin was installed
    # Plugin #2 should have been disabled
    assert len(pi.plugins) == 1
    assert pi.plugin_configs.get("TestPlugin2").get("enabled") == False
