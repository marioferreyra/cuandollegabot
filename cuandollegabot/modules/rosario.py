# -*- coding: UTF-8 -*-
import requests
import logging
from json import loads
from pyquery import PyQuery as PQ
from utils import magic_decode

logger = logging.getLogger('CuandoLlegaBot')


class RosarioCuandoLlega():

    """docstring for RosarioCuandoLlega"""

    def __init__(self, db):
        self.db = db

        self.URL_DATA = 'http://www.emr.gov.ar/cuandollega.php'
        self.URL_ACTION = 'http://www.emr.gov.ar/ajax/cuandollega/getInfoParadas.php'
        self.URL_INFO = 'http://www.emr.gov.ar/ajax/cuandollega/getSmsResponseEfisat.php'

        self.ACTION_FIRST_STREET = "getCalle"
        self.ACTION_SECOND_STREET = "getInterseccion"
        self.ACTION_STOP = "getParadasXCalles"
        self.ACTION_INFO = "getSmsEfisat"

    def getBusArray(self):
        page = PQ(self.URL_DATA)
        array_buttons = []
        selectList = PQ('#linea', page)('option')
        for option in selectList:
            bus = PQ(option).attr('idlinea')
            if bus:
                array_buttons.append([PQ(option).text()])

        return array_buttons

    def getBusFirstStreet(self, bus):
        page = PQ(self.URL_DATA)
        array_buttons = []
        selectList = PQ('#linea', page)('option')
        for option in selectList:
            bus_number = PQ(option).text()
            if bus_number == str(bus):
                idLinea = PQ(option).attr('idlinea')
                print(idLinea)
        data = {"accion": self.ACTION_FIRST_STREET, "idLinea": idLinea}
        r = requests.post(self.URL_ACTION, data=data)
        for street in loads(r._content.decode("utf-8-sig").encode("utf-8")):
            array_buttons.append([street["desc"]])
        return array_buttons

    def getBusSecondStreet(self, bus, first_street):
        page = PQ(self.URL_DATA)
        array_buttons = []
        selectList = PQ('#linea', page)('option')
        for option in selectList:
            bus_number = PQ(option).text()
            if bus_number == str(bus):
                idLinea = PQ(option).attr('idlinea')

        data = {"accion": self.ACTION_FIRST_STREET, "idLinea": idLinea}
        r = requests.post(self.URL_ACTION, data=data)
        for street in loads(r._content.decode("utf-8-sig").encode("utf-8")):
            if street["desc"] == first_street:
                idCalle = int(street["id"])

        data = {"accion": self.ACTION_SECOND_STREET, "idLinea": idLinea, "idCalle": idCalle}
        r = requests.post(self.URL_ACTION, data=data)
        for street in loads(r._content.decode("utf-8-sig").encode("utf-8")):
            array_buttons.append([street["desc"]])
        return array_buttons

    def getBusStops(self, bus, first_street, second_street):
        page = PQ(self.URL_DATA)
        array_buttons = []
        selectList = PQ('#linea', page)('option')
        for option in selectList:
            bus_number = PQ(option).text()
            if bus_number == str(bus):
                idLinea = PQ(option).attr('idlinea')

        data = {"accion": self.ACTION_FIRST_STREET, "idLinea": idLinea}
        resp_first = requests.post(self.URL_ACTION, data=data)
        for street in loads(resp_first._content.decode("utf-8-sig").encode("utf-8")):
            if street["desc"] == first_street:
                idCalle = int(street["id"])

        data = {"accion": self.ACTION_SECOND_STREET, "idLinea": idLinea, "idCalle": idCalle}
        resp_second = requests.post(self.URL_ACTION, data=data)
        for street in loads(resp_second._content.decode("utf-8-sig").encode("utf-8")):
            if street["desc"] == second_street:
                idInt = int(street["id"])

        data = {
            "accion": self.ACTION_STOP,
            "idLinea": idLinea,
            "idCalle": idCalle,
            "idInt": idInt,
            "txtLinea": bus}
        resp_stop = requests.post(self.URL_ACTION, data=data)

        resp_uno = PQ(resp_stop._content)('.restUno')
        if resp_uno:
            for td in PQ(resp_uno)('td'):
                td_nro = PQ(td)('.link-nro-sms').text()
                if td_nro:
                    stop_nro = td_nro
                else:
                    stop_desc = PQ(td).text()
        array_buttons.append(["%s \n%s" % (stop_nro, stop_desc)])
        resp_dos = PQ(resp_stop._content)('.restDos')
        if resp_dos:
            for td in PQ(resp_dos)('td'):
                td_nro = PQ(td)('.link-nro-sms').text()
                if td_nro:
                    stop_nro = td_nro
                else:
                    stop_desc = PQ(td).text()
        array_buttons.append(["%s \n%s" % (stop_nro, stop_desc)])
        return array_buttons

    def getBusStopInfo(self, bus, stop):
        try:
            page = PQ(self.URL_DATA)
            selectList = PQ('#linea', page)('option')
            for option in selectList:
                bus_number = PQ(option).text()
                if bus_number == str(bus):
                    idLinea = PQ(option).attr('idlinea')

            data = {"accion": self.ACTION_INFO, "parada": stop, "linea": idLinea}
            r = requests.post(self.URL_INFO, data=data)
            r.encoding = 'UTF-8'
            return r.text.splitlines()[:1][-1].strip()
        except Exception as e:
            logger.debug(e)
            return "Error, por favor intente nuevamente en unos minutos"

    def getOtherBusesInStop(self, stop):
        buses_collection = self.db["buses"]
        buses = buses_collection.find(
            {'firsts_streets.second_streets.stops.nro': int(stop)}, {"nro": 1})
        other_buses = [magic_decode(b['nro'], deco='cp1251') for b in buses]
        logger.debug(other_buses)
        return other_buses
