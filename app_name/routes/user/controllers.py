from cmath import tan
from datetime import datetime
from flask import Blueprint, request
from flask import current_app as app
from time import strftime
import os
import threading
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, JWTManager

from ...dbFunctions import Database
from ...utilities import *
from ...queries import *
from app_name.helpers.validator import *
from app_name.helpers.function import *

user = Blueprint(
    name='user', 
    import_name=__name__, 
    static_folder = '../../static/foto/user', 
    static_url_path="/media",
    url_prefix='/user'
)

@user.post('/')
def create_user():
    try :
        dataInput = request.json
        dataRequired = ["nama", "email", "password", "is_pengusaha", "nomor_telepon", "nama_usaha", "bidang_usaha", "alamat_usaha"]
        
        for data in dataRequired:
            if dataInput == None:
                return bad_request("Body request tidak boleh kosong")
            if data not in dataInput:
                return parameter_error(f"Tidak ada data {data} pada Body request")
            if dataInput[data] == None:
                dataInput[data] = "" 
                
        nama = dataInput["nama"].strip().title()
        email = dataInput["email"].strip().lower() 
        password = dataInput["password"].strip()
        is_pengusaha = dataInput["is_pengusaha"]
        nomor_telepon = dataInput["nomor_telepon"]
        nama_usaha = dataInput["nama_usaha"]
        bidang_usaha = dataInput["bidang_usaha"]
        alamat_usaha = dataInput["alamat_usaha"]

        if is_pengusaha and (not nama_usaha or not bidang_usaha or not alamat_usaha):
            return defined_error("nama_usaha, bidang_usaha, alamat_usaha tidak boleh kosong",'Bad Request', 400)
 
        #validasi apakah nama, email, dan password sudah sesuai format
        error_list = account_validator(nama,email,password, nomor_telepon, is_pengusaha, nama_usaha, bidang_usaha, alamat_usaha)
        if len(error_list) != 0:
            return defined_error(error_list,'Bad Request', 400)
        
        # Cek apakah email sudah terdaftar ?
        query = QUERY_CHECK_EMAIL
        values = (email, )
        result = Database().get_data(query, values)
        if len(result) != 0:
            return defined_error(f"email {email} sudah terdaftar",'Bad Request', 400)

        # Insert data to database
        values = {
            "nama" : nama,
            "email" : email,
            "is_pengusaha" : is_pengusaha,
            "nomor_telepon": nomor_telepon,
            "password" : hashPassword(password),
        }

        if is_pengusaha:
            values = {
                "nama" : nama,
                "email" : email,
                "is_pengusaha" : is_pengusaha,
                "nama_usaha" : nama_usaha,
                "bidang_usaha" : bidang_usaha,
                "alamat_usaha": alamat_usaha,
                "nomor_telepon": nomor_telepon,
                "password" : hashPassword(password),
            }


        id_user = Database().saveReturn(table="user", data=values)

        token = create_token(id_user)

        template_email = render_template(
            template_name_or_list="template_email.html",
            data={
                "showGambar" : True,
                "gambarURL" : app.config["BASE_URL"] + "/" + url_for("static", filename="icons/login.png"),
                "judul" : "Verifikasi Akun Email",
                "deskripsi" : "Terima kasih telah bergabung di aplikasi Central Admin. Silahkan aktifkan akun anda dengan menekan tombol dibawah ini",
                "buttonLink" : app.config["WEB_UTAMA_URL"] + f"/auth/email/{token}",
                "buttonText" : "Verifikasi Email"
            }
        )

        # 📭 Fungsi untuk mengirim verfikasi email pengguna baru
        def send_email_verification():
            send_email(
                penerima=email, 
                judul="Verifikasi Akun Email Central Admin", 
                template=template_email
            )
        
        thread = threading.Thread(target=send_email_verification)
        thread.start()

        #membuat log
        create_log(f"create user baru dengan email:{email}")

        # Send success response
        return success(message=f"Berhasil mendaftarkan user baru dengan email {email}")
    except Exception as e:
        return bad_request(str(e))

@user.post('/login')
def user_login():
    # ===================================
    # ======== Handle Data Input ========
    # ===================================
    dataInput = request.json
    dataRequired = ["password", "email"]
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

    email = dataInput["email"].strip().lower()
    password = dataInput["password"].strip()

    error_list = login_validator(email,password)
    if len(error_list) != 0:
        return defined_error(error_list,'Bad Request', 400)

    
    # =================================
    # ======== Data Validation ========
    # =================================
    
    # Cek apakah email dan password benar ?
    query = QUERY_CHECK_PASSWORD
    values = (email, )
    result = Database().get_data(query, values)
    if len(result) == 0:
        return defined_error(f"Akun tidak valid",'Bad Request', 400)
    
    savedPassword = result[0]['password']
    validPassword = checkPassword(savedPassword,password)
    
    if not validPassword:
        return defined_error(f"Akun tidak valid",'Bad Request', 400)

    # ========================
    # ======== Action ========
    # ========================
    
    # Create jwt_payload
    jwt_payload = {
        "id" : result[0]["id"],
        "role" : "USER",
        "email" : email,
        "nama" : result[0]["nama"]
    }
    
    # Create access_token by email & jwt_payload
    access_token = create_access_token(email, additional_claims=jwt_payload)

    # Insert access_token to jwt_payload
    jwt_payload["access_token"] = access_token


    # Send success response
    return success_data(message="Berhasil login", data=jwt_payload)

@user.get('/myprofile')
@jwt_required()
def get_data_current_user():  
    currentUser_id = str(get_jwt()["id"])
    currentUser_email = str(get_jwt()["email"])
    try:
        query = QUERY_GET_CURRENT_PROFILE
        values = (currentUser_id,currentUser_email, )
        result = Database().get_data(query, values)
        if len(result) == 0:
            return defined_error("Data user tidak ditemukan",'Not Found', 404)
        else:
            # ====================================
            # ======== Data Preprocessing ========
            # ====================================
            if result[0]['foto']:
                result[0]['foto'] = f"{request.url[:-10]}/media/{result[0]['foto']}"
                
            # ========================
            # ======== Action ========
            # ========================

            return success_data(message="Berhasil mengambil data user", data=result[0])
    except Exception as e:
        return bad_request(str(e))

@user.put('/myprofile')
@jwt_required()
def update_current_user_profile():
    currentUser_id = str(get_jwt()["id"])
    currentUser_email = str(get_jwt()["email"])
    try:
    # ===================================
    # ======== Handle Data Input ========
    # ===================================
        dataInput = request.json
        dataRequired = [
        "nama", "foto", "jenis_kelamin", 
        "tanggal_lahir","is_pengusaha","nama_usaha",
        "bidang_usaha","alamat_usaha","nomor_telepon", "linkedin", 
        "instagram", "riwayat_kerja", "alamat", 
        "password_baru","confirm_password", "password_lama"
        ]

        for data in dataRequired:
            if dataInput == None:
                return bad_request("Body request tidak boleh kosong")
            if data not in dataInput:
                return parameter_error(f"Tidak ada data {data} pada Body request")
            if dataInput[data] == None and data != "foto":
                dataInput[data] = ""

        # ====================================
        # ======== Data Preprocessing ========
        # ====================================
           
        # mapping and trim data  
        nama = dataInput["nama"].strip().title()
        foto = dataInput["foto"]
        jenis_kelamin = dataInput["jenis_kelamin"].strip()
        tanggal_lahir = dataInput["tanggal_lahir"].strip() 
        is_pengusaha = dataInput["is_pengusaha"] 
        nama_usaha = dataInput["nama_usaha"].strip() 
        bidang_usaha = dataInput["bidang_usaha"].strip() 
        alamat_usaha = dataInput["alamat_usaha"].strip() 
        nomor_telepon = dataInput["nomor_telepon"].strip()
        linkedin = dataInput["linkedin"].strip() 
        instagram = dataInput["instagram"].strip() 
        riwayat_kerja = dataInput["riwayat_kerja"].strip() 
        alamat = dataInput["alamat"].strip()
        password_baru = dataInput["password_baru"].strip() 
        confirm_password = dataInput["confirm_password"].strip()
        password_lama = dataInput["password_lama"].strip() 

        # =================================
        # ======== Data Validation ========
        # =================================
        if is_pengusaha and (not nama_usaha or not bidang_usaha or not alamat_usaha):
            return defined_error("nama_usaha, bidang_usaha, alamat_usaha tidak boleh kosong",'Bad Request', 400)

        query = QUERY_GET_ACCOUNT_USER
        values = (currentUser_id,currentUser_email )

        result = Database().get_data(query, values)
        if len(result) == 0:
            return defined_error("Data user tidak ditemukan",'Not Found', 404)
            
        # Menyimpan foto pada server
        #check apakah ada password baru pada body request
        password_field = [password_baru,password_lama,confirm_password]
        if password_baru != '':
            if confirm_password == '':
                return defined_error("confirm password kosong",'Bad Request', 400)
            if password_lama == '':
                return defined_error("password lama kosong",'Bad Request', 400)
       
        ready_to_update_password = password_field.count('') == 0 

        password_tersimpan = result[0]['password']

        success_update_password = ""

        profile_error_list = profile_validator(nama,jenis_kelamin,nomor_telepon,instagram,linkedin,is_pengusaha, nama_usaha, bidang_usaha, alamat, riwayat_kerja, tanggal_lahir, alamat_usaha)
        if len(profile_error_list) != 0:
            return defined_error(profile_error_list,'Bad Request', 400)

        foto_filename = result[0]["foto"]
        if foto:
            foto_filename = secure_filename(strftime("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_user.jpg")
            check_and_remove_file(app.config["FOTO_USER"],result[0]["foto"])
            save(foto, os.path.join(app.config["FOTO_USER"], foto_filename))
            
        # ========================
        # ======== Action ========
        # ======================== 
        if ready_to_update_password:
            error_list = update_password_validator(password_baru,confirm_password,password_lama,password_tersimpan)
            if len(error_list) != 0:
                return defined_error(error_list,'Bad Request', 400)
            else:
                hashedPassword = hashPassword(password_baru)
                query = QUERY_UPDATE_PASSWORD
                values = (hashedPassword,currentUser_id,currentUser_email, )
                Database().update_data(query, values)
                create_log(f"mengubah password user dengan id:{currentUser_id}")
                success_update_password = ' dan password berhasil diubah'

        update_at= datetime.datetime.now()

        query = QUERY_GET_CURRENT_PROFILE
        values = (currentUser_id,currentUser_email)

        result = Database().get_data(query, values)
        if len(result) == 0:
            return defined_error("Data user tidak ditemukan",'Not Found', 404)

        data_sebelum = json.dumps(result[0],default=str)

        data_sesudah = {
            "nama": nama, 
            "is_pengusaha": is_pengusaha, 
            "bidang_usaha": bidang_usaha, 
            "nama_usaha": nama_usaha, 
            "tanggal_lahir": tanggal_lahir, 
            "foto": foto_filename, 
            "jenis_kelamin": jenis_kelamin, 
            "nomor_telepon": nomor_telepon, 
            "linkedin": linkedin, 
            "instagram": instagram , 
            "alamat":alamat, 
            "riwayat_kerja": riwayat_kerja
        }       

        # Update data to database
        query = QUERY_UPDATE_PROFILE
        values = (
            nama, tanggal_lahir,foto_filename, 
            jenis_kelamin, is_pengusaha, bidang_usaha,
            nama_usaha,alamat_usaha,nomor_telepon, linkedin, 
            instagram, alamat, riwayat_kerja,
            update_at,currentUser_id,currentUser_email, 
        )
        Database().update_data(query, values)

        #membuat log
        create_log(f"mengubah profile user dengan id:{currentUser_id} dari:{data_sebelum} menjadi:{data_sesudah}")

        return success(f'profile berhasil di update{success_update_password}')     

    except Exception as e:
        return bad_request(str(e))