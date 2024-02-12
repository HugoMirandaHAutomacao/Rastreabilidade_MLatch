import serial
import time
import threading
from settings import MainProperties, sleep_time
import os
from pymongo import MongoClient
CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"
class Rfid:
    def __init__(self):
        self.banned_variables = []
        self.properties = {}
        self.con = None
        self.port = "ttyACM1"
        self.readed = ""
        self.last_readed = ""
        self.last_retrabalho = None

    def updateProperties(self, serializable=False):
        self.properties = self.__dict__.copy()

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

    def openPort(self):
        client = MongoClient(CONNECTION_STRING)
        db = client["geral"]
        configs = db["config"].find({"_id": 1})

        configs = [config for config in configs][0]
        device_list = [device for device in os.listdir("/dev") if "ttyUSB" in device]
        print(device_list)
        if len(device_list) == 0:
            return
        else:
            device_path = f"/dev/ttyUSB{configs['rfid_com_port']}"
            os.system(f"sudo chmod 777 {device_path}")
            self.con = serial.Serial(device_path)

    def getUser(self):
        LOCAL_CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"
        client = MongoClient(LOCAL_CONNECTION_STRING)
        db = client["geral"]
        configs = db["config"].find({"_id": 1})
        configs = [config for config in configs][0]

        db_ip = configs["ip_ultimo_posto"]
        CONNECTION_STRING = f"mongodb://{db_ip}:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"
        client = MongoClient(CONNECTION_STRING)
        db = client["geral"]
        users = db["users"].find({"rfid": self.readed})
        user = [user for user in users]
        if len(user) > 0:
            user = user[0]
            user.pop("password")
            if not MainProperties["retrabalho"]:
                MainProperties["user"] = user
            else:
                MainProperties["user_retrabalho"] = user
                self.last_retrabalho = time.time()
                return True

    def thread(self):
        while True:
            try:
                time.sleep(sleep_time)
                self.openPort()
                while True:
                    time.sleep(sleep_time)
                    if self.con == None:
                        print("Cannot connect to RFID")
                        print("Trying to connect")
                        self.openPort()
                        if self.con != None:
                            print("RFID Connected")
                    if self.con.in_waiting > 0:
                        if self.con.read(1) == b"\x02":
                            readed = b""
                            while 1:
                                read = self.con.read(1)
                                if read == b"\x03":
                                    break
                                readed += read
                            self.readed = readed.decode("utf-8")
                    retrabalho = None
                    if self.readed != "" and self.readed != self.last_readed or MainProperties["retrabalho"]:
                        self.getUser()
                    if self.readed != self.last_readed:
                        self.last_readed = self.readed
                        MainProperties["rfid"] = self.readed

                    if self.last_retrabalho is not None and time.time() - self.last_retrabalho > 5:
                        self.last_retrabalho = None
                        self.readed = ""
                        self.last_readed = "-1"
            except Exception as e:
                self.con = None
                print(e)


RFID_Module = Rfid()
threading.Thread(target=RFID_Module.thread).start()