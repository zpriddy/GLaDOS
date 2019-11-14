from datetime import datetime

from slack.web.classes.blocks import ContextBlock, SectionBlock
from slack.web.classes.messages import Message
from slack.web.classes.objects import MarkdownTextObject

from glados import GladosBot, GladosPlugin, GladosRequest, RouteType


class TestPlugin(GladosPlugin):
    def __init__(self, name, bot: GladosBot, **kwargs):
        super().__init__(name, bot, **kwargs)

        self.add_route(RouteType.SendMessage, "test_send_message", self.send_message)
        self.add_route(RouteType.SendMessage, 'test_update_message', self.update_message)

    def send_message(self, request: GladosRequest, **kwargs):
        message = Message(text=request.params.message, blocks=[
            SectionBlock(text=MarkdownTextObject(text=request.params.message))])
        return self.bot.send_message(channel=request.params.channel, message=message)

    def update_message(self, request: GladosRequest, **kwargs):
        message = Message(text=request.params.message, blocks=[
            ContextBlock(elements=[MarkdownTextObject(
                text=f"Message Updated: {datetime.now().isoformat(sep=' ', timespec='minutes')}")]),
            SectionBlock(text=MarkdownTextObject(text=request.params.message))])
        return self.bot.update_message(channel=request.params.channel, ts=request.params.ts,
                                       message=message)
