from slack import WebClient
from slack.web.classes.messages import Message
from slack.web.slack_response import SlackResponse
from slack.errors import SlackRequestError

import logging

from glados import GladosRequest


class GladosBot:
    """ GLaDOS Bot represents all the required data and functions for a Slack bot.

    Notes
    -----
    All Slack Web API functions can be called from MyBot.client.*

    Parameters
    ----------
    name: str
        The name of the bot (URL Safe)
    token: str
        The bot token
    client: WebClient
        A Slack client generated for that bot

    Attributes
    ----------
    name: str
        The name of the bot (URL Safe)
    token: str
        The bot token
    client: WebClient
        A Slack client generated for that bot

    """

    def __init__(self, token, name, signing_secret=None, **kwargs):
        self.name = name
        self.token = token
        self.client = WebClient(token=token)
        self.signing_secret = signing_secret

    def validate_slack_signature(self, request: GladosRequest):
        valid = self.client.validate_slack_signature(
            signing_secret=self.signing_secret, **request.slack_verify.json
        )
        logging.info(f"valid payload signature from slack: {valid}")
        if not valid:
            raise SlackRequestError("Signature of request is not valid")

    def send_message(self, channel: str, message: Message) -> SlackResponse:
        """Send a message as the bot

        Parameters
        ----------
        channel : str
            channel to send the message to
        message : Message
            message object to send

        Returns
        -------

        """
        return self.client.chat_postMessage(
            channel=channel, as_user=True, **message.to_dict()
        ).data

    def update_message(self, channel: str, ts: str, message: Message) -> SlackResponse:
        """Updates a message that was sent by the bot

        Parameters
        ----------
        channel :
        ts :
        message :

        Returns
        -------

        """
        return self.client.chat_update(channel=channel, ts=ts, **message.to_dict()).data

    def delete_message(self, channel: str, ts: str) -> SlackResponse:
        """Deletes a message that was sent by a bot

        Parameters
        ----------
        channel :
        ts :

        Returns
        -------

        """
        return self.client.chat_delete(channel=channel, ts=ts).data
