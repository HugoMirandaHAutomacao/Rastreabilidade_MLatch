import serial
import time
import threading
from settings import MainProperties, sleep_time
import os
from pymongo import MongoClient
import csv
import urllib3
CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"


class Parafusadeira:
    def __init__(self, plc):
        self.banned_variables = []
        self.properties = {}
        self.passos = {}
        self.plc = plc

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

    def thread_parafusadeira(self, parafusadeira):
        ip_parafusadeira = parafusadeira["ip"]
        db = int(parafusadeira["db_parafusadeira"])
        if parafusadeira["ip"] not in list(self.passos):
            self.passos[ip_parafusadeira] = 0
        while True:
            try:
                time.sleep(sleep_time)
                passo = self.passos[ip_parafusadeira]

                if MainProperties["updateParafusadeira"]:
                    break

                if passo == 0:
                    if self.plc.variables_parafusadeira[parafusadeira["ip"]][f'bit_confirmação']["value"]:
                        self.plc.writeVar(
                            self.plc.variables_parafusadeira[parafusadeira["ip"]][f'bit_confirmação'], False, db)
                    if self.plc.variables_parafusadeira[parafusadeira["ip"]][f'bit_solicitação']["value"]:
                        self.passos[ip_parafusadeira] = 10

                elif passo == 10:
                    if "Deprag" in parafusadeira["marca"]:
                        print(ip_parafusadeira)
                        time.sleep(.5)
                        http = urllib3.PoolManager()
                        url = parafusadeira["link"]

                        response = http.request('GET', url)
                        matriz = response.data.decode().split(",")
                        torque = float(matriz[int(parafusadeira["index_torque"])])
                        tempo = float(matriz[int(parafusadeira["index_tempo"])])

                        self.plc.writeVar(
                            self.plc.variables_parafusadeira[parafusadeira["ip"]][f'memoria_torque'], torque, db)
                        self.plc.writeVar(
                            self.plc.variables_parafusadeira[parafusadeira["ip"]][f'memoria_tempo'], tempo, db)
                        self.passos[ip_parafusadeira] = 20
                        
                elif passo == 20:
                    if not self.plc.variables_parafusadeira[parafusadeira["ip"]][f'bit_confirmação']["value"]:
                        self.plc.writeVar(
                            self.plc.variables_parafusadeira[parafusadeira["ip"]][f'bit_confirmação'], True, db)
                    else:
                        self.passos[ip_parafusadeira] = 30

                elif passo == 30:
                    if not self.plc.variables_parafusadeira[parafusadeira["ip"]][f'bit_solicitação']["value"]:
                        self.passos[ip_parafusadeira] = 40

                elif passo == 40:
                    if self.plc.variables_parafusadeira[parafusadeira["ip"]][f'bit_confirmação']["value"]:
                        self.plc.writeVar(
                            self.plc.variables_parafusadeira[parafusadeira["ip"]][f'bit_confirmação'], False, db)
                    else:
                        self.passos[ip_parafusadeira] = 0
            except ConnectionAbortedError as e:
                print(e)

    def thread(self):
        print("Parafusadeira Inited")
        while True:
            time.sleep(sleep_time)
            try:
                client = MongoClient(CONNECTION_STRING)
                db = client["geral"]
                all_parafusadeiras = db["parafusadeira"].find()
                all_parafusadeiras = [parafusadeira for parafusadeira in all_parafusadeiras]
                threads = []
                for parafusadeira in all_parafusadeiras:
                    thread = threading.Thread(target=self.thread_parafusadeira, args=(parafusadeira,))
                    thread.start()
                    threads.append(thread)
                    
                for thread in threads:
                    thread.join()
                
                self.passos = {}
                MainProperties["updateParafusadeira"] = False
            except Exception as e:
                self.con = None
                print(e)
