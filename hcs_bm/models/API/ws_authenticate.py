from .ws_valida_base_confiable import ApiWsValidaBaseConfiable
from types import SimpleNamespace
from datetime import datetime, timedelta
import logging
import requests
import json

logger = logging.getLogger(__name__)


class ApiWsAuthenticate:
    """
    # Servicio: Authenticate
    Metodo: POST
    URL: http://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_Authenticate?Execute
    """

    def __init__(self, base_url, authenticate, config_parameter):
        self.service = "WSAuthenticate"
        self.request_url = base_url.replace(
            "odwsbt_BSPAYROLL?", "odwsbt_Authenticate?Execute")
        self.authenticate = authenticate
        self.config_parameter = config_parameter

    def get_token(self):
        last_check = self.config_parameter.get_param('bm.token.last_check')
        expiration = self.config_parameter.get_param('bm.token.expiration')
        token = self.config_parameter.get_param('bm.token')

        # Checkeo que el token todavia sirva
        if datetime.now() > datetime.strptime(last_check, '%Y-%m-%d %H:%M:%S'):
            logger.info([self.service, "Checkeando: now = {} | last_check = {}".format(datetime.now(), datetime.strptime(last_check, '%Y-%m-%d %H:%M:%S'))], exc_info=True)
            new_date_check = datetime.now() + timedelta(hours=1)
            # renuevo el ultimo chequeo
            self.config_parameter.set_param(
                'bm.token.last_check', new_date_check.strftime('%Y-%m-%d %H:%M:%S'))

            token_check = self.check_session(token)
            if token_check['Erroresnegocio']:
                logger.info([self.service, 'Renovando token'], exc_info=True)
                token = '' # Vacio el token para que se renueve si o si.
            else:
                logger.info([self.service, 'NO se necesita renovar token'], exc_info=True)
        else:
            logger.info([self.service, 'NO se necesita checkear token'], exc_info=True)

        # El token es valido hasta las 23:59 del dia actual, si es mayor, se renueva
        if datetime.now() > datetime.strptime('%s 23:59:00' % expiration, '%Y-%m-%d %H:%M:%S') or token == '':
            try:
                service_response = self.ws_authenticate()
                # Primero verifico que la API haya respondido bien
                if service_response['Erroresnegocio']:
                    logger.error([self.service, 'Exception', service_response['Erroresnegocio']], exc_info=True)
                    # Si devuelve Erroresnegocio, detengo la interaccion
                else:
                    token = service_response['SessionToken']
                    # Actualizo el token y la fecha de expiraci??n
                    self.config_parameter.set_param(
                        'bm.token.expiration', datetime.now().date().strftime('%Y-%m-%d'))
                    self.config_parameter.set_param('bm.token', token)
                    logger.info([self.service, 'Token Renovado'], exc_info=True)
            except:
                token = '' # Dejo el token vacio para probar la proxima vez
        else:
            logger.info([self.service, 'Token valido'], exc_info=True)
        return token

    def ws_authenticate(self, *args, **kwargs):
        """
        # Parametros
        Device:			IP del host
        Usuario:		Usuario del servicio
        Requerimiento:	ID de requerimiento		(siempre 1).
        Canal:			Canal de consulta		(siempre BTINTERNO).
        Token:			Token de conexi??n
        UserId:			Usuario del servicio
        UserPassword:	Password del usuario
        # RESPONSE
        SessionToken:	Token devuelto			C(24)
        Fecha:          Fecha devuelta			D(AAAA-MM-DD)
        Hora:           Hora devuelta			D(HH:MM:SS)

        # C??digos de Errores

        SEGURIDAD
        - Sesi??n inv??lida		10011

        PLATAFORMA
        - Excepci??n de Plataforma								10001
        - Error en la ejecuci??n del programa					10002

        CONFIGURACI??N
        - Canal no declarado									10021
        - Canal se encuentra deshabilitado						10022
        - Servicio no habilitado en el canal					10023
        - Servicio no declarado en el canal						10024
        - Servicio no existe									10025
        - Usuario Bantotal no v??lido							10026
        - Usuario externo no tiene asignado usuario Bantotal	10027
        - Usuario no habilitado para el Servicio				10028
        - Usuario externo deshabilitado							10029
        - Usuario externo no asociado al servicio en el canal	10030
        - Servicio mal configurado								10031
        """
        request_body = json.dumps(self.authenticate)
        response = {
            "SessionToken": "",
            "Fecha": "",
            "Hora": "",
            "Erroresnegocio": ""
        }
        try:
            request = requests.post(self.request_url, data=request_body, headers={
                'Content-Type': 'application/json'}, verify=False, timeout=3)
            request = request.text
            logger.info([self.service, request])
            request = json.loads(request)

            response['SessionToken'] = request["SessionToken"]
            response['Fecha'] = request['Btoutreq']['Fecha']
            response['Hora'] = request['Btoutreq']['Hora']
            for BTErrorNegocio in request['Erroresnegocio']['BTErrorNegocio']:
                response["Erroresnegocio"] = BTErrorNegocio['Descripcion']

        except Exception as e:
            exp_message = str(e)
            if 'HTTPConnectionPool' in exp_message: # HTTPConnectionPool == Conection Timeout
                exp_message = '(HTTPConnectionPool): No se puede conectar al banco'
            logger.error([self.service, 'Exception', exp_message], exc_info=True)
            response["Erroresnegocio"] = exp_message

        return response

    def check_session(self, token):
        """# CHECK SESSION: API Valida Base Confiable"""
        self.authenticate['Btinreq']['Token'] = token
        request_url = self.request_url.replace(
            "odwsbt_Authenticate?Execute", "odwsbt_BSPAYROOL?")
        _api_service = ApiWsValidaBaseConfiable(request_url, self.authenticate)
        # Valores por default para checkear si responde bien la consulta
        # SimpleNamespace lo utilizo para acceder a los parametros por punto "official.country.code_number"
        official = SimpleNamespace(**{
            "country": SimpleNamespace(**{
                "code_number": 586
            }),
            "identification_type": "1",
            "identification_id": "2178913",
            "name_first": "2178913",
            "name_second": "",
            "surname_first": "2178913",
            "surname_second": "",
            "birthday": datetime.now().date()
        })
        return _api_service.ws_valida_base_confiable(official)
