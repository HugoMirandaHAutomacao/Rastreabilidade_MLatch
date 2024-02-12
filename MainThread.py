import time
import threading
from settings import sleep_time, MainProperties, verifyConnection
import datetime
import os
import json
import socket
import modules
import datetime
from modules.Parafusadeira import Parafusadeira
from PIL import Image
import urllib3
from urllib3.exceptions import MaxRetryError
from pymongo import MongoClient
CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"


class MainThread:

    def __init__(self):
        self.banned_variables = ["files", "readed_info"]
        self.properties = {}
        self.producao = False
        self.receita = {}
        self.passo = 0
        self.code = ""
        self.status_rastreabilidade = None
        self.status_final = None
        self.readed = ""
        self.readed_info = []
        self.last_readed = ""
        self.files = {}
        self.retrabalho = None
        self.continua_retrabalho = None
        self.isRetrabalho = False
        self.from_server = False
        self.db_name_server = ""
        self.aprovados = 0
        self.reprovados = 0
        self.netmask_notation = {
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

    def updateProperties(self):
        if "properties" in self.__dict__:
            self.__dict__.pop("properties")
        self.properties = self.__dict__.copy()
        for key in self.banned_variables:
            if key in list(self.properties):
                self.properties.pop(key)

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

    def updateMainProperties(self):
        last_readed = "-1"
        while True:
            try:
                time.sleep(sleep_time)
                MainProperties["Cycle"] = self.getProperties()
                MainProperties["PLC"] = modules.plc.getProperties()
                if modules.rfid.readed != "" and modules.rfid.readed != last_readed:
                    last_readed = modules.rfid.readed
                    MainProperties["rfid"] = modules.rfid.readed
                MainProperties["Scanner"] = modules.scanner.getProperties()

            except Exception as e:
                print(e)

    def verifyCodes(self):
        while True:
            try:
                client = MongoClient(CONNECTION_STRING)
                db = client["geral"]
                import datetime
                now = datetime.datetime.now()
                tt = now.timetuple()
                julian_day = tt.tm_yday
                aprovados = db["aprovados"].find()

                aprovados = [aprovado for aprovado in aprovados]

                for aprovado in aprovados:
                    try:
                        if int(julian_day) - int(aprovado["day"]) >= 10:
                            db["aprovados"].delete_many(
                                {"_id": aprovado["_id"]})
                    except KeyError:
                        pass

                reprovados = db["reprovados"].find()

                reprovados = [reprovado for reprovado in reprovados]

                for reprovados in reprovados:
                    try:
                        if int(julian_day) - int(reprovados["day"]) >= 10:
                            db["reprovados"].delete_many(
                                {"_id": reprovados["_id"]})
                    except KeyError:
                        pass

                time.sleep(1800)
            except Exception as e:
                print(e)

    def thread(self):
        threading.Thread(target=self.updateMainProperties).start()
        threading.Thread(target=self.verifyCodes).start()
        while True:
            try:
                time.sleep(sleep_time)
                client = MongoClient(CONNECTION_STRING)
                db = client["geral"]
                self.configs = db["config"].find({"_id": 1})

                self.configs = [config for config in self.configs][0]

                # self.configureEthernet()

                while True:
                    try:
                        time.sleep(sleep_time)
                        if self.producao:
                            if self.configs["etiqueta"] == "true":
                                modules.cycles.etiqueta.cycle(self.configs)
                                self.code = modules.cycles.etiqueta.code
                                self.status_rastreabilidade = modules.cycles.etiqueta.status_rastreabilidade
                                self.status_final = modules.cycles.etiqueta.status_final
                                self.readed = modules.cycles.etiqueta.readed
                                self.msg = modules.cycles.etiqueta.msg

                            elif self.configs["consulta"] == "true":
                                modules.cycles.consulta.cycle(self.configs)
                                self.code = modules.cycles.consulta.code
                                self.status_rastreabilidade = modules.cycles.consulta.status_rastreabilidade
                                self.status_final = modules.cycles.consulta.status_final
                                self.readed = modules.cycles.consulta.readed
                                self.msg = modules.cycles.consulta.msg

                            elif self.configs["subEtiqueta"] == "true":
                                modules.cycles.subEtiqueta.cycle(self.configs)
                                self.code = modules.cycles.subEtiqueta.code
                                self.status_rastreabilidade = modules.cycles.subEtiqueta.status_rastreabilidade
                                self.status_final = modules.cycles.subEtiqueta.status_final
                                self.readed = modules.cycles.subEtiqueta.readed
                                self.msg = modules.cycles.subEtiqueta.msg
                                
                            elif self.configs["consulta_cod"] == "true":
                                self.code = modules.cycles.ConsultaCodPadrao.read_code
                                self.status_final = modules.cycles.ConsultaCodPadrao.status_final
                                self.status_rastreabilidade = modules.cycles.ConsultaCodPadrao.status_rastreabilidade
                                self.msg = modules.cycles.ConsultaCodPadrao.msg
                                self.aprovados = modules.cycles.ConsultaCodPadrao.aprovados
                                self.reprovados = modules.cycles.ConsultaCodPadrao.reprovados
                                modules.cycles.ConsultaCodPadrao.executeStep(self.passo)
                            

                        else:
                            modules.cycles.consulta.passo = 0
                            modules.cycles.etiqueta.passo = 0
                            modules.cycles.subEtiqueta.passo = 0
                            self.code = ""
                            self.status_rastreabilidade = None
                            self.status_final = None
                            self.readed = ""

                    except Exception as e:
                        print(e)

            except Exception as e:
                print(e)

    def configureEthernet(self):
        os.system(
            "sudo chmod 777 /etc/netplan/01-network-manager-all.yaml")
        with open("/etc/netplan/01-network-manager-all.yaml", "w") as f:
            f.write(f"""
                                network:
                                    ethernets:
                                        enp3s0:
                                            dhcp4: false
                                            addresses: [{self.configs['ip']}/{self.netmask_notation[self.configs['netmask']]}]
                                            gateway4: {self.configs['gateway']}
                                            nameservers:
                                                addresses: [{self.configs['gateway']}]
                                    version: 2""")
        os.system("sudo netplan apply")


Parafusadeira_module = Parafusadeira(modules.plc)
threading.Thread(target=Parafusadeira_module.thread).start()

MainClass = MainThread()
threading.Thread(target=MainClass.thread).start()
