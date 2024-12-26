from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import  Session
from sqlalchemy.exc import OperationalError, IntegrityError

from module.core_class import TgConfig, Request, RequestType, Reply, ReplyType, CmdType
from module.core_class import Base, DbTgConn, DbCommand, DbMenu, DbButtons
from module.core_exception import CoreException

class Core():
    def __init__(self, conn_str: str):
        try:
            self.engine = create_engine(conn_str, echo=False)
            Base.metadata.create_all(self.engine)
            self.root = str("")
        except OperationalError as e:
            raise CoreException(str(e.args[0]))

    def get_tg_connect(self, session: str) -> TgConfig:
        # Get tg bot connection settings
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                data = conn.query(DbTgConn).filter(DbTgConn.session == session).one_or_none()
                if data is not None:
                    self.root = data.root_uid
                    return TgConfig(api_id=data.api_id,
                                    api_hash=data.api_hash,
                                    session=data.session,
                                    token=data.token,
                                    root_uid=data.root_uid,
                                    info=data.info
                                   )
                else:
                    raise CoreException(f'''Config session {session} not found''')
        except IntegrityError:
            raise CoreException(f'''ERROR: Get tg connect <{session}>''')

    def request(self, request: Request) -> list[Reply]:
        # Processing a request from a user
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                cmd_list = conn.query(DbCommand).filter(and_(DbCommand.request_type == request.type.value), DbCommand.request_text== request.data).order_by(DbCommand.sorting).all()
                if 0 < len(cmd):
                    result = []
                    for cmd in cmd_list:
                        if cmd.reply_type == CmdType.menu.value:
                            result.append(self.__get_menu__(cmd.reply_id))
                    return result
                else:
                    return [Reply(type=ReplyType.error, text=f'''Error: Command <{request.data}> not found.''', data=None)]
        except IntegrityError as e:
            raise CoreException(f'''ERROR: Request <{e.args[0]}>''')

    def __get_menu__(self, menu_id: int) -> Reply:
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                rec = (conn.query(DbMenu, DbButtons)
                        .join(DbButtons, DbButtons.menu_id==DbMenu.id)
                        .filter(DbMenu.id == menu_id)
                        .order_by(DbButtons.sorting)
                        .all()
                      )
                if 0 < len(rec):
                    return Reply(type=ReplyType.menu,
                                 text=rec[0].DbMenu.title,
                                 data=[(btn.DbButtons.btn_text, btn.DbButtons.btn_data) for btn in rec]
                                )
                else:
                    return Reply(type=ReplyType.error, text=f'''Error: Menu not found.''', data=None)
        except IntegrityError as e:
            raise CoreException(f'''ERROR: Get Menu: <{e.args[0]}>''')