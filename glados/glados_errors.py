# TODO(zpriddy): Add these errors
# RouteExistsError: route with name already exists
# RouteError: no matching route for request


class GladosError(Exception):
    """Base class for Client errors"""
    pass

class GladosRouteNotFoundError(GladosError):
    """Error raised when the requested path is not found"""
    pass

class GladosPathExistsError(GladosError):
    """Error raised when trying to add a path that already exists"""
    pass