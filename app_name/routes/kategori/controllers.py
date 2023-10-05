from flask import Blueprint, request, redirect
from flask_jwt_extended import get_jwt, jwt_required
from ...dbFunctions import Database
from ...utilities import *
from ...queries import *
from app_name.helpers.function import *

kategori = Blueprint(
    name='kategori',
    import_name=__name__,
    url_prefix='/kategori'
)

@kategori.post('/')
@jwt_required()
def create_kategori():
    currentRole = str(get_jwt()["role"])
    currentEmail = str(get_jwt()["email"])
    try:
        if currentRole != "ADMIN":
            return defined_error("Only admin who can access this session",'Bad request',400)

        dataInput = request.json
        dataRequired = ["kategori"]
        for data in dataRequired:
            if dataInput == None:
                return defined_error("body request tidak boleh kosong")
            if data not in dataInput:
                return parameter_error(f"Missing {data} in Request Body")

        kategori = dataInput["kategori"].strip()

        if not sanitize_deskripsi(kategori):
            return defined_error(f"kategori {INVALID_CHARACTER_INPUT}",'Bad Request',400)
            
        query = QUERY_GET_KATEGORI_BY_NAME
        values = (kategori,)
        result = Database().get_data(query,values)
        if len(result) != 0:
            return defined_error(f"kategori:{kategori} sudah ada",'Bad Request',400)
        
        data = {"kategori":kategori}

        Database().save(table="kategori", data=data)

        create_log(f"{currentRole} dengan email:{currentEmail} membuat kategori:{kategori}")

        return success(f"kategori: {kategori} berhasil dibuat")
    
    except Exception as e:
        return bad_request(str(e))

@kategori.get('/')
def get_kategori():
    try:
        query = QUERY_GET_ALL_KATEGORI
        values = ()
        result = Database().get_data(query,values)
        if len(result) == 0:
            return defined_error(f"belum ada kategori tersimpan",'Not Found',404)
   
        return success_data(message="Berhasil", data=result)

    except Exception as e:
        return bad_request(str(e))

@kategori.delete('id/<id>')
@jwt_required()
def delete_kategori(id):
    currentRole = str(get_jwt()["role"])
    currentEmail = str(get_jwt()["email"])
    try:
        if currentRole != "ADMIN":
            return defined_error("Only admin who can access this session",'Bad request',400)
        
        query = QUERY_GET_KATEGORI
        values = (id,)
        result = Database().get_data(query,values)
        if len(result) == 0:
            return defined_error(f"kategori id:{id} tidak ditemukan",'Not Found',404)

        updated_at = datetime.datetime.now()
        # delete data
        query = QUERY_DELETE_KATEGORI_BY_ID
        value = (updated_at,id,)
        Database().update_data(query=query, values=value)

        create_log(f"{currentRole} dengan email:{currentEmail} menghapus kategori dengan id:{id}")
        return success(f"kategori id:{id} berhasil dihapus")

    except Exception as e:
        return bad_request(str(e))
