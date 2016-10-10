# -*- coding: UTF-8 -*-
import os
import logging
from logging.handlers import SysLogHandler
from functools import wraps
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

logger = logging.getLogger("CuandoLlegaBot")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
logger.setLevel(logging.DEBUG)

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

    logger.addHandler(fhandler)


shandler = logging.StreamHandler()
shandler.setFormatter(formatter)
logger.addHandler(shandler)

processing = []


def is_processing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        json_data = request.get_json()
        update_id = json_data["update_id"]
        if update_id in processing:
            return 'ok'
        processing.append(update_id)
        ret = func(*args, **kwargs)
        processing.remove(update_id)
        return ret
    return wrapper


@app.route("/bot", methods=['POST'])
@is_processing
def new_message():
    # logger.debug(os.environ.get("CL_TOKEN", "cuandollegabot"))
    if request.method == "POST":
        try:
            update = telegram.Update.de_json(request.get_json(force=True))
            eval_update(db, bot, update)
        except Exception as e:
            logger.debug(e)
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
