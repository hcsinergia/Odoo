from odoo import models
from datetime import datetime
import requests, json, logging

_logger = logging.getLogger(__name__)
_CodigoPaises = [('105', 'BRASIL'), ('845', 'URUGUAY'), ('63', 'ARGENTINA'), ('586', 'PARAGUAY'),
('589', 'PERU'), ('13', 'AFGANISTAN'), ('17', 'ALBANIA'), ('20', 'ALBORANYPEREJIL,I'),
('23', 'ALEMANIA'), ('31', 'ALTOVOLTA'), ('37', 'ANDORRA'), ('39', 'AUSTRALIA'),
('40', 'ANGOLA'), ('43', 'ANTIGUA,ISLA'), ('47', 'ANTILLASHOLANDESAS'),
('53', 'ARABIASAUDITA'), ('59', 'ARGELIA'), ('69', 'AUSTRALIA'), ('72', 'AUSTRIA'),
('77', 'BAHAMAS,ISLAS'), ('80', 'BAHREIN'), ('81', 'BANGLADESH'), ('83', 'BARBADOS'),
('85', 'TOKELAN,ISLAS'), ('87', 'BELGICA-LUXEMBURGO'), ('88', 'BELICE'), ('90', 'BERMUDAS'),
('93', 'BIRMANIA'), ('97', 'BOLIVIA'), ('101', 'BOTSWANA'), ('108', 'BRUNEI'),
('111', 'BULGARIA'), ('115', 'BURUNDI'), ('119', 'BUTAN'), ('127', 'CABOVERDE,RCA.DE'),
('137', 'CAIMAN,ISLAS'), ('141', 'CAMBOYA'), ('145', 'CAMERUM'), ('149', 'CANADA'),
('153', 'CANARIAS,ISLAS'), ('159', 'CIUDADDELVATICANO'), ('165', 'COCOS,ISLAS'), ('169', 'COLOMBIA'),
('173', 'COMORAS'), ('177', 'CONGO'), ('183', 'COOK,ISLAS'), ('187', 'COREADELNORTE'),
('190', 'COREADELSUR'), ('193', 'COSTADEMARFIL'), ('196', 'COSTARICA'), ('199', 'CUBA'),
('203', 'CHAD'), ('207', 'CHECOSLOVAQUIA'), ('211', 'CHILE'), ('215', 'CHINA'),
('218', 'TAIWAN'), ('221', 'CHIPRE'), ('229', 'DENIN'), ('232', 'DINAMARCA'),
('235', 'DOMINICA,ISLA'), ('239', 'ECUADOR'), ('240', 'EGIPTO'), ('242', 'ELSALVADOR'),
('244', 'EMIRATOSARABESUNID'), ('245', 'ESPAÑA'), ('249', 'ESTADOSUNIDOS'), ('253', 'ETIOPIA'),
('259', 'FEROE,ISLAS'), ('267', 'FILIPINAS'), ('271', 'FINLANDIA'), ('275', 'FRANCIA'),
('281', 'GABON'), ('285', 'GAMBIA'), ('289', 'GHANA'), ('293', 'GIBRALTAR'),
('297', 'GRENADA'), ('301', 'GRECIA'), ('305', 'GROENLANDIA'), ('309', 'GUADALUPEYDEPENDEN'),
('313', 'GUAM'), ('317', 'GUATEMALA'), ('325', 'GUAYANAFRANCESA'), ('329', 'GUINEA'),
('331', 'GUINEAECUATORIAL'), ('334', 'GUINEABISSAU'), ('337', 'GUYANA'), ('341', 'HAITI'),
('345', 'HONDURAS'), ('351', 'HONGKONG'), ('355', 'HUNGRIA'), ('361', 'INDIA'),
('365', 'INDONESIA'), ('369', 'IRAK'), ('372', 'IRAN'), ('375', 'IRLANDA-EIRE-'),
('379', 'ISLANDIA'), ('383', 'ISRAEL'), ('386', 'ITALIA'), ('391', 'JAMAICA'),
('399', 'JAPON'), ('403', 'JORDANIA'), ('410', 'KENIA'), ('413', 'KUWAIT'),
('420', 'LAOS'), ('426', 'LESOTHO'), ('431', 'LIBANO'), ('434', 'LIBERIA'),
('438', 'LIBIA'), ('445', 'LUXEMBURGO'), ('447', 'MACAO'), ('450', 'MADAGASCAR'),
('455', 'MALASIA'), ('458', 'MALAWI'), ('461', 'MALDIVAS'), ('464', 'MALI'),
('467', 'MALTA'), ('474', 'MARRUECOS'), ('477', 'MARTINICA'), ('485', 'MAURICIO'),
('488', 'MAURITANIA'), ('493', 'MEXICO'), ('497', 'MONGOLIAREP.POPULAR'), ('501', 'MONTSERRAT,ISLA'),
('504', 'MOYOTTE'), ('505', 'MOZAMBIQUE'), ('508', 'NAURU'), ('511', 'NAVIDAD,ISLAS'),
('517', 'NEPAL'), ('521', 'NICARAGUA'), ('525', 'NIGER'), ('528', 'NIGERIA'),
('531', 'NIUE,ISLA'), ('535', 'NORFOLK,ISLA'), ('538', 'NORUEGA'), ('542', 'NUEVACALEDONIA'),
('545', 'PAPUANUEVAGUINEA'), ('548', 'NUEVAZELANDIA'), ('551', 'NUEVASHEBRIDAS'), ('556', 'OMAN'),
('563', 'PACIFICO,ISLAS-ADMIN'), ('566', 'PACIFICO,ISLAS-POSES'), ('569', 'PACIFICO,ISLAS-FIDEI'), ('573', 'HOLANDA'),
('576', 'PAKISTAN'), ('580', 'PANAMA'), ('593', 'PITCAIRN,ISLA'), ('599', 'POLINESIAFRANCESA'),
('603', 'POLONIA'), ('607', 'PORTUGAL'), ('611', 'PUERTORICO'), ('618', 'QATAR'),
('628', 'REINOUNIDO'), ('640', 'REPUBLICACENTROAFRI'), ('647', 'REPUBLICADOMINICANA'), ('660', 'REUNION,ISLA'),
('665', 'RODESIA'), ('670', 'RUMANIA'), ('675', 'RWANDA'), ('690', 'SAMOAOCCIDENTAL,EDO'),
('695', 'S.CRISTOBALNEVISY'), ('700', 'SANPEDROYMIQUELON'), ('705', 'SANVICENTE,ISLA'), ('710', 'SANTAELENA'),
('715', 'SANTALUCIA,ISLA'), ('720', 'SANTOTOMEYPRINCIP'), ('728', 'SENEGAL'), ('731', 'SEYCHELLES'),
('735', 'SIERRALEONA'), ('741', 'SINGAPUR'), ('744', 'SIRIA'), ('748', 'SOMALIA'),
('750', 'SRILANKA'), ('756', 'SUDAFRICAYNAMIBIA'), ('759', 'SUDAN'), ('764', 'SUECIA'),
('767', 'SUIZA'), ('770', 'SURINAM'), ('776', 'TAILANDIA'), ('780', 'TANZANIA'),
('783', 'DJIBOUTI'), ('785', 'TERRIT.ALTACOMIS.PA'), ('800', 'TOGO'), ('810', 'REINODETONGA'),
('815', 'TRINIDADYTOBAGO'), ('820', 'TUNEZ'), ('823', 'TURCASYCAICOS,ISLA'), ('827', 'TURQUIA'),
('833', 'UGANDA'), ('840', 'U.R.S.S.'), ('850', 'VENEZUELA'), ('855', 'VIETNAM'),
('863', 'VIRGENES,ISLAS-BRITA'), ('866', 'VISGENES,ISLAS-U.S.A'), ('870', 'FIDJI,ISLAS'), ('875', 'WALLISYFUTUNA,ISL'),
('880', 'YEMENDELNORTE'), ('881', 'YEMENDELSUR'), ('885', 'YUGOESLAVIA'), ('888', 'ZAIRE'),
('890', 'ZAMBIA'), ('895', 'ZONADELCANALDEPA'), ('896', 'HOLANDA'), ('897', 'ESCOCIA')]


class SudamerisApi:
  #Variables de la clase
  
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
    ### RESPONSE
    SessionToken:   Token devuelto  | C(24)
    Fecha:          Fecha devuelta  | D(AAAA-MM-DD)
    Hora:           Hora devuelta   | D(HH:MM:SS)
    ### Códigos de Errores
    ## SEGURIDAD
    Sesión inválida                                     |   10011
    ## PLATAFORMA
    Excepción de Plataforma                             |   10001
    Error en la ejecución del programa                  |   10002
    ## CONFIGURACIÓN
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
    #_logger.debug(response)
    #xml_response = """
    #<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope">
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
    #</SOAP-ENV:Envelope>
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
    for paises in _CodigoPaises:
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

  """
  Servicio: Estado de la Caja de Ahorro
  Metodo: POST
  URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSEstadoCA
  """
  def ws_estado_ca(self, *args, **kwargs):
    """ Parametros
    Btinreq:    Credenciales        |   Object
    Cuenta:     Número de cuenta    |   N(9)
    Sucursal:   Número de sucursal  |   N(3)    | Si no se envía, se busca la Caja de Ahorro por Modulo y moneda
    Modulo:     Módulo(?)           |   N(3)
    Moneda:     Código de moneda    |   N(4)
    ### JSON
    {
      "Btinreq": {
        "Device": "10.103.103.31",
        "Usuario": "RUIZMAU",
        "Requerimiento": "1",
        "Canal": "BTINTERNO",
        "Token": "4d9a84ffae088C9B822DF6FA"
      },
      "Parametros": {
        "Parametro": {
          "sBTRepParametros.It": [
            {
              "Tipo": "Texto",
              "Nombre": "CUENTA",
              "Codigo": 5,
              "Valor": "302059"
                    },
            {
              "Tipo": "Entero",
              "Nombre": "MODULO",
              "Codigo": 6,
              "Valor": 21
                    },
            {
              "Tipo": "Entero",
              "Nombre": "MONEDA",
              "Codigo": 7,
              "Valor": 6900
                    }
                ]
        }
      }
    }
    ### RESPONSE
    Cuenta:         Número de cuenta    |   N(9)
    Sucursal:       Número de sucursal  |   N(3)
    Modulo:         Módulo(?)           |   N(3)
    Moneda:         Código de moneda    |   N(4)
    Estado:         Estado de la Cuenta |   N(2)
    CodRetorno:     Código de Retorno   |   N(2)
    Mensaje:        Nombre de Persona   |   C(100)  | Puede existir varias CA para una cuenta en sucursales distintas.
    """
    wsurl = self.base_url + "WSEstadoCA"
    self.authenticate['Btinreq']['Token'] = self.__get_token()
    return [wsurl, self.authenticate['Btinreq']['Token']]
  """
  Servicio: Alta de CAJA DE AHORRO
  Metodo: POST
  URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSAltaCA
  """
  def ws_alta_ca(self, Pais, Tdoc, Ecivil, Ciudad, Departamento, Barrio, *args, **kwargs):        
    """ Parametros
    Btinreq:    Credenciales        |   Object
    Cuenta:     Número de cuenta    |   N(9)
    Sucursal:   Número de sucursal  |   N(3)
    Modulo:     Módulo(?)           |   N(3)
    Moneda:     Código de moneda    |   N(4)
    Estado:     Estado de alta(*)   |   N(2)
    ### JSON
    {
      "Btinreq": {
        "Device": "10.103.103.31",
        "Usuario": "RUIZMAU",
        "Requerimiento": "1",
        "Canal": "BTINTERNO",
        "Token": "9ae861095c088C9B822DF6FA"
      },
      "Pgcod": 1,
      "CtNro": 4003349,
      "Pgmoca": 21,
      "Suc": 10,
      "PgMNac": 6900,
      "Papel": 0,
      "Totope": 0,
      "Scsbop": 0,
      "PCvNom": " ",
      "CodRetorno": " ",
      "Mensaje": " "
    }
    ### RESPONSE
    CodRetorno:     Código de Retorno       |   N(3)
    Mensaje:        Nombre de Persona       |   C(100)
    """
    wsurl = self.base_url + "WSAltaCA"
    self.authenticate['Btinreq']['Token'] = self.__get_token()
    return [wsurl, self.authenticate['Btinreq']['Token'], Pais, Tdoc, Ecivil, Ciudad, Departamento, Barrio]
  
  """
  Servicio: Estado de la Tarjeta de Debito
  Metodo: POST
  URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSEstadoTD
  """
  def ws_estado_td(self, *args, **kwargs):
    """ Parametros
    Btinreq:    Credenciales        |   Object
    Cuenta:     Número de cuenta    |   N(9)
    Sucursal:   Número de sucursal  |   N(3)
    Modulo:     Módulo(?)           |   N(3)
    Moneda:     Código de moneda    |   N(4)
    ### JSON
    {
      "Btinreq": {
        "Device": "10.103.103.31",
        "Usuario": "RUIZMAU",
        "Requerimiento": "1",
        "Canal": "BTINTERNO",
        "Token": "4d9a84ffae088C9B822DF6FA"
      },
      "Parametros": {
        "Parametro": {
          "sBTRepParametros.It": [
            {
              "Tipo": "Texto",
              "Nombre": "CUENTA",
              "Codigo": 5,
              "Valor": "302059"
                    },
            {
              "Tipo": "Entero",
              "Nombre": "MONEDA",
              "Codigo": 7,
              "Valor": 6900
                    }
                ]
        }
      }
    }
    ### RESPONSE
    CodRetorno:     Código de Retorno       |   N(3)
    Mensaje:        Nombre de Persona       |   C(100)
    """
    wsurl = self.base_url + "WSEstadoTD"
    self.authenticate['Btinreq']['Token'] = self.__get_token()
    return [wsurl, self.authenticate['Btinreq']['Token']]

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
    ### JSON  
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
    ### RESPONSE
    CodRetorno:     Código de Retorno       |   N(3)
    Mensaje:        Nombre de Persona       |   C(100)
    """
    wsurl = self.base_url + "WSAltaTD"
    self.authenticate['Btinreq']['Token'] = self.__get_token()
    return [wsurl, self.authenticate['Btinreq']['Token']]
  
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
    ### JSON
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
    ### RESPONSE
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
  
  """
  Servicio: Validación de documentos contra la base BCP/BASE CONFIABLE
  Metodo: POST
  URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSValidaBaseConfiable
  """
  def ws_valida_base_confiable(self):
    """ Parametros
    Btinreq:    Credenciales        |   Object
    Pais:       País                |   N(3)
    Tdoc:       Tipo de Documento   |   N(2)
    Ndoc:       Número de Documento |   C(12)
    Nomb1:      Primer Nombre       |   C(25)
    Nomb2:      Segundo Nombre      |   C(25)
    Apell1:     Primer Apellido     |   C(30)
    Apell2:     Segundo Apellido    |   C(30)
    FecNac:     Fecha de Nacimiento |   D(AAAA/MM/DD)
    ### JSON
    {
      "Btinreq": {
        "Device": "10.103.103.31",
        "Usuario": "RUIZMAU",
        "Requerimiento": "1",
        "Canal": "BTINTERNO",
        "Token": "887d6e2551088C9B822DF6FA"
      },
      "Pais": 586,
      "Tdoc": 1,
      "Ndoc": "2178913",
      "Nomb1": "2178913",
      "Nomb2": " ",
      "Apell1": "2178913",
      "Apell2": " ",
      "CodMensaje": " ",
      "Mensaje": " "
    }
    ### RESPONSE
    CodRetorno:     Código de Retorno       |   N(2)
    Mensaje:        Nombre de Persona       |   C(100)
    """
    wsurl = self.base_url + "WSValidaBaseConfiable"
    self.authenticate['Btinreq']['Token'] = self.__get_token()
    return [wsurl, self.authenticate['Btinreq']['Token']]
