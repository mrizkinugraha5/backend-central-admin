import os
from flask import Blueprint, request, render_template, url_for
from flask import current_app as app
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, JWTManager

from ...queries import *
from ...dbFunctions import Database
from ...utilities import *

from app_name.helpers.validator import *
from app_name.helpers.function import *

admin = Blueprint(
    name='admin', 
    import_name=__name__, 
    url_prefix='/admin'
)

@admin.post('/')
def create_admin():
    try :
        # ===================================
        # ======== Handle Data Input ========
        # ===================================
        
        # validasi header apakah request memuat Admin-Key
        adminKey = request.headers.get("Admin-Key")
        if adminKey == None or adminKey != os.getenv("ADMIN_KEY"):
            return defined_error("Admin Key tidak valid")
        
        # validasi body request
        dataInput = request.json
        dataRequired = ["nama", "password", "email"]
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
        password = dataInput["password"].strip()
        
        # =================================
        # ======== Data Validation ========
        # =================================
        
        #validasi apakah nama, email, dan password sudah sesuai format
        error_list = regist_validator(nama,email,password)
        if len(error_list) != 0:
            return defined_error(error_list,'Bad Request', 400)
        
        # Cek apakah email sudah terdaftar ?
        query = QUERY_CHECK_EMAIL_ADMIN
        values = (email, )
        result = Database().get_data(query, values)
        if len(result) != 0:
            return defined_error(f"email {email} sudah terdaftar", 'Bad Request', 400)

        # ========================
        # ======== Action ========
        # ========================
        # Insert data to database
        values = {
            "nama" : nama,
            "email" : email,
            "password" : hashPassword(password),
        }
        Database().save(table="admin", data=values)

        #membuat log
        create_log(f"ADMIN baru dengan email:{email} berhasil dibuat")

        #return response
        return success(message=f"Berhasil membuat admin baru")

    except Exception as e:
        return bad_request(str(e))

@admin.post('/login')
def admin_login():
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
    query = QUERY_CHECK_PASSWORD_ADMIN
    values = (email, )
    result = Database().get_data(query, values)
    if len(result) == 0:
        return defined_error(f"Akun tidak valid",'Bad Request', 400)
    
    savedPassword = result[0]['password']
    validPassword = checkPassword(savedPassword,password)

    if not validPassword:
        return defined_error(f"Akun tidak valid", 'Bad Request', 400)

    # ========================
    # ======== Action ========
    # ========================
    
    # Create jwt_payload
    jwt_payload = {
        "id" : result[0]["id"],
        "role" : "ADMIN",
        "email" : email,
        "nama" : result[0]["nama"]
    }
    
    # Create access_token by email & jwt_payload
    access_token = create_access_token(email, additional_claims=jwt_payload)

    # Insert access_token to jwt_payload
    jwt_payload["access_token"] = access_token

    # membuat log

    # Send success response
    return success_data(message="Berhasil login", data=jwt_payload)