from datetime import datetime
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class SudamerisApi:
    # Variables de la clase

    def __init__(self, config_parameter):
        self.config_parameter = config_parameter
        self.base_url = "http://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?"
        self.authenticate = {
            "Btinreq": {
                "Device": "10.103.103.31",
                "Usuario": "GEIER",
                "Requerimiento": "1",
                "Canal": "BTINTERNO",
                "Token": None
            },
            "userID": "GEIER",
            "userPassword": "Albuquerque2021"
        }

    """
    Servicio: Alta de CAJA DE AHORRO
    Metodo: POST
    URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSAltaCA
    """
    def ws_alta_ca(self, Pais, Tdoc, Ecivil, Ciudad, Departamento, Barrio, *args, **kwargs):        
      """ Parametros
      Btinreq:    Credenciales        |   Object
      Cuenta:     Número de cuenta    |   N(9)
      Sucursal:   Número de sucursal  |   N(3)
      Modulo:     Módulo(?)           |   N(3)
      Moneda:     Código de moneda    |   N(4)
      Estado:     Estado de alta(*)   |   N(2)
      # JSON
      {
        "Btinreq": {
          "Device": "10.103.103.31",
          "Usuario": "RUIZMAU",
          "Requerimiento": "1",
          "Canal": "BTINTERNO",
          "Token": "9ae861095c088C9B822DF6FA"
        },
        "Pgcod": 1,
        "CtNro": 4003349,
        "Pgmoca": 21,
        "Suc": 10,
        "PgMNac": 6900,
        "Papel": 0,
        "Totope": 0,
        "Scsbop": 0,
        "PCvNom": " ",
        "CodRetorno": " ",
        "Mensaje": " "
      }
      # RESPONSE
      CodRetorno:     Código de Retorno       |   N(3)
      Mensaje:        Nombre de Persona       |   C(100)
      """
      wsurl = self.base_url + "WSAltaCA"
      self.authenticate['Btinreq']['Token'] = self.__get_token()
      return [wsurl, self.authenticate['Btinreq']['Token'], Pais, Tdoc, Ecivil, Ciudad, Departamento, Barrio]

