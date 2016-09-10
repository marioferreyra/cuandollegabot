# -*- coding: UTF-8 -*-

import logging
import datetime
from pymongo import MongoClient
import telegram

from cuandollegabotconfig import TOKEN, OWNER_ID, DB_CLIENT, DB_FULL_URI

logger = logging.getLogger('CuandoLlegaBot')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

shandler = logging.StreamHandler()
shandler.setFormatter(formatter)

logger.addHandler(shandler)

token = TOKEN
bot = telegram.Bot(token=token)
chat_id = OWNER_ID

client = MongoClient(DB_FULL_URI)
db = client[DB_CLIENT]


def test_test():
    from backend import eval_update

    update = getUpdateForTest(chat_id, "Matias", "Hola")
    eval_update(db, bot, update)


def test_cuando():
    from backend import eval_update

    update = getUpdateForTest(chat_id, "Matias", "/cuando")
    eval_update(db, bot, update)


def test_start():
    from backend import eval_update

    update = getUpdateForTest(chat_id, "Matias", "/start")
    eval_update(db, bot, update)


def test_help():
    from backend import eval_update

    update = getUpdateForTest(chat_id, "Matias", "/help")
    eval_update(db, bot, update)


def test_generic(text):
    from backend import eval_update

    update = getUpdateForTest(chat_id, "Matias", text)
    eval_update(db, bot, update)


def test_send_message():
    from backend import eval_update
    update = getUpdateForTest(chat_id, "Matias",
                              u"""/send Ya arreglamos las consultas en Rosario
Perdón por las molestias""")
    eval_update(db, bot, update)


def getUpdateForTest(chat_id, first_name="", text=""):
    update = telegram.Update(1)
    user = telegram.User(chat_id, first_name)
    message = telegram.Message(1, user, datetime.datetime.now(), user)
    message.text = text
    update.message = message

    return update
