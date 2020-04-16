import logging
from typing import Callable, Dict, List, NoReturn, Optional, TYPE_CHECKING

from glados import GladosRequest, GladosRouteNotFoundError, RouteType

if TYPE_CHECKING:
    from glados import GladosPlugin


class GladosRoute(object):
    """Represents a single route"""

    def __init__(self, route_type: RouteType, route: str, function: Callable):
        self.route_type = route_type
        self.route = route
        self.function = function

    def __repr__(self):
        return f"<GladosRoute| route: {self.route} | route type: {self.route_type.name} | function: {self.function.__name__} >"


class GladosRouter(object):
    """GladosRouter"""
    def __init__(self, **kwargs):
        # routes are stored as: {RouteType.SendMessage: {"ask_user",ask_user, "confirm":confirm}}
        self.routes = dict()  # type: Dict[RouteType, Dict[str, Callable]]
        for route in RouteType._member_names_:
            self.routes[RouteType[route].value] = dict()  # type: Dict[str, Callable]

    def add_route(self, plugin: "GladosPlugin", route: GladosRoute) -> NoReturn:
        """Add a route to the router

        Parameters
        ----------
        plugin
            the plugin the route belongs to
        route
            the route to be added

        Raises
        ------
        KeyError
            a route with the same type and same name already exists

        """
        logging.debug(f"adding route: {route}")
        if route.route in self.routes[route.route_type.value]:
            raise KeyError(
                f"a route with the name of {route.route} already exists in the route type: {route.route_type.name}"
            )
        self.routes[route.route_type.value][route.route] = plugin.send_request

    def add_routes(self, plugin: "GladosPlugin") -> NoReturn:
        """Add multiple routes to the router.

        Parameters
        ----------
        routes
            the plugin to add routes from

        """
        for route in plugin.routes:
            self.add_route(plugin, route)

    def get_route(self, route_type: RouteType, route: str) -> Callable:
        """Get a GladosRoute object for the requested route.

        Parameters
        ----------
        route_type
            the type of route to get
        route
            the route to get

        Raises
        ------
        GladosRouteNotFoundError
            the requested route is not found
        """
        if not self.routes[route_type.value].get(route):
            raise GladosRouteNotFoundError(
                f"no route with the name of {route} exists in route type: {route_type.name}"
            )
        return self.routes[route_type.value][route]

    def route_function(self, route_type: RouteType, route: str) -> Callable:
        """Return only the callable function for the requested GladosRoute.

        Parameters
        ----------
        route_type
            the type of route to get
        route
            the route to get

        Returns
        -------
        Callable
            return the requested routes callable function

        """
        return self.get_route(route_type, route)

    def exec_route(self, request: GladosRequest):
        """Execute a route function directly

        Parameters
        ----------
        request
            the GLaDOS request

        Returns
        -------
            the data returned by the plugin

        Examples
        ----------
        >>> def mock_function(request: GladosRequest):
        ...     print(f"Mock Function: {request.params.message}")
        ...     return True
        >>> router = GladosRouter()
        >>> route = GladosRoute(RouteType.SendMessage, "send_mock", mock_function)
        >>> router.add_route(route)
        >>> request = GladosRequest(RouteType.SendMessage, "send_mock", message="Hello World!")
        >>> successful = router.exec_route(request)
        Mock Function: Hello World!
        >>> print(successful)
        True

        >>> def mock_function(request: GladosRequest):
        ...     print(f"Mock Function: {request.params.message}")
        ...     return True
        >>> router = GladosRouter()
        >>> route = GladosRoute(RouteType.SendMessage, "send_mock", mock_function)
        >>> router.add_route(route)
        >>> request = GladosRequest(RouteType.SendMessage, "send_mock_fail", message="Hello World!")
        >>> successful = router.exec_route(request)
        >>> print(successful)
        False
        """
        logging.debug(f"calling route function for {request.route}")
        return self.route_function(request.route_type, request.route)(request)
