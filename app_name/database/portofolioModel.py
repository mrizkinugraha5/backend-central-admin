from .. import db
from sqlalchemy.sql import func
from app_name.database.userModel import User
from app_name.database.kategoriModel import Kategori

class Portofolio(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='CASCADE'),nullable=False)
    approved = db.Column(db.Integer, nullable=True, server_default='0', comment="1 = approved, 0 = not approved")
    judul = db.Column(db.String(50), nullable=False)
    deskripsi_singkat = db.Column(db.Text(), nullable=False)
    deskripsi_lengkap = db.Column(db.Text(), nullable=False)
    id_kategori = db.Column(db.Integer,db.ForeignKey(Kategori.id, ondelete='CASCADE'),nullable=False)
    thumbnail = db.Column(db.String(100), nullable=True)
    foto_1 = db.Column(db.String(100), nullable=True)
    foto_2 = db.Column(db.String(100), nullable=True)
    foto_3 = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    is_delete = db.Column(db.Integer, nullable=True, server_default='0', comment="1 = deleted, 0 = not deleted")

    def __repr__(self):
        return '<Portofolio {}>'.format(self.name)