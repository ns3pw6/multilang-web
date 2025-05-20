from model.dbModel import LogDB
from server import db

class Log(LogDB):
    
    @classmethod
    def insert(cls, u_id: int, type_id: int, log: str) -> bool:
        log = cls(
            u_id=u_id,
            type_id=type_id,
            log=log
        )
        try:
            db.session.add(log)
            db.session.commit()
            return
        except Exception as e:
            return str(e)
    