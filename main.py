from flask import Flask
from routes.pages import pages
from routes.config import config
from routes.plc import plc
from routes.parameters import parameter
from routes.desvioRotas import desvio_rota
from routes.logic import logic
from routes.users import users
from routes.ipsLinha import ips_linha
from routes.parafusadeira import parafusadeira
from routes.receitas import recipes
import logging
from settings import verifyConnection
import threading

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Define o main app e registra outros endpoints
app = Flask(__name__)
app.register_blueprint(pages)
app.register_blueprint(config)
app.register_blueprint(plc, url_prefix="/clp")
app.register_blueprint(parameter, url_prefix="/param")
app.register_blueprint(desvio_rota, url_prefix="/rotas")
app.register_blueprint(users, url_prefix="/users")
app.register_blueprint(ips_linha, url_prefix="/ips")
app.register_blueprint(parafusadeira, url_prefix="/parafusadeiras")
app.register_blueprint(recipes, url_prefix="/receitas")
app.register_blueprint(logic)

if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    threading.Thread(target=app.run, args=("0.0.0.0", 5000, False)).start()
    verifyConnection()