import requests
import json
import logging

logger = logging.getLogger(__name__)


class ApiWsConsultaCuentaServicio:
    """
    # Servicio: Consulta Cliente Payroll (últimos 35 días si cobro)
    Metodo: POST
    URL: http://10.1.41.33:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPAYROOL?ConsultaCuentaServicio
    """

    def __init__(self, base_url, authenticate):
        self.service = "ConsultaCuentaServicio"
        self.request_url = base_url + self.service
        self.authenticate = authenticate

    def ws_consulta_cuenta_servicio(self, cuenta, *args, **kwargs):
        """
        # Parametros
        - Btinreq:		Credenciales				Object
        - Cuenta:		Cuenta						N(9)

        # Response
        - Mensaje:		Código de retorno			C(100)
        - NroContrato:	Número de contrato (código) D(AAAA/MM/DD)
        - DesContrato:	Nombre de la empresa		D(AAAA/MM/DD)
        - Datos:
            - sBTCuenta_Lista:
                - Sucursal:	    Sucursal de la empresa		C(1)
                - Moneda:		Moneda de la empresa		C(1)
                - Cuenta:	    Cuenta de la empresa		C(1)
                - Modulo:		Modulo de la empresa        C(1)

        # Observación
        - Mensaje:      Si responde TRUE, devuelve los datos de la empresa
        """

        request_body = json.dumps({
            "Btinreq": self.authenticate['Btinreq'],
            "Cuenta": cuenta,
        })
        response = {
            "Mensaje": "",
            "NroContrato": "",
            "DesContrato": "",
            "Datos": "",
            "Erroresnegocio": ""
        }

        try:
            request = requests.post(self.request_url, data=request_body, headers={
                'Content-Type': 'application/json'}, verify=False, timeout=3)
            request = request.text
            logger.info([self.service, request])
            request = json.loads(request)

            response["Mensaje"] = request["Mensaje"]
            response["NroContrato"] = request["NroContrato"]
            response["DesContrato"] = request["DesContrato"]
            response["Datos"] = request["Datos"]
            for BTErrorNegocio in request['Erroresnegocio']['BTErrorNegocio']:
                response["Erroresnegocio"] = BTErrorNegocio['Descripcion']

        except Exception as e:
            exp_message = str(e)
            if 'HTTPConnectionPool' in exp_message: # HTTPConnectionPool == Conection Timeout
                exp_message = '(HTTPConnectionPool): No se puede conectar al banco'
            logger.error([self.service, 'Exception', exp_message], exc_info=True)
            response["Erroresnegocio"] = exp_message

        return response
