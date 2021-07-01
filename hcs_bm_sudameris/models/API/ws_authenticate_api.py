from datetime import datetime
import json, requests, logging

_logger = logging.getLogger(__name__)


class ApiWsAuthenticate:
  def __init__(self, base_url, authenticate, config_parameter):
    self.base_url = base_url
    self.authenticate = authenticate
    self.config_parameter = config_parameter

  """
  Función para obtener el token guardado en env['config_parameter'] y si está expirado
  obtener uno nuevo con el servicio Authenticate para no usar el mismo innecesariamente
  """
  def get_token(self):
    expiration = self.config_parameter.get_param('sudameris.expiration')
    token      = self.config_parameter.get_param('sudameris.token')
    # El token es valido hasta las 23:59 del dia actual, si es mayor, se renueva
    if datetime.now().date() > datetime.strptime(expiration, '%Y-%m-%d %H:%M:%S').date():
      # Como está vencido, actualizo el token
      try:
        new_auth = self.ws_authenticate()
        token = new_auth['token']
        self.config_parameter.set_param('sudameris.expiration', new_auth['expiration'])
        self.config_parameter.set_param('sudameris.token', token)
      except:
        token = None
    return token

  """
  Servicio: Authenticate
  Metodo: POST
  URL: http://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_Authenticate?Execute
  """
  def ws_authenticate(self, *args, **kwargs):
    """ Parametros
    Device:         IP del host             |
    Usuario:        Usuario del servicio    |
    Requerimiento:  ID de requerimiento     | (siempre 1).
    Canal:          Canal de consulta       | (siempre BTINTERNO).
    Token:          Token de conexión       |
    UserId:         Usuario del servicio    |
    UserPassword:   Password del usuario    |
    # RESPONSE
    SessionToken:   Token devuelto  | C(24)
    Fecha:          Fecha devuelta  | D(AAAA-MM-DD)
    Hora:           Hora devuelta   | D(HH:MM:SS)
    # Códigos de Errores
    # SEGURIDAD
    Sesión inválida                                     |   10011
    # PLATAFORMA
    Excepción de Plataforma                             |   10001
    Error en la ejecución del programa                  |   10002
    # CONFIGURACIÓN
    Canal no declarado                                  |   10021
    Canal se encuentra deshabilitado                    |   10022
    Servicio no habilitado en el canal                  |   10023
    Servicio no declarado en el canal                   |   10024
    Servicio no existe                                  |   10025
    Usuario Bantotal no válido                          |   10026
    Usuario externo no tiene asignado usuario Bantotal  |   10027
    Usuario no habilitado para el Servicio              |   10028
    Usuario externo deshabilitado                       |   10029
    Usuario externo no asociado al servicio en el canal |   10030
    Servicio mal configurado                            |   10031
    """
    wsurl = self.base_url.replace("odwsbt_BSPAYROOL?", "odwsbt_Authenticate?Execute")
    request_body = json.dumps(self.authenticate)
    headers = {'Content-Type': 'application/json'} # set what your server accepts
    try:
      response = requests.post(wsurl, data=request_body, headers=headers, verify=False, timeout=10)
      _logger.debug(['APIRESPONSE', response.text])
      response = json.loads(response.text)
      new_auth = {
        "token": response['SessionToken'],
        "expiration": "{} {}".format(response['Btoutreq']['Fecha'], response['Btoutreq']['Hora']),
        "expiration": datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
      }
      return new_auth
    except:
      new_auth = {
        "token": "TOKENINVALIDO",
        "expiration": datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
      }
      return new_auth
