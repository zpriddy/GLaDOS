import pytest
from glados import GladosPlugin, RouteType
from glados.errors import GladosPathExistsError


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
