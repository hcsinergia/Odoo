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
  Servicio: Consulta Cliente Payroll (últimos 35 días si cobro)
  Metodo: POST
  URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSControlClientePayroll
  """
  def ws_control_cliente_payroll(self, *args, **kwargs):
    """ Parametros
    Btinreq:    Credenciales                |   Object
    Cuenta:     Cuenta                      |   N(9)
    Ctccli:     Codigos de Clasificación    |   N(9)    |   Por código de empresa
    # JSON
    {
      "Btinreq": {
        "Device": "10.103.103.31",
        "Usuario": "RUIZMAU",
        "Requerimiento": "1",
        "Canal": "BTINTERNO",
        "Token": "9d86efbf80088C9B822DF6FA"
      },
      "CTNRO": 3604451,
      "CtCCli": 567,
      "FcUltCobro": "",
      "ENTFCBAJA": "",
      "Payroll": "",
      "CodRetorno": "",
      "Mensaje": ""
    }
    # RESPONSE
    FcUltCobro:     Fecha de ultimo cobro       |   D(AAAA/MM/DD)
    Ctfalt:         Fecha de alta               |   D(AAAA/MM/DD)
    ENTFCBAJA:      Fecha de baja               |   D(AAAA/MM/DD)
    GxExiste:       Clasificación si es Payroll |   C(1)            | S o N, '': nunca fue, A: pendiente a cobrar
    CodRetorno:     Código de Retorno           |   N(3)
    Mensaje:        Nombre de Persona           |   C(100)
    """
    wsurl = self.base_url + "WSControlClientePayroll"
    self.authenticate['Btinreq']['Token'] = self.__get_token()
    return [wsurl, self.authenticate['Btinreq']['Token']]
