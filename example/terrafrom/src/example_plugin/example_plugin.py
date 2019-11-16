from glados import GladosPlugin, GladosRequest, GladosBot, RouteType
from slack.web.classes.messages import Message
from slack.web.classes.objects import MarkdownTextObject

class ExamplePlugin(GladosPlugin):
    def __init__(self, bot: GladosBot, name="Example Plugin", **kwargs):
        super().__init__(name, bot, **kwargs)

        self.add_route(RouteType.SendMessage, "example_send_message", self.send_message)

    def send_message(self, request: GladosRequest, **kwargs):
        message = request.json.message
        channel = request.json.channel
        return self.bot.send_message(channel, Message(text=message))