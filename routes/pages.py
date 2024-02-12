from flask import render_template, Blueprint, request
from MainThread import MainClass
from settings import MainProperties
import modules
from pymongo import MongoClient
CONNECTION_STRING = "mongodb://127.0.0.1:27017"
pages = Blueprint("pages", __name__)
app = pages


@app.route("/", methods=["GET"])
def index():
    if str(request.root_url).split("/")[2].split(":")[0] == "127.0.0.1":
        MainClass.producao = False
    if MainProperties["inited"]:
        return render_template("index/index.html")
    else:
        return render_template("splashScreen/index.html")
    

@app.route("/home", methods=["GET"], )
def home():
    if str(request.root_url).split("/")[2].split(":")[0] == "127.0.0.1":
        MainClass.producao = False
    return render_template("home/index.html")

@app.route("/config", methods=["GET"], )
def config():
    if str(request.root_url).split("/")[2].split(":")[0] == "127.0.0.1":
        MainClass.producao = False
    return render_template("config/index.html")

@app.route("/producao", methods=["GET"], )
def producao():
    if str(request.root_url).split("/")[2].split(":")[0] == "127.0.0.1":
        if MainClass.configs["leitura_plc"] == "true":
            MainClass.zeraStringLeitura()
        else:
            modules.scanner.readed = ""
            
        MainClass.producao = True
    return render_template("producao/index.html")

@app.route("/consulta", methods=["GET"], )
def consulta():   
    if str(request.root_url).split("/")[2].split(":")[0] == "127.0.0.1":
        MainClass.producao = False
    return render_template("consulta/index.html")

@app.route("/engeneering/<page>", methods=["GET"], )
def engeneering(page):
    if str(request.root_url).split("/")[2].split(":")[0] == "127.0.0.1":
        MainClass.producao = False
    return render_template(f"engeneering/{page}/index.html")
