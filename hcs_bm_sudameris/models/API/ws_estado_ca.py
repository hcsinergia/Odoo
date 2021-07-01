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
  Servicio: Estado de la Caja de Ahorro
  Metodo: POST
  URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSEstadoCA
  """
  def ws_estado_ca(self, *args, **kwargs):
    """ Parametros
    Btinreq:    Credenciales        |   Object
    Cuenta:     Número de cuenta    |   N(9)
    Sucursal:   Número de sucursal  |   N(3)    | Si no se envía, se busca la Caja de Ahorro por Modulo y moneda
    Modulo:     Módulo(?)           |   N(3)
    Moneda:     Código de moneda    |   N(4)
    # JSON
    {
      "Btinreq": {
        "Device": "10.103.103.31",
        "Usuario": "RUIZMAU",
        "Requerimiento": "1",
        "Canal": "BTINTERNO",
        "Token": "4d9a84ffae088C9B822DF6FA"
      },
      "Parametros": {
        "Parametro": {
          "sBTRepParametros.It": [
            {
              "Tipo": "Texto",
              "Nombre": "CUENTA",
              "Codigo": 5,
              "Valor": "302059"
                    },
            {
              "Tipo": "Entero",
              "Nombre": "MODULO",
              "Codigo": 6,
              "Valor": 21
                    },
            {
              "Tipo": "Entero",
              "Nombre": "MONEDA",
              "Codigo": 7,
              "Valor": 6900
                    }
                ]
        }
      }
    }
    # RESPONSE
    Cuenta:         Número de cuenta    |   N(9)
    Sucursal:       Número de sucursal  |   N(3)
    Modulo:         Módulo(?)           |   N(3)
    Moneda:         Código de moneda    |   N(4)
    Estado:         Estado de la Cuenta |   N(2)
    CodRetorno:     Código de Retorno   |   N(2)
    Mensaje:        Nombre de Persona   |   C(100)  | Puede existir varias CA para una cuenta en sucursales distintas.
    """
    wsurl = self.base_url + "WSEstadoCA"
    self.authenticate['Btinreq']['Token'] = self.__get_token()
    return [wsurl, self.authenticate['Btinreq']['Token']]
