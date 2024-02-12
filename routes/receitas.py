from pymongo import MongoClient
from flask import Blueprint, request, jsonify
from settings import getDBConnection
import bson
import modules

recipes = Blueprint("recipes", __name__)
app = recipes

def serializeDict(unsearizableDict:dict):
    for key in unsearizableDict.keys():
        if type(unsearizableDict[key]) == bson.objectid.ObjectId:
            unsearizableDict[key] = str(unsearizableDict[key])
    
    return unsearizableDict


def isNameAvailable(name, include_self=False, self_id=""):
    [client, db] = getDBConnection()
    receitas = db["receitas"]
    
    find_query = {"nome": name} if not include_self else {"$and": [{"nome": name}, {"_id": {"$ne": bson.objectid.ObjectId(self_id)} }]}
    sameNameRecipes = list(receitas.find(find_query))  
    
    print(sameNameRecipes, name)  
    client.close()
    return len(sameNameRecipes) == 0


@app.route("/register", methods=["POST"])
def registerRecipe():
    [client, db] = getDBConnection()
    receitas = db["receitas"]
    
    data = request.form
    nameAvailable = isNameAvailable(data["name"])
    if(not nameAvailable): return jsonify({"status": 400, "message": "Nome já utilizado"})
    
    newRecipe = {
        "nome": data["name"],
        "codigo": data["cod"],
    }
    receitas.insert_one(newRecipe)
    
    client.close()
    return jsonify({"status": 0})


@app.route("/update", methods=["POST"])
def updateRecipe():
    [client, db] = getDBConnection()
    receitas = db["receitas"]
    
    data = request.form
    print(data)
    nameAvailable = isNameAvailable(data["name"], True, data["id"])
    if(not nameAvailable): return jsonify({"status": 400, "message": "Nome já utilizado"})
    
    newRecipe = {
        "nome": data["name"],
        "codigo": data["cod"],
    }
    receitas.update_one({"_id": bson.objectid.ObjectId(data['id'])}, {"$set": newRecipe})
    
    client.close()
    return jsonify({"status": 0})


@app.route("/getAll", methods=["GET"])
def getAllRecipes():
    [client, db] = getDBConnection()
    receitas = db["receitas"].find()
    receitas = list(receitas)
    receitas = [serializeDict(receita) for receita in receitas]

    client.close()
    return jsonify({"recipes": receitas}), 200


@app.route("/delete", methods=["POST"])
def deleteRecipe():
    [client, db] = getDBConnection()
    receitas = db["receitas"]

    data = request.form
    receitas.delete_one({"_id": bson.objectid.ObjectId(data['id'])})
    
    client.close()
    return jsonify({"status": 0})
