# -*- coding: UTF-8 -*-
import os
import logging
from logging.handlers import SysLogHandler
from flask import Flask, request
from pymongo import MongoClient
import telegram
from backend import eval_update


app = Flask(__name__)
app.config.from_pyfile('cuandollegabotconfig.py')

client = MongoClient(app.config["DB_FULL_URI"])
db = client[app.config["DB_CLIENT"]]
token = app.config["TOKEN"]

global bot
bot = telegram.Bot(token=token)

logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

if os.environ.get("PAPERTRAIL_API_TOKEN"):
    pass
    # syslog = SysLogHandler(address=('<host>.papertrailapp.com', 11111))
    # formatter = logging.Formatter(
    #     '%(asctime)s %(hostname)s YOUR_APP: %(message)s', datefmt='%b %d %H:%M:%S')
    # syslog.setFormatter(formatter)
    # logger.setLevel(logging.INFO)
    # logger.addHandler(syslog)
else:
    fhandler = logging.FileHandler(__name__ + ".log")
    fhandler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fhandler)


shandler = logging.StreamHandler()
shandler.setFormatter(formatter)
logger.addHandler(shandler)


@app.route("/bot", methods=['POST'])
def new_message():
    # logger.debug(os.environ.get("CL_TOKEN", "cuandollegabot"))
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True))
        eval_update(db, bot, update)

    return 'ok'


@app.route("/reloadDBRosario")
def reloadDBRosario():
    from scrappers import reloadDB
    reloadDB.reloadBus(1, override=True)
    return 'ok'


@app.route("/")
def index():
    return "Index"

if __name__ == '__main__':
    debugging = False if os.environ.get('DEBUG') else True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=debugging)
