from pymongo import MongoClient
from flask import Blueprint, request, jsonify
import modules

parafusadeira = Blueprint("parafusadeira", __name__)
app = parafusadeira
CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"


@app.route("/register", methods=["POST"])
def registerParafusadeira():
    data = request.form

    for info in list(data):
        if data[info] == "":
            return jsonify({"msg": "Preencha todos os campos!"}), 400

    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    try:
        last_id = next(
            i["_id"] + 1 for i in db["parafusadeira"].find().sort('_id', -1).limit(1))
    except:
        last_id = 1

    query = db["parafusadeira"].find(
        {"db_parafusadeira": data["db_parafusadeira"]})
    results = [i for i in query]
    if len(results) > 0:
        return jsonify({"msg": "Essa db ja foi utilizada!"}), 400

    bit_solicitacao = f"0.0"
    bit_confirmacao = f"0.1"
    bit_erro = f"0.2"

    bit_torque = "2.0"
    bit_tempo = "6.0"

    parafusadeira = {"_id": last_id, "ip": data["ip"], "link": data["link"], "marca": data["marca"], "index_torque": data["index_torque"], "index_tempo": data["index_tempo"], "db_parafusadeira": data["db_parafusadeira"],
                     "bit_solicitacao": bit_solicitacao, "bit_confirmacao": bit_confirmacao, "bit_erro": bit_erro, "memoria_torque": bit_torque, "memoria_tempo": bit_tempo}

    db["parafusadeira"].insert_one(parafusadeira)
    modules.plc.setupVariables()
    return jsonify({"msg": "sucesso!"}), 200


@app.route("/update", methods=["PUT"])
def updateParafusadeira():
    data = request.form
    for info in list(data):
        if data[info] == "":
            return jsonify({"msg": "Preencha todos os campos!"}), 400

    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    parafusadeira = {"ip": data["ip"], "link": data["link"], "marca": data["marca"], "index_torque": data["index_torque"], "index_tempo": data["index_tempo"], "db_parafusadeira": data["db_parafusadeira"]}
    db["parafusadeira"].update_one({"_id": int(data['id'])},
                                   {"$set": parafusadeira})
    modules.plc.setupVariables()
    return jsonify({"msg": "sucesso!"}), 200


@app.route("/delete/<id>", methods=["DELETE"])
def deleteParafusadeira(id):
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    db["parafusadeira"].delete_one({"_id": int(id)})
    modules.plc.setupVariables()
    return jsonify({"msg": "Successo!"}), 200


@app.route("/getAll", methods=["GET"])
def getAllparafusadeiras():
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    parafusadeiras = db["parafusadeira"].find()

    parafusadeiras = [parafusadeira for parafusadeira in parafusadeiras]
    return jsonify({"parafusadeiras": parafusadeiras}), 200


@app.route("/get/<id>", methods=["GET"])
def getParafusadeira(id):
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    result = db["parafusadeira"].find({"_id": int(id)})
    parafusadeira = [parafusadeira for parafusadeira in result]
    return jsonify({"parafusadeira": parafusadeira[0]}), 200
