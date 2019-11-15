from slack import WebClient
from slack.web.classes.messages import Message
from slack.web.slack_response import SlackResponse
from slack.errors import SlackRequestError

from glados import GladosRequest


class GladosBot(object):
    def __init__(self, token, name, signing_secret=None, **kwargs):
        self.name = name
        self.token = token
        self.client = WebClient(token=token)
        self.signing_secret = signing_secret

    def validate_slack_signature(self, request: GladosRequest):
        valid = self.client.validate_slack_signature(signing_secret=self.signing_secret, **request.slack_verify.json)
        if not valid:
            raise SlackRequestError("Signature of request is not valid")



    def send_message(self, channel: str, message: Message) -> SlackResponse:
        return self.client.chat_postMessage(channel=channel, as_user=True, **message.to_dict()).data

    def update_message(self, channel: str, ts: str, message: Message) -> SlackResponse:
        return self.client.chat_update(channel=channel, ts=ts, **message.to_dict()).data

    def delete_message(self, channel: str, ts: str) -> SlackResponse:
        return self.client.chat_delete(channel=channel, ts=ts).data
