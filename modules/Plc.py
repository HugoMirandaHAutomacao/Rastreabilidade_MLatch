import time
import threading
from settings import sleep_time, MainProperties
from pymongo import MongoClient
import os
import snap7
from snap7.util import *

CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"


class Plc:
    def __init__(self):
        self.banned_variables = ["plc"]
        self.properties = {}
        self.con = None
        self.variables = {}
        self.variables_parafusadeira = {}
        self.plc = {}

    def updateProperties(self):
        if "properties" in list(self.__dict__):
            self.__dict__.pop("properties")
        self.properties = self.__dict__.copy()
        for variable in self.banned_variables:
            if variable in list(self.properties):
                self.properties.pop(variable)

    def setupPlcs(self):
        client = MongoClient(CONNECTION_STRING)
        db = client["geral"]

        all_plcs = db["plc"].find()
        plc_info = [plc for plc in all_plcs][0]

        rack = plc_info["rack"]
        slot = plc_info["slot"]
        ip = plc_info["ip"]

        self.plc = {
            "read": snap7.client.Client(),
            "write": snap7.client.Client(),
            "info": plc_info
        }

        self.plc["read"].connect(ip, int(rack), int(slot))
        self.plc["write"].connect(ip, int(rack), int(slot))
        self.setupVariables()
        
        
    def getVariablesDbSize(self):
        
        db_size = max([int(float(variable["memoria"])) for variable in self.variables.values()]) + 4
        return db_size

    def setupVariables(self):
        client = MongoClient(CONNECTION_STRING)
        db = client["geral"]
        all_params = db["parameter"].find()
        all_params = [param for param in all_params]

        all_parafusadeiras = db["parafusadeira"].find()
        all_parafusadeiras = [parafusadeira for parafusadeira in all_parafusadeiras]
        
        self.variables = {}
        self.variables_parafusadeira = {}
        defaultVariables = [
            {
                "param": "Aprovado",
                "memoria": "0.0",
                "type": "BOOL"
            },
            {
                "param": "Reprovado",
                "memoria": "0.1",
                "type": "BOOL"
            },
            {
                "param": "Rastreabilidade_OK",
                "memoria": "0.2",
                "type": "BOOL"
            },
            {
                "param": "Rastreabilidade_NG",
                "memoria": "0.3",
                "type": "BOOL"
            },
            {
                "param": "Código_Cliente",
                "memoria": "6",
                "type": "STRING[58]"
            },
            {
                "param": "Código_Etiqueta",
                "memoria": "66",
                "type": "STRING[28]"
            },
            {
                "param": "Contador_Aprovadas",
                "memoria": "2",
                "type": "INT"
            },
            {
                "param": "Contador_Reprovadas",
                "memoria": "4",
                "type": "INT"
            },
            {
                "param": "Zerar_Contador",
                "memoria": "0.4",
                "type": "BOOL"
            },
        ]
        for var in defaultVariables:
            self.variables[var["param"]] = var

        for param in all_params:
            self.variables[param["param"]] = param

        for parafusadeira in all_parafusadeiras:
            self.variables_parafusadeira[parafusadeira["ip"]] = {}
            self.variables_parafusadeira[parafusadeira["ip"]]["db"] = parafusadeira["db_parafusadeira"]
            self.variables_parafusadeira[parafusadeira["ip"]]['bit_solicitação'] = {
                "param": "bit_solicitação",
                "memoria": parafusadeira["bit_solicitacao"],
                "type": "BOOL"
            }
            self.variables_parafusadeira[parafusadeira["ip"]][f'bit_confirmação'] = {
                "param": "bit_confirmacão",
                "memoria": parafusadeira["bit_confirmacao"],
                "type": "BOOL"
            }
            self.variables_parafusadeira[parafusadeira["ip"]][f'memoria_torque'] = {
                "param": "memoria_torque",
                "memoria": parafusadeira["memoria_torque"],
                "type": "REAL"
            }
            self.variables_parafusadeira[parafusadeira["ip"]][f'memoria_tempo'] = {
                "param": "memoria_tempo",
                "memoria": parafusadeira["memoria_tempo"],
                "type": "REAL"
            }
            
            MainProperties["updateParafusadeira"] = True

    def writeVar(self, var, value, db=None):
        return
        if db is None:
            db = self.plc["info"]["db"]
        if "type" in list(var):
            if "STRING" in var["type"]:
                length = int(var["type"].split("[")[1].replace("]", ""))
                db_buffer = self.plc["write"].db_read(db,
                                                      int(var["memoria"]),
                                                      length)
                

                set_string(db_buffer, 0, value, length)
            elif var["type"] == "INT":
                db_buffer = self.plc["write"].db_read(db,
                                                      int(var["memoria"]), 2)

                set_int(db_buffer, 0, value)
            elif var["type"] == "BOOL":
                db_buffer = self.plc["write"].db_read(db,
                                                      int(float(
                                                          var["memoria"])),
                                                      1)
                set_bool(db_buffer, 0, int(
                    var["memoria"].split(".")[1]), value)
            else:
                db_buffer = self.plc["write"].db_read(db,
                                                      int(float(var["memoria"])), 4)
                
                set_real(db_buffer,0, value)
        else:
            print("AQUI")
            db_buffer = self.plc["write"].db_read(db,
                                                  int(float(var["memoria"])),
                                                  4)
            set_real(db_buffer, 0, value)
        self.plc["write"].db_write(db, int(
            float(var["memoria"])), db_buffer)

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

    def thread(self):
        while True:
            try:
                #self.setupPlcs()
                while True:
                    time.sleep(sleep_time)
                    self.variables["Aprovado"] = True
                    self.variables["Contador_Aprovadas"] = 20
                    self.variables["Contador_Reprovadas"] = 2
                    self.variables["Reprovado"] = False
                    self.variables["Rastreabilidade_OK"] = True
                    self.variables["Rastreabilidade_NG"] = False
                    return
                    db_size = self.getVariablesDbSize()
                    
                    db_buffer = self.plc["read"].db_read(
                        self.plc["info"]["db"], 0, db_size)
                    for variable in self.variables.values():
                        if "type" in list(variable):
                            if variable["type"] == "BOOL":
                                variable["value"] = get_bool(
                                    db_buffer, int(
                                        variable["memoria"].split(".")[0]),
                                    int(variable["memoria"].split(".")[1]))
                            elif variable["type"] == "INT":
                                variable["value"] = get_int(
                                    db_buffer, int(variable["memoria"]))
                            elif "STRING" in variable["type"]:
                                length = int(variable["type"].split(
                                    "[")[1].replace("]", ""))
                                variable["value"] = get_fstring(
                                    db_buffer, int(variable["memoria"]), length)
                        else:
                            variable["value"] = get_real(
                                db_buffer, int(variable["memoria"].split(".")[0]))
                    """ for values in self.variables_parafusadeira.values():
                        db = values["db"]
                        db_size = 10
                        db_buffer = self.plc["read"].db_read(
                            int(db), 0, db_size)
                        for key, variable in values.items():
                            if key != "db":
                                if "type" in list(variable):
                                    if variable["type"] == "BOOL":
                                        variable["value"] = get_bool(
                                            db_buffer, int(
                                                variable["memoria"].split(".")[0]),
                                            int(variable["memoria"].split(".")[1]))
                                    elif variable["type"] == "INT":
                                        variable["value"] = get_int(
                                            db_buffer, int(variable["memoria"]))
                                    elif "STRING" in variable["type"]:
                                        length = int(variable["type"].split(
                                            "[")[1].replace("]", ""))
                                        variable["value"] = get_fstring(
                                            db_buffer, int(variable["memoria"]), length)
                                else:
                                    variable["value"] = get_real(
                                        db_buffer, int(variable["memoria"].split(".")[0])) """
            except Exception as e:
                time.sleep(20)
                print(e)


Plc_Module = Plc()
threading.Thread(target=Plc_Module.thread).start()
