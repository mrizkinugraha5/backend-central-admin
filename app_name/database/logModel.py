from .. import db
from sqlalchemy.sql import func

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    activity = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    is_delete = db.Column(db.Integer, nullable=True, server_default='0', comment="1 = deleted, 0 = not deleted")

    def __repr__(self):
        return '<Log {}>'.format(self.name)