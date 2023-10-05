from datetime import datetime
from flask import Blueprint, request
from flask import current_app as app
from flask_jwt_extended import  get_jwt, jwt_required
import pandas as pd

import threading

from ...queries import *
from ...dbFunctions import Database
from ...utilities import *

from app_name.helpers.validator import *
from app_name.helpers.function import *

kehadiran = Blueprint(
    name='kehadiran', 
    import_name=__name__, 
    url_prefix='/kehadiran'
)

def create_kehadiran(kode, isPublic=True, isImportMode=False, dataImport=None):
    url_list = request.url.split('/')[:-3]
    if isPublic:
        url_list = request.url.split('/')[:-2]
    url = ('/').join(url_list)
    base_url_sertifikat = f'{url}/sertifikat/media'
    url_create = f'{url}/sertifikat/create'
    url_send = f'{url}/sertifikat/send/peserta'
    jwt = get_jwt()
    role = None
    if jwt:
        role = jwt['role']
    try :
        # ===================================
        # ======== Handle Data Input ========
        # ===================================
        if isImportMode:
            dataInput = dataImport
        else:
            dataInput = request.json
        dataRequired = ["nama", "email", "nomor_telepon", "sumber_info", "is_pengusaha"]
        for data in dataRequired:
            if dataInput == None:
                return bad_request("body request tidak boleh kosong")
            if data not in dataInput:
                return parameter_error(f"Missing {data} in Request Body")
            if dataInput[data] == None:
                dataInput[data] = ""
        # ====================================
        # ======== Data Preprocessing ========
        # ====================================

        # map dan sanitize input dengan trim 
        nama = dataInput["nama"].strip().title()
        email = dataInput["email"].strip().lower()
        nomor_telepon = dataInput["nomor_telepon"].strip()
        sumber_info = dataInput["sumber_info"].strip()
        is_pengusaha = dataInput["is_pengusaha"]
        nama_usaha = dataInput.get("nama_usaha")
        bidang_usaha = dataInput.get("bidang_usaha")
        alamat_usaha = dataInput.get("alamat_usaha")
        kode_kehadiran = uuid.uuid4().hex[:6]

        # =================================
        # ======== Data Validation ========
        # =================================

        # validasi data
        error_list = kehadiran_validator(nama, email, nomor_telepon, sumber_info, is_pengusaha, nama_usaha, bidang_usaha,alamat_usaha)
        if len(error_list) != 0:
            return defined_error(error_list,'Bad Request', 400)

        # jika is_pengusaha == true maka form data usaha wajib diisi
        if is_pengusaha:
            for key in [nama_usaha, bidang_usaha, alamat_usaha]:
                if key == None or key == "":
                    return defined_error(f"Nama, Bidang, Alamat Usaha tidak boleh kosong",'Bad Request', 400)

        # Cek data event terkait
        query = QUERY_GET_EVENT_BY_KODE_RAHASIA 
        if isPublic:
            query = QUERY_GET_EVENT_BY_KODE

        values = (kode,)
        result = Database().get_data(query, values)
        if len(result) == 0:
            return defined_error(f"event dengan kode:{kode} tidak ditemukan", 'Not Found', 404)

        id_event = result[0]["id"]
        nama_event = result[0]["nama"]
        jenis_event = result[0]["jenis"]
        tanggal = result[0]["tanggal"].strftime("%d-%m-%Y")
        waktu_mulai = result[0]["waktu_mulai"]
        waktu_berakhir = result[0]["waktu_berakhir"]
        waktu_sekarang = datetime.datetime.now()
        
        # Absen hanya bisa diisi setidaknya 30 menit setelah berlangsung
        # waktu_mulai = waktu_mulai + datetime.timedelta(minutes=30)
        # Penambahan waktu 15 menit untuk pengisian kehadiran webinar
        # waktu_berakhir = waktu_berakhir + datetime.timedelta(minutes=15)

        # if role != "ADMIN":
        #     if waktu_sekarang < waktu_mulai or waktu_sekarang > waktu_berakhir:
        #         pesan = "Waktu Pengisian Form Kehadiran sudah Berakhir,Form Kehadiran hanya bisa diisi setidaknya 30 menit setelah acara dimulai dan selambat lambatnya 15 menit setelah acara selesai"
        #         return defined_error(pesan, 'Bad Request', 400)

        if is_pengusaha and (not nama_usaha or not bidang_usaha):
            return defined_error("nama_usaha dan bidang_usaha tidak boleh kosong",'Bad Request', 400)

        # cek apakah peserta telah mengisi kehadiran 
        query = QUERY_CHECK_KEHADIRAN_BY_EMAIL_AND_EVENT_ID
        values = (id_event,email,)
        kehadiran = Database().get_data(query, values)
        if len(kehadiran) != 0:
            return defined_error(f"email:{email} sudah menghadiri event dengan kode:{kode}", 'Bad Request', 400)

        # ========================
        # ======== Action ========
        # ========================
        # Insert data to database
        values = {
            "id_event":id_event,
            "nama_peserta" : nama,
            "email_peserta" : email,
            "nomor_telepon" : nomor_telepon,
            "is_pengusaha": is_pengusaha, 
            "sumber_info": sumber_info, 
            "bidang_usaha": bidang_usaha, 
            "nama_usaha": nama_usaha, 
            "alamat_usaha": alamat_usaha, 
            "kode_kehadiran": kode_kehadiran
        }

        Database().save(table="kehadiran", data=values)
        #membuat log
        create_log(f"peserta dengan email:{email} menghadiri event dengan id:{id} kode:{kode}")

        def generate_sertifikat():
            qr_code = instant_QR(id_event,email)
            sertifikat = get_sertifikat(nama,nama_event,kode_kehadiran,"peserta",jenis_event,qr_code,tanggal,url_create)
            url_sertifikat = sertifikat.json()['data'].split('/')[-1]
            url_sertifikat = f"{base_url_sertifikat}/{url_sertifikat}"
            save_sertifikat(url_sertifikat,kode_kehadiran)
            if sumber_info == "centralai.id":
                send_sertifikat(email,url_sertifikat,url_send)
    
        thread = threading.Thread(target=generate_sertifikat)
        thread.start()

        return success(message=f"Berhasil menambahkan data kehadiran")

    except Exception as e:
        return bad_request(str(e))

@kehadiran.post('/<kode>')
@jwt_required()
def kehadiran_by_kode_publik(kode):
    user_role = get_jwt()["role"]
    if user_role != "ADMIN":
        return defined_error("hanya admin yang dapat mengakses","Forbidden",403)  
    return create_kehadiran(kode,isPublic=True)

@kehadiran.post('kode/<kode>')
@jwt_required(optional=True)
def kehadiran_by_kode_rahasia(kode):
    return create_kehadiran(kode,isPublic=False)

def get_kehadiran_by_event_kode(kode,is_kode_publik=True): 
    offset = request.args.get('page')
    limit = request.args.get('row')
    limit  = int(limit) if limit else 3000
    offset  = (int(offset) - 1) * limit if offset else 0
    user_role = get_jwt()["role"]
    user_email = get_jwt()["email"]
    try :
        if user_role != "ADMIN":
            return defined_error("hanya admin yang dapat mengakses","Forbidden",403)   
        # =================================
        # ======== Data Validation ========
        # =================================
        query = QUERY_GET_EVENT_BY_KODE_RAHASIA
        if is_kode_publik:
            query = QUERY_GET_EVENT_BY_KODE

        values = (kode,)
        result = Database().get_data(query, values)
        if len(result) == 0:
            return defined_error(f"event dengan kode:{kode} tidak ditemukan", 'Not Found', 404)

        id_event = result[0]["id"]
        # ========================
        # ======== Action ========
        # ========================
        query = QUERY_GET_ALL_KEHADIRAN_BY_EVENT
        values = (id_event,limit,offset)
        result = Database().get_data(query,values) 
        if len(result) == 0:
            return defined_error(f"belum ada yang menghadiri event dengan kode:{kode}", 'Not Found', 404)

        
        return success_data(message=f"Success", data=result)

    except Exception as e:
        return bad_request(str(e))

@kehadiran.get('/kode/<kode>')
@jwt_required()
def get_kehadiran_by_kode_publik(kode):
    return get_kehadiran_by_event_kode(kode, is_kode_publik=True)

@kehadiran.get('/kode-rahasia/<kode>')
@jwt_required()
def get_kehadiran_by_kode_rahasia(kode):
    return get_kehadiran_by_event_kode(kode, is_kode_publik=False)

@kehadiran.get('/id/<id>')
@jwt_required()
def get_kehadiran_by_event_id(id): 
    offset = request.args.get('page')
    limit = request.args.get('row')
    limit  = int(limit) if limit else 3000
    offset  = (int(offset) - 1) * limit if offset else 0
    user_role = get_jwt()["role"]
    user_email = get_jwt()["email"]
    try :
        if user_role != "ADMIN":
            return defined_error("hanya admin yang dapat mengakses","Forbidden",403)   
        # =================================
        # ======== Data Validation ========
        # =================================
        query = QUERY_GET_EVENT_BY_ID
        values = (id,)
        result = Database().get_data(query, values)
        if len(result) == 0:
            return defined_error(f"event dengan id:{id} tidak ditemukan", 'Not Found', 404)

        id_event = result[0]["id"]
        # ========================
        # ======== Action ========
        # ========================
        query = QUERY_GET_ALL_KEHADIRAN_BY_EVENT
        values = (id_event,limit,offset)
        result = Database().get_data(query,values)
        if len(result) == 0:
            return defined_error(f"belum ada yang menghadiri event dengan id:{id}", 'Not Found', 404)

        return success_data(message=f"Success", data=result)

    except Exception as e:
        return bad_request(str(e))

def get_QR_code(identifier, type="id"):
    user_role = get_jwt()["role"]
    try :
        if user_role != "ADMIN":
            return defined_error("hanya admin yang dapat mengakses","Forbidden",403) 
        query = QUERY_GET_KEHADIRAN_BY_ID
        if type == "kode":
            query = QUERY_GET_KEHADIRAN_BY_KODE

        values = (identifier,)
        result = Database().get_data(query,values)
        if len(result) == 0:
            return defined_error(f"kehadiran dengan {type}:{identifier} tidak ditemukan", 'Not Found', 404)

        payload = result[0]
        payload['tanggal'] = payload['tanggal'].strftime("%d-%m-%Y")
        del payload["link_sertifikat"]

        data = {
            "qr_code": generate_qr_code(payload)
        }

        return success_data(message=f"Success", data=data)

    except Exception as e:
        return bad_request(str(e))

@kehadiran.get('/qrcode/id/<id>')
@jwt_required()
def get_QR_code_by_id(id): 
    return get_QR_code(id,type=id)

@kehadiran.get('/qrcode/kode/<kode>')
@jwt_required()
def get_QR_code_by_kode(kode):    
    return get_QR_code(kode,type="kode")

@kehadiran.get('/jumlah/<kode>')
def get_jumlah_kehadiran(kode):
    try :
        query = QUERY_GET_EVENT_BY_KODE     
        values = (kode,)
        found_event = Database().get_data(query,values)

        query = QUERY_GET_JUMLAH_KEHADIRAN_BY_KODE
        values = (kode,)
        result = Database().get_data(query,values)
        if len(result) == 0 or len(found_event) == 0:
            return defined_error(f"event dengan kode:{kode} tidak ditemukan", 'Not Found', 404)

        data = {
            "jumlah":result[0]["COUNT(kehadiran.id)"]
        }

        return success_data(message=f"Success", data=data)

    except Exception as e:
        return bad_request(str(e))

@kehadiran.post('/import')
@jwt_required()
def import_data_kehadiran():
    try :
        f = request.files["file"]
        kode_event = request.form["kode_event"]

        if f == None or f == "":
            return defined_error("file import wajib diisi")
        
        if kode_event == None or kode_event == "":
            return defined_error("kode_event wajib diisi")
        
        data_df = pd.read_excel(f)
        data_dict = data_df.to_dict('list')

        columns = list()
        for column in data_dict.keys():
            columns.append(column)
        
        row_number = len(data_dict[columns[0]])
        # var_dump = list()
        
        for index in range(row_number):
            data_dump = dict()
            for column in columns:
                data_dump[column] = data_dict[column][index]
            
            # rename key data
            data_dump['nama'] = data_dump.pop('Nama Lengkap')
            data_dump['email'] = data_dump.pop('Email Address')
            data_dump['nomor_telepon'] = str(data_dump.pop('Nomor HP'))
            data_dump['sumber_info'] = 'centralai.id'
            data_dump['is_pengusaha'] = 0

            # add data_dump to var_dump list
            # var_dump.append(data_dump)

            # call create_kehadiran function
            response = create_kehadiran(
                kode=kode_event,
                isPublic=True,
                isImportMode=True,
                dataImport=data_dump
            )
            if response.status_code != 200:
                return make_response(response.json, response.status_code)
        
        # return success_data(message="Berhasil ekstrak data pada file excel", data=var_dump)
        return success(message="Berhasil mengimport data kehadiran")

    except Exception as e:
        return bad_request(str(e))