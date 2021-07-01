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
  Servicio: Alta de Cuentas Payroll/Proveedores
  Metodo: POST
  URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSAltaCuenta
  """
  def ws_alta_cuenta(self):
    """ Parametros
    Btinreq:        Credenciales                            |   Object
    CodEmpresa:     Codigo de la Empresa                    |   N(9)
    TpGrup:         Tipo de Grupo                           |   N(3)
    Ejecutivo:      Ejecutivo                               |   N(3)
    TPContrato:     Tipo Contrato                           |   C(1)
    Pais:           País(*)                                 |   N(3)
    Tdoc:           Tipo de Documento(*)                    |   N(2)
    Ndoc:           Numero de Documento                     |   C(12)
    Nomb1:          Primer Nombre                           |   C(30)
    Nomb2:          Segundo Nombre                          |   C(30)
    Apell1:         Primer Apellido                         |   C(30)
    Apell2:         Segundo Apellido                        |   C(30)
    Pnac:           Pais de Nacimiento                      |   N(3)
    FecNac:         Fecha de Nacimiento                     |   D(AAAA/MM/DD) 
    Sexo:           Sexo(M o F)                             |   C(1)
    Ecivil:         Estado Civil(*)                         |   C(1)
    venciDoc:       Vencimiento del Documento de Identidad  |   D(AAAA/MM/DD)
    Salario:        Salario                                 |   N(18.2)
    Fingreso:       Fecha de ingreso a la Empresa           |   D(AAAA/MM/DD)
    CodDirec:       Codigo dirección(Enviar siempre “1”)    |   N(3)
    DomicilioR:     Domicilio Real                          |   C(50)
    NroCasa:        Numero de Casa                          |   N(4)
    Ciudad:         Ciudad(*)                               |   N(5)
    Departamento:   Departamento(*)                         |   N(4)
    Barrio:         Barrio(*)                               |   N(9)
    CalleT:         Calle Transversal                       |   C(35)
    Referencia:     Referencia                              |   C(50)
    Dotelp:         Teléfono Particular                     |   C(20)
    Dotell:         Teléfono Laboral                        |   C(20)
    SubSegm:        SubSegmentacion(S o N)                  |   C(1)
    ### JSON
    {
      "Btinreq": {
        "Device": "10.103.103.31",
        "Usuario": "RUIZMAU",
        "Requerimiento": "1",
        "Canal": "BTINTERNO",
        "Token": "94dc59851e088C9B822DF6FA"
      },
      "CodEmpresa": 425,
      "Tgcod": 95,
      "CodEjct": 730,
      "TContrato": "I",
      "CodSuc": 10,
      "PePais": 586,
      "PeTdoc": 1,
      "PeNdoc": "8795821",
      "Nomb1": "Mauricio",
      "Nomb2": " ",
      "Apell1": "Ruiz Diaz",
      "Apell2": "Meza",
      "PfPnac": 586,
      "PfFnac": "1997-01-25",
      "Sexo": "M",
      "PfEciv": "S",
      "IngSalario": "500000",
      "PfxEmcFch": "2019-11-21",
      "DomReal": "Soldado Ovelar 122 c/Eusebio Ayala",
      "NroCasa": "122",
      "DoDepCodP": "9",
      "Barrio": "12",
      "CalleT": "Julia Miranda Cuento",
      "Referencia": "Frente al estacionamiento de Fonoluz",
      "TelCel": "0993548924",
      "TelLab": " ",
      "CtNro": " ",
      "Ctnom": " ",
      "SubSegm": "N",
      "CodRetorno": " ",
      "Mensaje": " "
    }
    ### RESPONSE
    CTNRO:          Cuenta                      |   N(9)
    CTNOM:          Descripción de la cuenta    |   C(30)
    CodRetorno:     Código de Retorno           |   N(3)
    Mensaje:        Nombre de Persona           |   C(100)
    """
    wsurl = self.base_url + "WSAltaCuenta"
    token = self.__get_token()
    if token is None:
      return "Hubo un problema al conectarse al Banco, intente más tarde"
    else:
      self.authenticate['Btinreq']['Token'] = token
      return [wsurl, self.authenticate['Btinreq']['Token']]

