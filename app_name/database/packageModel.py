from .. import db
from sqlalchemy.sql import func

class Packages(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    package_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.BigInteger, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    features = db.Column(db.JSON, nullable=True)
    platform = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=True, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    is_delete = db.Column(db.Integer, nullable=True, server_default='0', comment="1 = deleted, 0 = not deleted")

    def __repr__(self):
        return '<Package {}>'.format(self.name)
