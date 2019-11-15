from glados import RouteType


class GladosParams(object):
    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            self.add_param(name, value)

    def add_param(self, name, value):
        self.__setattr__(name, value)

    def __getattr__(self, item):
        try:
            return super().__getattribute__(item)
        finally:
            return None


class SlackVerification():
    def __init__(self, data: str, timestamp: str = None, signature: str = None):
        """

        Parameters
        ----------
        data: str
            raw request body. This is used to verify the message is from slack.
        timestamp: str
            The X-Slack-Request-Timestamp from the headers of the request. This is used to verify the message is from slack.
        signature: str
            The X-Slack-Signature from the headers of the request. This is used to verify the message is from slack.
        """
        self.data = data
        self.timestamp = timestamp
        self.signature = signature

    @property
    def json(self):
        return {
            "data":      self.data,
            "timestamp": self.timestamp,
            "signature": self.signature
        }


class GladosRequest(object):
    def __init__(self, route_type: RouteType, route: str, slack_verify: SlackVerification = None,
                 bot_name: str = None, **kwargs):
        """

        Parameters
        ----------
        route_type
        route
        slack_verify: SlackVerification
            slack data used for verifying the request came from Slack
        bot_name: str
            The name of the bot to send the request to. This is used for select RouteTypes
        kwargs

        Examples
        --------
        >>> request = GladosRequest(RouteType.SendMessage, "send_mock", message="my message")
        >>> print(request.params.message)
        my message
        >>> print(request.params.other_param)
        None
        """
        self.route_type = route_type
        self.bot_name = bot_name
        self._route = route
        self.bot_route = f"{bot_name}_{route}"
        self.params = GladosParams(**kwargs)
        self.slack_verify = slack_verify

    @property
    def route(self):
        return self.bot_route if self.route_type in [RouteType.Events] else self._route

    @route.setter
    def route(self, value):
        self._route = value
