from slack import WebClient
from slack.web.classes.messages import Message
from slack.web.slack_response import SlackResponse


class GladosBot(object):
    def __init__(self, token, name, **kwargs):
        self.name = name
        self.token = token
        self.client = WebClient(token=token)

    def send_message(self, channel: str, message: Message) -> SlackResponse:
        return self.client.chat_postMessage(channel=channel, as_user=True, **message.to_dict())

    def update_message(self, channel: str, ts: str, message: Message) -> SlackResponse:
        return self.client.chat_update(channel=channel, ts=ts, **message.to_dict())

    def delete_message(self, channel: str, ts: str) -> SlackResponse:
        return self.client.chat_delete(channel=channel, ts=ts)
