from enum import Enum


class RouteType(Enum):
    SendMessage = 1
    Response = 2
    Callback = 3
    Slash = 4
    Events = 5
    Interaction = 6
    Menu = 7


class EventRoutes(Enum):
    app_home_opened = 1