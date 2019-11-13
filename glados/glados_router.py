from typing import Dict, Callable, NoReturn, Optional, List
from enum import Enum


class RouteType(Enum):
    SendMessage = 1
    Response = 2
    Callback = 3
    Slash = 4


class GladosRoute(object):
    def __init__(self, route_type: RouteType, route: str, function: Callable):
        self.route_type = route_type
        self.route = route
        self.function = function


class GladosRouter(object):
    def __init__(self, **kwargs):
        # routes are stored as: {RouteType.SendMessage: {"ask_user",ask_user, "confirm":confirm}}
        self.routes = dict()  # type: Dict[RouteType, Dict[str, GladosRoute]]
        for route in RouteType._member_names_:
            self.routes[RouteType[route]] = dict()  # type: Dict[str, GladosRoute]

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
        if route.route in self.routes[route.route_type]:
            # TODO(zpriddy): Add custom errors to GLaDOS and raise a RouteExistsError
            raise KeyError(
                    f"a route with the name of {route.route} already exists in the route type: {route.route_type.name}")
        self.routes[route.route_type][route.route] = route

    def add_routes(self, routes: List[GladosRoute]):
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
        KeyError
            the requested route is not found
        """
        if not self.routes[route_type].get(route):
            # TODO(zpriddy): Add custom errors to GLaDOS and raise a RouteError
            raise KeyError(
                    f"no route with the name of {route} exists in route type: {route_type.name}")
        return self.routes[route_type][route]

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

    def exec_route(self, route_type: RouteType, route: str, **kwargs) -> bool:
        """Execute a route function directly

        Examples
        ----------
        >>> def mock_function(message):
        ...     print(f"Mock Function: {message}")
        ...     return True
        >>> router = GladosRouter()
        >>> route = GladosRoute(RouteType.SendMessage, "send_mock", mock_function)
        >>> router.add_route(route)
        >>> successful = router.exec_route(RouteType.SendMessage, "send_mock", message="Hello World!")
        Mock Function: Hello World!
        >>> print(successful)
        True

        >>> def mock_function(message):
        ...     print(f"Mock Function: {message}")
        ...     return True
        >>> router = GladosRouter()
        >>> route = GladosRoute(RouteType.SendMessage, "send_mock", mock_function)
        >>> router.add_route(route)
        >>> successful = router.exec_route(RouteType.SendMessage, "send", message="Hello World!")
        >>> print(successful)
        False



        Parameters
        ----------
        route_type: RouteType
            what type of route to execute
        route: str
            what is the route/path to execute
        kwargs:
            the arguments to pass into the plugin function
            # TODO(zpriddy): Replace this with a request object?

        Returns
        -------
        bool:
            Did the function execute successfully
        """
        try:
            return self.route_function(route_type, route)(**kwargs)
        except KeyError as e:
            # TODO(zpriddy): Replace this with logging.
            print("Error calling route function")
            print(str(e))
            return False
