from sqlalchemy import create_engine
from sqlalchemy.orm import  Session
from sqlalchemy.exc import OperationalError, IntegrityError

from module.core_class import Base, DbTgConn
from module.core_exception import CoreException

class Core():
    def __init__(self, conn_str: str):
        try:
            self.engine = create_engine(conn_str, echo=False)
            Base.metadata.create_all(self.engine)
        except OperationalError as e:
            raise CoreException(str(e.args[0]))

    def get_tg_connect(self, session: str) -> dict:
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