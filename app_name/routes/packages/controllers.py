from flask import Blueprint, request
from flask_jwt_extended import get_jwt, jwt_required

from app_name.queries import QUERY_DELETE_PACKAGES_BY_ID, QUERY_GET_ALL_PACKAGES, QUERY_GET_PACKAGE_BY_ID, QUERY_GET_PACKAGES_BY_NAME, QUERY_UPDATE_PACKAGE_BY_ID
from ...dbFunctions import Database
from ...utilities import *
import json

# Start Block ============================== set Blueprint
packages = Blueprint(
    name='packages',
    import_name=__name__,
    url_prefix='/packages'
)
# End Block ============================== set Blueprint


# Show All Packages
# GET http://127.0.0.1:7000/packages/
@packages.get('/')
def show_all_packages():
    try:
        # Start Block ============================== check data in database
        query = QUERY_GET_ALL_PACKAGES
        result = Database().execute(query)
        if len(result) == 0:
            return defined_error("There is no package yet.", 'Bad request', 400)
        # End Block ============================== check data in database
        
        # Start Block ============================== if data is available
        else:
            data = []
            for i in range(len(result)):
                values = {
                    "name" : result[i]['package_name'],
                    "description" : result[i]['description'],
                    "features" : json.loads(result[i]['features'].decode('utf-8')),
                    "platform": result[i]['platform'],
                    "duration": result[i]['duration'],
                    "price" : result[i]['price']
                }
                data.append(values)
                
            return success_data(message=f"Successful", data=data)
        # End Block ============================== if data is available

    except Exception as e:
        return bad_request(str(e))


# Show packages by id
# GET http://127.0.0.1:7000/packages/<id>
@packages.get('/id/<id>')
def show_packages_by_id(id):
    try:
        # Start Block ============================== check data by id in database
        query = QUERY_GET_PACKAGE_BY_ID
        values = (id,)
        result = Database().get_data(query,values)
        if len(result) == 0:
            return defined_error("No data found.")
        # End Block ============================== check data by id in database

        # Start Block ============================== if data is available
        data = {
            "name" : result[0]['package_name'],
            "description" : result[0]['description'],
            "features" : json.loads(result[0]['features'].decode('utf-8')),
            "platform": result[0]['platform'],
            "duration": result[0]['duration'],
            "price" : result[0]['price']
        }
        return success_data(message=f"Successful!", data=data)
        # End Block ============================== if data is available

    except Exception as e:
        return bad_request(str(e))

# Create Package
# POST http://127.0.0.1:7000/packages/
@packages.post('/')
@jwt_required()
def add_package():
    # Get role from token login
    currentRole = str(get_jwt()["role"]).lower()
    try:
        # Start Block ============================== Validation role
        if currentRole != "admin":
            return defined_error("Only the admin can access this session.",'Bad request',400)
        # End Block ============================== Validation role
        
        # Start Block ============================== Initialize body request
        dataInput = request.json
        dataRequired = ["package_name","price","description",
                        "features", "platform", "duration"]
        # End Block ============================== Initialize body request

        # Start Block ============================== validation body request
        for data in dataRequired:
            if dataInput == None:
                return defined_error("A body request cannot be empty.")
            if data not in dataInput:
                return parameter_error(f"Missing {data} in Request Body")
        # End Block ============================== validation body request

        # Start Block ============================== Input body request
        name = dataInput["package_name"]
        price = dataInput["price"]
        desc = dataInput["description"]
        features = dataInput["features"]
        platform = dataInput["platform"]
        duration = dataInput["duration"]
        features_json = json.dumps(features, indent = 4)
        # End Block ============================== Input body request

        # Start Block ==================== Checking data if exists on database
        query = QUERY_GET_PACKAGES_BY_NAME
        values = (name, duration)
        result = Database().get_data(query, values)
        if len(result) != 0:
            return defined_error("The package already exists.")
        # End Block ==================== Checking data if exists on database

        # Start Block ============================== if data no exists
        else:
            data = {
                "package_name":name,
                "price":price,
                "description":desc,
                "features":features_json,
                "platform":platform,
                "duration":duration
            }
            Database().save(table="packages", data=data)
            return success(f"Successful! {name} was added")
        # End Block ============================== if data no exists

    except Exception as e:
        return bad_request(str(e))


# Update Packages
# PUT http://127.0.0.1:7000/packages/id/<id>
@packages.put('/id/<id>')
@jwt_required()
def update_packages(id):
    # Get current role from token login
    currentRole = str(get_jwt()["role"]).lower()
    try:
        # Start Block ============================== Validation role
        if currentRole != "admin":
            return defined_error("Only the admin can access this session.",'Bad request',400)
        # End Block ============================== Validation role

        # Start Block ============================== initialize body request
        dataInput = request.json
        dataRequired = ["package_name", "description", "features", 
                        "platform", "duration", "price"]
        # End Block ============================== initialize body request

        # Start Block ============================== validation body request
        for data in dataRequired:
            if dataInput == None:
                return defined_error("A body request cannot be empty.", 'Bad request', 400)
            if data not in dataRequired:
                return parameter_error(f"Missing {data} in Request Body")
        # End Block ============================== validation body request
        
        # Start Block ============================== input body request
        pack_name = dataInput["package_name"]
        desc = dataInput["description"]
        features = dataInput["features"]
        platform = dataInput["platform"]
        duration = dataInput["duration"]
        price = dataInput["price"]
        features_json = json.dumps(features, indent = 4)
        # End Block ============================== input body request

        # Start Block ============================== check data in database
        query = QUERY_GET_PACKAGE_BY_ID
        values = (id,)
        result = Database().get_data(query, values)
        if len(result) == 0:
            return defined_error("No data found.")
        # End Block ============================== check data in database
        
        # Start Block ============================== update data - if data is available
        queryUp = QUERY_UPDATE_PACKAGE_BY_ID
        values = (pack_name, desc, features_json, platform, duration, price, id,)
        Database().update_data(query=queryUp, values=values)
        return success("Update data is successful!")
        # End Block ============================== update data - if data is available

    except Exception as e:
        return bad_request(str(e))


# Delete Packages
# DELETE http://127.0.0.1:7000/packages/id/<id>
@packages.delete('/id/<id>')
@jwt_required()
def delete_packages(id):
    # Get current role from token login
    currentRole = str(get_jwt()["role"]).lower()
    try:
        # Start Block ============================== validation role
        if currentRole != "admin":
            return defined_error("Only the admin can access this session.",'Bad request',400)
        # End Block ============================== validation role

        # Start Block ============================== check data in database
        query = QUERY_GET_PACKAGE_BY_ID
        values = (id,)
        result = Database().get_data(query, values)
        if len(result) == 0:
            return defined_error("No data found.")
        # End Block ============================== check data in database
        
        # Start Block ============================== delete data - if data is available
        # changes kolom is_delete
        queryUp = QUERY_DELETE_PACKAGES_BY_ID
        value = (id,)
        Database().update_data(query=queryUp, values=value)
        return success("Successful! This package was deleted.")
        # End Block ============================== delete data - if data is available

    except Exception as e:
        return bad_request(str(e))

