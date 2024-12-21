from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import  Session
from sqlalchemy.exc import OperationalError, IntegrityError

from module.core_class import RequestType, ReplyType
from module.core_class import Base, DbTgConn, DbCommand
from module.core_exception import CoreException

class Core():
    def __init__(self, conn_str: str):
        try:
            self.engine = create_engine(conn_str, echo=False)
            Base.metadata.create_all(self.engine)
        except OperationalError as e:
            raise CoreException(str(e.args[0]))

    def get_tg_connect(self, session: str) -> dict:
        # Get tg bot connection settings
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                data = conn.query(DbTgConn).filter(DbTgConn.session == session).one_or_none()
                if data is None:
                    raise CoreException(f'''Config session {session} not found''')
                else:
                    return {
                        "api_id" : data.api_id,
                        "api_hash" : data.api_hash,
                        "session" : data.session,
                        "token" : data.token,
                        "root_uid" : data.root_uid,
                        "info" : data.info
                    }
        except IntegrityError:
            raise CoreException(f'''ERROR: Get tg connect <{session}>''')

    def request(self, data: dict) -> list[dict]:
        # Processing a request from a user
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                cmd_lst = conn.query(DbCommand) \
                    .filter(and_(DbCommand.request_type == data['type'].value), DbCommand.request_text== data['data']) \
                    .order_by(DbCommand.sorting).all()
                if 0 == len(cmd_lst):
                    return [{'type' : ReplyType.error, 'error' : [f'''Error: Command <{data['data']}> not found.''']}]
                for cmd in cmd_lst:
                    pass
                return []
        except IntegrityError as e:
            raise CoreException(f'''ERROR: Request <{e.args[0]}>''')