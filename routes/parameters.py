from pymongo import MongoClient
from flask import Blueprint, request, jsonify
import modules

parameter = Blueprint("parameter", __name__)
app = parameter
CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"


@app.route("/register", methods=["POST"])
def registerParameter():
    data = request.form

    for info in list(data):
        if data[info] == "":
            return jsonify({"msg": "Preencha todos os campos!"}), 400

    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    memoria_exists = len([
        parameter
        for parameter in db["parameter"].find({"memoria": data['memoria']})
    ]) > 0
    param_exists = len([
        parameter
        for parameter in db["parameter"].find({"param": data['param']})
    ]) > 0

    if int(data["memoria"]) < 100:
        return jsonify(
            {"msg": "Devem ser utilizados endereços apartir de 100.0!"}), 400

    if param_exists:
        return jsonify({"msg": "Esse parâmetro ja existe!"}), 400

    if memoria_exists:
        return jsonify({"msg": "Esse endereço ja foi utilizado!"}), 400

    if int(data["memoria"]) % 4 != 0:
        return jsonify({"msg": "Endereço inválido!"}), 400

    try:
        last_id = next(i["_id"] + 1 for i in db["parameter"].find().sort('_id', -1).limit(1))
    except:
        last_id = 1

    parameter = {
        "_id": last_id,
        "param": data["param"],
        "memoria": data["memoria"]
    }
    db["parameter"].insert_one(parameter)
    modules.plc.setupVariables()
    return jsonify({"msg": "sucesso!"}), 200


@app.route("/update", methods=["PUT"])
def updateParameter():
    data = request.form
    for info in list(data):
        if data[info] == "":
            return jsonify({"msg": "Preencha todos os campos!"}), 400

    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    memoria_exists = len([
        parameter
        for parameter in db["parameter"].find({"memoria": data['memoria']})
        if parameter["_id"] != int(data["id"])
    ]) > 0
    param_exists = len([
        parameter
        for parameter in db["parameter"].find({"param": data['param']})
        if parameter["_id"] != int(data["id"])
    ]) > 0

    if int(data["memoria"]) < 100:
        return jsonify(
            {"msg": "Devem ser utilizados endereços apartir de 100.0!"}), 400

    if param_exists:
        return jsonify({"msg": "Esse parâmetro ja existe!"}), 400

    if memoria_exists:
        return jsonify({"msg": "Esse endereço ja foi utilizado!"}), 400

    if int(data["memoria"]) % 4 != 0:
        return jsonify({"msg": "Endereço inválido!"}), 400

    parameter = {"memoria": data["memoria"], "param": data["param"]}

    db["parameter"].update_one({"_id": int(data['id'])}, {"$set": parameter})
    modules.plc.setupVariables()
    return jsonify({"msg": "sucesso!"}), 200


@app.route("/delete/<id>", methods=["DELETE"])
def deleteParameter(id):
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    db["parameter"].delete_one({"_id": int(id)})
    modules.plc.setupVariables()
    return jsonify({"msg": "Successo!"}), 200


@app.route("/getAll", methods=["GET"])
def getAllparameters():
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    parameters = db["parameter"].find()

    parameters = [parameter for parameter in parameters]
    return jsonify({"params": parameters}), 200


@app.route("/get/<id>", methods=["GET"])
def getParameter(id):
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    result = db["parameter"].find({"_id": int(id)})
    parameter = [parameter for parameter in result]
    return jsonify({"param": parameter[0]}), 200
