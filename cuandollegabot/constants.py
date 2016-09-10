# -*- coding: UTF-8 -*-

COMAND_WHEN = '/cuando'
COMAND_START = '/start'
COMAND_HELP = '/help'
COMAND_STOP = '/parada'

COMANDS_THANKS = ['gracias', '/gracias', 'muchas gracias', 'graciela']

COMANDS_SEND_MSG = '/send'

COMANDS = [COMAND_WHEN,
           COMAND_START,
           COMAND_STOP,
           COMAND_HELP]

MODULE_ROSARIO = 1

NICE_MESSAGE = """{0}, eres la persona más maravillosa y bella del mundo \
pero tu mensaje no es correcto"""

WHEN_SENDING_INFO = """Voy a enviarte la información del colectivo, asegúrate de estar antes\
 en la esquina. Disculpame si no es acertada, es el dato que me dan."""
WHEN_PARAMS_ERROR = "Recuerda que debes enviar /cuando, un colectivo y y un número de 4 dígitos."
WHEN_RIGHT_COMMAND = ""

STOP_SENDING_BUSES = """Voy a enviarte todos los colectivos de esa parada, espero no olvidar ninguno\
. Asegúrate de estar en la esquina."""
STOP_PARAMS_ERROR = "Recuerda que debes enviar /parada y un número de 4 dígitos."
STOP_RIGHT_COMMAND = ""
STOP_WRONG_STOP = "Oops, no tengo ese dato."

HELP_TEXT = """
Obtiene el tiempo estimado de llegada del colectivo a una parada
Módulo : Rosario, Argentina (beta)
Mejorando : Rosario, Argentina

Comandos:

/cuando Para saber cuanto falta para que el colectivo arribe
    Ej /cuando 141 6410

/parada Para saber cuanto falta para que cada colectivo de esa parada arribe
    EJ /parada 6410

/help Para ver este menú de ayuda
"""
