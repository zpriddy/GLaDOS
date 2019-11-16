from glados import RouteType, BOT_ROUTES, PyJSON
from typing import Union


class SlackVerification:
    """An object to hold slack verification data

    Parameters
    ----------
    data: str
        raw request body. This is used to verify the message is from slack.
    timestamp: str
        The X-Slack-Request-Timestamp from the headers of the request. This is used to verify the message is from slack.
    signature: str
        The X-Slack-Signature from the headers of the request. This is used to verify the message is from slack.
    """

    def __init__(self, data: str, timestamp: str = None, signature: str = None):
        self.data = data
        self.timestamp = timestamp
        self.signature = signature

    @property
    def json(self) -> dict:
        return {
            "data": self.data,
            "timestamp": self.timestamp,
            "signature": self.signature,
        }


class GladosRequest:
    """GLaDOS Request Object. This holds all the data required to process the request.

    Parameters
    ----------
    route_type: RouteType
        what type of route is this
    route: str
        what is the route to be called
    slack_verify: SlackVerification
        slack data used for verifying the request came from Slack
    bot_name: str
        The name of the bot to send the request to. This is used for select RouteTypes
    json:
        the json paylod of the request
    kwargs

    Examples
    --------
    >>> request = GladosRequest(RouteType.SendMessage, "send_mock", json={"message":"my message"})
    >>> print(request.json.message)
    my message
    >>> try:
    ...    print(request.json.other_param)
    ... except AttributeError:
    ...     print("ERROR")
    ERROR
    """

    def __init__(
        self,
        route_type: RouteType,
        route: str,
        slack_verify: SlackVerification = None,
        bot_name: str = None,
        json: Union[str, dict] = None,
        **kwargs,
    ):

        if not json:
            json = dict()
        self.route_type = route_type
        self.bot_name = bot_name
        self._route = route
        self.bot_route = f"{bot_name}_{route}"
        self.slack_verify = slack_verify
        self.json = PyJSON(json)

    @property
    def route(self) -> str:
        """the actual route

        If the route automatically prefixed the route with the bot name, it will return the route with the prefix
        """
        return self.bot_route if self.route_type in BOT_ROUTES else self._route

    @route.setter
    def route(self, value):
        self._route = value
