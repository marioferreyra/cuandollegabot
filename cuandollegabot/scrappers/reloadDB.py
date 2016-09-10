# -*- coding: UTF-8 -*-
import os
import requests
import logging
import datetime
import time
from json import loads
from pymongo import MongoClient
from pyquery import PyQuery as PQ

DB_FULL_URI = os.environ.get('MONGODB_URI')
DB_CLIENT = os.environ.get('DB_CLIENT')

logger = logging.getLogger('CuandoLlegaBot')
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

shandler = logging.StreamHandler()
shandler.setFormatter(formatter)

logger.addHandler(shandler)

MODULE_ROSARIO = 1

client = MongoClient(DB_FULL_URI)
db = client[DB_CLIENT]


def magic_decode(text):
    return text.decode("UTF-8-sig")


def reloadBus(id_module, override=False):
    buses = db["buses"]

    if id_module == MODULE_ROSARIO:

        URL_DATA = 'http://www.emr.gov.ar/cuandollega.php'
        URL_ACTION = 'http://www.emr.gov.ar/ajax/cuandollega/getInfoParadas.php'

        ACTION_FIRST_STREET = "getCalle"
        ACTION_SECOND_STREET = "getInterseccion"
        ACTION_STOP = "getParadasXCalles"

        page = PQ(URL_DATA)
        selectList = PQ('#linea', page)('option')
        for option in selectList:
            bus_data = PQ(option).attr('idlinea')
            if bus_data:
                bus_nro = PQ(option).text()
                if (override or buses.find_one({"id": bus_data}) is None):
                    bus = {"id": bus_data, "nro": bus_nro, "module": MODULE_ROSARIO}
                    logger.debug(bus["nro"])
                    data = {"accion": ACTION_FIRST_STREET, "idLinea": bus["id"]}
                    resp_first = requests.post(URL_ACTION, data=data)
                    bus_firsts_streets = []
                    for first_street in loads(magic_decode(resp_first._content)):
                        second_streets = []
                        logger.debug(first_street["desc"])
                        data = {"accion": ACTION_SECOND_STREET,
                                "idLinea": bus["id"],
                                "idCalle": first_street["id"]}
                        resp_second = requests.post(URL_ACTION, data=data)
                        for second_street in loads(magic_decode(resp_second._content)):
                            stop = []
                            logger.debug(second_street["desc"])
                            data = {"accion": ACTION_STOP, "idLinea": bus["id"],
                                    "idCalle": first_street["id"],
                                    "idInt": second_street["id"],
                                    "txtLinea": bus["nro"]}
                            resp_stop = requests.post(URL_ACTION, data=data)
                            resp_uno = PQ(resp_stop._content)('.restUno')
                            if resp_uno:
                                for td in PQ(resp_uno)('td'):
                                    td_nro = PQ(td)('.link-nro-sms').text()
                                    if td_nro:
                                        stop_nro = td_nro
                                    else:
                                        stop_desc = PQ(td).text()
                                stop.append({"nro": int(stop_nro), "desc": stop_desc})
                                logger.debug((stop_nro, stop_desc))

                            resp_dos = PQ(resp_stop._content)('.restDos')
                            if resp_dos:
                                for td in PQ(resp_dos)('td'):
                                    td_nro = PQ(td)('.link-nro-sms').text()
                                    if td_nro:
                                        stop_nro = td_nro
                                    else:
                                        stop_desc = PQ(td).text()
                                stop.append({"nro": int(stop_nro), "desc": stop_desc})
                                logger.debug((stop_nro, stop_desc))
                            second_streets.append(
                                {"id": int(second_street["id"]),
                                 "name": second_street["desc"],
                                 "stops": stop})

                        bus_firsts_streets.append(
                            {"id": int(first_street["id"]),
                             "name": first_street["desc"],
                             "second_streets": second_streets})

                    logger.debug("--------------------SLEEP--------------------")
                    time.sleep(0.5)
                    bus["firsts_streets"] = bus_firsts_streets
                    buses.find_one_and_replace({"nro": bus["nro"]}, bus, upsert=True)
                    logger.info("Update Bus %s" % bus["nro"])
                else:
                    logger.info("Not override Bus %s" % bus_nro)

if __name__ == '__main__':
    reloadBus(MODULE_ROSARIO)
