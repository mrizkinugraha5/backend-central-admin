from flask import Blueprint, request, redirect
from flask_jwt_extended import get_jwt, jwt_required
from ...dbFunctions import Database
from ...utilities import *
from ...queries import *
from app_name.helpers.function import *
from app_name.helpers.validator import *

links = Blueprint(
    name='links',
    import_name=__name__,
    url_prefix='/s'
)

@links.post('/')
@jwt_required()
def create_link():
    currentRole = str(get_jwt()["role"])
    currentEmail = str(get_jwt()["email"])
    try:
        if currentRole != "ADMIN":
            return defined_error("Only admin who can access this session",'Bad request',400)

        dataInput = request.json
        dataRequired = ["link","custom_name"]
        for data in dataRequired:
            if dataInput == None:
                return defined_error("body request tidak boleh kosong")
            if data not in dataInput:
                return parameter_error(f"Missing {data} in Request Body")

        link = dataInput["link"].strip()
        custom_name = dataInput["custom_name"]

        error_list = link_validator(link,custom_name)
        if len(error_list) != 0:
            return defined_error(error_list,'Bad Request', 400)

        if not custom_name:
            custom_name = uuid.uuid4().hex[-7:]
        
        query = QUERY_GET_LINK_BY_NAME
        values = (custom_name,)
        result = Database().get_data(query,values)
        if len(result) != 0:
            return defined_error(f"link dengan name:{custom_name} sudah dipakai",'Bad Request',400)
        
        data = {"link_asli":link, "link_shorten":custom_name}

        Database().save(table="link", data=data)

        
        create_log(f"{currentRole} dengan email:{currentEmail} membuat link:{custom_name}")

        return success(f"shorten link berhasil dibuat link:{request.url}{custom_name}")
    
    except Exception as e:
        return bad_request(str(e))

@links.get('/<name>')
@jwt_required()
def get_link(name):
    try:
        query = QUERY_GET_LINK_BY_NAME
        values = (name,)
        result = Database().get_data(query,values)
        if len(result) == 0:
            return defined_error(f"Link:{name} tidak ditemukan",'Not Found',404)
        
        link = result[0]["link_asli"]

        return redirect(link,code=302)

    except Exception as e:
        return bad_request(str(e))

@links.get('/')
@jwt_required()
def get_all_link():
    offset = request.args.get('page')
    limit = request.args.get('row')
    limit  = int(limit) if limit else 1000
    offset  = (int(offset) - 1) * limit if offset else 0
    currentRole = str(get_jwt()["role"])
    try:
        if currentRole != "ADMIN":
            return defined_error("Only admin who can access this session",'Bad request',400)

        query = QUERY_GET_ALL_LINK
        values = (limit,offset,)
        result = Database().get_data(query,values)
        if len(result) == 0:
            return defined_error(f"belum ada link tersimpan di database",'Not Found',404)
        
        return success_data(message=f"Success", data=result)

    except Exception as e:
        return bad_request(str(e))


@links.delete('/<name>')
@jwt_required()
def delete_links(name):
    currentRole = str(get_jwt()["role"])
    currentEmail = str(get_jwt()["email"])
    try:
        if currentRole != "ADMIN":
            return defined_error("Only admin who can access this session",'Bad request',400)
        
        query = QUERY_GET_LINK_BY_NAME
        values = (name,)
        result = Database().get_data(query,values)
        if len(result) == 0:
            return defined_error(f"Link:{name} tidak ditemukan",'Not Found',404)

        updated_at = datetime.datetime.now()
        # delete data
        query = QUERY_DELETE_LINK_BY_NAME
        value = (updated_at,name,)
        Database().update_data(query=query, values=value)

        create_log(f"{currentRole} dengan email:{currentEmail} menghapus link:{result[0]['link_shorten']}")
        return success("link berhasil dihapus")

    except Exception as e:
        return bad_request(str(e))
