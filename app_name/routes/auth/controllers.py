from flask import Blueprint
from ...dbFunctions import Database
from ...utilities import *


auth = Blueprint(
    name='auth', 
    import_name=__name__, 
    url_prefix='/auth'
)

@auth.get('email/<token>')
def email_verification(token):
    try:
        query = "SELECT * FROM auth WHERE token = %s"
        values = (token, )
        result = Database().get_data(query, values)
        
        if len(result) == 0 :
            return authorization_error()  

        id_user = result[0]["id_user"]

        query = "SELECT id,email,nama FROM user WHERE id = %s AND is_delete = 0"
        values = (id_user, )
        result = Database().get_data(query, values)
        
        email = result[0]["email"]

        if len(result) == 0:
            return defined_error("user tidak ditemukan silahkan mendaftar terlebih dahulu",'Not Found', 404)
        
        query = "UPDATE user SET is_active=1 WHERE id=%s"
        values = (id_user, )
        Database().insert_data(query, values)

        
        return success(message=f"Berhasil mengaktifkan user  dengan email :{email}")

    except Exception as e:
        return bad_request(str(e))
