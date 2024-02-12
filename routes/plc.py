from pymongo import MongoClient
from flask import Blueprint, request, jsonify

plc = Blueprint("plc", __name__)
app = plc
CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"

@app.route("/register", methods=["POST"])
def registerPlc():
    data = request.form
    
    for info in list(data):
        if data[info] == "":
            return jsonify({"msg": "Preencha todos os campos!"}), 400
    
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"],        

    try:
        last_id = next(i["_id"] + 1 for i in db["plc"].find().sort('_id', -1).limit(1))
    except:
        last_id = 1
        
    plc = {
        "_id": last_id,
        "ip": data["ip"],
        "rack": data["rack"],
        "slot": data["slot"],
        "desc": data["desc"],
        "db": int(data["db"]),
    } 
    db["plc"].insert_one(plc)

    return jsonify({"msg": "sucesso!"}), 200

@app.route("/update", methods=["PUT"])
def updatePlc():
    data = request.form
    for info in list(data):
        if data[info] == "":
            print("a")
            return jsonify({"msg": "Preencha todos os campos!"}), 400
    
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]
    
    try:
        int(data["db"])
    except:
        print("b")
        return jsonify({"msg": "A DB deve ser um número!"}), 400
        
    
    plc = {
        "ip": data["ip"],
        "rack": data["rack"],
        "slot": data["slot"],
        "desc": data["desc"],
        "db": int(data["db"])
    }

    db["plc"].update_one({"_id": 1}, {"$set": plc})
    return jsonify({"msg": "sucesso!"}), 200

@app.route("/get", methods=["GET"])
def getPlc():
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    result = db["plc"].find()
    plc = [plc for plc in result]
    return jsonify({"plc": plc[0]}), 200
