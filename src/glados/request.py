from glados import RouteType, BOT_ROUTES, PyJSON, DataStoreInteraction, DataStore
from typing import Union, Optional, TYPE_CHECKING, NoReturn
import json
import logging
from datetime import datetime

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class SlackVerification:
    """An object to hold slack verification data

    Parameters
    ----------
    data
        raw request body. This is used to verify the message is from slack.
    timestamp
        The X-Slack-Request-Timestamp from the headers of the request. This is used to verify the message is from slack.
    signature:
        The X-Slack-Signature from the headers of the request. This is used to verify the message is from slack.
    """

    def __init__(self, data: str, timestamp: str = None, signature: str = None):
        self.data = data
        self.timestamp = timestamp
        self.signature = signature

    @property
    def json(self) -> dict:
        """Returns the dict of the SlackVerification"""
        return {
            "data": self.data,
            "timestamp": self.timestamp,
            "signature": self.signature,
        }


class GladosRequest:
    """GLaDOS Request Object. This holds all the data required to process the request.

    Parameters
    ----------
    route_type
        what type of route is this
    route
        what is the route to be called
    slack_verify
        slack data used for verifying the request came from Slack
    bot_name
        The name of the bot to send the request to. This is used for select RouteTypes
    json
        the json paylod of the request
    data
        data to send with the request. This should be from a database
    kwargs

    Examples
    --------
    >>> request = GladosRequest(RouteType.SendMessage, "send_mock", json={"message":"my message"})
    >>> print(request.json.message)
    my message
    >>> try:
    ...    print(request.json.other_param)
    ... except AttributeError:
    ...     print("ERROR")
    ERROR
    """

    def __init__(
        self,
        route_type: RouteType,
        route: str = None,
        slack_verify: SlackVerification = None,
        bot_name: str = None,
        json: Union[str, dict] = None,
        data: dict = None,
        **kwargs,
    ):

        if not json:
            json = dict()

        self.json = PyJSON(json)
        self.route_type = route_type
        self.bot_name = bot_name
        self._route = route
        self.slack_verify = slack_verify
        self.response_url = None
        self.trigger_id = None

        self._data = data

        self._datastore = None  #  type: Optional[DataStore]
        self._session = (
            None
        )  # type: Optional[Session] # This is the datastore session for this request.
        self._interaction = None  #  type: Optional[DataStoreInteraction] # This is the interaction database object for this request.
        self.auto_link = False  # if this is true, then it will expect the response from the plugin to want to try to autolink to the interaction datastore.

        if route_type is RouteType.Interaction:
            self.response_url = self.json.get("response_url")
            self.trigger_id = self.json.get("trigger_id")

        if route_type is RouteType.Menu:
            self._route = self.json.action_id
        if route_type is RouteType.Interaction:
            self._route = self.json.actions[0].action_id
        if route_type is RouteType.Events:
            self._route = self.json.event.type

        self.new_interaction = None

    @property
    def route(self) -> str:
        """the actual route

        If the route automatically prefixed the route with the bot name, it will return the route with the prefix
        """
        return (
            f"{self.bot_name}_{self._route}"
            if self.route_type in BOT_ROUTES
            else self._route
        )

    @route.setter
    def route(self, value):
        self._route = value

    def set_session(self, session: "Session") -> NoReturn:
        """Set the session for this request.

        Parameters
        ----------
        session
            session to use for this request.

        Raises
        ------
        :obj: `ConnectionError`
            If the session is not active raise a ConnectionError
        """
        self._session = session
        if not self._session.is_active:
            raise ConnectionError("request session is not active")

    def set_datastore(self, datastore: "DataStore") -> NoReturn:
        """Set the Datastore and session for the request.

        Parameters
        ----------
        datastore
            Datastore to use. This datastore will be used to create the session.

        """
        self._datastore = datastore
        self.set_session(self._datastore.create_session())

    def set_interaction_from_datastore(self) -> NoReturn:
        """Get the interaction object from the datastore."""
        # Get the interaction object from the datastore
        # see if there is channel and message ts in the payload.
        if not self._session:
            raise ConnectionError("session not set for request")

        container_payload = self.json.get("container")
        if not container_payload:
            logging.warning(f"no container block in body: {self.json.to_dict()}")
            self._interaction = None
            return self.interaction

        channel = container_payload.get("channel_id")
        message_ts = container_payload.get("message_ts")

        if None in [channel, message_ts]:
            logging.warning(
                f"missing channel_id or message_ts in container: {container_payload}"
            )
            self._interaction = None
            return self.interaction

        interaction = self._datastore.find_interaction_by_channel_ts(
            channel, message_ts, self._session
        )
        self._interaction = interaction

    def add_interaction_to_datastore(
        self, interaction: DataStoreInteraction
    ) -> Optional[DataStoreInteraction]:
        """Add an interaction to the datastore and return the updated interaction.

        Notes
        -----
        The interaction_id can be retrieved by doing interaction.interaction_id

        Parameters
        ----------
        interaction
            the interaction to be added
        """
        if not self._datastore:
            logging.warning("datastore not set for request")
            return
        if not self._session:
            raise ConnectionError("session not set for request")
        return self._datastore.insert_interaction(interaction, self._session)

    def link_interaction_to_message_response(
        self, interaction_id: str, message_response: dict
    ) -> NoReturn:
        """Link interaction to message response

        Parameters
        ----------
        interaction_id
            interaction ID to be linked
        message_response
            JSON payload response from sending message on slack.
        """
        if not self._session:
            raise ConnectionError("session not set for request")

        self._datastore.link_to_message_response(
            interaction_id, message_response, self._session
        )

    def link_interaction_to_message(
        self, interaction_id: str, channel: str, message_ts: datetime
    ) -> NoReturn:
        """Link interaction to message

        Parameters
        ----------
        interaction_id
            interaction ID to link
        channel
            channel to be linked to
        message_ts
            ts to be linked to

        Returns
        -------

        """
        if not self._session:
            raise ConnectionError("session not set for request")
        self._datastore.link_to_message(
            interaction_id, channel, message_ts, self._session
        )

    def close_session(self) -> NoReturn:
        """Close session for request"""
        if not self._session or not self._session.is_active:
            self._session.close()

    def rollback_session(self) -> NoReturn:
        """Rollback the session."""
        if self._session.is_active:
            self._session.rollback()

    def has_interaction(self) -> bool:
        """Check if request has interaction.        """
        return True if self.interaction else False

    def has_new_interaction(self) -> bool:
        """check if request has a new interaction object."""
        return True if self.new_interaction else False

    def gen_new_interaction(
        self,
        *,
        followup_action=None,
        followup_ts=None,
        ttl=None,
        data=None,
        auto_link: bool = True,
        auto_set: bool = True,
    ) -> DataStoreInteraction:
        """Generate a new interaction object and set it as new_interaction.

        Parameters
        ----------
        followup_action
        followup_ts
        ttl
        data
        auto_link
            set this request to auto-link using the return payload. The return payload must be the response from sending a slack message.
        auto_set
            set this new interaction object as the request new_interaction
        """
        if not data:
            data = dict()

        self.auto_link = auto_link

        new_interaction = DataStoreInteraction(
            bot=self.bot_name,
            followup_action=followup_action,
            followup_ts=followup_ts,
            ttl=ttl,
            data=data,
        )

        if auto_set:
            self.new_interaction = new_interaction
            return self.new_interaction

        return new_interaction

    @property
    def interaction_id(self) -> Optional[str]:
        """Returns the interaction_id of request.interaction"""
        if not self.has_interaction():
            return None
        return self.interaction.interaction_id

    @property
    def interaction(self) -> Optional[DataStoreInteraction]:
        """Returns the interaction for the request"""
        if not self.has_interaction():
            return None
        return self.interaction

    @property
    def data(self) -> PyJSON:
        """Returns the data object of the request"""
        return PyJSON(self._data)

    @property
    def data_blob(self) -> dict:
        """Returns the raw dict of the data object"""
        return self._data

    @data.setter
    def data(self, value):
        if type(value) is str:
            try:
                self._data = json.loads(value)
            except json.JSONDecodeError:
                logging.error(f"JSONDecodeError on string {value}")
            except Exception as e:
                logging.error(f"{e} on parsing JSON from: {value}")
        if type(value) is dict:
            self._data = value
