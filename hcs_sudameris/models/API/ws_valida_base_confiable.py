from datetime import datetime
from random import seed, randint
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class ApiWsValidaBaseConfiable:
    def __init__(self, base_url, authenticate, codigo_paises):
        self.base_url = base_url
        self.authenticate = authenticate
        self.codigo_paises = codigo_paises

    """
    Servicio: Validación de documentos contra la base BCP/BASE CONFIABLE
    Metodo: POST
    URL: http://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPAYROOL?WSValidaBaseConfiable
    """

    def ws_valida_base_confiable(self, Pais, Tdoc, Ndoc, Nomb1, Nomb2, Apell1, Apell2, FecNac):
        """ Parametros
            btinreq:    Credenciales        |   Object
            Pais:       País                |   N(3)
            Tdoc:       Tipo de Documento   |   N(2)
            Ndoc:       Número de Documento |   C(12)
            Nomb1:      Primer Nombre       |   C(25)
            Nomb2:      Segundo Nombre      |   C(25)
            Apell1:     Primer Apellido     |   C(30)
            Apell2:     Segundo Apellido    |   C(30)
            FecNac:     Fecha de Nacimiento |   D(AAAA/MM/DD) """

        _errors = []
        if not (Pais and Tdoc and Ndoc and Nomb1 and Apell1 and FecNac):
            if not Pais:
                _errors.append('Pais')
            if not Tdoc:
                _errors.append('Tipo de documento')
            if not Ndoc:
                _errors.append('Numero de documento')
            if not Nomb1:
                _errors.append('Primer Nombre')
            if not Apell1:
                _errors.append('Primer Apellido')
            if not FecNac:
                _errors.append('Fecha de nacimiento')
        if len(_errors) > 0:
            return "Faltan los siguientes datos: \n\n{}".format('\n'.join(_errors))
        wsurl = self.base_url + "WSValidaBaseConfiable"
        #self.authenticate['Btinreq']['Token'] = self.__get_token()

        request_body = {
            "Btinreq": self.authenticate['Btinreq'],
            "Pais": Pais,
            "Tdoc": Tdoc,
            "Ndoc": Ndoc,
            "Nomb1": Nomb1,
            "Nomb2": Nomb2,
            "Apell1": Apell1,
            "Apell2": Apell2,
            "CodMensaje": "",
            "Mensaje": ""
        }

        for _ in range(2):
            random_value = randint(0, 2)
        if random_value == 1:
            response = self._response_ok()
        else:
            response = self._response_error()
        response = json.loads(response)
        if response['Mensaje'] == "La Persona Existe":
            return [True]
        return [False, response['Mensaje']]

    def _response_ok(self):
        return json.dumps({
            "Btinreq": self.authenticate['Btinreq'],
            "CodMensaje": "0",
            "Mensaje": "La Persona Existe",
            "Erroresnegocio": {
                "BTErrorNegocio": []
            },
            "Btoutreq": {
                "Numero": "17749",
                "Servicio": "BSPAYROOL.WSValidaBaseConfiable",
                "Estado": "OK",
                "Fecha": "2021-04-15",
                "Requerimiento": "1",
                "Canal": "BTINTERNO",
                "Hora": "23:05:31"
            }
        })

    def _response_error(self):
        for _ in range(4):
            random_value = randint(0, 4)
        if random_value == 0:
            _msg = "No coincide Fecha de Nacimiento."
        elif random_value == 1:
            _msg = "No coinciden Nombres."
        elif random_value == 2:
            _msg = "No coinciden Apellidos."
        else:
            _msg = "Persona No Encontrada."
        return json.dumps({
            "Btinreq": self.authenticate['Btinreq'],
            "CodMensaje": "0",
            "Mensaje": _msg,
            "Erroresnegocio": {
                "BTErrorNegocio": []
            },
            "Btoutreq": {
                "Numero": "13024",
                "Estado": "OK",
                "Servicio": "BSPayroll.WSValidaBaseConfiable",
                "Fecha": "2020-11-23",
                "Requerimiento": "1",
                "Hora": "09:24:07",
                "Canal": "BTINTERNO"
            }
        })
