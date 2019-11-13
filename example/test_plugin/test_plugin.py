from slack.web.classes.blocks import SectionBlock
from slack.web.classes.messages import Message
from slack.web.classes.objects import MarkdownTextObject

from glados.glados_bot import GladosBot
from glados.glados_plugin import GladosPlugin
from glados.glados_request import GladosRequest
from glados.glados_router import RouteType


class TestPlugin(GladosPlugin):
    def __init__(self, name, bot: GladosBot, **kwargs):
        super().__init__(name, bot, **kwargs)

        self.add_route(RouteType.SendMessage, "test_send_message", self.send_message)

    def send_message(self, request: GladosRequest, **kwargs):
        message = Message(text=request.params.message, blocks=[
            SectionBlock(text=MarkdownTextObject(text=request.params.message))])
        return self.bot.send_message(channel=request.params.channel, message=message)
