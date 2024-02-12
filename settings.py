import threading
import time
from pymongo import MongoClient
CONNECTION_STRING = "mongodb://127.0.0.1:27017"
MainProperties = {
    "user": {},
    "rfid": "",
    "user_retrabalho": {},
    "retrabalho": False,
    "updateParafusadeira": False,
    "ponta_estoque": False,
    "inited": False
}


def verifyConnection():
    while True:
        try:
            _, db = getDBConnection()
            configs = [i for i in db["config"].find({})]
            if len(configs) > 0:
                MainProperties["inited"] = True
                break
        except:
            time.sleep(2)

sleep_time = .02


def getDBConnection():
    client = MongoClient(CONNECTION_STRING)
    db = client["geral"]
    return (client, db,)
