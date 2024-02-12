from flask import Blueprint, jsonify, request
from settings import MainProperties, getDBConnection
from MainThread import MainClass
from bson.objectid import ObjectId
from pymongo import MongoClient
import modules
import bcrypt
import urllib3
from datetime import datetime



logic = Blueprint("logic", __name__)
app = logic
CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"

@app.route("/getProperties", methods=["GET"])
def updateMainProperties():
    return jsonify({"properties": MainProperties})

@app.route("/authUser", methods=["POST"])
def authUser():
    data = request.form
    for info in list(data):
        if data[info] == "":
            return jsonify({"msg": "Preencha todos os campos!"}), 400
    db_ip = MainClass.configs["ip_ultimo_posto"]
    CONNECTION_STRING = f"mongodb://{db_ip}:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]
    users = db["users"].find({"chapa": data["chapa"]})
    users = [user for user in users]
    
    if len(users) == 0:
        return jsonify({"msg": "Chapa não registrada!"}), 400
    
    if not users[0]["permissions"]["Engenharia"]:
        return jsonify({"msg": "Você não tem acesso ao acesso remoto!"}), 400
    user = [user for user in users if bcrypt.checkpw(data["pass"].encode(), user["password"].encode())]
    if len(user) == 0:
        return jsonify({"msg": "Senha incorreta!"}), 400
    user = user[0]
    user.pop("password")
    return jsonify({"user": user}), 200

@app.route("/resetCycle", methods=["GET"])
def resetCycle():
    MainClass.passo = 0
    modules.scanner.readed = ""
    return ""

@app.route("/logout", methods=["GET"])
def logout():
    MainProperties["rfid"] = ""
    modules.rfid.last_readed = ""
    modules.rfid.readed = ""
    return ""

@app.route("/deleteDb", methods=["DELETE"])
def deleteDb():
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]
    
    db["aprovados"].delete_many({})
    return ""

@app.route("/zeraContador", methods=["GET"])
def zeraContador():
    modules.cycles.ConsultaCodPadrao.aprovados = 0
    modules.cycles.ConsultaCodPadrao.reprovados = 0
    return ""

@app.route("/retrabalho/<option>", methods=["GET"])
def retrabalho(option):
    option = int(option)
    
    MainClass.continua_retrabalho = bool(int(option))
    MainClass.retrabalho = False
    return ""

@app.route("/getInfo/<code>", methods=["GET"])
def getInfo(code):
    db_ip = MainClass.configs["ip_ultimo_posto"]
    CONNECTION_STRING = f"mongodb://{db_ip}:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]
    
    all_info = db["aprovados"].find({"code": code})
    info = [info for info in all_info]
    if len(info) == 0:
        all_info = db["aprovados"].find({"sub_code": code})
        info = [info for info in all_info]
        if len(info) == 0:
            return jsonify({"msg": "Código não encontrado!"})

    info = info[0]
    if "files" in list(info):
        files = info["files"]
        
        for file, value in files.items():
            with open(f"static/temp_consulta/{file}", "wb") as f:
                f.write(value)
        
        info["files"] = [file for file in list(files)]
    modules.scanner.readed = ""
    return jsonify({"info": info})

@app.route("/testeLink", methods=["POST"])
def testeLink():
    url = request.form.get("link")
    print(url)
    http = urllib3.PoolManager()
    
    response = http.request('GET', url)
    
    array = response.data.decode().split(",")
    
    return jsonify({"index": array})

@app.route("/setPontaEstoque")
def setPontaEstoque():
    MainProperties["ponta_estoque"] = not MainProperties["ponta_estoque"]
    return "", 200

@app.route("/setRecipe", methods=["POST"])
def setRecipe():
    [client, db] = getDBConnection()
    data = request.form
    
    
    receita = list(db["receitas"].find(  {"_id": ObjectId(data["recipeId"])} ))[0]
    receita["_id"] = str(receita["_id"])
    MainClass.receita = receita
    
    client.close()
    return jsonify({"status": 0, "message": "Receita alterada com sucesso"})


@app.route("/searchAprovas", methods=["POST"])
def searchAprovas():
    [client, db] = getDBConnection()


    body = request.form
    hora = body.get("hora")
    selected_db = body.get("receita")
    data = body.get("data")
    
    query = {}    

    ################################### Inutiliza os campos sem fitro ###################################

    if not data:
        query["date"] = -1
    else:
        anoMesDia = data.split("-")
        if hora:
            start_date = datetime(int(anoMesDia[0]), int(anoMesDia[1]), int(anoMesDia[2]), int(hora))
            end_date = datetime(int(anoMesDia[0]), int(anoMesDia[1]), int(anoMesDia[2]), int(hora) + 1)
        else:
            start_date = datetime(int(anoMesDia[0]), int(anoMesDia[1]), int(anoMesDia[2]) - 1, 23)
            end_date = datetime(int(anoMesDia[0]), int(anoMesDia[1]), int(anoMesDia[2]), 23)
        
        query["date"] = {"$lt": end_date, "$gte": start_date}
        

    result = db["buffer_aprovadas" if int(selected_db) else "buffer_reprovadas"].find(query)
    newResultFormated = []
    ################################# Converte os resultados que não podem ser passados para JSON #########################
    for code in result:
        code.pop("_id")
        for key, value in code.items():
            if(type(value) == datetime):
                code[key] = value.strftime("%d-%m-%Y %H:%M:%S")
        
        newResultFormated.append(code)
    return jsonify({"data": newResultFormated})


