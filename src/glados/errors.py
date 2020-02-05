class GladosError(Exception):
    """Base class for Client errors"""

    pass


class GladosBotNotFoundError(GladosError):
    """Error raised when GladosBot is not found"""


class GladosRouteNotFoundError(GladosError):
    """Error raised when the requested path is not found"""

    pass


class GladosPathExistsError(GladosError):
    """Error raised when trying to add a path that already exists"""

    pass
