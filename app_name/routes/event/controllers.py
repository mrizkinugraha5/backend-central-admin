from wsgiref.util import request_uri
from flask import Blueprint, request
from flask import render_template, url_for
from flask_jwt_extended import  get_jwt, jwt_required
from werkzeug.utils import secure_filename
from flask import current_app as app
from time import strftime
import os
from ...dbFunctions import Database
from ...utilities import *
from ...queries import *
from app_name.helpers.validator import *
from app_name.helpers.function import *
import threading

event = Blueprint(
    name='event',
    import_name=__name__,  
    static_folder = '../../static/foto/event', 
    url_prefix='/event'
)

def get_all(published_only=True):
    offset = request.args.get('page')
    limit = request.args.get('row')
    search = request.args.get('search')
    limit  = int(limit) if limit else 1000
    offset  = (int(offset) - 1) * limit if offset else 0
    search = f"%{search}%" if search else "%%"
    url_list = request.url.split('/')[:-1]
    url = ('/').join(url_list)
    try: 
        # ========================
        # ======== Action ========
        # ========================
        if published_only:
            url = str(url).replace('published', '')
            query = QUERY_GET_ALL_PUBLISHED_EVENT
        else:
            query = QUERY_GET_ALL_EVENT
        values = (search,limit,offset,)
        result = Database().get_data(query,values)

        if len(result) == 0:
            return defined_error(f"belum ada event yang tersimpan",'Not Found', 404)

        for i in range(len(result)):
            if result[i]["poster"]:
                result[i]["poster"] = f"{app.config['BASE_URL']}/static/foto/event/{result[i]['poster']}"
            result[i]["tanggal"] = format_datetime(result[i]["tanggal"])
            result[i]["waktu_mulai"] = format_datetime(result[i]["waktu_mulai"])
            result[i]["waktu_berakhir"] = format_datetime(result[i]["waktu_berakhir"])

        data = result

        return success_data(message=f"Success", data=data)
    except Exception as e:
        return bad_request(str(e))

def get_by_id(id, published_only=True):
    url_list = request.url.split('/')[:-1]
    url = ('/').join(url_list)
    try:
        # ========================
        # ======== Action ========
        # ========================
        if published_only:
            url = str(url).replace('published', '')
            query = QUERY_GET_EVENT_BY_ID
        else:
            query = QUERY_GET_PUBLISHED_EVENT_BY_ID
        values = (id,)
        result = Database().get_data(query,values)

        if len(result) == 0:
            return defined_error(f"event dengan id:{id} tidak ditemukan",'Not Found', 404)

        if result[0]["poster"]:
                result[0]["poster"] = f"{app.config['BASE_URL']}/static/foto/event/{result[0]['poster']}"

        data = result

        data[0]["tanggal"] = format_datetime(data[0]["tanggal"])
        data[0]["waktu_mulai"] = format_datetime(data[0]["waktu_mulai"])
        data[0]["waktu_berakhir"] = format_datetime(data[0]["waktu_berakhir"])

        return success_data(message=f"Berhasil", data=data)
    except Exception as e:
        return bad_request(str(e))

def get_by_code(kode, published_only=True):
    url_list = request.url.split('/')[:-1]
    url = ('/').join(url_list)
    try:
        if published_only:
            query = QUERY_GET_PUBLISHED_EVENT_BY_KODE
        else:
            query = QUERY_GET_EVENT_BY_KODE
        # ========================
        # ======== Action ========
        # ========================
        values = (kode,)
        result = Database().get_data(query,values)

        if len(result) == 0:
            return defined_error(f"event dengan kode:{kode} tidak ditemukan",'Not Found', 404)

        if result[0]["poster"]:
                result[0]["poster"] = f"{app.config['BASE_URL']}/static/foto/event/{result[0]['poster']}"

        data = result

        data[0]["tanggal"] = format_datetime(data[0]["tanggal"])
        data[0]["waktu_mulai"] = format_datetime(data[0]["waktu_mulai"])
        data[0]["waktu_berakhir"] = format_datetime(data[0]["waktu_berakhir"])

        return success_data(message=f"Berhasil", data=data)
    except Exception as e:
        return bad_request(str(e))

def get_by_secret_code(kode, published_only=True):
    url_list = request.url.split('/')[:-1]
    url = ('/').join(url_list)
    try:
        if published_only:
            query = QUERY_GET_PUBLISHED_EVENT_BY_KODE_RAHASIA
        else:
            query = QUERY_GET_EVENT_BY_KODE
        # ========================
        # ======== Action ========
        # ========================
        values = (kode,)
        result = Database().get_data(query,values)

        if len(result) == 0:
            return defined_error(f"event dengan kode:{kode} tidak ditemukan",'Not Found', 404)

        if result[0]["poster"]:
                result[0]["poster"] = f"{app.config['BASE_URL']}/static/foto/event/{result[0]['poster']}"

        data = result

        data[0]["tanggal"] = format_datetime(data[0]["tanggal"])
        data[0]["waktu_mulai"] = format_datetime(data[0]["waktu_mulai"])
        data[0]["waktu_berakhir"] = format_datetime(data[0]["waktu_berakhir"])

        return success_data(message=f"Berhasil", data=data)
    except Exception as e:
        return bad_request(str(e))

@event.get('/published')
def get_published_events():
    return get_all()

@event.get('/published/id/<id>')
def get_published_event_by_id(id):
    return get_by_id(id)

@event.get('/published/kode/<kode>')
def get_published_event_by_code(kode):
    return get_by_code(kode)

@event.get('/published/kode-rahasia/<kode>')
def get_published_event_by_secret_code(kode):
    return get_by_secret_code(kode)

@event.get('/')
@jwt_required()
def get_all_event():
    return get_all(published_only=False)

@event.get('/id/<id>/')
@jwt_required()
def get_event_by_id(id):
    return get_by_id(id, published_only=False)

@event.get('/kode/<kode>/')
@jwt_required()
def get_event_by_code(kode):
    return get_by_code(kode, published_only=False)

@event.post('/')
@jwt_required()
def create_event():
    user_role = get_jwt()["role"]
    user_email = get_jwt()["email"]
    try:
        # ===================================
        # ======== Handle Data Input ========
        # ===================================
        if user_role != "ADMIN":
            return defined_error("hanya admin yang dapat menambahkan event","Forbidden",403)   

        dataInput = request.json
        dataRequired = [
            "nama", "tanggal", "waktu_mulai", "waktu_berakhir", "nama_pemateri", "deskripsi",
            "poster", "deskripsi", "link_conference", "password", "jenis_event"
        ]
        for data in dataRequired:
            if dataInput == None:
                return bad_request("body request tidak boleh kosong")
            if data not in dataInput:
                return parameter_error(f"Missing {data} in Request Body")
            if dataInput[data] == None and data != "poster":
                dataInput[data] = ""
        # ====================================
        # ======== Data Preprocessing ========
        # ====================================
        
        #map and sanitize data
        nama = dataInput["nama"].strip()
        tanggal = dataInput["tanggal"].strip()
        waktu_mulai = f"{tanggal} {dataInput['waktu_mulai'].strip()}"
        waktu_berakhir = f"{tanggal} {dataInput['waktu_berakhir'].strip()}"
        nama_pemateri = dataInput["nama_pemateri"].strip()
        nama_pemateri_2 = dataInput.get("nama_pemateri_2")
        contact_whatsapp = dataInput.get("contact_whatsapp")
        email = dataInput["email"].strip()
        email_2 = dataInput.get("email_2")
        jenis_event = dataInput.get("jenis_event")
        poster = dataInput["poster"]
        deskripsi = dataInput["deskripsi"].strip()
        link_conference = dataInput["link_conference"].strip()
        password = dataInput.get("password")
        kode = uuid.uuid4().hex[:6]
        kode_rahasia = uuid.uuid4().hex[:19]

        # =================================
        # ======== Data Validation ========
        # =================================

        # validate data
        error_validator_list = event_validator(nama,nama_pemateri,nama_pemateri_2,link_conference,tanggal,waktu_mulai,waktu_berakhir,email,email_2,deskripsi,password,contact_whatsapp)
        if len(error_validator_list) > 0 :
            return defined_error(error_validator_list,'Bad Request', 400)

        validEvent = ['softskill','hardskill','centralclass']
        if jenis_event not in validEvent:
            return defined_error('jenis event tidak valid','Bad Request', 400)

        # ========================
        # ======== Action ========
        # ========================
        
        #save image
        poster_filename = None
        if poster :
            poster_filename = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_poster_event.jpg")
            save(poster, os.path.join(app.config["FOTO_EVENT"], poster_filename))
        
        values = {
            "kode":kode,
            "kode_rahasia":kode_rahasia,
            "nama":nama,
            "tanggal":tanggal,
            "waktu_mulai":waktu_mulai,
            "waktu_berakhir":waktu_berakhir,
            "nama_pemateri":nama_pemateri,
            "nama_pemateri_2":nama_pemateri_2,
            "contact_whatsapp":contact_whatsapp,
            "email":email,
            "email_2":email_2,
            "poster":poster_filename,
            "jenis":jenis_event,
            "deskripsi":deskripsi,
            "link_conference":link_conference,
            "password":password,
            "is_published": 1,
        }

        Database().save(table="event", data=values)
        
        create_log(f"{user_role} dengan email:{user_email} berhasil membuat event baru dengan kode:{kode}")

        # Send success response
        return success_data(message=f"Berhasil memasukan event baru", data=values)
    except Exception as e:
        return bad_request(str(e))

@event.post('/request')
def request_create_event():
    """
    Penjelasan :
        API ini dapat diakses oleh public
        Event yang didaftarkan pada dari endpoint ini secara default tidak akan langsung di publish di platform
    """
    try:
        # ===================================
        # ======== Handle Data Input ========
        # ===================================
        dataInput = request.json
        dataRequired = [
            "nama", "tanggal", "waktu_mulai", "waktu_berakhir", "nama_pemateri", "deskripsi",
            "poster", "deskripsi", "link_conference", "contact_whatsapp", "email"
        ]

        for data in dataRequired:
            if dataInput == None:
                return bad_request("body request tidak boleh kosong")
            if data not in dataInput:
                return parameter_error(f"Missing {data} in Request Body")
            if dataInput[data] == None and data != "poster":
                dataInput[data] = ""
        # ====================================
        # ======== Data Preprocessing ========
        # ====================================
        
        #map and sanitize data
        nama = dataInput["nama"].strip()
        tanggal = dataInput["tanggal"].strip()
        waktu_mulai = f"{tanggal} {dataInput['waktu_mulai'].strip()}"
        waktu_berakhir = f"{tanggal} {dataInput['waktu_berakhir'].strip()}"
        nama_pemateri = dataInput["nama_pemateri"].strip()
        nama_pemateri_2 = dataInput.get("nama_pemateri_2")
        contact_whatsapp = dataInput.get("contact_whatsapp")
        email = dataInput["email"].strip()
        email_2 = dataInput.get("email_2")
        poster = dataInput["poster"]
        deskripsi = dataInput["deskripsi"].strip()
        link_conference = dataInput["link_conference"].strip()
        password = dataInput.get("password")
        kode = uuid.uuid4().hex[:6]
        kode_rahasia = uuid.uuid4().hex[:19]

        # =================================
        # ======== Data Validation ========
        # =================================
        
        # validate data
        error_validator_list = event_validator(nama,nama_pemateri,nama_pemateri_2,link_conference,tanggal,waktu_mulai,waktu_berakhir,email,email_2,deskripsi,password,contact_whatsapp)
        if len(error_validator_list) > 0 :
            return defined_error(error_validator_list,'Bad Request', 400)

        # ========================
        # ======== Action ========
        # ========================
        
        #save image
        poster_filename = None
        if poster :
            poster_filename = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_poster_event.jpg")
            save(poster, os.path.join(app.config["FOTO_EVENT"], poster_filename))
    
        values = {
            "kode":kode,
            "kode_rahasia":kode_rahasia,
            "nama":nama,
            "tanggal":tanggal,
            "waktu_mulai":waktu_mulai,
            "waktu_berakhir":waktu_berakhir,
            "nama_pemateri":nama_pemateri,
            "nama_pemateri_2":nama_pemateri_2,
            "contact_whatsapp":contact_whatsapp,
            "email":email,
            "email_2":email_2,
            "poster":poster_filename,
            "deskripsi":deskripsi,
            "link_conference":link_conference,
            "password":password,
            "is_published": 0,
        }

        Database().save(table="event", data=values)
        
        create_log(f"Seseorang dengan email:{email} melakukan pengajuan event baru dengan kode:{kode}")

        # Kirim email pemberitahuan ke email admin
        template_email = render_template(
            template_name_or_list="template_email.html",
            data={
                "showGambar" : True,
                "gambarURL" : app.config["BASE_URL"] + "/" + url_for("static", filename="icons/login.png"),
                "judul" : "Pemberitahuan Event Baru",
                "deskripsi" : f"Seseorang dengan email:{email} melakukan pengajuan event baru dengan kode:{kode}",
                "buttonLink" : "http://admin.centralai.id/",
                "buttonText" : "Cek Aplikasi"
            }
        )

        # 📭 Fungsi untuk mengirim email
        if os.getenv("PRODUCT_ENVIRONMENT") == "DEV":
            email_admin = "radityo.hanif@gmail.com"
        elif os.getenv("PRODUCT_ENVIRONMENT") == "PROD":
            email_admin = "taqiyyaghazi@gmail.com"
        
        def send_email_verification():
            send_email(
                penerima=email_admin, 
                judul="Central Admin - Pemberitahuan Event Baru", 
                template=template_email
            )

        thread = threading.Thread(target=send_email_verification)
        thread.start()

        # Send success response
        return success_data(message=f"Berhasil memasukan event baru", data=values)
    except Exception as e:
        return bad_request(str(e))


def update_event(identifier,type="id"):
    user_role = get_jwt()["role"]
    user_email = get_jwt()["email"]
    try:
        if user_role != "ADMIN":
            return defined_error("hanya admin yang dapat mengupdate event","Forbidden",403)   

        dataInput = request.json
        dataRequired = [
            "nama", "tanggal", "waktu_mulai", "waktu_berakhir", "nama_pemateri", "deskripsi",
            "poster", "deskripsi", "link_conference", "contact_whatsapp", "email"
        ]

        for data in dataRequired:
            if dataInput == None:
                return bad_request("body request tidak boleh kosong")
            if data not in dataInput:
                return parameter_error(f"Missing {data} in Request Body")
            if dataInput[data] == None and data != "poster":
                dataInput[data] = ""
        # ====================================
        # ======== Data Preprocessing ========
        # ====================================
        
        #map and sanitize data
        nama = dataInput["nama"].strip()
        tanggal = dataInput["tanggal"].strip()
        waktu_mulai = f"{tanggal} {dataInput['waktu_mulai'].strip()}"
        waktu_berakhir = f"{tanggal} {dataInput['waktu_berakhir'].strip()}"
        nama_pemateri = dataInput["nama_pemateri"].strip()
        nama_pemateri_2 = dataInput.get("nama_pemateri_2")
        contact_whatsapp = dataInput.get("contact_whatsapp")
        email = dataInput["email"].strip()
        email_2 = dataInput.get("email_2")
        poster = dataInput["poster"]
        deskripsi = dataInput["deskripsi"].strip()
        link_conference = dataInput["link_conference"].strip()
        password = dataInput.get("password")
        # =================================
        # ======== Data Validation ========
        # =================================
        # check apakah terdapat data tersimpan di database
        query = QUERY_GET_EVENT_BY_ID
        if type == "kode":
            query = QUERY_GET_EVENT_BY_KODE
        values = (identifier,)
        result = Database().get_data(query,values)
        if len(result) == 0:
            return defined_error(f"event dengan {type}:{identifier} tidak ditemukan",'Not Found', 404)
        # validate data
        error_validator_list = event_validator(nama,nama_pemateri,nama_pemateri_2,link_conference,tanggal,waktu_mulai,waktu_berakhir,email,email_2,deskripsi,password,contact_whatsapp)
        if len(error_validator_list) > 0 :
            return defined_error(error_validator_list,'Bad Request', 400)
        # ========================
        # ======== Action ========
        # ========================   
        # replace image   
        check_and_remove_file(app.config["FOTO_EVENT"],result[0]["poster"])
        poster_filename = None
        if poster :
            poster_filename = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_poster_event.jpg")
            save(poster, os.path.join(app.config["FOTO_EVENT"], poster_filename))

        query = QUERY_UPDATE_EVENT_BY_ID
        if type == "kode":
            query = QUERY_UPDATE_EVENT_BY_KODE

        updated_at = datetime.datetime.now()

        values = (
            nama,tanggal, waktu_mulai, waktu_berakhir, nama_pemateri,
            nama_pemateri_2,contact_whatsapp, email, email_2,
            poster_filename,deskripsi, link_conference, password, updated_at,identifier,  
        )
        Database().update_data(query, values)
           
        create_log(f"{user_role} dengan email:{user_email} berhasil mengupdate event dengan {type}:{identifier}")

        # Send success response
        return success(message=f"Berhasil mengupdate event dengan {type}:{identifier}")
    except Exception as e:
        return bad_request(str(e))

@event.put('/id/<id>')
@jwt_required()
def update_by_id(id):
    return update_event(id,"id")
   
@event.put('/kode/<kode>')
@jwt_required()
def update_by_kode(kode):
    return update_event(kode,"kode")

def delete_event(identifier,type="id"):
    user_role = get_jwt()["role"]
    user_email = get_jwt()["email"]
    try:
        if user_role != "ADMIN":
            return defined_error("hanya admin yang dapat menghapus event","Forbidden",403)   
        # =================================
        # ======== Data Validation ========
        # =================================
        # check apakah terdapat data tersimpan di database
        query = QUERY_GET_EVENT_BY_ID
        if type == "kode":
            query = QUERY_GET_EVENT_BY_KODE
        values = (identifier,)
        result = Database().get_data(query,values)
        if len(result) == 0:
            return defined_error(f"event dengan {type}:{identifier} tidak ditemukan",'Not Found', 404)
        # ========================
        # ======== Action ========
        # ========================   
        check_and_remove_file(app.config["FOTO_EVENT"],result[0]["poster"])
        updated_at = datetime.datetime.now()
        query = QUERY_DELETE_EVENT_BY_ID
        if type == "kode":
            query = QUERY_DELETE_EVENT_BY_KODE
        values = (updated_at,identifier,)
        Database().update_data(query, values)        
        create_log(f"{user_role} dengan email:{user_email} berhasil menghapus event dengan {type}:{identifier}")
        # Send success response
        return success(message=f"Berhasil menghapus event dengan {type}:{identifier}")
    except Exception as e:
        return bad_request(str(e))


@event.delete('/id/<id>')
@jwt_required()
def delete_by_id(id):
    return delete_event(id,"id")

@event.delete('/kode/<kode>')
@jwt_required()
def delete_by_kode(kode):
    return delete_event(kode,"kode")
  
@event.put('<action>/<kode>')
@jwt_required()
def publisher(action,kode):
    if action not in ["publish", "unpublish"]:
        return bad_request('action not valid')
    
    user_role = get_jwt()["role"]
    user_email = get_jwt()["email"]
    # try:
    if user_role != "ADMIN":
        return defined_error("hanya admin yang dapat mengupdate event","Forbidden",403)   

    if action == "publish":
        query = QUERY_PUBLISH_EVENT
    elif action == "unpublish":
        query = QUERY_UNPUBLISH_EVENT
    
    updated_at = datetime.datetime.now()
    values = (updated_at,kode, )
    Database().update_data(query, values)
        
    create_log(f"{user_role} dengan email:{user_email} berhasil {action} event dengan kode:{kode}")

    # Cek apakah webinar bukan di upload oleh admin
    query = "SELECT email, nama, kode_rahasia FROM event WHERE kode=%s"
    values = (kode, )
    result = Database().get_data(query, values)
    if len(result) == 0:
        return defined_error("Data event tidak ditemukan", "Not Found", 404)
    email_narasumber = result[0]['email']
    judul_webinar = result[0]['nama']
    kode_rahasia = result[0]['kode_rahasia']
    
    # Info ke email narasumber apabila eventnya di publish/unpublish
    if(email_narasumber != ""):
        
        # Susun deskripsi email berdasarkan action
        if action == "publish":
            link_form_kehadiran = f"https://centralai.id/event/kehadiran/{kode_rahasia}"
            deskripsi = f"Event dengan judul {judul_webinar} sudah di {action} di Platfrom Central AI, berikut link form kehadiran peserta {link_form_kehadiran} yang bisa kamu share ketika kegiatan berlangsung agar peserta dapat mendapatkan e-sertifikat",
        elif action == "unpublish":
            deskripsi = f"Event dengan judul {judul_webinar} sudah di {action} dari Platfrom Central AI",

        # Kirim email pemberitahuan ke email narasumber
        template_email = render_template(
            template_name_or_list="template_email.html",
            data={
                "showGambar" : True,
                "gambarURL" : app.config["BASE_URL"] + "/" + url_for("static", filename="icons/published.png"),
                "judul" : f"Pemberitahuan Event Kamu Telah di {action}",
                "deskripsi" : f"{deskripsi}",
                "buttonLink" : f"https://centralai.id/event/",
                "buttonText" : "Lihat Event"
            }
        )
        # 📭 Fungsi untuk mengirim email
        def send_email_verification():
            send_email(
                penerima=email_narasumber, 
                judul="Central AI - Informasi Kepada Narasumber Event", 
                template=template_email
            )

        thread = threading.Thread(target=send_email_verification)
        thread.start()

    # Send success response
    return success(message=f"Berhasil {action} event dengan kode:{kode}")
    # except Exception as e:
    #     return bad_request(str(e))
