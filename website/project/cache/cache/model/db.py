from server import db

class Updated(db.Model):
    __tablename__ = 'updated'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    string_update_time = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    still_caching = db.Column(db.Integer, nullable=False, default=0)