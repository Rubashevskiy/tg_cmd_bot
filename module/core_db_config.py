import json
import random
from string import ascii_uppercase, digits
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import  Session, aliased
from sqlalchemy.exc import OperationalError, IntegrityError

from module.core_class import TgConnect, TgUser, TgMenu, TgButton, TgTextCmd, SlotType, SignalType, TgAuto
from module.core_class import Base, DbTgConnect, DbTgUser, DbTgMenu, DbTgButton, DbTgTextCmd, DbTgAuto
from module.core_plugin import CorePlugin
from module.core_exception import CoreException

from module.config import db_conn_str, session

class CoreDbConfig():
    def __init__(self, reset: bool = False):
        try:
            self.engine = create_engine(db_conn_str, echo=False)
            if reset:
                Base.metadata.drop_all(self.engine)
            Base.metadata.create_all(self.engine)
            self.uid = []
            self.errors = []
        except OperationalError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))


    def __uid_generate__(self) -> str:
        all_symbols = ascii_uppercase + digits
        while True:
            uid = f'''{''.join(random.choice(all_symbols) for _ in range(8))}'''
            if uid not in self.uid:
                self.uid.append(uid)
                return uid

    #ADD

    def add_connect(self, connect: TgConnect) -> None:
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                conn.add(DbTgConnect(api_id=connect.api_id,
                                     api_hash=connect.api_hash,
                                     session=connect.session,
                                     token=connect.token,
                                     info=connect.info
                                    )
                        )
                conn.commit()
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def add_user(self, user: TgUser):
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                conn.add(DbTgUser(name=user.name, auto_msg=user.auto_msg, info=user.info))
                conn.commit()
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def add_menu(self, menu: TgMenu):
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                db_menu = DbTgMenu(text=menu.text , info=menu.info)
                for s, tg_btn in enumerate(menu.get_all_buttons()):
                    uid_data = self.__uid_generate__()
                    db_btn = DbTgButton(text=tg_btn.text,
                                        data=uid_data,
                                        sorting=s+1,
                                        slot_type=tg_btn.slot_type.value,
                                        slot_uid=tg_btn.slot_uid,
                                        params=json.dumps(tg_btn.params),
                                        info=tg_btn.info
                                       )
                    db_btn.menu = db_menu
                    conn.add(db_btn)
                conn.commit()
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def add_text_cmd(self, txt_cmd: TgTextCmd):
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                db_txt_cmd = DbTgTextCmd(text=txt_cmd.text.upper(),
                                         slot_type=txt_cmd.slot_type.value,
                                         slot_uid=txt_cmd.slot_uid,
                                         params=json.dumps(txt_cmd.params),
                                         info=txt_cmd.info
                                        )
                conn.add(db_txt_cmd)
                conn.commit()
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def add_tg_auto(self, auto: TgAuto) -> None:
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                conn.add(DbTgAuto(plugin_uid=auto.plugin_uid, params=json.dumps(auto.params), info=auto.info))
                conn.commit()
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    # GET

    def get_connect(self) -> TgConnect:
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                db_conn = conn.query(DbTgConnect).filter(DbTgConnect.session==session).one_or_none()
                if db_conn is None:
                    raise CoreException(f'Tg connect {session} not found')
                return TgConnect(api_id=db_conn.api_id,
                                 api_hash=db_conn.api_hash,
                                 session=db_conn.session,
                                 token=db_conn.token,
                                 info=db_conn.info
                                )
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def get_auto_users(self) -> list[str]:
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                return [rec.name for rec in conn.query(DbTgUser).filter(DbTgUser.auto_msg==True).all()]
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def get_menu(self, menu_text: str) -> TgMenu:
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                db_menu = (conn.query(DbTgMenu, DbTgButton)
                           .join(DbTgButton, DbTgButton.menu_id==DbTgMenu.id)
                           .filter(DbTgMenu.text==menu_text).order_by(DbTgButton.sorting).all()
                          )
                if 0 == len(db_menu):
                    raise CoreException(f'Menu <{menu_text}> not found')
                tg_menu = TgMenu(text=db_menu[0].DbTgMenu.text, info=db_menu[0].DbTgMenu.info)
                for rec in db_menu:
                    tg_menu.add_button(TgButton(text=rec.DbTgButton.text,
                                                slot_type=SlotType(rec.DbTgButton.slot_type),
                                                slot_uid=rec.DbTgButton.slot_uid,
                                                params=json.loads(rec.DbTgButton.params),
                                                info=rec.DbTgButton.info,
                                                data=rec.DbTgButton.data
                                               )
                                      )
                return tg_menu
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def get_text_cmd(self, txt_cmd_text: str) -> TgTextCmd:
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                db_txt_cmd = conn.query(DbTgTextCmd).filter(DbTgTextCmd.text==txt_cmd_text).one_or_none()
                if db_txt_cmd is None:
                    return None
                else:
                    return TgTextCmd(text=db_txt_cmd.text,
                                     slot_type=SlotType(db_txt_cmd.slot_type),
                                     slot_uid=db_txt_cmd.slot_uid,
                                     params=json.loads(db_txt_cmd.params),
                                     info=db_txt_cmd.info,
                                     data=None
                                    )
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def get_button(self, data: str) -> TgButton:
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                db_btn= conn.query(DbTgButton).filter(DbTgButton.data==data).one_or_none()
                if db_btn is None:
                    return None
                else:
                    return TgButton(text=db_btn.text,
                                    slot_type=SlotType(db_btn.slot_type),
                                    slot_uid=db_btn.slot_uid,
                                    params=json.loads(db_btn.params),
                                    info=db_btn.info,
                                    data=db_btn.data
                                   )
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def get_all_tg_auto(self) -> list[TgAuto]:
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                return [TgAuto(plugin_uid=rec.plugin_uid, params=json.loads(rec.params), info=rec.info) for rec in conn.query(DbTgAuto).all()]
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def get_errors(self) -> list[str]:
        return self.errors

    # CHECK

    def  check_user(self, user_name: str) -> bool:
        try:
            with Session(autoflush=False, bind=self.engine) as conn:
                db_user = conn.query(DbTgUser).filter(DbTgUser.name==user_name).one_or_none()
                return db_user is not None
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))

    def  check_errors_integrity(self) -> bool:
        try:
            self.errors.clear()
            pl = CorePlugin()
            plugin_list = pl.plugins()
            with Session(autoflush=False, bind=self.engine) as conn:
                # Check session
                if 0 == conn.query(DbTgConnect).filter(DbTgConnect.session==session).count():
                    self.errors.append(f'Session <{session}> not found')
                # Check users
                if 0 == conn.query(DbTgUser).count():
                    self.errors.append(f'Users not found')
                # Check menu
                if 0 != conn.query(DbTgMenu).count():
                    # All menus have buttons
                    for rec in (conn.query(DbTgMenu, DbTgButton)
                                .join(DbTgButton, DbTgButton.menu_id==DbTgMenu.id, isouter=True)
                                .filter(DbTgButton.id.is_(None)).all()):
                        self.errors.append(f'''Menu <{rec[0].text}> has no buttons''')
                    # Check Buttons slot link to menu object
                    menu_slot = aliased(DbTgMenu)
                    for rec in (conn.query(DbTgMenu, DbTgButton, menu_slot)
                                .join(DbTgButton, DbTgButton.menu_id==DbTgMenu.id, isouter=True)
                                .join(menu_slot, DbTgButton.slot_uid==menu_slot.text, isouter=True)
                                .filter(and_(DbTgButton.slot_type==1, menu_slot.id.is_(None))).all()):
                        self.errors.append(f'''Button <{rec[1].text}> in menu <{rec[0].text}> calls up non-existent menu <{rec[1].slot_uid}>''')
                    # Check Buttons slot link to plugin object
                    for rec in (conn.query(DbTgMenu, DbTgButton)
                                .join(DbTgButton, DbTgButton.menu_id==DbTgMenu.id, isouter=True)
                                .filter(and_(DbTgButton.slot_type==2, DbTgButton.slot_uid.notin_(plugin_list))).all()):
                        self.errors.append(f'''Button <{rec[1].text}> in menu <{rec[0].text}> calls up non-existent plugin <{rec[1].slot_uid}>''')
                # Check Text Command
                if 0 == conn.query(DbTgTextCmd).count():
                    self.errors.append(f'''Text Command not found''')
                else:
                    # Check Text Command slot link to menu object
                    for rec in (conn.query(DbTgTextCmd, DbTgMenu)
                                .join(DbTgMenu, DbTgTextCmd.slot_uid==DbTgMenu.text, isouter=True)
                                .filter(and_(DbTgTextCmd.slot_type==1, DbTgMenu.id.is_(None))).all()):
                        self.errors.append(f'''Text Command <{rec[0].text}> calls up non-existent menu <{rec[0].slot_uid}>''')
                    # Check Text Command slot link to plugin object
                    for rec in (conn.query(DbTgTextCmd)
                                .filter(and_(DbTgTextCmd.slot_type==2, DbTgTextCmd.slot_uid.notin_(plugin_list))).all()):
                        self.errors.append(f'''Text Command <{rec.text}> calls up non-existent plugin <{rec.slot_uid}>''')
                    for rec in (conn.query(DbTgAuto).filter(DbTgAuto.plugin_uid.notin_(plugin_list)).all()):
                        self.errors.append(f'''Auto Command  calls up non-existent plugin <{rec.plugin_uid}>''')
            return 0 == len(self.errors)
        except IntegrityError as e:
            raise CoreException(msg="Internal error", data=str(e.args[0]))