# -*- coding: UTF-8 -*-
import requests
import logging
from json import loads
import re
from pyquery import PyQuery as PQ

logger = logging.getLogger('CuandoLlegaBot')


def magic_decode(text, deco='utf-8-sig', enco='utf-8'):
    try:
        return text.decode(deco).encode()
    except UnicodeEncodeError:
        return text.encode(enco)
    except:
        return text


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
            try:
                buses_current_location = re.search(
                    'JSONcoordenadas( )?=( )?(.*);', r.text).group(0)
                re_string = "JSONcoordenadas( )?=( )?eval\("
                buses_array = eval(re.sub(re_string, '', buses_current_location).replace(');', ''))
                results = []
                for b in buses_array:
                    if b.get('interno'):
                        linea = b.get("LineaBandera")
                        time = b.get("arribo")
                        latitud = b.get("latitud")
                        longitud = b.get("longitud")
                        try:
                            # TODO Buscar calles donde está ahora
                            raise Exception("No implementado")
                        except:
                            bus_current_location = ""
                        results.append((linea, time, bus_current_location))
                return "\n".join(["{0}: {1}{2}".format(re[0], re[1], re[2]) for re in results])
            except Exception as e:
                logger.error("No se pudo usar el js")
                logger.error(e)
                arribos = PQ(".tablaArribos tbody tr", r.text)
                results = []
                for arribo in arribos:
                    arribo_tds = PQ("td", arribo)
                    linea = arribo_tds[0].text
                    time = arribo_tds[1].text
                    results.append((linea, time))
                return "\n".join(["{0}: {1}".format(re[0], re[1]) for re in results])
        except Exception as e:
            logger.error(e)
            return "Error, por favor intente nuevamente en unos minutos"

    def getOtherBusesInStop(self, stop):
        buses_collection = self.db["buses"]
        buses = buses_collection.find(
            {'firsts_streets.second_streets.stops.nro': int(stop)}, {"nro": 1})
        other_buses = [magic_decode(b['nro'], deco='cp1251') for b in buses]
        # logger.debug(other_buses)
        return other_buses
