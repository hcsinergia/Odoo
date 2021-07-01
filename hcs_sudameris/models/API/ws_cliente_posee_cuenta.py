from datetime import datetime
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class ApiWsClientePoseeCuenta:
    def __init__(self, base_url, authenticate, codigo_paises):
        self.base_url = base_url
        self.authenticate = authenticate
        self.codigo_paises = codigo_paises

    """
    Servicio: Chequera Pendiente de Retiro
    Metodo: POST
    URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSClientePoseeCuenta
    """

    def ws_cliente_posee_cuenta(self, Pais, Tdoc, Ndoc, *args, **kwargs):
        """ RESPONSE
        Cuenta:         Cuenta                  |   N(9)
        Sucursal:       Sucursal                |   N(2)
        Estado:         Estado de la Cuenta     |   C(1)
        CodRetorno:     Código de Retorno       |   N(3)
        Observasión:    Nombre de Persona       |   C(100)
        """
        _errores = []
        if not Pais:
            _errores.append('Pais de Nacimiento')
        if not Tdoc:
            _errores.append('Tipo de documento')
        if not Ndoc:
            _errores.append('Número de documento')
        if len(_errores) > 0:
            return "Necesita corregir los siguientes errores:\n\n" + '\n'.join(_errores)
        wsurl = self.base_url + "WSClientePoseeCuenta"
        # Obtengo el Token actual
        # token = self.__get_token()
        token = "asd"
        # if token is None:
        #   return "Hubo un problema al conectarse al Banco, intente más tarde"
        self.authenticate['Btinreq']['Token'] = token
        codig_pais = None
        for paises in self.codigo_paises:
            for pais in paises:
                if Pais.upper() in pais:
                    codig_pais = paises[0]
        # Armo la consulta
        request_body = {
            "Btinreq": self.authenticate['Btinreq'],
            "Parametros": {
                "Parametro": {
                    "sBTRepParametros.It": [
                        {
                            "Tipo": "Entero",
                            "Nombre": "pais",
                            "Codigo": 1,
                            "Valor": codig_pais
                        },
                        {
                            "Tipo": "Entero",
                            "Nombre": "tdoc",
                            "Codigo": 2,
                            "Valor": Tdoc
                        },
                        {
                            "Tipo": "Texto",
                            "Nombre": "ndoc",
                            "Codigo": 3,
                            "Valor": str(Ndoc)
                        }
                    ]
                }
            }
        }
        # try:
        #  headers = {'Content-Type': 'application/json'} # set what your server accepts
        #  response = requests.post(wsurl, data=json.dumps(request_body), headers=headers, verify=False, timeout=10)
        # except:
        #  return "Hubo un problema al conectarse al Banco, intente más tarde"
        response = {
            "Btinreq": {
                "Device": "10.103.103.31",
                "Usuario": "RUIZMAU",
                "Requerimiento": "1",
                "Canal": "BTINTERNO",
                "Token": "6b0e6aae8f088C9B822DF6FA"
            },
            "Mens": "",
            "Result": {
                "Consultas": {
                    "RepCons.Consulta": [
                      {
                          "Correlativo": "5",
                          "Top": "1",
                          "Columnas": {
                              "RepCols.Columna": [
                                  {
                                      "Numero": "5",
                                      "Tipo": "T",
                                      "Descripcion": "CTNRO",
                                      "Filas": {
                                          "RepFilas.Fila": [
                                              {
                                                  "Numero": "1",
                                                  "Valor": "3604451"
                                              }
                                          ]
                                      }
                                  },
                                  {
                                      "Numero": "10",
                                      "Tipo": "T",
                                      "Descripcion": "Ttnom",
                                      "Filas": {
                                          "RepFilas.Fila": [
                                              {
                                                  "Numero": "1",
                                                  "Valor": "TITULAR"
                                              }
                                          ]
                                      }
                                  },
                                  {
                                      "Numero": "15",
                                      "Tipo": "T",
                                      "Descripcion": "Cttfir",
                                      "Filas": {
                                          "RepFilas.Fila": [
                                              {
                                                  "Numero": "1",
                                                  "Valor": "T"
                                              }
                                          ]
                                      }
                                  },
                                  {
                                      "Numero": "20",
                                      "Tipo": "T",
                                      "Descripcion": "Observacion",
                                      "Filas": {
                                          "RepFilas.Fila": [
                                              {
                                                  "Numero": "1",
                                                  "Valor": "POSEE CUENTA"
                                              }
                                          ]
                                      }
                                  }
                              ]
                          },
                          "Nombre": "WSPoseeCuesta"
                      }
                    ]
                },
                "Usuario": "RUIZMAU",
                "Codigo": "90104",
                "Nombre": "WS PAYROLL",
                "Parametros": {
                    "RepParm.Parametro": [
                        {
                            "Tipo": "Entero",
                            "Codigo": "1",
                            "Nombre": "pais",
                            "Valor": "586"
                        },
                        {
                            "Tipo": "Entero",
                            "Codigo": "2",
                            "Nombre": "tdoc",
                            "Valor": "1"
                        },
                        {
                            "Tipo": "Texto",
                            "Codigo": "3",
                            "Nombre": "ndoc",
                            "Valor": "5978597"
                        }
                    ]
                }
            },
            "Erroresnegocio": {
                "BTErrorNegocio": []
            },
            "Btoutreq": {
                "Numero": "3416",
                "Servicio": "BSPAYROOL.WSClientePoseeCuenta",
                "Estado": "OK",
                "Requerimiento": "1",
                "Fecha": "2020-10-13",
                "Hora": "16:09:23",
                "Canal": "BTINTERNO"
            }
        }
        response = json.dumps(response)
        try:
            result = json.loads(response)
            return result['Result']['Consultas']["RepCons.Consulta"][0]['Columnas']["RepCols.Columna"]
        except:
            return "Problema interno del banco"

def _response_ok(self):
        return {
            "Btinreq": self.authenticate['Btinreq'],
            "CodMensaje": "0",
            "Mensaje": "La Persona Existe",
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
        }

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
        return {
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
        }
