from pymongo import MongoClient
from flask import Blueprint, request, jsonify
import modules

ips_linha = Blueprint("ips_linha", __name__)
app = ips_linha
CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"


@app.route("/register", methods=["POST"])
def registerIp():
    data = request.form

    for info in list(data):
        if data[info] == "":
            return jsonify({"msg": "Preencha todos os campos!"}), 400

    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    try:
        last_id = next(i["_id"] + 1 for i in db["ips_linha"].find().sort('_id', -1).limit(1))
    except:
        last_id = 1

    desvio_rota = {"_id": last_id, "ip": data["ip"], "posto": data["posto"]}

    db["ips_linha"].insert_one(desvio_rota)
    modules.plc.setupVariables()
    return jsonify({"msg": "sucesso!"}), 200


@app.route("/update", methods=["PUT"])
def updateIp():
    data = request.form
    for info in list(data):
        if data[info] == "":
            return jsonify({"msg": "Preencha todos os campos!"}), 400

    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    desvio_rota = {"ip": data["ip"], "posto": data["posto"]}

    db["ips_linha"].update_one({"_id": int(data['id'])},
                                  {"$set": desvio_rota})
    modules.plc.setupVariables()
    return jsonify({"msg": "sucesso!"}), 200


@app.route("/delete/<id>", methods=["DELETE"])
def deleteIp(id):
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    db["ips_linha"].delete_one({"_id": int(id)})
    modules.plc.setupVariables()
    return jsonify({"msg": "Successo!"}), 200


@app.route("/getAll", methods=["GET"])
def getAllIps():
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    desvio_rotas = db["ips_linha"].find()

    desvio_rotas = [desvio_rota for desvio_rota in desvio_rotas]
    return jsonify({"ips": desvio_rotas}), 200


@app.route("/get/<id>", methods=["GET"])
def getIp(id):
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    result = db["ips_linha"].find({"_id": int(id)})
    desvio_rota = [desvio_rota for desvio_rota in result]
    return jsonify({"ips": desvio_rota[0]}), 200
