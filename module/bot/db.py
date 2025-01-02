from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import  Session
from sqlalchemy.exc import OperationalError, IntegrityError
import json
import random
import string
from module.bot.core_class import Request, RequestType, Reply, ReplyType, CmdType
from module.bot.core_class import Base, DbTgConn, DbTgUsers, DbMenu, DbButtons


from module.bot.config import db_conn_str, session
from module.bot.core_exception import CoreException

class DB():
    def __init__(self, reset: bool = False):
        try:
            self.engine = create_engine(db_conn_str, echo=False)
            if reset:
                Base.metadata.drop_all(self.engine)
            Base.metadata.create_all(self.engine)
        except OperationalError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def add_tg_connect(self, api_id: int, api_hash: str, session: str, token: str, info: str = None):
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                conn.add(DbTgConn(api_id=api_id,
                                  api_hash=api_hash,
                                  session=session,
                                  token=token,
                                  info=info
                                 )
                        )
                conn.commit()
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def add_user(self, user: str,  info: str = None):
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                conn.add(DbTgUsers(user_uid=user, info=info))
                conn.commit()
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def add_menu(self, title: str, info: str = None):
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                conn.add(DbMenu(title=title, info=info))
                conn.commit()
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def add_button(self, title_menu: str, btn_text: str, info: str = None):
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                conn.add(DbButtons(title=title, info=info))
                conn.commit()
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def check_user(self, user_uid: str) -> bool:
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                user = conn.query(DbTgUsers).filter(DbTgUsers.user_uid == user_uid).one_or_none()
                return user is not None
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

