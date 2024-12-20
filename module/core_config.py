# Module set config tg_bot_cmd

from sqlalchemy import create_engine
from sqlalchemy.orm import  Session
from sqlalchemy.exc import OperationalError, IntegrityError

from module.core_class import Base, DbTgConn
from module.core_exception import CoreException

class CoreConfig():
    def __init__(self, conn_str: str, reset_db: bool = False):
        try:
            self.engine = create_engine(conn_str, echo=False)
            if reset_db:
                Base.metadata.drop_all(self.engine)
            Base.metadata.create_all(self.engine)
        except OperationalError as e:
            raise CoreException(str(e.args[0]))

    def set_tg_connect(self, conn_cfg: dict):
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                conn.add(DbTgConn(api_id=conn_cfg['api_id'],
                                  api_hash=conn_cfg['api_hash'],
                                  session=conn_cfg['session'],
                                  token=conn_cfg['token'],
                                  root_uid=conn_cfg['root_uid'],
                                  info=conn_cfg['info']
                                 ))
                conn.commit()
        except KeyError as k:
            raise CoreException(f''' Key not found <{k.args[0]}> in <connect>''')
        except IntegrityError:
            raise CoreException(f'''ERROR: Set tg connect <{conn_cfg['session']}>''')
