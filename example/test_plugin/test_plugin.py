from datetime import datetime

from slack.web.classes.blocks import ContextBlock, SectionBlock, DividerBlock
from slack.web.classes.messages import Message
from slack.web.classes.objects import MarkdownTextObject, PlainTextObject, OptionGroup, Option
from slack.web.classes.elements import ButtonElement, ExternalDataSelectElement
from slack.web.classes.actions import ActionButton

from glados import GladosBot, GladosPlugin, GladosRequest, RouteType, EventRoutes
from glados.message_blocks import ModalBuilder


class TestPlugin(GladosPlugin):
    def __init__(self, name, bot: GladosBot, **kwargs):
        super().__init__(name, bot, **kwargs)

        self.add_route(RouteType.SendMessage, "test_send_message", self.send_message)
        self.add_route(RouteType.SendMessage, 'test_update_message', self.update_message)
        self.add_route(RouteType.Events, EventRoutes.app_home_opened.name, self.app_home)
        self.add_route(RouteType.Slash, "security", self.slash_security)
        self.add_route(RouteType.Interaction, "gotoSecurityAlerts", self.action_go_to_alerts)
        self.add_route(RouteType.Menu, "testMenu", self.external_menu)

    def app_home(self, request: GladosRequest, **kwargs):
        print("AppHome")
        self.bot.validate_slack_signature(request)
        # modal =  ModalBuilder()
        # modal.title("Welcome to Glados!")
        # modal.close("The cake is a lie...")
        # modal.section(text=MarkdownTextObject(text="# Welcome to GLaDOS"))
        # import json
        # print(json.dumps(modal.to_dict(), indent=4))
        home = {
            "type":   "home",
            "blocks": [
                SectionBlock(text=MarkdownTextObject(text="*Welcome to GLaDOS*")).to_dict(),
                DividerBlock().to_dict(),
                SectionBlock(text="*Security Events*",
                             fields=["*New Alerts*\n20",
                                     "*Open Cases*\n5"],
                             accessory=ButtonElement(text="Go To Security Alerts",
                                                     action_id="gotoSecurityAlerts",
                                                     value="go")
                             ).to_dict(),
                DividerBlock().to_dict(),
                SectionBlock(text="*Service Tickets*",
                             fields=["*Total Tickets*\n23"],
                             accessory=ButtonElement(text="Go To Service Desk",
                                                     action_id="gotoServiceDesk",
                                                     value="go")).to_dict(),
                DividerBlock().to_dict(),
                SectionBlock(text="Test External Menu", accessory=ExternalDataSelectElement(placeholder="Loading", action_id="testMenu")).to_dict()
            ]
        }
        self.bot.client.views_publish(user_id=request.params.event.get("user"), view=home)
        return ""

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

    def slash_security(self, request: GladosRequest, **kwargs):
        home = {
            "type":   "modal",
            "title": PlainTextObject(text="Security Help Center").to_dict(),
            "blocks": [
                SectionBlock(text="*Travel Request*",
                             accessory=ButtonElement(text="File new travel request",
                                                     action_id="fileTravelRequest",
                                                     value="go")
                             ).to_dict(),
                DividerBlock().to_dict()
            ]
        }

        self.bot.client.views_open(view=home, trigger_id=request.params.trigger_id)
        return ""

    def action_go_to_alerts(self, request: GladosRequest, **kwargs):
        print("GO TO ALERTS")
        self.bot.send_message(message=Message(text="Going to alerts"), channel=request.params.user.get("id"))
        return ""

    def external_menu(self, request: GladosRequest, **kwargs):
        return {"options": [Option(label="Option 1", value="option1").to_dict(),
                            Option(label="Option 2", value="option2").to_dict()]}
