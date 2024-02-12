from pymongo import MongoClient
from flask import Blueprint, request, jsonify
from MainThread import MainClass
import time
import os
from werkzeug.utils import secure_filename
import modules
config = Blueprint("config", __name__)
app = config
CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"


@app.route("/updateConfig", methods=["PUT"])
def updateConfigs():
    data = request.form
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    for info in list(data):
        if data[info] == "":
            if info == "ip_consulta":
                if not data["etiqueta"] == "true":
                    return jsonify({"msg": "Preencha todos os campos!"}), 400
            elif info == "ip_impressora":
                if data["consulta"] == "false":
                    return jsonify({"msg": "Preencha todos os campos!"}), 400
            elif info == "qntd_ftp":
                if data["ftp"] == "true":
                    return jsonify({"msg": "Preencha todos os campos!"}), 400

            else:
                return jsonify({"msg": "Preencha todos os campos!"}), 400

    configs = {
        "ip": data["ip"],
        "gateway": data["gateway"],
        "netmask": data["netmask"],
        "etiqueta": data["etiqueta"],
        "subEtiqueta": data["subEtiqueta"],
        "consulta": data["consulta"],
        "ip_consulta": data["ip_consulta"],
        "cod_unico": data["cod_unico"],
        "ip_impressora": data["ip_impressora"],
        "tipo_etiqueta": data["tipo_etiqueta"],
        "nome_totem": data["nome_totem"],
        "ftp": data["ftp"],
        "qntd_ftp": data["qntd_ftp"],
        "leitura_plc": data["leitura_plc"],
        "ip_ultimo_posto": data["ip_ultimo_posto"],
        "rfid_com_port": data["rfid_com_port"],
        "scanner_com_port": data["scanner_com_port"],
        "ultimo_posto": data["ultimo_posto"],
        "consulta_cod": data["consultaCod"]
    }

    netmask_notation = {
                    "0.0.0.0": 0,
                    "128.0.0.0": 1,
                    "192.0.0.0": 2,
                    "224.0.0.0": 3,
                    "240.0.0.0": 4,
                    "248.0.0.0": 5,
                    "252.0.0.0": 6,
                    "254.0.0.0": 7,
                    
                    
                    "255.0.0.0": 8,
                    "255.128.0.0": 9,
                    "255.192.0.0": 10,
                    "255.224.0.0": 11,
                    "255.240.0.0": 12,
                    "255.248.0.0": 13,
                    "255.252.0.0": 14,
                    "255.254.0.0": 15,
                    
                    
                    "255.255.0.0": 16,
                    "255.255.128.0": 17,
                    "255.255.192.0": 18,
                    "255.255.224.0": 19,
                    "255.255.240.0": 20,
                    "255.255.248.0": 21,
                    "255.255.252.0": 22,
                    "255.255.254.0": 23,
                    
                    
                    "255.255.255.0": 24,
                    "255.255.255.128": 25,
                    "255.255.255.192": 26,
                    "255.255.255.224": 27,
                    "255.255.255.240": 28,
                    "255.255.255.248": 29,
                    "255.255.255.252": 30,
                    "255.255.255.254": 31,
                    "255.255.255.255": 32,
                }
    if data["netmask"] not in list(netmask_notation):
        return jsonify({"msg": "Netmask inválido!!"}), 400
    os.system("sudo chmod 777 /etc/netplan/01-network-manager-all.yaml")
    with open("/etc/netplan/01-network-manager-all.yaml", "w") as f:
        f.write(f"""
                    network:
                        ethernets:
                            enp1s0:
                                dhcp4: false
                                addresses: [{data["ip"]}/{netmask_notation[data['netmask']]}]
                                gateway4: {data['gateway']}
                                nameservers:
                                    addresses: [{data['gateway']}]
                        version: 2""")
    os.system("sudo netplan apply")

    db["config"].update_one({"_id": 1}, {"$set": configs})
    configs = db["config"].find({"_id": 1})
    configs = [config for config in configs][0]
    MainClass.configs = configs
    try:
        modules.scanner.openPort()
    except:
        pass
    try:
        modules.rfid.openPort()
    except:
        pass
    return jsonify({"msg": "sucesso!"}), 200


@app.route("/getConfig", methods=["GET"])
def getConfig():
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]

    configs = db["config"].find({"_id": 1})

    configs = [config for config in configs][0]
    MainClass.configs = configs

    return jsonify({"configs": configs}), 200


@app.route("/changeImage", methods=["POST"])
def changeImage():
    files = request.files.getlist('files[]')


    for file in files:
        file.save(os.path.join("/home/kiosk/Hassegawa/static/imgs/producao", f"1.jpeg"))
    return "", 200

@app.route("/changePDF", methods=["POST"])
def changePDF():
    files = request.files.getlist('files[]')

    for file in files:
        file.save(os.path.join("/home/kiosk/Hassegawa/static", "1.pdf"))

    return "", 200
