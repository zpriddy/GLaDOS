from glados import GladosRequest, RouteType


def test_it():
    request = GladosRequest(
        RouteType.Webhook, "send_mock", json={"message": "my message"}
    )
    assert request.json.message == "my message"
