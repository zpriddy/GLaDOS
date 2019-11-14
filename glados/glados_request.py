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


class GladosRequest(object):
    def __init__(self, route_type: RouteType, route: str, **kwargs):
        """

        Parameters
        ----------
        route_type
        route
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
        self.route = route
        self.params = GladosParams(**kwargs)