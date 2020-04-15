import logging
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, create_engine
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query, Session, sessionmaker

Metadata = MetaData()
Base = declarative_base(metadata=Metadata)

TABLE_INTERACTIONS = "interactions"


class DataStoreInteraction(Base):
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
    cron_followup_action = Column(
        String, default=None
    )  # TODO(zpriddy): Do I need? Is this the same as followup_action?
    followed_up = Column(DateTime, default=None)
    followed_up_ts = Column(DateTime, default=None)

    @property
    def __sql_values__(self) -> dict:
        values = self.__dict__.copy()
        values.pop("_sa_instance_state")
        values.pop("interaction_id")
        return values

    @property
    def object(self):
        return self

    def update_row(self, session: Session):
        session.query(DataStoreInteraction).filter(
            DataStoreInteraction.interaction_id == self.interaction_id
        ).update(self.__sql_values__)


class DataStore:
    def __init__(
        self, host: str, username: str, password: str, port: int = 5432, database: str = "glados"
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

    def create_session(self) -> Session:
        """Generate a new session with the existing connection.

        Returns
        -------
        Session:
            the session that was generated
        """
        session = sessionmaker(self.db)  # type: sessionmaker
        return session()

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

        logging.debug(result.interaction_id)
        return result.object

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
        kwargs : dict
            fields and new values to update

        Returns
        -------

        """
        s = (
            session.query(DataStoreInteraction)
            .filter(DataStoreInteraction.interaction_id == interaction_id)
            .update(kwargs)
        )
        return s

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

        self.update_interaction(interaction_id, session, message_channel=channel, message_ts=ts)

    def link_to_message(self, interaction_id: str, channel: str, ts: datetime, session: "Session"):
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
        self.update_interaction(interaction_id, session, message_channel=channel, message_ts=ts)

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
        query = session.query(DataStoreInteraction).filter(
            DataStoreInteraction.message_ts == ts
            and DataStoreInteraction.message_channel == channel
        )  # type: Query
        if query.count() == 1:
            return query.all()[0]
        elif query.count() == 0:
            logging.error(f"no matching interaction for channel: {channel} and ts: {ts}")
            return None
        else:
            raise ReferenceError(
                f"more than one matching interaction for channel: {channel} and ts: " f"{ts}"
            )
