from typing import Callable, Dict, List, NoReturn, Optional

from glados import GladosRequest, RouteType, GladosRouteNotFoundError


class GladosRoute(object):
    """Represents a single route"""

    def __init__(self, route_type: RouteType, route: str, function: Callable):
        self.route_type = route_type
        self.route = route
        self.function = function


class GladosRouter(object):
    def __init__(self, **kwargs):
        # routes are stored as: {RouteType.SendMessage: {"ask_user",ask_user, "confirm":confirm}}
        self.routes = dict()  # type: Dict[RouteType, Dict[str, GladosRoute]]
        for route in RouteType._member_names_:
            self.routes[RouteType[route].value] = dict()  # type: Dict[str, GladosRoute]

    def add_route(self, route: GladosRoute) -> NoReturn:
        """Add a route to the router

        Parameters
        ----------
        route: GladosRoute
            the route to be added

        Raises
        ------
        KeyError
            a route with the same type and same name already exists

        """
        # print(f"Adding route: {route.__dict__}")
        if route.route in self.routes[route.route_type.value]:
            # TODO(zpriddy): Add custom errors to GLaDOS and raise a RouteExistsError
            raise KeyError(
                    f"a route with the name of {route.route} already exists in the route type: {route.route_type.name}")
        self.routes[route.route_type.value][route.route] = route

    def add_routes(self, routes: List[GladosRoute]):
        """Add multiple routes to the router.

        Parameters
        ----------
        routes : List[GladosRoute]
            a list with the routes to be added

        Returns
        -------

        """
        for route in routes:
            self.add_route(route)

    def get_route(self, route_type: RouteType, route: str) -> Optional[GladosRoute]:
        """Get a GladosRoute object for the requested route.

        Parameters
        ----------
        route_type: RouteType
            the type of route to get
        route: str
            the route to get

        Returns
        -------
        GladosRoute
            return the request route

        Raises
        ------
        GladosRouteNotFoundError
            the requested route is not found
        """
        if not self.routes[route_type.value].get(route):
            raise GladosRouteNotFoundError(
                    f"no route with the name of {route} exists in route type: {route_type.name}")
        return self.routes[route_type.value][route]

    def route_function(self, route_type: RouteType, route: str) -> Callable:
        """Return only the callable function for the requested GladosRoute.

        Parameters
        ----------
        route_type: RouteType
            the type of route to get
        route: str
            the route to get

        Returns
        -------
        Callable
            return the requested routes callable function

        """
        return self.get_route(route_type, route).function

    def exec_route(self, request: GladosRequest):
        """Execute a route function directly

        Parameters
        ----------
        request: GladosRequest
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
        return self.route_function(request.route_type, request.route)(request)
