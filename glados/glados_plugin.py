from glados_bot import GladosBot
from glados_router import RouteType, GladosRoute
from typing import Dict, Callable


class GladosPlugin(object):
    def __init__(self, name, bot: GladosBot, **kwargs):
        self.name = name
        self.bot = bot

        self._routes = dict()  # type: Dict[RouteType, Dict[str, GladosRoute]]

        for route in RouteType._member_names_:
            self._routes[RouteType[route].value] = dict()  # type: Dict[str, GladosRoute]

    def add_route(self, route_type: RouteType, route: str, function: Callable):
        new_route = GladosRoute(route_type, route, function)
        if new_route.route in self._routes[new_route.route_type.value]:
            # TODO(zpriddy): Add custom errors to GLaDOS and raise a RouteExistsError
            raise KeyError(
                    f"a route with the name of {new_route.route} already exists in the route type: {new_route.route_type.name}")
        self._routes[new_route.route_type.value][new_route.route] = new_route

    @property
    def routes(self):
        """

        Examples
        --------
        >>> from glados_plugin import GladosPlugin
        >>> from glados_router import RouteType, GladosRoute
        >>> plugin = GladosPlugin("mockPlugin", None)
        >>> plugin.routes
        []
        >>> plugin.add_route(RouteType.SendMessage, "send_message", (lambda x: 1))
        >>> r = plugin.routes[0] # type: GladosRoute
        >>> r.route == "send_message"
        True
        >>> r.function("NULL")
        1

        Returns
        -------

        """
        routes = list()
        [routes.extend(route_object) for route_object in
         [list(route.values()) for route in [route_type for route_type in self._routes.values()]]]
        return routes
