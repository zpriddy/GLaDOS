from slack.web.classes.blocks import DividerBlock, SectionBlock
from slack.web.classes.elements import ButtonElement, ExternalDataSelectElement
from slack.web.classes.messages import Message
from slack.web.classes.objects import MarkdownTextObject

from glados import EventRoutes, GladosBot, GladosPlugin, GladosRequest, RouteType
from glados.slack_classes.views import Home

HOME_VIEW = Home(
    blocks=[
        SectionBlock(text=MarkdownTextObject(text="*Welcome to GLaDOS From Lambda!*")),
        DividerBlock(),
        SectionBlock(
            text="*Security Events*",
            fields=["*New Alerts*\n20", "*Open Cases*\n5"],
            accessory=ButtonElement(
                text="Go To Security Alerts", action_id="gotoSecurityAlerts", value="go"
            ),
        ),
        DividerBlock(),
        SectionBlock(
            text="*Service Tickets*",
            fields=["*Total Tickets*\n23"],
            accessory=ButtonElement(
                text="Go To Service Desk", action_id="gotoServiceDesk", value="go"
            ),
        ),
        DividerBlock(),
        SectionBlock(
            text="Test External Menu",
            accessory=ExternalDataSelectElement(
                placeholder="Loading", action_id="testMenu"
            ),
        ),
    ]
)


class ExamplePlugin(GladosPlugin):
    def __init__(self, bot: GladosBot, name="Example Plugin", **kwargs):
        super().__init__(name, bot, **kwargs)

        self.add_route(RouteType.Webhook, "example_send_message", self.send_message)
        self.add_route(RouteType.Events, EventRoutes.app_home_opened, self.app_home)

    def send_message(self, request: GladosRequest, **kwargs):
        message = request.json.message
        channel = request.json.channel
        return self.bot.send_message(channel, Message(text=message))

    def app_home(self, request: GladosRequest, **kwargs):
        if request.json.event.tab == "home":
            self.bot.client.views_publish(
                user_id=request.json.event.user, view=HOME_VIEW.to_dict()
            )
        if request.json.event.tab == "messages":
            pass
