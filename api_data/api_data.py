""" ================================================================================================
Institucion..: Universidad Tecnica Nacional
Sede.........: Del Pacifico
Carrera......: Tecnologias de Informacion
Periodo......: 3-2020
Charla.......: Uso de Python para demostracion de servicio en Droplet - Digital Ocean
Documento....: api_data.py
Objetivos....: Demostracion de un micro servicio web con api-REST.
Profesor.....: Jorge Ruiz (york)
Estudiante...:
================================================================================================"""
# -------------------------------------------------------
# Import libraries API service support
# -------------------------------------------------------
from datetime import datetime
import random

from flask import Flask, jsonify, abort, make_response, request
from flask_cors import CORS

# Create flask app
app = Flask(__name__)
CORS(app)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

# Create connection with MongoDB
from pymongo import MongoClient

def contextDB():
    conex = MongoClient(host=['10.90.42.1:27017'], username='admin', password='admin123')
    #conexDB = conex.apiData_01
    return conex


# -------------------------------------------------------
# Create data objets, only memory
# -------------------------------------------------------
users = []
ldata = []

# -------------------------------------------------------
# Create local API functions
# -------------------------------------------------------
def token():
    ahora = datetime.now()
    antes = datetime.strptime("1970-01-01", "%Y-%m-%d")
    return str(hex(abs((ahora - antes).seconds) * random.randrange(10000000)).split('x')[-1]).upper()

def token2():
    ahora = datetime.now()
    antes = datetime.strptime("1970-01-01", "%Y-%m-%d")
    return str(hex(abs((ahora - antes).seconds) * random.randrange(1000000000)).split('x')[-1]).upper()

# -------------------------------------------------------
# Error control, httpRequest rules
# -------------------------------------------------------
@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request....!'}), 400)

@app.errorhandler(401)
def unauthorized(error):
    return make_response(jsonify({'error': 'Unauthorized....!'}), 401)

@app.errorhandler(403)
def forbiden(error):
    return make_response(jsonify({'error': 'Forbidden....!'}), 403)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'test 2Not found....!'}), 404)

@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'error': 'Inernal Server Error....!'}), 500)

# ---------------------------------------------------
# Create references routes
# ---------------------------------------------------
@app.route('/', methods=['GET'])
def index():
    try:
        data = {
            "status_code": 200,
            "status_message": "Ok",
            "body_message": {
                 "description": "ApiData, API-Rest demonstration",
		 "author": "Jorge Ruiz (york)"
            }
        }
    except Exception as expc:
        abort(404)
    return jsonify(data)

# --------------------------------------------------
# Create routes and user control functions
# --------------------------------------------------

# User signup, register new user
@app.route('/signup', methods=['POST'])
def create_user():
    if not request.json or \
            not 'name' in request.json or \
            not 'email' in request.json or \
            not 'passwd' in request.json:
        abort(400)

    tkn1 = token()
    user = {
        "_id" : tkn1,
        'name': request.json['name'],
        'email': request.json['email'],
        'passwd': request.json['passwd']
    }
    try:
        conexDB= contextDB()
        conexDB.apiData_01.user.insert_one(user)
        user2 = {
            'token':tkn1,
            'name': request.json['name'],
            'email': request.json['email'],
            'passwd': request.json['passwd']
        }
        data = {
            "status_code": 201,
            "status_message": "Data was created",
            "data": {'user': user2}
        }
        conexDB.close()
    except Exception as expc:
        print(expc)
        abort(500)
    return jsonify(data), 201

# Retrieve data user from token
@app.route('/<string:token>/me', methods=['GET'])
def get_user(token):
    try:
        conexDB = contextDB()
        user = conexDB.apiData_01.user.find_one({"_id":{"$eq":token}})

        if user == None:
            abort(404)

        data = {
            "status_code": 200,
            "status_message": "Ok",
            "data": {'user': {"name": user['name'],
                              "email": user['email']
                              }
                    }
        }
        conexDB.close()
    except Exception as expc:
        abort(404)
    return jsonify(data)

# Retrieve token field from login data
@app.route('/login/<string:email>/<string:passwd>', methods=['GET'])
def get_login(email, passwd):
    try:
        conexDB = contextDB()
        user = conexDB.apiData_01.user.find_one({"email":{"$eq":email},"passwd":{"$eq":passwd}})
        if user == None:
            abort(404)
        data = {
            "status_code": 200,
            "status_message": "Ok",
            "data": {'user': {"name": user['name'],
                              "token": user['_id']
                              }
                    }
        }
        conexDB.close()
    except Exception as expc:
        abort(404)
    return jsonify(data)

# --------------------------------------------------
# Procesos relacionados con el control de clientes
# --------------------------------------------------
# Registra los datos de un cliente para un usuario
@app.route('/<string:token>/customer', methods=['POST'])
def create_customer(token):
    if not ((request.json and 'name' in request.json) and 'cellphone' in request.json):
        abort(400)
    conexDB = contextDB()
    tkn2 = token2()

    data = {
        '_id': tkn2,
        'idcard': request.json['idcard'],
        'name': request.json['name'],
        'cellphone': request.json['cellphone'],
        'email': request.json.get('email', "sin definir"),
        'token': token
    }
    try:
        conexDB.apiData_01.customer.insert_one(data)
        data2 = {
            'id': tkn2,
            'idcard': request.json['idcard'],
            'name': request.json['name'],
            'cellphone': request.json['cellphone'],
            'email': request.json.get('email', "sin definir"),
            'token': token
        }
        salida = {
            "status_code": 201,
            "status_message": "Data was created",
            "data": data2
        }
    except Exception as expc:
        abort(500)
    conexDB.close()
    return jsonify({'customer': salida}), 201

# Recupera la lista de clientes para un usuario
@app.route('/<string:token>/customer', methods=['GET'])
def get_customers(token):
    try:
        conexDB = contextDB()
        datos = conexDB.apiData_01.customer.find({"token":{"$eq":token}})

        if datos.count() == 0:
            data = {
                "status_code": 200,
                "status_message": "Ok",
                "data": "Empty customers list"
            }
        else:
            lista = []
            for collect in datos:
                lista.append({"id": collect['_id'],
                      "idcard": collect['idcard'],
                      "name": collect['name'],
                      "cellphone": collect['cellphone'],
                      "email": collect['email'],
                      "token":collect['token']})

            data = {
                "status_code": 200,
                "status_message": "Ok",
                "data": lista
            }
        conexDB.close()
    except:
        abort(500)
    return jsonify(data)

# Recupera los datos de un cliente para un usuario
@app.route('/<string:token>/customer/<string:cus_id>', methods=['GET'])
def get_customer_id(token, cus_id):
    try:
        conexDB = contextDB()
        datos = conexDB.apiData_01.customer.find_one({"token":{"$eq":token},"_id":{"$eq":cus_id}})

        if datos == None:
            data = {
                "status_code": 200,
                "status_message": "Ok",
                "data": "Customer data not found"
            }
        else:
            data = {
                "status_code": 200,
                "status_message": "Ok",
                "data": {"id": datos['_id'],
                         "idcard": datos['idcard'],
                         "name": datos['name'],
                         "cellphone": datos['cellphone'],
                         "email": datos['email'],
                         "token":datos['token']}
            }
        conexDB.close()
    except Exception as expc:
        abort(404)
    return jsonify(data)

# Modifica los datos de un cliente para un usuario
@app.route('/<string:token>/customer/<string:cus_id>', methods=['PUT'])
def update_customer(token, cus_id):
    try:
        conexDB = contextDB()
        datos = conexDB.apiData_01.customer.find_one({"token":{"$eq":token},"_id":{"$eq":cus_id}})
        if datos == None:
            abort(404)
        if not request.json:
            abort(400)
        if 'name' in request.json and request.json['name'] == '':
            abort(400)
        if 'cellphone' in request.json and request.json['cellphone'] == '':
            abort(400)
        if 'email' in request.json and request.json['email'] == '':
            abort(400)

        conexDB.apiData_01.customer.update_one({'_id':datos['_id']},
                                    {'$set':{'idcard':request.json.get('idcard', datos['idcard']),
                                             'name':request.json.get('name', datos['name']),
                                             'cellphone':request.json.get('cellphone', datos['cellphone']),
                                             'email':request.json.get('email', datos['email'])}})
        conexDB.close()
    except Exception as expc:
        abort(404)

    datos2 = {'idcard':request.json.get('idcard', datos['idcard']),
              'name':request.json.get('name', datos['name']),
              'cellphone':request.json.get('cellphone', datos['cellphone']),
              'email':request.json.get('email', datos['email'])}

    data = {
        "status_code": 200,
        "status_message": "Ok",
        "data": datos2
    }

    return jsonify(data), 200

# Elimna un cliente para un usuario
@app.route('/<string:token>/customer/<string:cus_id>', methods=['DELETE'])
def delete_customer(token, cus_id):
    try:
        conexDB = contextDB()
        datos = conexDB.apiData_01.customer.find_one({"token":{"$eq":token},"_id":{"$eq":cus_id}})
        if datos == None:
            abort(404)
        conexDB.apiData_01.customer.delete_one({'_id':datos['_id']})

    except Exception as expc:
        abort(404)
    return jsonify({'result': True})

if __name__ == '__main__':
    HOST = '0.0.0.0'
    PORT = 5000
    app.run(HOST, PORT)
