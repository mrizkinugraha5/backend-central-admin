from app_name.dbFunctions import Database
from app_name.queries import *
from app_name.utilities import *
import os
from flask import render_template,url_for
from flask import current_app as app
import datetime

def create_log(log):
    query = QUERY_CREATE_LOG
    val = (log,)
    Database().insert_data(query,val)

def check_and_remove_file(appConfig,savedPath):
    if savedPath and  os.path.exists(os.path.join(appConfig, savedPath)):
        os.remove(os.path.join(appConfig, savedPath))

def format_portofolio_data(url,result,i=0):
    image_list = ['thumbnail','foto_1','foto_2','foto_3']

    for field in image_list:
        if result[i][field]:
            result[i][field] = f"{url}/media/{result[i][field]}"

    if result[i]["foto"]:
        result[i]["foto"] = f"{url[:-11]}/user/media/{result[i]['foto']}"

    
    created_at = format_datetime(result[i]["created_at"])

    status = "Sudah disetujui" if result[i]["approved"] == 1 else "Belum disetujui"

    return {
            "id" : result[i]["id"],
            "judul" : result[i]["judul"],
            "deskripsi_singkat" :  result[i]["deskripsi_singkat"],
            "deskripsi_lengkap" :  result[i]["deskripsi_lengkap"],
            "kategori" :  result[i]["kategori"],
            "approved" :  status,
            "thumbnail" :  result[i]["thumbnail"],
            "foto_1" :  result[i]["foto_1"],
            "foto_2" :  result[i]["foto_2"],
            "foto_3" :  result[i]["foto_3"],
            "owner" : {
                "nama":result[i]["nama"],
                "foto":result[i]["foto"],
                "linkedin":result[i]["linkedin"],
                "instagram":result[i]["instagram"],
            },
            "created_at": created_at
        }

def instant_QR(id_event,email):
    query = QUERY_GET_KEHADIRAN_BY_EMAIL_AND_EVENT_ID
    values = (id_event,email,)
    result = Database().get_data(query, values)
    if len(result) == 0:
        return False
            
    payload = result[0]
    del payload["link_sertifikat"]
    payload['tanggal'] = payload['tanggal'].strftime("%d-%m-%Y")

    qr_code = generate_qr_code(payload)
  
    return qr_code

def save_sertifikat(url_sertifikat,kode_kehadiran):
    query = QUERY_UPDATE_KEHADIRAN_BY_KODE
    values = (url_sertifikat,kode_kehadiran)
    Database().update_data(query, values)
    return True


def is_date(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False  

def is_datetime(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False     

def create_token(id_user):
	token = f"{random_string_number_only(5)}{random_string(3).upper()}{random_string_number_only(8)}{random_string(12)}{random_string_number_only(5)}"
	# Cek apakah token sudah terdaftar pada database
	query = "SELECT id FROM auth WHERE token = %s"
	values = (token, )
	if len(Database().get_data(query, values)) != 0:
		create_token(id_user) # Jika token sudah terdaftar generate lagi token baru (fungsi rekrusif)
	else:
		# Cek apakah data dari id_user sudah ada, jika iya=update | tidak=buat_baru
		query = "SELECT id FROM auth WHERE id_user = %s"
		values = (id_user, )
		result = Database().get_data(query, values)
		if(len(result) != 0):
			# Update
			query = "UPDATE auth SET token=%s WHERE id_user=%s"
			values = (token, id_user)
			Database().insert_data(query, values)
		else:
			# Insert
			query = "INSERT INTO auth (id_user, token) values (%s,%s)"
			values = (id_user, token)
			Database().insert_data(query, values)
	return token

    
