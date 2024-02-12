import time
from settings import MainProperties
import os
from pymongo import MongoClient
import modules
import datetime
from PIL import Image
import socket
CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"


class SubEtiqueta:
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

    def verifyRetrabalho(self, db):
        all_codes = db.find_one({"sub_code": self.readed})
        if all_codes is not None:
            self.retrabalho = True
            self.passo = 16
            self.readed_info = [all_codes]
            return True

        all_codes = db.find_one({"code": self.readed})
        if all_codes is not None:
            self.retrabalho = True
            self.passo = 16
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
            self.isRetrabalho = False
            self.readed = ""
            if self.configs["leitura_plc"] == "true":
                readed = self.parseReaded()
                if len(readed) in [16, 14]:
                    self.readed = readed
                else:
                    self.msg = "Falha na leitura da etiqueta, número de caracteres inválidos"
            else:
                readed = modules.scanner.readed
                if len(readed) in [16, 14]:
                    self.readed = readed
                else:
                    self.msg = "Falha na leitura da etiqueta, número de caracteres inválidos"
            if self.readed != "" and self.readed != "0":
                self.passo = 5

        elif self.passo == 5:
            self.msg = ""
            self.last_readed = self.readed
            ret = self.verifyRetrabalho(db["aprovados"])
            if ret:
                return
            ret = self.verifyRetrabalho(db["reprovados"])
            if ret:
                return

            self.passo = 10

        elif self.passo == 10:
            all_routes = db["desvio_rotas"].find()
            cod_cliente = plc.variables["Código_Cliente"]["value"]
            cod_cliente = str(cod_cliente).encode().replace(
                b"\x00", b"").decode("utf-8")[2:]

            ip_desvio = [
                rota["ip"] for rota in all_routes
                if rota["codigo"] == cod_cliente
            ]
            ip_consulta = ip_desvio[0] if len(
                ip_desvio) > 0 else self.configs["ip_consulta"]
            con_string = f"mongodb://{ip_consulta}:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"

            client_ = MongoClient(con_string)

            db_ = client_["geral"]
            part_info = []
            all_codes = db_["aprovados"].find_one({"code": self.readed})
            if all_codes is not None:
                part_info.append(all_codes)

            self.readed_info = part_info
            self.passo = 15

        elif self.passo == 15:
            if len(self.readed_info) == 1:
                print("Código Aprovado!")
                if self.configs["leitura_plc"] == "true":
                    self.zeraStringLeitura()
                else:
                    modules.scanner.readed = ""
                self.passo = 20
                self.from_server = False
            else:
                self.msg = f"O código lido '{self.readed}' não existe no posto anterior!"
                while not plc.variables["Rastreabilidade_NG"]["value"]:
                    plc.writeVar(plc.variables["Rastreabilidade_NG"], True)
                    time.sleep(.2)
                if self.configs["leitura_plc"] == "true":
                    self.zeraStringLeitura()
                else:
                    modules.scanner.readed = ""
                print("Código Reprovado")
                self.passo = 0

        elif self.passo == 16:
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
                                    self.passo = 10
                            else:
                                if auth:
                                    MainProperties["user_retrabalho"] = {}
                                    MainProperties["retrabalho"] = False

                                    self.isRetrabalho = True
                                    self.passo = 10
                    except Exception as e:
                        print(e)
                else:
                    if self.configs["leitura_plc"] == "true":
                        self.zeraStringLeitura()
                    else:
                        modules.scanner.readed = ""
                    self.passo = 0

        if self.passo == 20:
            self.generateSubCode()
            print("Imprimindo etiqueta!")
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.configs["ip_impressora"], 9100))
            except:
                self.msg = f"Falha ao conectar-se a impressora, tentando novamente...!"
                return 0

            self.msg = ""
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
            DMATRIX 210,13,100,100,x5,18,18,"{self.code}"
            CODEPAGE 1252
            TEXT 200,113,"ROMAN.TTF",180,1,7,"{self.code[:11]}"
            TEXT 200,83,"ROMAN.TTF",180,1,7,"{self.code[11:16]}"
            TEXT 200,53,"ROMAN.TTF",180,1,7,"{self.code[16:21]}"
            TEXT 200,23,"ROMAN.TTF",180,1,7,"{self.code[21:]}"
            PRINT 1,1
            """
            try:
                s.sendall(txt.encode())
            except:
                self.msg = f"Falha ao conectar-se a impressora, tentando novamente...!"
                return 0
            self.msg = ""
            self.passo = 30

        elif self.passo == 30:
            self.readed = ""
            if self.configs["leitura_plc"] == "true":
                readed = self.parseReaded()
                if len(readed) == 26:
                    self.readed = readed
                else:
                    self.msg = "Falha na leitura da etiqueta, número de caracteres inválidos"
            else:
                readed = modules.scanner.readed
                if len(readed) == 26:
                    self.readed = readed
                else:
                    self.msg = "Falha na leitura da etiqueta, número de caracteres inválidos"
            if self.readed != "" and self.readed != "0":
                self.passo = 35

        elif self.passo == 35:
            self.last_readed = self.readed
            print(f"> Valor lido: {self.readed}")
            print(f"> Código atual: {self.code}")
            if self.readed == self.code:
                print("Código igual!")
                if self.configs["leitura_plc"] == "true":
                    self.zeraStringLeitura()
                else:
                    modules.scanner.readed = ""
                self.passo = 40
            else:
                self.msg = f"O código lido '{self.readed}' é diferente do código gerado '{self.code}'"
                time.sleep(2)
                if self.configs["leitura_plc"] == "true":
                    self.zeraStringLeitura()
                else:
                    modules.scanner.readed = ""
                print("Código diferente")
                self.passo = 41

        elif self.passo == 40:
            while not plc.variables["Rastreabilidade_OK"]["value"]:
                plc.writeVar(plc.variables["Rastreabilidade_OK"], True)
                time.sleep(.2)
            print("ENVIOU RASTREABILIDADE OK")
            self.status_rastreabilidade = True

            if self.configs["leitura_plc"] == "true":
                self.zeraStringLeitura()
            else:
                modules.scanner.readed = ""
            self.passo = 50

        elif self.passo == 41:
            while not plc.variables["Rastreabilidade_NG"]["value"]:
                plc.writeVar(plc.variables["Rastreabilidade_NG"], True)
                time.sleep(.2)
            print("ENVIOU RASTREABILIDADE NG")
            self.status_rastreabilidade = False

            if self.configs["leitura_plc"] == "true":
                self.zeraStringLeitura()
            else:
                modules.scanner.readed = ""
            self.readed = ""
            self.passo = 0

        elif self.passo == 50:
            all_routes = db["desvio_rotas"].find()
            cod_cliente = plc.variables["Código_Cliente"]["value"]
            cod_cliente = str(cod_cliente).encode().replace(
                b"\x00", b"").decode("utf-8")[2:]

            ip_desvio = [
                rota["ip"] for rota in all_routes
                if rota["codigo"] == cod_cliente
            ]
            ip_consulta = ip_desvio[0] if len(
                ip_desvio) > 0 else self.configs["ip_consulta"]
            con_string = f"mongodb://{ip_consulta}:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"
            client_ = MongoClient(con_string)
            db_ = client_["geral"]
            if plc.variables["Aprovado"]["value"]:
                print("Recebeu aprovado do plc")
                self.status_final = True

                self.status_final = True
                if self.configs["ftp"] == "true":
                    self.passo = 55
                else:
                    self.passo = 60
            elif plc.variables["Reprovado"]["value"]:
                self.status_final = False

                if self.configs["ftp"] == "true":
                    img_count = int(self.configs["qntd_ftp"])
                    for path, _, files in os.walk("static/FTP/files"):
                        if len(files) == img_count:
                            for file in files:
                                os.remove(os.path.join(path, file))
                self.passo = 51
                
        elif self.passo == 51:
            try:
                last_id = next(
                    i["_id"] + 1 for i in db["reprovados"].find().sort('_id', -1).limit(1))
            except:
                last_id = 1
            part_info = self.readed_info[0]
            now = datetime.datetime.now()
            tt = now.timetuple()
            nome_totem = self.configs["nome_totem"]
            part_info[nome_totem] = {}
            part_info[nome_totem]["operador"] = MainProperties["user"]
            part_info[nome_totem]["horário"] = f"{now.hour}:{now.minute}:{now.second}"
            part_info[nome_totem]["data"] = f"{now.day}/{now.month}/{now.year}"
            part_info[nome_totem]["retrabalho"] = self.isRetrabalho
            part_info["sub_code"] = self.code
            for key, var in plc.variables.items():
                if "type" not in list(var):
                    part_info[nome_totem][key] = var["value"]
            part_info["code"] = self.code
            part_info["_id"] = last_id
            part_info["files"] = self.files

            part_info["day"] = tt.tm_yday

            db["reprovados"].insert_one(part_info)

            self.status_final = False
            while plc.variables["Reprovado"]["value"]:
                plc.writeVar(plc.variables["Reprovado"], False)
                time.sleep(.2)
            self.status_rastreabilidade = False

            if self.configs["leitura_plc"] == "true":
                self.zeraStringLeitura()
            else:
                modules.scanner.readed = ""
            self.passo = 0

        elif self.passo == 55:
            img_count = int(self.configs["qntd_ftp"])
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
                    self.passo = 60

        elif self.passo == 60:
            try:
                last_id = next(
                    i["_id"] + 1 for i in db["aprovados"].find().sort('_id', -1).limit(1))
            except:
                last_id = 1
            part_info = self.readed_info[0]
            import datetime
            now = datetime.datetime.now()
            tt = now.timetuple()
            part_info["day"] = tt.tm_yday
            part_info["_id"] = last_id

            nome_totem = self.configs["nome_totem"]
            part_info[nome_totem] = {}
            part_info[nome_totem]["operador"] = MainProperties["user"]
            part_info[nome_totem]["horário"] = f"{now.hour}:{now.minute}:{now.second}"
            part_info[nome_totem]["data"] = f"{now.day}/{now.month}/{now.year}"
            part_info[nome_totem]["retrabalho"] = self.isRetrabalho
            for key, var in plc.variables.items():
                if "type" not in list(var):
                    part_info[nome_totem][key] = var["value"]
            part_info["sub_code"] = self.code
            if self.configs["ultimo_posto"] == "true":
                part_info["processado"] = False
                ips_linha = [i for i in db["ips_linha"].find()]
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
            db["aprovados"].insert_one(part_info)
            self.passo = 70

        elif self.passo == 70:
            while plc.variables["Aprovado"]["value"]:
                plc.writeVar(plc.variables["Aprovado"], False)
                time.sleep(.2)
            self.status_rastreabilidade = True
            time.sleep(.5)
            if self.configs["leitura_plc"] == "true":
                self.zeraStringLeitura()
            else:
                modules.scanner.readed = ""

            self.passo = 0

    def generateSubCode(self):
        client = MongoClient(CONNECTION_STRING)
        db = client["geral"]
        plc = modules.plc
        cod_unico = self.configs["cod_unico"]
        cod_cliente = plc.variables["Código_Cliente"]["value"]
        cod_cliente = str(cod_cliente).encode().replace(
            b"\x00", b"").decode("utf-8")[2:]
        new_code = [code for code in db["rastreabilidade"].find({"_id": 1})
                    ][0]["count"] + 1
        new_value = {"count": new_code}
        db["rastreabilidade"].update_one({"_id": 1}, {"$set": new_value})
        sequencial = str(new_code).zfill(5)
        now = datetime.datetime.now()
        dt = datetime.datetime.now()
        julian_day = str(dt.timetuple().tm_yday).zfill(3)
        self.code = f"{cod_cliente}{cod_unico}{sequencial}{julian_day}{now.strftime('%y')}"


SubEtiqueta_module = SubEtiqueta()
