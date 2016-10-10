# -*- coding: UTF-8 -*-
import logging
import time
import telegram
from modules import rosario
from constants import (NICE_MESSAGE, COMANDS, COMAND_START, COMAND_HELP,
                       COMANDS_THANKS, HELP_TEXT, MODULE_ROSARIO,
                       COMAND_WHEN, WHEN_SENDING_INFO, WHEN_PARAMS_ERROR, WHEN_RIGHT_COMMAND,
                       COMAND_STOP, STOP_SENDING_BUSES, STOP_PARAMS_ERROR,
                       STOP_RIGHT_COMMAND, STOP_WRONG_STOP, COMANDS_SEND_MSG)
from cuandollegabotconfig import OWNER_ID, SKIP_PARADA

logger = logging.getLogger('CuandoLlegaBot')
sleep_time = 10


def eval_update(db, bot, update):
    user_name = update.message.from_user.first_name
    message_text = update.message.text.strip().lower()
    chat_id = update.message.chat_id
    logger.debug("ID {0} - User {1} - Msg {2}".format(chat_id, user_name, message_text))

    try:
        setUpUser(db, user_name, chat_id)
    except Exception as ex:
        logger.debug(ex)

    if COMANDS.__contains__(message_text):
        if(message_text == COMAND_WHEN):
            text = """ {0}, el comando correcto es
            /cuando COLECTIVO PARADA""".format(user_name)
            reply_markup = telegram.ReplyKeyboardHide()

        elif message_text == COMAND_HELP:
            text = HELP_TEXT
            reply_markup = telegram.ReplyKeyboardHide()

        elif message_text == COMAND_START:
            setUpUser(db, user_name, chat_id)
            text = HELP_TEXT
            reply_markup = telegram.ReplyKeyboardHide()

        elif message_text == COMAND_STOP:
            text = """{0}, el comando correcto es
            /parada PARADA
            ACTUALMENTE DESHABILITADO""".format(user_name)
            reply_markup = telegram.ReplyKeyboardHide()

        else:
            text = None
            reply_markup = None

        botSendMessage(bot, chat_id, user_name, text=text, reply_markup=reply_markup)

    elif COMANDS_THANKS.__contains__(message_text):
        botSendMessage(bot, chat_id, user_name, text="De nada {0}".format(user_name))

    elif (message_text.startswith(COMANDS_SEND_MSG) and int(chat_id) == int(OWNER_ID)):
        pass
        message = message_text.replace(COMANDS_SEND_MSG, "")
        for user_id in getUsers(db):
            botSendMessage(bot, user_id, None, text=message, disable_notification=True)

    elif message_text.__contains__(COMAND_WHEN):
        botSendTextAndAction(bot, chat_id,
                             WHEN_SENDING_INFO, telegram.ChatAction.TYPING)
        params = message_text.strip().replace(
            COMAND_WHEN, '').strip().split(' ')
        if len(params) != 2:
            text = WHEN_PARAMS_ERROR
            array_buttons = None
            logger.debug(message_text)
        else:
            bus, stop = params
            text = getBusStopInfo(chat_id, db, bus, stop)
            logger.debug("Bus:{0}, Stop:{1}".format(bus, stop))
            array_buttons = []
            array_buttons.extend(getOtherBusesInStop(chat_id, db, stop))
            array_buttons.extend([["{0} {1}".format(COMAND_STOP, stop)]])
        if(array_buttons):
            reply_markup = telegram.ReplyKeyboardMarkup(array_buttons,
                                                        one_time_keyboard=True,
                                                        resize_keyboard=True)
        else:
            reply_markup = telegram.ReplyKeyboardHide()

        botSendMessage(bot, chat_id, user_name, text=text, reply_markup=reply_markup)

    elif message_text.__contains__(COMAND_STOP):
        # Comando deshabilitado
        if(SKIP_PARADA):
            text = "Disculpá {0}, el comando /parada " \
                "está ACTUALMENTE DESHABILITADO".format(user_name)
            reply_markup = telegram.ReplyKeyboardHide()
            botSendMessage(bot, chat_id, user_name, text=text, reply_markup=reply_markup)
            return

        params = message_text.strip().replace(
            COMAND_STOP, '').strip().split(' ')
        if len(params) != 1 or not params[0].isdigit():
            text = STOP_PARAMS_ERROR
            array_buttons = None
            logger.debug(message_text)
        else:
            botSendTextAndAction(bot, chat_id, STOP_SENDING_BUSES, telegram.ChatAction.TYPING)
            stop = params[0]
            buses = getOtherBusesInStop(chat_id, db, stop, with_format=False)
            if len(buses) > 0:
                logger.debug(buses)
                for bus in buses[:-1]:
                    text = getBusStopInfo(chat_id, db, bus, stop)
                    botSendMessage(bot, chat_id, user_name, text=text)
                    logger.debug("Bus:{0}, Stop:{1}".format(bus, stop))
                    bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                    time.sleep(sleep_time)
                array_buttons = [[message_text]]
                array_buttons.extend(getOtherBusesInStop(chat_id, db, stop))
                text = getBusStopInfo(chat_id, db, buses[-1], stop)
                if(array_buttons):
                    reply_markup = telegram.ReplyKeyboardMarkup(array_buttons,
                                                                one_time_keyboard=True,
                                                                resize_keyboard=True)
                else:
                    reply_markup = None

                botSendMessage(bot, chat_id, user_name, text=text, reply_markup=reply_markup)

            else:
                text = STOP_WRONG_STOP
                botSendMessage(bot, chat_id, user_name, text=text)

    else:
        botSendMessage(bot, chat_id, user_name)

# BOT MESSAGES


def botSendMessage(bot, chat_id, user_name,
                   text=None, reply_markup=None, parse_mode=None,
                   disable_web_page_preview=None, reply_to_message_id=None,
                   disable_notification=False):
    text = text if text else NICE_MESSAGE.format(user_name)

    reply_markup = reply_markup if reply_markup else telegram.ReplyKeyboardHide()

    bot.sendMessage(chat_id=chat_id,
                    **{"text": text,
                        "reply_markup": reply_markup,
                        "parse_mode": parse_mode,
                        "disable_web_page_preview": disable_web_page_preview,
                        "reply_to_message_id": reply_to_message_id,
                        "disable_notification": disable_notification})


def botSendTextAndAction(bot, chat_id, text, action):
    bot.sendMessage(chat_id=chat_id, text=text)
    bot.sendChatAction(chat_id=chat_id, action=action)

# USERS API #


def setUpUser(db, user_name, chat_id):
    users = db["users"]
    user = {"_id": chat_id, "name": user_name, "module": MODULE_ROSARIO}
    users.find_one_and_replace({"_id": chat_id}, user, upsert=True)
    return rosario.RosarioCuandoLlega(db)


def getUserModule(db, chat_id):
    users = db["users"]
    module = users.find_one({"_id": chat_id}, {"module": 1})
    if module["module"] == MODULE_ROSARIO:
        return rosario.RosarioCuandoLlega(db)
    else:
        return None


def getUsers(db):
    users = db["users"].find({}, {"_id": 1})
    return [u["_id"] for u in users]
# MODULES API #


def getBusArray(chat_id, db):
    module = getUserModule(db, chat_id)
    return module.getBusArray()


def getBusFirstStreet(chat_id, db, bus):
    module = getUserModule(db, chat_id)
    return module.getBusFirstStreet(bus)


def getBusSecondStreet(chat_id, db, bus, first_street):
    module = getUserModule(db, chat_id)
    return module.getBusSecondStreet(bus, first_street)


def getBusStops(chat_id, db, bus, first_street, second_street):
    module = getUserModule(db, chat_id)
    return module.getBusStops(bus, first_street, second_street)


def getBusStopInfo(chat_id, db, bus, stop):
    module = getUserModule(db, chat_id)
    return module.getBusStopInfo(bus, stop)


def getOtherBusesInStop(chat_id, db, stop, with_format=True):
    module = getUserModule(db, chat_id)
    buses = [["{0} {1} {2}".format(
        COMAND_WHEN, bus, stop)]
        for bus
        in module.getOtherBusesInStop(stop)]

    buses = [bus for bus in module.getOtherBusesInStop(stop)]

    if with_format:
        buses = [["{0} {1} {2}".format(COMAND_WHEN, bus, stop)]
                 for bus
                 in buses]
        # buses.extend(["{0} {1}".format(COMAND_STOP, stop)])
    return buses

# from pymongo import MongoClient

# client = MongoClient('localhost', 27017)
# db = client['test']

# print getOtherBusesInStop(rosario.RosarioCuandoLlega(db), "1939", with_format=False)
