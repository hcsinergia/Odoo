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
  Servicio: Alta de TD (MAESTRO-VISA)
  Metodo: POST
  URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSAltaTD
  """
  def ws_alta_td(self, TPtarjeta, Pais, Tdoc, *args, **kwargs):
    """ Parametros
    Btinreq:    Credenciales                |   Object
    TPtarjeta:  Tipo de tarjeta(*)          |   N(4)
    Pais:       País(*)                     |   N(3)
    Tdoc:       Tipo de Documento(*)        |   N(2)
    Ndoc:       Número de documento         |   C(12)
    Sucursal:   Sucursal                    |   N(2)
    Modulo:     Modulo Cuentas Vistas(?)    |   C(2)
    Moneda:     Moneda                      |   N(4)
    # JSON  
    {
      "Btinreq": {
        "Device": "10.103.103.31",
        "Usuario": "RUIZMAU",
        "Requerimiento": "1",
        "Canal": "BTINTERNO",
        "Token": "9ae861095c088C9B822DF6FA"
      },
      "CodEmpresa": 425,
      "PgMNac": 6900,
      "PeNdoc": "8774527",
      "PePais": 586,
      "PeTdoc": 1,
      "CodSuc": 10,
      "CodRetorno": " ",
      "Mensaje": " "
    }
    # RESPONSE
    CodRetorno:     Código de Retorno       |   N(3)
    Mensaje:        Nombre de Persona       |   C(100)
    """
    wsurl = self.base_url + "WSAltaTD"
    self.authenticate['Btinreq']['Token'] = self.__get_token()
    return [wsurl, self.authenticate['Btinreq']['Token']]
  
