from wsgiref.util import request_uri
from flask import Blueprint, request
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

portofolio = Blueprint(
    name='portofolio',
    import_name=__name__,  
    static_folder = '../../static/foto/portofolio', 
    static_url_path="/media",
    url_prefix='/portofolio'
)

# Create portofolio =====================
@portofolio.post('/')
@jwt_required()
def create_portfolio():  
    currentUser_id = str(get_jwt()["id"])
    currentUser_email = str(get_jwt()["email"])
    currentUser_role = str(get_jwt()["role"])
    try:
        if currentUser_role != "USER":
            return defined_error("hanya user yang dapat menambahkan portofolio","Forbidden",403)    
        # ===================================
        # ======== Handle Data Input ========
        # ===================================
        dataInput = request.json
        dataRequired = ["judul", "deskripsi_singkat", 
        "deskripsi_lengkap", "id_kategori", "thumbnail","foto_1", "foto_2", "foto_3"]

        # checking data input
        image_field = ["thumbnail","foto_1","foto_2","foto_3"]
        for data in dataRequired:
            if dataInput == None:
                return bad_request("body request tidak boleh kosong")
            if data not in dataInput:
                return parameter_error(f"Missing {data} in Request Body")
            if dataInput[data] == None and data not in image_field:
                dataInput[data] = ""

        # ====================================
        # ======== Data Preprocessing ========
        # ====================================

        # mapping and sanitize data input 
        judul = dataInput["judul"].strip().title()
        deskripsi_singkat = dataInput["deskripsi_singkat"].strip()
        deskripsi_lengkap = dataInput["deskripsi_lengkap"].strip()
        id_kategori = dataInput["id_kategori"]
        thumbnail = dataInput["thumbnail"]
        foto_1 = dataInput["foto_1"]
        foto_2 = dataInput["foto_2"]
        foto_3 = dataInput["foto_3"]
  
        #validate judul dan deskripsi
        error_list = portofolio_validator(judul,deskripsi_singkat,deskripsi_lengkap)
        if len(error_list) != 0:
            return defined_error(error_list,'Bad Request', 400)

        # validate kategori
        query = QUERY_GET_KATEGORI
        values = (id_kategori,)
        result = Database().get_data(query, values)
        if len(result) == 0:
            return defined_error("Data kategori tidak ditemukan",'Not Found', 404)

        # saving portfolio pictures 
        filename_thumbnail = None
        filename1 = None
        filename2 = None
        filename3 = None

        if thumbnail:
            filename_thumbnail = secure_filename(strftime(("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_porto.jpg"))  
            save(thumbnail,  os.path.join(app.config["FOTO_PORTOFOLIO"], filename_thumbnail))
        if foto_1:
            filename1 = secure_filename(strftime(("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_porto.jpg"))  
            save(foto_1,  os.path.join(app.config["FOTO_PORTOFOLIO"], filename1))
        if foto_2:
            filename2 = secure_filename(strftime(("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_porto.jpg"))
            save(foto_2,  os.path.join(app.config["FOTO_PORTOFOLIO"], filename2))
        if foto_3:
            filename3 = secure_filename(strftime(("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_porto.jpg"))
            save(foto_3,  os.path.join(app.config["FOTO_PORTOFOLIO"], filename3))

        # ========================
        # ======== Action ========
        # ========================
        
        # Insert data to database
        values = {
            "id_user" : currentUser_id,
            "judul" : judul,
            "deskripsi_singkat" : deskripsi_singkat,
            "deskripsi_lengkap" : deskripsi_lengkap,
            "id_kategori" : id_kategori,
            "thumbnail" : filename_thumbnail,
            "foto_1" : filename1,
            "foto_2" : filename2,
            "foto_3" : filename3
        }
        Database().save(table="portofolio", data=values)
        
        create_log(f"{currentUser_role} dengan email:{currentUser_email} berhasil menambahkan portofolio")

        # Send success response
        return success_data(message=f"Berhasil memasukan portofolio baru", data=values)

    except Exception as e:
        return bad_request(str(e))

# get portofolio by id =====================
@portofolio.get('id/<id>')
def get_portfolio_by_id(id):
    url_list = request.url.split('/')[:-2]
    url = ('/').join(url_list)
    try:
        # Ambil id_user dari jwt
        query = QUERY_GET_PORTOFOLIO_BY_ID
        values = (id,)
        result = Database().get_data(query,values)

        if len(result) == 0:
            return defined_error(f"portofolio dengan id:{id} tidak ditemukan",'Not Found', 404)

        data = format_portofolio_data(url,result)
        del data["id"]

        return success_data(message="Berhasil", data=data)

    except Exception as e:
        return bad_request(str(e))

# get all approved portofolio
@portofolio.get('/')
def get_portfolio():
    offset = request.args.get('page')
    limit = request.args.get('row')
    search = request.args.get('search')
    category = request.args.get('category')
    limit  = int(limit) if limit else 1000
    offset  = (int(offset) - 1) * limit if offset else 0
    search = f"%{search}%" if search else "%%"
    url_list = request.url.split('/')[:-1]
    url = ('/').join(url_list)
    
    query = QUERY_GET_ALL_PORTOFOLIO
    values = (search,1,limit,offset)

    if category != None:
        values = (category,1,limit,offset)
        query = QUERY_GET_PORTOFOLIO_BY_CATEGORY
    
    try:
        result = Database().get_data(query,values)

        if len(result) == 0:
            return defined_error(f"belum ada portofolio",'Not Found', 404)
        
        all_portofolio = []
        for i in range(len(result)): 
            data = format_portofolio_data(url,result,i)
            all_portofolio.append(data)
        
        return success_data(message="Berhasil", data=all_portofolio)

    except Exception as e:
        return bad_request(str(e))

#get unapproved portofolio (admin only)
@portofolio.get('/all')
@jwt_required()
def get_portfolio_unapproved():
    currentUser_role = get_jwt()["role"]
    currentUser_email = str(get_jwt()["email"])
    offset = request.args.get('page')
    limit = request.args.get('row')
    search = request.args.get('search')
    limit  = int(limit) if limit else 1000
    offset  = (int(offset) - 1) * limit if offset else 0
    search = f"%{search}%" if search else "%%"
    category = request.args.get('category')
    url_list = request.url.split('/')[:-1]
    url = ('/').join(url_list)
    try:
        if currentUser_role != "ADMIN":
            return defined_error(f"Hanya admin yang dapat mengakses",'Forbidden', 403)

        query = QUERY_ADMIN_GET_ALL_PORTOFOLIO
        values = (search,limit,offset)
        
        if category != None:
            values = (category,limit,offset)
            query = QUERY_ADMIN_GET_PORTOFOLIO_BY_CATEGORY
        
        result = Database().get_data(query,values)

        if len(result) == 0:
            return defined_error(f"belum ada portofolio",'Not Found', 404)
        
        all_portofolio = []
        for i in range(len(result)):
            data = format_portofolio_data(url,result,i)
            all_portofolio.append(data)

        return success_data(message="Berhasil", data=all_portofolio)

    except Exception as e:
        return bad_request(str(e))

#get current logged in user portofolio
@portofolio.get('/myportofolio')
@jwt_required()
def get_myportfolio():
    user_role = get_jwt()["role"]
    user_id = get_jwt()["id"]
    currentUser_email = str(get_jwt()["email"])
    offset = request.args.get('page')
    limit = request.args.get('row')
    approved = request.args.get('approved')
    
    limit  = int(limit) if limit else 10
    offset  = (int(offset) - 1) * limit if offset else 0

    url_list = request.url.split('/')[:-1]
    url = ('/').join(url_list)
    try:
        if user_role != "USER":
            return defined_error(f"Hanya user yang dapat mengakses",'Forbidden', 403)

        query = QUERY_GET_ALL_PORTOFOLIO_BY_USER_ID
        values = (user_id,limit,offset,)
        result = Database().get_data(query,values)

        if len(result) == 0:
            return defined_error(f"belum ada portofolio",'Not Found', 404)
        
        all_portofolio = []
        for i in range(len(result)):
            data = format_portofolio_data(url,result,i)
            all_portofolio.append(data)

        return success_data(message="Berhasil", data=all_portofolio)

    except Exception as e:
        return bad_request(str(e))

@portofolio.put('/<id>')
@jwt_required()
def update_portfolio(id):  
    currentUser_id = str(get_jwt()["id"])
    currentUser_role = str(get_jwt()["role"])
    currentUser_email = str(get_jwt()["email"])
    try:  
        if currentUser_role != "USER":
            return defined_error("hanya user yang dapat mengupdate portofolio",'Forbidden', 403)   
        # ===================================
        # ======== Handle Data Input ========
        # ===================================
        dataInput = request.json
        dataRequired = ["judul", "deskripsi_singkat", 
        "deskripsi_lengkap", "id_kategori", "thumbnail","foto_1", "foto_2", "foto_3"]

        # checking data input
        image_field = ["thumbnail","foto_1","foto_2","foto_3"]
        for data in dataRequired:
            if dataInput == None:
                return bad_request("body request tidak boleh kosong")
            if data not in dataInput:
                return parameter_error(f"Missing {data} in Request Body")
            if dataInput[data] == None and data not in image_field:
                dataInput[data] = ""
        # ====================================
        # ======== Data Preprocessing ========
        # ====================================

        # get data by id
        query = QUERY_GET_PORTOFOLIO_BY_ID
        values = (id,)
        result = Database().get_data(query, values)
        if len(result) == 0:
            return defined_error(f"portofolio id:{id} tidak ditemukan",'Not Found', 404)

        if int(result[0]["id_user"]) != int(currentUser_id):
            return defined_error(f"anda tidak punya akses untuk mengubah data",'Forbidden', 403)

        # mapping and sanitize data input 
        judul = dataInput["judul"].strip().title()
        deskripsi_singkat = dataInput["deskripsi_singkat"].strip()
        deskripsi_lengkap = dataInput["deskripsi_lengkap"].strip()
        id_kategori = dataInput["id_kategori"]
        thumbnail = dataInput["thumbnail"]
        foto_1 = dataInput["foto_1"]
        foto_2 = dataInput["foto_2"]
        foto_3 = dataInput["foto_3"]
  
        #validate judul dan deskripsi
        error_list = portofolio_validator(judul,deskripsi_singkat,deskripsi_lengkap)
        if len(error_list) != 0:
            return defined_error(error_list,'Bad Request', 400)

        # validate kategori
        query = QUERY_GET_KATEGORI
        values = (id_kategori,)
        result_kategori = Database().get_data(query, values)
        if len(result_kategori) == 0:
            return defined_error("Data kategori tidak ditemukan",'Not Found', 404)

        #remove saved image
        check_and_remove_file(app.config["FOTO_PORTOFOLIO"],result[0]["thumbnail"])
        check_and_remove_file(app.config["FOTO_PORTOFOLIO"],result[0]["foto_1"])
        check_and_remove_file(app.config["FOTO_PORTOFOLIO"],result[0]["foto_2"])
        check_and_remove_file(app.config["FOTO_PORTOFOLIO"],result[0]["foto_3"])
        

        # saving portfolio pictures 
        filename_thumbnail = None
        filename1 = None
        filename2 = None
        filename3 = None

        if thumbnail:
            filename_thumbnail = secure_filename(strftime(("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_porto.jpg"))  
            save(thumbnail,  os.path.join(app.config["FOTO_PORTOFOLIO"], filename_thumbnail))
             
        if foto_1:
            filename1 = secure_filename(strftime(("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_porto.jpg"))  
            save(foto_1,  os.path.join(app.config["FOTO_PORTOFOLIO"], filename1))
      
        if foto_2:
            filename2 = secure_filename(strftime(("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_porto.jpg"))
            save(foto_2,  os.path.join(app.config["FOTO_PORTOFOLIO"], filename2))
    
        if foto_3:
            filename3 = secure_filename(strftime(("%Y-%m-%d %H:%M:%S")+"_"+str(random_string_number_only(5))+"_foto_porto.jpg"))
            save(foto_3,  os.path.join(app.config["FOTO_PORTOFOLIO"], filename3))
       
        # ========================
        # ======== Action ========
        # ========================
        updated_at = datetime.datetime.now()
        # Insert data to database
        query = QUERY_UPDATE_PORTOFOLIO
        values = (
            judul, deskripsi_singkat, deskripsi_lengkap, id_kategori, 
            filename_thumbnail, filename1, filename2, filename3, updated_at ,id
        )
        Database().update_data(query, values)

        create_log(f"{currentUser_role} dengan email:{currentUser_email} melakukan update portofolio dengan id:{id}")
        # Send success response
        return success(f'portofolio berhasil di update')    
    
    except Exception as e:
        return bad_request(str(e))

@portofolio.put('<action>/<id>')
@jwt_required()
def approver(action, id):
    if action not in ["approve", "unapprove"]:
        return bad_request('action not valid')  
    
    currentUser_role = str(get_jwt()["role"])
    currentUser_email = str(get_jwt()["email"])
    try:  
        if currentUser_role != "ADMIN":
            return defined_error("hanya admin yang dapat approve portofolio",'Forbidden', 403)   

        # get data by id
        query = QUERY_GET_PORTOFOLIO_BY_ID
        values = (id,)
        result = Database().get_data(query, values)
        if len(result) == 0:
            return defined_error(f"portofolio id:{id} tidak ditemukan",'Not Found', 404)

        # Insert data to database
        query = QUERY_APPROVE_PORTOFOLIO
        if action == "approve":
            values = ('1',id,)
        elif action == "unapprove":
            values = ('0',id,)
        Database().update_data(query, values)

        create_log(f"{currentUser_role} dengan email:{currentUser_email} approve portofolio dengan id:{id}")

        # Send success response
        return success(f'portofolio berhasil di approve')    
    
    except Exception as e:
        return bad_request(str(e))

@portofolio.delete('/<id>')
@jwt_required()
def delete_portfolio(id):  
    currentUser_id = str(get_jwt()["id"])
    currentUser_role = str(get_jwt()["role"])
    currentUser_email = str(get_jwt()["email"])
    try:  
        if currentUser_role != "USER":
            return defined_error("hanya user yang dapat menghapus portofolio",'Forbidden', 403)   
        # ===================================
        # ======== Handle Data Input ========
        # ===================================
   
        # get data by id
        query = QUERY_GET_PORTOFOLIO_BY_ID
        values = (id,)
        result = Database().get_data(query, values)
        if len(result) == 0:
            return defined_error(f"portofolio id:{id} tidak ditemukan",'Not Found', 404)

        if int(result[0]["id_user"]) != int(currentUser_id):
            return defined_error(f"anda tidak punya akses untuk mengubah data",'Forbidden', 403)

        # delete portfolio pictures 
        filename_thumbnail = result[0]["thumbnail"]
        filename1 = result[0]["foto_1"]
        filename2 = result[0]["foto_2"]
        filename3 = result[0]["foto_3"]

        if filename_thumbnail:
            check_and_remove_file(app.config["FOTO_PORTOFOLIO"],filename_thumbnail)

        if filename1:
            check_and_remove_file(app.config["FOTO_PORTOFOLIO"],filename1)

        if filename2:  
            check_and_remove_file(app.config["FOTO_PORTOFOLIO"],filename2)

        if filename3:
            check_and_remove_file(app.config["FOTO_PORTOFOLIO"],filename3)

        # ========================
        # ======== Action ========
        # ========================
        
        # Insert data to database
        updated_at = datetime.datetime.now()
        query = QUERY_DELETE_PORTOFOLIO
        values = (updated_at,id,)
        Database().update_data(query, values)

        
        create_log(f"{currentUser_role} dengan email:{currentUser_email} menghapus portofolio dengan id:{id}")

        # Send success response
        return success(f'portofolio berhasil di hapus')    
    
    except Exception as e:
        return bad_request(str(e))





