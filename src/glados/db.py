import logging
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, create_engine
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query, Session, sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound

Metadata = MetaData()
Base = declarative_base(metadata=Metadata)

TABLE_INTERACTIONS = "interactions"


class DataStoreInteraction(Base):
    """DataStoreInteraction represents a row in the datastore. This is used to update data in the datastore.

    Attributes
    ----------
    interaction_id: str
        This is the primary key of the datastore. This is the ID of the entry in the datastore.
    ts: datetime
        This is the time the row was put into the database.
    bot: str
        This is the name of the bot it should use when completing followup actions.
    data: dict
        Any extra data stored with the interaction. This is a JSON blob.
    message_channel: str
        The channel that this interaction was sent to.
    message_ts: datetime
        The message timestamp when this interaction was sent.
    ttl: int
        How long this interaction should live for.
    followup_ts: datetime
        When should the follow up action happen.
    followup_action: str
        The action name to execute when following up. If None then no action will happen.
    cron_followup_action: str
        The action name to execute on a normal cron schedule like every 5 min. If None then no action will happen.
    followed_up: datetime
        This is the time when the action was followed up at. If it has not happened yet this value will be None.
    """

    __tablename__ = TABLE_INTERACTIONS
    interaction_id = Column(UUID, primary_key=True, default=str(uuid4()))
    ts = Column(DateTime, default=datetime.now())
    bot = Column(String, nullable=False)
    data = Column(JSONB, default=dict())
    message_channel = Column(String, default=None)
    message_ts = Column(DateTime, default=None)
    ttl = Column(Integer, default=None)
    followup_ts = Column(DateTime, default=None)
    followup_action = Column(String, default=None)
    cron_followup_action = Column(String, default=None)
    followed_up = Column(DateTime, default=None)

    def update(self, **kwargs):
        """Update the object dropping any arguments that are not valid"""
        for k, v in kwargs:
            if hasattr(self, k):
                setattr(self, k, v)


class DataStore:
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 5432,
        database: str = "glados",
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database

        self.db = create_engine(
            f"postgres://{self.username}:{self.password}@{self.host}:{self.port}/"
            f"{self.database}"
        )
        self.session_maker = sessionmaker(self.db)

    def create_session(self) -> Session:
        """Generate a new session with the existing connection.

        Returns
        -------
        Session:
            the session that was generated
        """
        return self.session_maker()

    def table_exists(self, table=TABLE_INTERACTIONS) -> bool:
        """Check to see if the GLaDOS table is found in postgres.

        Returns
        -------
        bool:
            True if the table is found. False if it is not found.

        """
        return table in self.db.table_names()

    def drop_table(self, table=TABLE_INTERACTIONS, force=False):
        """Drop the GLaDOS table so that it can be re-created.

        Returns
        -------
        bool:
            was the drop table successful.
        """
        Table(table, Metadata).drop(self.db, checkfirst=not force)

    def create_table(self, tables: Optional[List[str]] = None, force=False):
        """Create the table.

        If you set force to True then it will drop the existing tables and
        then recreate them. ALL DATA WILL BE LOST

        Parameters
        ----------
        tables : Optional[List[str]]
            only take action on these tables. If None, then take action on all tables
        force : bool
            drop existing tables and rebuild. (default: False)

        Returns
        -------

        """
        if force:
            if tables:
                for table in tables:
                    self.drop_table(table)
            else:
                Base.metadata.drop_all(self.db, checkfirst=False)

        if tables:
            for table in tables:
                Table(table, Metadata).create(self.db)
        else:
            Metadata.create_all(self.db)

    def find_by_id(self, interaction_id: str, session: Session) -> DataStoreInteraction:
        """Find an interaction by interaction_id.

        Parameters
        ----------
        interaction_id : str
            interaction ID to find
        session : Session
            session to be used

        Returns
        -------
        DataStore :
            The interaction object

        """
        result = session.query(DataStoreInteraction).get(interaction_id)
        return result

    def update_interaction(
        self, interaction_id, session: Session, **kwargs
    ) -> DataStoreInteraction:
        """Find and update an interaction with the provided values.

        Parameters
        ----------
        interaction_id : str
            interaction ID to update
        session : Session
            session to be used
        kwargs :
            fields and new values to update

        Returns
        -------

        """
        interaction = session.query(DataStoreInteraction).get(
            interaction_id
        )  # type: DataStoreInteraction
        for k, v in kwargs.items():
            if hasattr(interaction, k):
                continue
            kwargs.pop(k)
        interaction.update(**kwargs)
        return interaction

    def insert_interaction(self, interaction: DataStoreInteraction, session: Session):
        """Insert an interaction object into the database.

        Parameters
        ----------
        row : DataStoreInteraction
            The row to be inserted
        session : Session
            session to be used

        Returns
        -------

        """
        session.add(interaction)
        session.commit()
        return interaction

    def link_to_message_response(
        self, interaction_id: str, message_response: dict, session: Session
    ):
        """Add info from the Slack message into the database for the interaction.

        Parameters
        ----------
        interaction_id : str
            The interaction ID that was returned on adding the message to the database.
        message_response : dict
            The raw message response from slack. The channel and ts will be pulled from this.
        session: Session
            session to be used

        Returns
        -------

        """
        ts_str = message_response.get("ts")
        if not ts_str:
            raise KeyError(f"ts missing from message body: {message_response}")
        channel = message_response.get("channel", {}).get("id")
        if not channel:
            raise KeyError(f"channel missing from message body: {message_response}")
        ts = datetime.fromtimestamp(ts_str)

        self.update_interaction(
            interaction_id, session, message_channel=channel, message_ts=ts
        )

    def link_to_message(
        self, interaction_id: str, channel: str, ts: datetime, session: "Session"
    ):
        """Link to message by setting message ts and channel.

        Parameters
        ----------
        interaction_id : str
            interaction ID to link
        channel : str
            channel to link interaction to
        ts : datetime
            ts to link interaction to
        session : Session
            session to be used

        Returns
        -------

        """
        self.update_interaction(
            interaction_id, session, message_channel=channel, message_ts=ts
        )

    def find_interaction_by_channel_ts(
        self, channel: str, ts: datetime, session: Session
    ) -> Optional[DataStoreInteraction]:
        """Find the interaction in the datastore by channel and message ts.

        Parameters
        ----------
        channel : str
            channel of the interaction youre looking for
        ts : datetime
            ts of the interaction you are looking for
        session : Session
            session to be used

        Returns
        -------
        DataStoreInteraction :
            the interaction object

        Raises
        ------
        ReferenceError :
            There were more than one interaction that matched the channel and message_ts
        """
        query = (
            session.query(DataStoreInteraction)
            .filter(DataStoreInteraction.message_ts == ts)
            .filter(DataStoreInteraction.message_channel == channel)
        )  # type: Query
        try:
            result = query.one_or_none()
            return result
        except MultipleResultsFound as e:
            raise ReferenceError(e)
