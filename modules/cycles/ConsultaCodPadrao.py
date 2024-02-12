import modules
import MainThread
import time
import threading
from pymongo import MongoClient
from datetime import datetime
CONNECTION_STRING = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.2"


class ConsultaCodPadrao:
    read_code = ""
    status_final = None
    status_rastreabilidade = None
    msg = ""
    aprovados = 0
    reprovados = 0

    def __init__(self):
        raise TypeError("Can't instantiate this class")

    @classmethod
    def executeStep(cls, step):
        steps = {
            0: cls.resetCycle,  # RESET DE CICLO
            10: cls.waitReadCode,  # AGUARDA A LEITURA DO CÓDIGO
            20: cls.readCodeJudgment,  # JULGAMENTO DO CÓDIGO LIDO
        }
        steps[step]()

    @classmethod
    def resetCycle(cls):
        while cls.read_code != "":
            cls.read_code = ""

        time.sleep(.5)
        MainThread.MainClass.passo = 10

    @classmethod
    def waitReadCode(cls):
        if MainThread.MainClass.configs["leitura_plc"] == "true":
            readed = MainThread.MainClass.parseReaded()
        else:
            readed = modules.scanner.readed

        if readed != "" and readed != "0":
            cls.status_final = None
            cls.status_rastreabilidade = None
            print(f"> Valor lido: {readed}")
            print(f"> Tamanho do valor lido: {len(readed)}")

            cls.read_code = readed
            MainThread.MainClass.passo = 20

            if MainThread.MainClass.configs["leitura_plc"] == "true":
                MainThread.MainClass.zeraStringLeitura()
            else:
                modules.scanner.readed = ""
            time.sleep(.5)

    @classmethod
    def readCodeJudgment(cls):
        code_template = MainThread.MainClass.receita["codigo"]
        if code_template in cls.read_code:
            client = MongoClient(CONNECTION_STRING)
            db = client["geral"]
            db["buffer_aprovadas"].insert_one({
                "code": cls.read_code,
                "date": datetime.now()
            })
            # modules.plc.defaultVariables[3] -> Rastreabilidade OK
            modules.plc.writeVar(
                modules.plc.variables["Rastreabilidade_OK"], True)
            cls.status_final = True
            cls.status_rastreabilidade = True
            threading.Thread(target=cls.messageTimeout, args=(cls, 5,)).start()
            cls.aprovados += 1
        else:
            # modules.plc.defaultVariables[3] -> Rastreabilidade NG
            modules.plc.writeVar(
                modules.plc.variables["Rastreabilidade_NG"], True)
            client = MongoClient(CONNECTION_STRING)
            db = client["geral"]
            db["buffer_reprovadas"].insert_one({
                "code": cls.read_code,
                "date": datetime.now()
            })
            cls.status_final = False
            cls.status_rastreabilidade = False

            cls.msg = "Código lido não corresponde ao cadastrado na receita"
            threading.Thread(target=cls.messageTimeout, args=(cls, 5,)).start()
            cls.reprovados += 1

        MainThread.MainClass.passo = 0
        time.sleep(.5)

    def messageTimeout(cls, secondsTimeout):
        startTime = time.time()
        while time.time() - startTime < secondsTimeout:

            time.sleep(0.1)
        cls.status_final = None
        cls.status_rastreabilidade = None

        cls.msg = ""
