from random import randint
from requests import post
import json, logging

_logger = logging.getLogger(__name__)


class ApiWsValidaBaseConfiable:
    def __init__(self, base_url, authenticate):
        self.base_url = base_url
        self.authenticate = authenticate

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
        wsurl = self.base_url + "WSValidaBaseConfiable"
        headers = {'Content-Type': 'application/json'} # set what your server accepts
        request_body = json.dumps({
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
        })
        try:
            response = post(wsurl, data=request_body, headers=headers, verify=False, timeout=10)
            #_logger.debug(['APIRESPONSE', response.text])
            return json.loads(response.text)
        except:
            return False