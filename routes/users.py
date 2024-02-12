from pymongo import MongoClient
from flask import Blueprint, request, jsonify
import modules
import json
import bcrypt
users = Blueprint("users", __name__)
app = users
LOCAL_CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"


@app.route("/register", methods=["POST"])
def registerUser():
    client = MongoClient(LOCAL_CONNECTION_STRING)
    db = client["geral"]
    configs = db["config"].find({"_id": 1})
    configs = [config for config in configs][0]

    db_ip = configs["ip_ultimo_posto"]

    CONNECTION_STRING = f"mongodb://{db_ip}:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"
    data = request.form
    permissions = json.loads(data.get("permissions"))
    for info in list(data):
        if data[info] == "":
            if info == "password":
                if permissions["Engenharia"]:
                    return jsonify({"msg": "Preencha todos os campos!"}), 400
            else:
                return jsonify({"msg": "Preencha todos os campos!"}), 400
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    user_exists = len([
        user
        for user in db["users"].find({"rfid": data['rfid']})
    ]) > 0

    chapa_exists = len([
        user
        for user in db["users"].find({"chapa": data['chapa']})
    ]) > 0

    if user_exists:
        return jsonify({"msg": "Esse RFID ja foi cadastrado!"}), 400

    if chapa_exists:
        return jsonify({"msg": "Essa chapa ja foi cadastrada!"}), 400

    try:
        last_id = next(i["_id"] + 1 for i in db["users"].find().sort('_id', -1).limit(1))
    except:
        last_id = 1
        
    password = data["password"]
    if permissions["Engenharia"]:
        salt = bcrypt.gensalt(8)
        password = bcrypt.hashpw(password.encode(), salt).decode()
    
    user = {
        "_id": last_id,
        "nome": data["nome"],
        "rfid": data["rfid"],
        "chapa": data["chapa"],
        "password": password,
        "permissions": json.loads(data.get("permissions"))
    }
    db["users"].insert_one(user)
    return jsonify({"msg": "sucesso!"}), 200


@app.route("/update", methods=["PUT"])
def updateUser():
    client = MongoClient(LOCAL_CONNECTION_STRING)
    db = client["geral"]
    configs = db["config"].find({"_id": 1})
    configs = [config for config in configs][0]

    db_ip = configs["ip_ultimo_posto"]

    CONNECTION_STRING = f"mongodb://{db_ip}:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"
    data = request.form
    permissions = json.loads(data.get("permissions"))
    for info in list(data):
        if data[info] == "":
            if info != "password":
                return jsonify({"msg": "Preencha todos os campos!"}), 400

    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    user_exists = len([
        user
        for user in db["users"].find({"rfid": data['rfid']})
        if user["_id"] != int(data["id"])
    ]) > 0

    chapa_exists = len([
        user
        for user in db["users"].find({"chapa": data['chapa']}) if user["_id"] != int(data["id"])
    ]) > 0

    if user_exists:
        return jsonify({"msg": "Esse RFID ja foi cadastrado!"}), 400

    if chapa_exists:
        return jsonify({"msg": "Essa ja foi cadastrada!"}), 400
    password = data["password"]
    if password != "":
        if permissions["Engenharia"]:
            salt = bcrypt.gensalt(8)
            password = bcrypt.hashpw(password.encode(), salt).decode()

    user = {
        "nome": data["nome"],
        "rfid": data["rfid"],
        "chapa": data["chapa"],
        "password": password,
        "permissions": json.loads(data.get("permissions"))
    }
    if password == "":
        user.pop("password")
    db["users"].update_one({"_id": int(data['id'])}, {"$set": user})
    return jsonify({"msg": "sucesso!"}), 200


@app.route("/delete/<id>", methods=["DELETE"])
def deleteUser(id):
    client = MongoClient(LOCAL_CONNECTION_STRING)
    db = client["geral"]
    configs = db["config"].find({"_id": 1})
    configs = [config for config in configs][0]

    db_ip = configs["ip_ultimo_posto"]

    CONNECTION_STRING = f"mongodb://{db_ip}:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    db["users"].delete_one({"_id": int(id)})
    return jsonify({"msg": "Successo!"}), 200


@app.route("/getAll", methods=["GET"])
def getAllUsers():
    client = MongoClient(LOCAL_CONNECTION_STRING)
    db = client["geral"]
    configs = db["config"].find({"_id": 1})
    configs = [config for config in configs][0]

    db_ip = configs["ip_ultimo_posto"]

    CONNECTION_STRING = f"mongodb://{db_ip}:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    users = db["users"].find()

    users = [user for user in users]
    return jsonify({"users": users}), 200


@app.route("/get/<id>", methods=["GET"])
def getUser(id):
    client = MongoClient(LOCAL_CONNECTION_STRING)
    db = client["geral"]
    configs = db["config"].find({"_id": 1})
    configs = [config for config in configs][0]

    db_ip = configs["ip_ultimo_posto"]

    CONNECTION_STRING = f"mongodb://{db_ip}:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    result = db["users"].find({"_id": int(id)})
    user = [user for user in result]
    return jsonify({"user": user[0]}), 200
