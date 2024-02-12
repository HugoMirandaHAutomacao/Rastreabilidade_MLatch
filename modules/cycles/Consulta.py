import time
import os
from settings import MainProperties, sleep_time
from pymongo import MongoClient
import modules
import datetime
from PIL import Image
CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"


class Consulta:
    def __init__(self):
        self.banned_variables = []
        self.properties = {}
        self.passo = 0
        self.msg = ""
        self.code = ""
        self.last_passo = -1

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

    def verifyRetrabalho(self, db):
        all_codes = db.find_one({"sub_code": self.readed})
        if all_codes is not None:
            self.retrabalho = True
            self.passo = 26
            self.readed_info = [all_codes]
            return True

        all_codes = db.find_one({"code": self.readed})
        if all_codes is not None:
            self.retrabalho = True
            self.passo = 26
            self.readed_info = [all_codes]
            return True

        return False

    def cycle(self, configs):
        plc = modules.plc
        client = MongoClient(CONNECTION_STRING)
        db = client["geral"]
        part_info = []
        if self.passo != self.last_passo:
            self.last_passo = self.passo
            print(f"Consulta > Passo {self.passo}")

        if self.passo == 0:
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
            self.retrabalho = None
            self.continua_retrabalho = None
            self.isRetrabalho = False

            if configs["leitura_plc"] == "true":
                self.readed = self.parseReaded()
            else:
                self.readed = modules.scanner.readed

            if self.readed != "" and self.readed != "0":
                self.passo = 10

        elif self.passo == 10:
            self.msg = ""
            self.last_readed = self.readed
            print(f"> Valor lido: {self.readed}")
            self.passo = 15

        elif self.passo == 15:
            ret = self.verifyRetrabalho(db["aprovados"])
            if ret:
                return
            ret = self.verifyRetrabalho(db["reprovados"])
            if ret:
                return

            self.passo = 20

        elif self.passo == 20:

            all_routes = db["desvio_rotas"].find()
            cod_cliente = plc.variables["Código_Cliente"]["value"]
            cod_cliente = str(cod_cliente).encode().replace(
                b"\x00", b"").decode("utf-8")[2:]

            ip_desvio = [
                rota["ip"] for rota in all_routes
                if rota["codigo"] == cod_cliente
            ]
            ip_consulta = ip_desvio[0] if len(
                ip_desvio) > 0 else configs["ip_consulta"]
            con_string = f"mongodb://{ip_consulta}:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"
            client_ = MongoClient(con_string)
            self.db_consulta = client_["geral"]

            self.passo = 25

        elif self.passo == 25:
            part_info = []
            all_codes = self.self.db_consulta["aprovados"].find_one(
                {"sub_code": self.readed})
            if all_codes is not None:
                part_info.append(all_codes)
            all_codes = self.self.db_consulta["aprovados"].find_one(
                {"code": self.readed})
            if all_codes is not None:
                part_info.append(all_codes)

            self.readed_info = part_info
            if len(part_info) > 0:
                print("Consulta > Código aprovado!")
                if configs["leitura_plc"] == "true":
                    self.zeraStringLeitura()
                else:
                    modules.scanner.readed = ""
                self.passo = 30
                self.from_server = False
            else:
                self.msg = f"O código lido '{self.readed}' não existe no posto anterior!"
                time.sleep(2)
                if configs["leitura_plc"] == "true":
                    self.zeraStringLeitura()
                else:
                    modules.scanner.readed = ""
                self.passo = 0

        elif self.passo == 26:
            if not self.retrabalho:
                if self.continua_retrabalho:
                    permissions = MainProperties["user"]["permissions"]
                    auth = permissions["Administrador"] or permissions["Líder"]
                    MainProperties["retrabalho"] = not auth
                    try:
                        if MainProperties["user_retrabalho"] != {} or auth:
                            if len(list(MainProperties["user_retrabalho"])) > 0 and not auth:
                                permissions = MainProperties["user_retrabalho"]["permissions"]
                                if permissions["Administrador"] or permissions["Líder"] or auth:
                                    MainProperties["user_retrabalho"] = {}
                                    MainProperties["retrabalho"] = False

                                    self.isRetrabalho = True
                                    self.passo = 30
                            else:
                                if auth:
                                    MainProperties["user_retrabalho"] = {}
                                    MainProperties["retrabalho"] = False

                                    self.isRetrabalho = True
                                    self.passo = 30
                    except Exception as e:
                        print(e)
                else:
                    if configs["leitura_plc"] == "true":
                        self.zeraStringLeitura()
                    else:
                        modules.scanner.readed = ""
                    self.passo = 0

        elif self.passo == 30:
            while not plc.variables["Rastreabilidade_OK"]["value"]:
                plc.writeVar(plc.variables["Rastreabilidade_OK"], True)
                time.sleep(.2)
            print("Consulta > Código aprovado")
            self.status_rastreabilidade = True
            if configs["leitura_plc"] == "true":
                self.zeraStringLeitura()
            else:
                modules.scanner.readed = ""
            self.passo = 35

        elif self.passo == 35:
            while not plc.variables["Rastreabilidade_NG"]["value"]:
                plc.writeVar(plc.variables["Rastreabilidade_NG"], True)
                time.sleep(.2)
            print("Consulta > Código reprovado")
            self.status_rastreabilidade = False
            if configs["leitura_plc"] == "true":
                self.zeraStringLeitura()
            else:
                modules.scanner.readed = ""
            self.passo = 40

        elif self.passo == 40:
            if plc.variables["Aprovado"]["value"]:
                print("Consulta > Peça aprovada!")
                self.status_final = True

                if configs["ftp"] == "true":
                    self.passo = 45
                else:
                    self.passo = 50
                self.status_final = True
            elif plc.variables["Reprovado"]["value"]:
                self.passo = 41

        elif self.passo == 41:
            self.status_final = False
            print("Consulta > Peça reprovada!")

            if configs["ftp"] == "true":
                img_count = int(configs["qntd_ftp"])
                for path, _, files in os.walk("static/FTP/files"):
                    if len(files) == img_count:
                        for file in files:
                            os.remove(os.path.join(path, file))

            self.passo = 42
        elif self.passo == 42:
            try:
                last_id = next(
                    i["_id"] + 1 for i in db["reprovados"].find().sort('_id', -1).limit(1))
            except:
                last_id = 1
            part_info = self.readed_info[0]
            now = datetime.datetime.now()
            tt = now.timetuple()
            nome_totem = configs["nome_totem"]
            part_info[nome_totem] = {}
            part_info[nome_totem]["operador"] = MainProperties["user"]
            part_info[nome_totem]["horário"] = f"{now.hour}:{now.minute}:{now.second}"
            part_info[nome_totem]["data"] = f"{now.day}/{now.month}/{now.year}"
            part_info[nome_totem]["retrabalho"] = self.isRetrabalho
            for key, var in plc.variables.items():
                if "type" not in list(var):
                    part_info[nome_totem][key] = var["value"]
            part_info["code"] = self.code
            part_info["_id"] = last_id
            part_info["files"] = self.files

            part_info["day"] = tt.tm_yday

            db["reprovados"].insert_one(part_info)

            self.passo = 43

        elif self.passo == 43:
            while plc.variables["Reprovado"]["value"]:
                plc.writeVar(plc.variables["Reprovado"], False)
                time.sleep(.2)
            self.status_rastreabilidade = False
            self.status_final = False
            if configs["leitura_plc"] == "true":
                self.zeraStringLeitura()
            else:
                modules.scanner.readed = ""
            self.passo = 0

        elif self.passo == 45:
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
                    self.passo = 50

        elif self.passo == 50:
            if self.continua_retrabalho:
                db["aprovados"].delete_one(
                    {"sub_code": self.readed})
                db["aprovados"].delete_one({"code": self.readed})

            self.passo = 51

        elif self.passo == 51:

            try:
                last_id = next(
                    i["_id"] + 1 for i in db["aprovados"].find().sort('_id', -1).limit(1))
            except:
                last_id = 1
            self.readed_info = self.readed_info[0]
            now = datetime.datetime.now()
            tt = now.timetuple()
            self.readed_info["day"] = tt.tm_yday
            self.readed_info["_id"] = last_id
            nome_totem = configs["nome_totem"]
            self.readed_info[nome_totem] = {}
            self.readed_info[nome_totem]["operador"] = MainProperties["user"]
            self.readed_info[nome_totem]["horário"] = f"{now.hour}:{now.minute}:{now.second}"
            self.readed_info[nome_totem]["data"] = f"{now.day}/{now.month}/{now.year}"
            self.readed_info[nome_totem]["retrabalho"] = self.isRetrabalho
            for key, var in plc.variables.items():
                if "type" not in list(var):
                    self.readed_info[nome_totem][key] = var["value"]

            self.passo = 52

        elif self.passo == 52:
            if configs["ultimo_posto"] == "true":
                self.readed_info["processado"] = False
                ips_linha = [i for i in db["ips_linha"].find()]
                try:
                    for ip in ips_linha:
                        con_string = f"mongodb://{ip['ip']}:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"
                        client_ = MongoClient(con_string)
                        db_ = client_["geral"]

                        db_["aprovados"].delete_many({"code": self.readed})
                        db_["reprovados"].delete_many({"code": self.readed})
                        db_["aprovados"].delete_many({"sub_code": self.readed})
                        db_["reprovados"].delete_many(
                            {"sub_code": self.readed})
                except Exception as e:
                    print(e)
            db["aprovados"].insert_one(self.readed_info)
            self.passo = 60

        elif self.passo == 60:
            while plc.variables["Aprovado"]["value"]:
                plc.writeVar(plc.variables["Aprovado"], False)
                time.sleep(.2)
            self.status_rastreabilidade = True

            time.sleep(2)

            if configs["leitura_plc"] == "true":
                self.zeraStringLeitura()
            else:
                modules.scanner.readed = ""

            self.passo = 0


Consulta_Module = Consulta()
