from typing import Callable, Dict

from glados import GladosBot, RouteType, GladosRoute, BOT_ROUTES, GladosPathExistsError


class GladosPlugin():
    """Parent class for a GLaDOS Plugin"""

    def __init__(self, name: str, bot: GladosBot, **kwargs):
        """

        Parameters
        ----------
        name : str
            the name of the plugin
        bot : GladosBot
            the GLaDOS bot that this plugin will use
        kwargs :

        Examples
        --------
        >>> def mock_function(request):
        ...     print("Mock Function")
        >>> plugin = GladosPlugin("mock", None)
        >>> plugin.add_route(RouteType.SendMessage, "send_message", mock_function)
        >>> from glados import GladosRoute
        >>> plugin.routes[0].__dict__ == GladosRoute(RouteType.SendMessage, "send_message", mock_function).__dict__
        True
        >>> try:
        ...     plugin.add_route(RouteType.SendMessage, "send_message", mock_function)
        ... except GladosPathExistsError:
        ...     print("Got Error")
        Got Error
        """
        """"""
        self.name = name
        self.bot = bot

        self._routes = dict()  # type: Dict[int, Dict[str, GladosRoute]]

        for route in RouteType._member_names_:
            self._routes[RouteType[route].value] = dict()  # type: Dict[str, GladosRoute]

    def add_route(self, route_type: RouteType, route: str, function: Callable):
        """Add a new route to the plugin

        Parameters
        ----------
        route_type : RouteType
            what type of route this is this
        route : ste
            what is the route to be added
        function : Callable
            the function to be executed when this route runs

        Returns
        -------

        """
        new_route = GladosRoute(route_type, route, function)
        if route_type in BOT_ROUTES:
            new_route.route = f"{self.bot.name}_{route}"
        if new_route.route in self._routes[new_route.route_type.value]:
            raise GladosPathExistsError(
                    f"a route with the name of {new_route.route} already exists in the route type: {new_route.route_type.name}")
        self._routes[new_route.route_type.value][new_route.route] = new_route

    @property
    def routes(self):
        """List all routes for the plugin.

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
