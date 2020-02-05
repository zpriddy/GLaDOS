from slack import WebClient
from slack.web.classes.messages import Message
from slack.web.slack_response import SlackResponse
from slack.errors import SlackRequestError
import yaml
import glob
from typing import Dict, Union

import logging

from glados import GladosRequest, get_var, get_enc_var


class BotImporter:
    def __init__(self, bots_dir: str):
        logging.info(f"starting BotImporter with config dir: {bots_dir}")
        self.bots = dict()  # type: Dict[str, GladosBot]
        self._bots_yaml = dict()
        self._dir = bots_dir

    def import_bots(self):
        """Import all bots in the bots config folder

        Returns
        -------

        """
        files = glob.glob(f"{self._dir}/*.yaml")
        logging.debug(f"bot config files found: {files}")
        for f in files:
            with open(f) as file:
                self._bots_yaml.update(yaml.load(file, Loader=yaml.FullLoader))

        for bot_name, bot_config in self._bots_yaml.items():
            self.bots[bot_name] = GladosBot(name=bot_name, **bot_config)


class GladosBot:
    """ GLaDOS Bot represents all the required data and functions for a Slack bot.

    Notes
    -----
    All Slack Web API functions can be called from MyBot.client.*

    Parameters
    ----------
    name: str
        The name of the bot (URL Safe)
    token: str, Dict[str, str]
        The bot token
    signing_secret: str, Dict[str, str]
        The bot signing secret.

    Attributes
    ----------
    name: str
        The name of the bot (URL Safe)
    token: str
        The bot token
    client: WebClient
        A Slack client generated for that bot
    signing_secret: str
        The bots signing secret.

    """

    def __init__(
        self,
        token: Union[str, Dict[str, str]],
        name,
        signing_secret: Union[str, Dict[str, str]] = None,
        **kwargs,
    ):
        # Get the values from the env vars if used.
        token = self.check_for_env_vars(token)
        signing_secret = self.check_for_env_vars(signing_secret)

        self.name = name
        self.token = token
        self.client = WebClient(token=token)
        self.signing_secret = signing_secret

    def check_for_env_vars(self, value):
        """Check an input value to see if it is an env_var or enc_env_var and get the value.

        Parameters
        ----------
        value : input to check.

        Returns
        -------
        Any:
            Returns the value of the var from either the passed in value, or the env var value.
        """
        if type(value) is dict and "env_var" in value:
            var_name = value["env_var"]
            try:
                return get_var(var_name)
            except KeyError:
                logging.critical(f"missing env var: {value['env_var']}")
        if type(value) is dict and "enc_env_var" in value:
            var_name = value["enc_env_var"]
            try:
                return get_enc_var(var_name)
            except KeyError:
                logging.critical(f"missing enc env var: {value['enc_env_var']}")
        return value

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
