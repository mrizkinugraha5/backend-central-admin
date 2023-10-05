from .. import db
from sqlalchemy.sql import func
from app_name.database.eventModel import Event

class Kehadiran(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_event = db.Column(db.Integer, db.ForeignKey(Event.id, ondelete='CASCADE'),nullable=False)
    kode_kehadiran = db.Column(db.String(7), nullable=False)
    nama_peserta = db.Column(db.String(255), nullable=False)
    email_peserta = db.Column(db.String(255), nullable=False)
    nomor_telepon = db.Column(db.String(17), nullable=False)
    is_pengusaha = db.Column(db.Boolean, nullable=False)
    sumber_info = db.Column(db.String(50), nullable=False)
    nama_usaha = db.Column(db.String(50), nullable=True)
    bidang_usaha = db.Column(db.String(50), nullable=True)
    alamat_usaha = db.Column(db.String(50), nullable=True)
    link_sertifikat = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    is_delete = db.Column(db.Integer, nullable=True, server_default='0', comment="1 = deleted, 0 = not deleted")

    def __repr__(self):
        return '<Kehadiran {}>'.format(self.name)