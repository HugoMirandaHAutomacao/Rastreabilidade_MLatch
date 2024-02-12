import serial
import time
import threading
from settings import MainProperties, sleep_time
import os
from pymongo import MongoClient
CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"


class Scanner:
    def __init__(self):
        self.banned_variables = ["con", "port"]
        self.properties = {}
        self.con = None
        self.port = "ttyS0"
        self.readed = ""
        self.last_readed = ""

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

    def openPort(self):
        device_path = f"/dev/ttyS0"
        os.system(f"sudo chmod 777 {device_path}")
        self.con = serial.Serial(device_path, 115200, rtscts=False, dsrdtr=False)

    def thread(self):
        while True:
            try:
                time.sleep(sleep_time)
                self.openPort()
                while True:
                    time.sleep(sleep_time)
                    if self.con == None:
                        print("Cannot connect to barcode scanner")
                        print("Trying to connect")
                        self.openPort()
                        if self.con != None:
                            print("Barcode Scanner Connected")

                    if self.con.in_waiting > 0:
                        readed = self.con.readline()

                        self.readed = readed.decode("utf8").split("\r\n")[0]
                        self.last_readed = self.readed

                        start = time.time()
                        while time.time() - start < 3:
                            while self.con.in_waiting > 0:
                                self.con.read(1)
                            time.sleep(.1)
            except Exception as e:
                time.sleep(1)
                self.con = None
                print(e)


Scanner_Module = Scanner()
threading.Thread(target=Scanner_Module.thread).start()