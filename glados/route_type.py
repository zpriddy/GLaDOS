from enum import Enum

class RouteType(Enum):
    SendMessage = 1
    Response = 2
    Callback = 3
    Slash = 4
    