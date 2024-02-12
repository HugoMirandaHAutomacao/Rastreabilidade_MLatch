import serial
import time
import threading
from settings import MainProperties, sleep_time
import os
from pymongo import MongoClient
import csv
import urllib3
import modules
import datetime
from PIL import Image
import socket
CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"


class Etiqueta:
    def __init__(self):
        self.banned_variables = []
        self.properties = {}
        self.passo = 0
        self.last_passo = 0

    def updateProperties(self):
        if "properties" in list(self.__dict__):
            self.__dict__.pop("properties")
        self.properties = self.__dict__.copy()

        for var in self.banned_variables:
            if var in list(self.properties):
                self.properties.pop(var)

    def getProperties(self):
        # Update properties dict
        self.updateProperties()
        # Return all properties
        return self.properties.copy()

    def getSerializableProperties(self):
        # Update properties dict
        self.updateProperties(serializable=True)
        # Return all properties
        return self.propertiesSerializable.copy()
    
    def zeraStringLeitura(self):
        modules.plc.writeVar(modules.plc.variables["Código_Etiqueta"],
                             b"".decode("utf-8"))
        code = modules.plc.variables["Código_Etiqueta"]["value"]
        code = str(code).encode().replace(b"\x00", b"").decode("utf-8")[2:]
        while len(code) > 1:
            code = modules.plc.variables["Código_Etiqueta"]["value"]
            code = str(code).encode().replace(b"\x00", b"").decode("utf-8")[2:]

    def parseReaded(self):
        self.readed = modules.plc.variables["Código_Etiqueta"]["value"]
        self.readed = str(self.readed).encode().replace(
            b"\x00", b"").decode("utf-8")[2:]
        return self.readed
    
    def generateNewCode(self):
        client = MongoClient(CONNECTION_STRING)
        db = client["geral"]
        new_code = [code for code in db["rastreabilidade"].find({"_id": 1})
                    ][0]["count"] + 1
        print(new_code)
        new_value = {"count": new_code}
        db["rastreabilidade"].update_one({"_id": 1}, {"$set": new_value})
        now = datetime.datetime.now()
        dt = datetime.datetime.now()
        julian_day = dt.timetuple()
        self.code = f"{str(new_code).zfill(5)}{now.strftime('%y')}{str(julian_day.tm_yday).zfill(3)}{now.strftime('%H%M%S')}"

    def print(self, configs):
        try:
            print("Imprimindo etiqueta!")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((configs["ip_impressora"], 9100))
        except:
            self.msg = "Falha ao conectar-se com a impressora, tentando novamente..."
            print("Falha ao conectar-se com a impressora!")
            return 0
        self.msg = ""

        self.generateNewCode()
        txt = f"""
        SIZE 45.5 mm, 15 mm
        DIRECTION 0,0
        REFERENCE 0,0
        OFFSET 0 mm
        SET PEEL OFF
        SET CUTTER OFF
        SET PARTIAL_CUTTER OFF
        SET TEAR ON
        CLS
        QRCODE 300,115,L,4,A,180,M2,S7,"{self.code}"
        CODEPAGE 1252
        TEXT 178,119,"ROMAN.TTF",180,1,9,"{self.code[:5]}"
        TEXT 178,85,"ROMAN.TTF",180,1,9,"{self.code[5:10]}"
        TEXT 178,49,"ROMAN.TTF",180,1,9,"{self.code[10:8]}:{self.code[12:14]}:{self.code[14:]}"
        PRINT 1,1
        """
        try:
            s.sendall(txt.encode())
        except:
            self.msg = "Falha ao enviar código para a impressora, tentando novamente..."
            print("Falha ao enviar código para impressora")
            return 0

    def cycle(self, configs):
        plc = modules.plc

        client = MongoClient(CONNECTION_STRING)
        
        if self.passo != self.last_passo:
            print(f"Etiqueta > Passo {self.passo}")
            self.last_passo = self.passo

        db = client["geral"]
        if self.passo == 0:
            self.isRetrabalho = False
            modules.plc.writeVar(modules.plc.variables["Rastreabilidade_OK"],
                                 False)
            modules.plc.writeVar(modules.plc.variables["Rastreabilidade_NG"],
                                 False)
            modules.plc.writeVar(modules.plc.variables["Reprovado"],
                                 False)
            modules.plc.writeVar(modules.plc.variables["Aprovado"],
                                 False)
            self.status_rastreabilidade = None
            self.status_final = None

            self.files = {}
            err = self.print(configs)
            
            if err is None:
                self.msg = ""
                self.passo = 10

        elif self.passo == 10:
            self.readed = ""
            if configs["leitura_plc"] == "true":
                self.readed = self.parseReaded()
            else:
                self.readed = modules.scanner.readed
            if self.readed != "" and self.readed != "0":
                self.passo = 15
        
        elif self.passo == 15:
            self.msg = ""
            self.last_readed = self.readed
            if self.readed == self.code:
                self.passo = 25
            else:
                self.msg = f"O código lido '{self.readed}' é diferente do código gerado!"
                time.sleep(.2)
                self.passo = 20

        elif self.passo == 20:
            while not plc.variables["Rastreabilidade_NG"]["value"]:
                plc.writeVar(plc.variables["Rastreabilidade_NG"], True)
                time.sleep(.2)
            self.status_rastreabilidade = False

            if configs["leitura_plc"] == "true":
                self.zeraStringLeitura()
            else:
                modules.scanner.readed = ""
            self.passo = 0

        elif self.passo == 25:
            while not plc.variables["Rastreabilidade_OK"]["value"]:
                plc.writeVar(plc.variables["Rastreabilidade_OK"], True)
                time.sleep(.2)
            self.status_rastreabilidade = True

            if configs["leitura_plc"] == "true":
                self.zeraStringLeitura()
            else:
                modules.scanner.readed = ""
            self.passo = 30


        elif self.passo == 30:
            if plc.variables["Aprovado"]["value"]:
                self.status_final = True
                if configs["ftp"] == "true":
                    self.passo = 35
                else:
                    self.passo = 40
                if configs["leitura_plc"] == "true":
                    self.zeraStringLeitura()
                else:
                    modules.scanner.readed = ""
                self.status_final = True

            elif plc.variables["Reprovado"]["value"]:
                self.status_final = False
                if configs["ftp"] == "true":
                    img_count = int(configs["qntd_ftp"])
                    for path, _, files in os.walk("static/FTP/files"):
                        if len(files) == img_count:
                            for file in files:
                                os.remove(os.path.join(path, file))
                self.passo = 33
                
                
            elif self.passo == 33:
                try:
                    last_id = next(
                        i["_id"] + 1 for i in db["reprovados"].find().sort('_id', -1).limit(1))
                except:
                    last_id = 1
                now = datetime.datetime.now()
                tt = now.timetuple()
                info = {}
                info[configs["nome_totem"]] = {}
                info[configs["nome_totem"]]["operador"] = MainProperties["user"]
                info[configs["nome_totem"]
                    ]["horário"] = f"{now.hour}:{now.minute}:{now.second}"
                info[configs["nome_totem"]
                    ]["data"] = f"{now.day}/{now.month}/{now.year}"
                for key, var in plc.variables.items():
                    if "type" not in list(var):
                        info[configs["nome_totem"]][key] = var["value"]
                info["code"] = self.code
                info["_id"] = last_id
                info["files"] = self.files

                info["day"] = tt.tm_yday
                db["reprovados"].insert_one(info)
                
                self.passo = 34
                
            elif self.passo == 34:
                while plc.variables["Reprovado"]["value"]:
                    plc.writeVar(plc.variables["Reprovado"], False)
                    time.sleep(.2)
                self.status_rastreabilidade = False

                if configs["leitura_plc"] == "true":
                    self.zeraStringLeitura()
                else:
                    modules.scanner.readed = ""
                self.readed = ""
                self.last_readed = ""
                self.status_final = False
                self.passo = 0

        elif self.passo == 35:
            img_count = int(configs["qntd_ftp"])
            for path, _, files in os.walk("static/FTP/files"):
                if len(files) == img_count:
                    for file in files:
                        file_ext = file.split(".")[-1].lower()
                        image_extensions = ["png", "jpeg", "jpg"]

                        if file_ext in image_extensions:
                            image = Image.open(os.path.join(path, file))

                            image.save(f"static/temp_ftp/{file}",
                                       "png",
                                       optimize=True,
                                       quality=50)
                            with open(f"static/temp_ftp/{file}", "rb") as f:
                                self.files[file] = f.read()
                            os.remove(f"static/temp_ftp/{file}")
                        else:
                            with open(os.path.join(path, file), "rb") as f:
                                self.files[file] = f.read()

                        os.remove(os.path.join(path, file))
                    self.passo = 40

        elif self.passo == 40:
            try:
                last_id = next(
                    i["_id"] + 1 for i in db["aprovados"].find().sort('_id', -1).limit(1))
            except:
                last_id = 1
            info = {}
            now = datetime.datetime.now()
            tt = now.timetuple()
            info[configs["nome_totem"]] = {}
            info[configs["nome_totem"]]["operador"] = MainProperties["user"]
            info[configs["nome_totem"]
                 ]["horário"] = f"{now.hour}:{now.minute}:{now.second}"
            info[configs["nome_totem"]
                 ]["data"] = f"{now.day}/{now.month}/{now.year}"
            for key, var in plc.variables.items():
                if "type" not in list(var):
                    info[configs["nome_totem"]][key] = var["value"]
            info["code"] = self.code
            info["_id"] = last_id
            info["files"] = self.files

            info["processado"] = False
            ips_linha = [i for i in db["ips_linha"].find()]
            info["day"] = tt.tm_yday
            if configs["ultimo_posto"] == "true":
                try:
                    for ip in ips_linha:
                        con_string = f"mongodb://{ip}:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"
                        client_ = MongoClient(con_string)
                        db_ = client_["geral"]

                        db_["aprovados"].delete_many({"code": self.code})
                        db_["reprovados"].delete_many({"code": self.code})
                        db_["aprovados"].delete_many({"sub_code": self.code})
                        db_["reprovados"].delete_many({"sub_code": self.code})
                except Exception as e:
                    print(e)
            db["aprovados"].insert_one(info)
            self.passo = 50

        elif self.passo == 50:
            while plc.variables["Aprovado"]["value"]:
                plc.writeVar(plc.variables["Aprovado"], False)
                time.sleep(.2)
            self.status_rastreabilidade = True

            time.sleep(.5)
            if configs["leitura_plc"] == "true":
                self.zeraStringLeitura()
            else:
                modules.scanner.readed = ""

            self.passo = 0
            
Etiqueta_Module = Etiqueta()