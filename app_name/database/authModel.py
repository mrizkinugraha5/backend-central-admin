from .. import db
from sqlalchemy.sql import func
from app_name.database.userModel import User

class Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='CASCADE'),nullable=False)
    token = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

    def __repr__(self):
        return '<Auth {}>'.format(self.name)