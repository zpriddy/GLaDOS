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

from glados.slack_classes.views import Home


HOME_VIEW = Home(
    blocks=[
        SectionBlock(text=MarkdownTextObject(text="*Welcome to GLaDOS!*")),
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

SECURITY_MENU_1 = {
    "type": "modal",
    "title": PlainTextObject(text="Security Help Center").to_dict(),
    "blocks": [
        SectionBlock(
            text="*Travel Request*",
            accessory=ButtonElement(
                text="File new travel request",
                action_id="fileTravelRequest",
                value="go",
            ),
        ).to_dict(),
        DividerBlock().to_dict(),
    ],
}
