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
  Función para obtener el token guardado en env['config_parameter'] y si está expirado
  obtener uno nuevo con el servicio Authenticate para no usar el mismo innecesariamente
  """
  def __get_token(self):
    expiration = self.config_parameter.get_param('sudameris.expiration')
    token      = self.config_parameter.get_param('sudameris.token')
    # Si la fecha de hoy es mayor a la fecha de expiración
    if datetime.today().date() > datetime.strptime(expiration, '%Y-%m-%d %H:%M:%S').date():
      # Como está vencido, actualizo el token
      try:
        new_auth = self.__ws_authenticate()
        token = new_auth['token']
        self.config_parameter.set_param('sudameris.expiration', new_auth['expiration'])
        self.config_parameter.set_param('sudameris.token', token)
      except:
        token = None
    return token

  """
  Servicio: Authenticate
  Metodo: POST
  URL: http://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_Authenticate
  """
  def __ws_authenticate(self, *args, **kwargs):
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
    # _logger.debug(response)
    # xml_response = """
    # <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope">
    #  <SOAP-ENV:Body>
    #    <Authenticate.ExecuteResponse xmlns="http://uy.com.dlya.bantotal/BTS0A/">
    #      <Btinreq>
    #        <Device>10.100.14.2</Device>
    #        <Usuario>FERNANDY</Usuario>
    #        <Requerimiento>1</Requerimiento>
    #        <Canal>BTINTERNO</Canal>
    #        <Token />
    #      </Btinreq>
    #      <SessionToken>FPEREZTOKEN</SessionToken>
    #      <Erroresnegocio></Erroresnegocio>
    #      <Btoutreq>
    #        <Numero>9608</Numero>
    #        <Estado>OK</Estado>
    #        <Servicio>Authenticate.Execute</Servicio>
    #        <Requerimiento>1</Requerimiento>
    #        <Fecha>2019-11-29</Fecha>
    #        <Hora>09:24:26</Hora>
    #        <Canal>BTINTERNO</Canal>
    #      </Btoutreq>
    #    </Authenticate.ExecuteResponse>
    #  </SOAP-ENV:Body>
    # </SOAP-ENV:Envelope>
    #      """
    wsurl = self.base_url.replace("odwsbt_BSPayroll?", "odwsbt_Authenticate")
    new_auth = {
      "token": None,
      "expiration": None
    }
    xml = """
      <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:bts="http://schemas.datacontract.org/2004/07/BtsWcf.Model">
        <soapenv:Header/>
        <soapenv:Body>
            <bts:Authenticate.Execute>
                <bts:Btinreq>
                    <bts:Device>10.100.14.2</bts:Device>
                    <bts:Usuario>GEIER</bts:Usuario>
                    <bts:Requerimiento>1</bts:Requerimiento>
                    <bts:Canal>BTINTERNO</bts:Canal>
                    <bts:Token></bts:Token>
                </bts:Btinreq>
                <bts:UserId>GEIER</bts:UserId>
                <bts:UserPassword>Albuquerque2021</bts:UserPassword>
            </bts:Authenticate.Execute>
        </soapenv:Body>
      </soapenv:Envelope>      
      """
    headers = {'Content-Type': 'application/xml'} # set what your server accepts
    try:
      response = requests.post(wsurl, data=xml, headers=headers, verify=False, timeout=10)
      # Formateo el resultado para obtener el Token y la fecha actual
      import xml.etree.ElementTree as ET
      xml_parsed = ET.ElementTree(ET.fromstring(response.content)).getroot()
      for childrens in xml_parsed:
        for children in childrens:
          for child in children:
            if "SessionToken" in child.tag:
              new_auth['token'] = child.text
            if "Btoutreq" in child.tag:
              for btoutreq in child:
                if "Fecha" in btoutreq.tag:
                  new_auth['expiration'] = btoutreq.text
                if "Hora" in btoutreq.tag:
                  new_auth['expiration'] += " " + btoutreq.text
      return new_auth
    except:
      return False
