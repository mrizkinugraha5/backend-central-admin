from .. import db
from sqlalchemy.sql import func

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    is_pengusaha = db.Column(db.Boolean, nullable=False)
    tanggal_lahir = db.Column(db.Date, nullable=True)
    foto = db.Column(db.String(100), nullable=True)
    jenis_kelamin = db.Column(db.String(10), nullable=True)
    nama_usaha = db.Column(db.String(50), nullable=True)
    bidang_usaha = db.Column(db.String(50), nullable=True)
    alamat_usaha = db.Column(db.String(200), nullable=True)
    nomor_telepon = db.Column(db.String(17), nullable=True)
    linkedin = db.Column(db.String(100), nullable=True)
    instagram = db.Column(db.String(100), nullable=True)
    alamat = db.Column(db.String(255), nullable=True)
    riwayat_kerja = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Integer, nullable=False, server_default='0', comment="1 = True, 0 = False")
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    is_delete = db.Column(db.Integer, nullable=True, server_default='0', comment="1 = deleted, 0 = not deleted")

    def _repr_(self):
        return '<User {}>'.format(self.name)