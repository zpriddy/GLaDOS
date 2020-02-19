from datetime import datetime

from slack.web.classes.blocks import ContextBlock, SectionBlock, DividerBlock
from slack.web.classes.messages import Message
from slack.web.classes.objects import (
    MarkdownTextObject,
    PlainTextObject,
    OptionGroup,
    Option,
)
from slack.web.classes.elements import ButtonElement, ExternalDataSelectElement
from slack.web.classes.actions import ActionButton

from glados import GladosBot, GladosPlugin, GladosRequest, RouteType, EventRoutes

from .test_plugin_views import HOME_VIEW, SECURITY_MENU_1
from .countries import COUNTRY_OPTIONS


class TestPlugin(GladosPlugin):
    def __init__(self, bot: GladosBot, name="test plugin", **kwargs):
        super().__init__(name, bot, **kwargs)

        self.add_route(RouteType.Webhook, "test_send_message", self.send_message)
        self.add_route(RouteType.Webhook, "test_update_message", self.update_message)
        self.add_route(RouteType.Events, EventRoutes.app_home_opened, self.app_home)
        self.add_route(RouteType.Slash, "security", self.slash_security)
        self.add_route(
            RouteType.Interaction, "gotoSecurityAlerts", self.action_go_to_alerts
        )
        self.add_route(RouteType.Menu, "testMenu", self.external_menu)
        self.add_route(RouteType.Events, EventRoutes.message, self.receive_message)

    def app_home(self, request: GladosRequest, **kwargs):
        # self.bot.validate_slack_signature(request)

        if request.json.event.tab == "home":
            self.bot.client.views_publish(
                user_id=request.json.event.user, view=HOME_VIEW.to_dict()
            )
        if request.json.event.tab == "messages":
            pass

    def send_message(self, request: GladosRequest, **kwargs):
        message = Message(
            text=request.json.message,
            blocks=[SectionBlock(text=MarkdownTextObject(text=request.json.message))],
        )
        return self.bot.send_message(channel=request.json.channel, message=message)

    def update_message(self, request: GladosRequest, **kwargs):
        message = Message(
            text=request.json.message,
            blocks=[
                ContextBlock(
                    elements=[
                        MarkdownTextObject(
                            text=f"Message Updated: {datetime.now().isoformat(sep=' ', timespec='minutes')}"
                        )
                    ]
                ),
                SectionBlock(text=MarkdownTextObject(text=request.json.message)),
            ],
        )
        return self.bot.update_message(
            channel=request.json.channel, ts=request.json.ts, message=message
        )

    def slash_security(self, request: GladosRequest, **kwargs):
        # self.bot.validate_slack_signature(request)

        self.bot.client.views_open(
            view=SECURITY_MENU_1, trigger_id=request.json.trigger_id
        )

    def action_go_to_alerts(self, request: GladosRequest, **kwargs):
        # self.bot.validate_slack_signature(request)
        self.bot.send_message(
            message=Message(text="Going to alerts"), channel=request.json.user.id,
        )

    def receive_message(self, request: GladosRequest, **kwargs):
        print(f"I got a message!! Message: {request.json.event.text}")

    def external_menu(self, request: GladosRequest, **kwargs):
        # self.bot.validate_slack_signature(request)

        return {"options": COUNTRY_OPTIONS}
