import logging
from datetime import datetime
from typing import List, Optional, NoReturn
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
    interaction_id: :obj: `str`
        This is the primary key of the datastore. This is the ID of the entry in the datastore.
    ts: :obj: `datetime`
        This is the time the row was put into the database.
    bot: :obj: `str`
        This is the name of the bot it should use when completing followup actions.
    data: :obj: `dict`
        Any extra data stored with the interaction. This is a JSON blob.
    message_channel: :obj: `str`
        The channel that this interaction was sent to.
    message_ts: :obj: `datetime`
        The message timestamp when this interaction was sent.
    ttl: :obj: `int`
        How long this interaction should live for.
    followup_ts: :obj: `datetime`
        When should the follow up action happen.
    followup_action: :obj: `str`
        The action name to execute when following up. If None then no action will happen.
    cron_followup_action: :obj: `str`
        The action name to execute on a normal cron schedule like every 5 min. If None then no action will happen.
    followed_up: :obj: `datetime`
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
    """DataStore is how GLaDOS stores async data.

    Parameters
    ----------
    host
        postgres host.
    username
        postgres username.
    password
        postgres password.
    port
        postgres port.
    database
        postgres database to use.
    """

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
        """Generate a new session with the existing connection."""
        return self.session_maker()

    def table_exists(self, table: str = TABLE_INTERACTIONS) -> bool:
        """Check to see if the GLaDOS table is found in postgres.

        Parameters
        ----------
        table
            table name to use.

        """
        return table in self.db.table_names()

    def drop_table(
        self, table: str = TABLE_INTERACTIONS, force: bool = False
    ) -> NoReturn:
        """Drop the GLaDOS table so that it can be re-created.

        Parameters
        ----------
        table
            table name to use.
        force
            if True will fill force drop the table without checks.
        """
        Table(table, Metadata).drop(self.db, checkfirst=not force)

    def create_table(
        self, tables: Optional[List[str]] = None, force: bool = False
    ) -> NoReturn:
        """Create the table.

        If you set force to True then it will drop the existing tables and
        then recreate them. ALL DATA WILL BE LOST

        Parameters
        ----------
        tables
            only take action on these tables. If None, then take action on all tables
        force
            drop existing tables and rebuild. (default: False)

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
        interaction_id
            interaction ID to find
        session
            session to be used
        """
        result = session.query(DataStoreInteraction).get(interaction_id)
        return result

    def update_interaction(
        self, interaction_id, session: Session, **kwargs
    ) -> DataStoreInteraction:
        """Find and update an interaction with the provided values.

        Parameters
        ----------
        interaction_id
            interaction ID to update
        session
            session to be used
        kwargs
            fields and new values to update
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

    def insert_interaction(
        self, interaction: DataStoreInteraction, session: Session
    ) -> NoReturn:
        """Insert an interaction object into the database.

        Parameters
        ----------
        interaction
            The row to be inserted
        session
            session to be used
        """
        session.add(interaction)
        session.commit()
        return interaction

    def link_to_message_response(
        self, interaction_id: str, message_response: dict, session: Session
    ) -> NoReturn:
        """Add info from the Slack message into the database for the interaction.

        Parameters
        ----------
        interaction_id
            The interaction ID that was returned on adding the message to the database.
        message_response
            The raw message response from slack. The channel and ts will be pulled from this.
        session:
            session to be used
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
    ) -> NoReturn:
        """Link to message by setting message ts and channel.

        Parameters
        ----------
        interaction_id
            interaction ID to link
        channel
            channel to link interaction to
        ts
            ts to link interaction to
        session
            session to be used
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
        channel
            channel of the interaction youre looking for
        ts
            ts of the interaction you are looking for
        session
            session to be used

        Raises
        ------
        ReferenceError
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
