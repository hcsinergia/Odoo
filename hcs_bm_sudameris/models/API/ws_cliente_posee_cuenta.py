from datetime import datetime
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class ApiWsClientePoseeCuenta:
    def __init__(self, base_url, authenticate):
        self.base_url = base_url
        self.authenticate = authenticate

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
        wsurl = self.base_url + "WSClientePoseeCuenta"
        headers = {'Content-Type': 'application/json'} # set what your server accepts
        request_body = json.dumps({
            "Btinreq": self.authenticate['Btinreq'],
            "Parametros": {
                "Parametro": {
                    "sBTRepParametros.It": [{
                        "Tipo":"Entero",
                        "Nombre":"PAIS",
                        "Codigo":1,
                        "Valor":Pais
                    }, {
                        "Tipo":"Entero",
                        "Nombre":"TDOC",
                        "Codigo":2,
                        "Valor":Tdoc
                    }, {
                        "Tipo":"Texto",
                        "Nombre":"NDOC",
                        "Codigo":3,
                        "Valor":Ndoc
                    }]
                }
            }
        })
        try:
            response = requests.post(wsurl, data=request_body, headers=headers, verify=False, timeout=10)
            _logger.debug(['APIRESPONSE', response.text])
            response = json.loads(response.text)

            if len(response['Result']['Consultas']['RepCons.Consulta'][0]['Columnas']['RepCols.Columna'][0]['Filas']['RepFilas.Fila']):
                account_number = response['Result']['Consultas']['RepCons.Consulta'][0]['Columnas']['RepCols.Columna'][0]['Filas']['RepFilas.Fila'][0]['Valor']
                account_name = response['Result']['Consultas']['RepCons.Consulta'][0]['Columnas']['RepCols.Columna'][1]['Filas']['RepFilas.Fila'][0]['Valor']
                branch_number = response['Result']['Consultas']['RepCons.Consulta'][0]['Columnas']['RepCols.Columna'][2]['Filas']['RepFilas.Fila'][0]['Valor']
                branch_number = 10 #Coloco 10 porque ninguna opción devuelve el numero de cuenta
            else:
                account_number = None
                account_name = None
                branch_number = None

            result = {
                "account_number": account_number,
                "account_name": account_name,
                "branch_number": branch_number
            }

            return result
        except:
            return {
                "account_number": -None,
                "account_name": None,
                "branch_number": None
            }