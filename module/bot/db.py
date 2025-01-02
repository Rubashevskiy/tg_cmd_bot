from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import  Session
from sqlalchemy.exc import OperationalError, IntegrityError
import json
import random
import string
from module.bot.core_class import TgConnect, TgUser, TgCmdData, TgMenu, TgButton, TgPlugin, TgTxtCmd, CmdType
from module.bot.core_class import Base, DbTgConnect, DbTgUser


from module.bot.core_exception import CoreException

class DB():
    def __init__(self, conn_str: str, reset_db: bool = False):
        try:
            self.engine = create_engine(conn_str, echo=False)
            if reset_db:
                Base.metadata.drop_all(self.engine)
            Base.metadata.create_all(self.engine)
        except OperationalError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    '''SET'''
    def set_tg_connect(self, tg_conn: TgConnect):
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                conn.add(DbTgConnect(api_id=tg_conn.api_id,
                                     api_hash=tg_conn.api_hash,
                                     session=tg_conn.session,
                                     token=tg_conn.token,
                                     info=tg_conn.info
                                    )
                        )
                conn.commit()
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def set_tg_user(self, user: TgUser):
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                conn.add(DbTgUser(user_uid=user.user_uid, info=user.info))
                conn.commit()
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def set_tg_menu(self, menu: TgMenu):
        pass

    '''GET'''
    def get_tg_connect(self, session: str) -> TgConnect:
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                tg_conn = conn.query(DbTgConnect).filter(DbTgConnect.session==session).one_or_none()
                if tg_conn is not None:
                    return TgConnect(api_id=tg_conn.api_id,
                                     api_hash=tg_conn.api_hash,
                                     session=tg_conn.session,
                                     token=tg_conn.token,
                                     info=tg_conn.info
                                    )
                else:
                    raise CoreException(msg="TG connect not found", data=session)
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def get_tg_user(self, user_uid: str) -> TgConnect:
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                user = conn.query(DbTgUser).filter(DbTgUser.user_uid==user_uid).one_or_none()
                if user is not None:
                    return TgUser(user_uid=user_uid, info=user.info)
                else:
                    raise CoreException(msg="TG user not found", data=user_uid)
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))
    # GET ALL
    def get_all_tg_connect(self) -> list[TgConnect]:
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                result = []
                for tg_conn in conn.query(DbTgConnect).all():
                    result.append(TgConnect(api_id=tg_conn.api_id,
                                            api_hash=tg_conn.api_hash,
                                            session=tg_conn.session,
                                            token=tg_conn.token,
                                            info=tg_conn.info
                                           )
                                 )
                return result
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def get_all_tg_user(self) -> list[TgUser]:
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                return [TgUser(user_uid=user.user_uid, info=user.info) for user in conn.query(DbTgUser).all()]
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))