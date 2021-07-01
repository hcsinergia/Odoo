from datetime import datetime
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class SudamerisApiBase:
    # Variables de la clase

    def __init__(self, config_parameter):
        self.config_parameter = config_parameter
        self.base_url = "http://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPAYROOL?"
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
        self.codigo_paises = [('105', 'BRASIL'), ('845', 'URUGUAY'), ('63', 'ARGENTINA'), ('586', 'PARAGUAY'),
                         ('589', 'PERU'), ('13', 'AFGANISTAN'), ('17',
                                                                 'ALBANIA'), ('20', 'ALBORANYPEREJIL,I'),
                         ('23', 'ALEMANIA'), ('31', 'ALTOVOLTA'), ('37',
                                                                   'ANDORRA'), ('39', 'AUSTRALIA'),
                         ('40', 'ANGOLA'), ('43',
                                            'ANTIGUA,ISLA'), ('47', 'ANTILLASHOLANDESAS'),
                         ('53', 'ARABIASAUDITA'), ('59', 'ARGELIA'), ('69',
                                                                      'AUSTRALIA'), ('72', 'AUSTRIA'),
                         ('77', 'BAHAMAS,ISLAS'), ('80', 'BAHREIN'), ('81',
                                                                      'BANGLADESH'), ('83', 'BARBADOS'),
                         ('85', 'TOKELAN,ISLAS'), ('87',
                                                   'BELGICA-LUXEMBURGO'), ('88', 'BELICE'), ('90', 'BERMUDAS'),
                         ('93', 'BIRMANIA'), ('97', 'BOLIVIA'), ('101',
                                                                 'BOTSWANA'), ('108', 'BRUNEI'),
                         ('111', 'BULGARIA'), ('115', 'BURUNDI'), ('119',
                                                                   'BUTAN'), ('127', 'CABOVERDE,RCA.DE'),
                         ('137', 'CAIMAN,ISLAS'), ('141',
                                                   'CAMBOYA'), ('145', 'CAMERUM'), ('149', 'CANADA'),
                         ('153', 'CANARIAS,ISLAS'), ('159', 'CIUDADDELVATICANO'), ('165',
                                                                                   'COCOS,ISLAS'), ('169', 'COLOMBIA'),
                         ('173', 'COMORAS'), ('177', 'CONGO'), ('183',
                                                                'COOK,ISLAS'), ('187', 'COREADELNORTE'),
                         ('190', 'COREADELSUR'), ('193',
                                                  'COSTADEMARFIL'), ('196', 'COSTARICA'), ('199', 'CUBA'),
                         ('203', 'CHAD'), ('207', 'CHECOSLOVAQUIA'), ('211',
                                                                      'CHILE'), ('215', 'CHINA'),
                         ('218', 'TAIWAN'), ('221', 'CHIPRE'), ('229',
                                                                'DENIN'), ('232', 'DINAMARCA'),
                         ('235', 'DOMINICA,ISLA'), ('239', 'ECUADOR'), ('240',
                                                                        'EGIPTO'), ('242', 'ELSALVADOR'),
                         ('244', 'EMIRATOSARABESUNID'), ('245',
                                                         'ESPAÑA'), ('249', 'ESTADOSUNIDOS'), ('253', 'ETIOPIA'),
                         ('259', 'FEROE,ISLAS'), ('267', 'FILIPINAS'), ('271',
                                                                        'FINLANDIA'), ('275', 'FRANCIA'),
                         ('281', 'GABON'), ('285', 'GAMBIA'), ('289',
                                                               'GHANA'), ('293', 'GIBRALTAR'),
                         ('297', 'GRENADA'), ('301', 'GRECIA'), ('305',
                                                                 'GROENLANDIA'), ('309', 'GUADALUPEYDEPENDEN'),
                         ('313', 'GUAM'), ('317', 'GUATEMALA'), ('325',
                                                                 'GUAYANAFRANCESA'), ('329', 'GUINEA'),
                         ('331', 'GUINEAECUATORIAL'), ('334',
                                                       'GUINEABISSAU'), ('337', 'GUYANA'), ('341', 'HAITI'),
                         ('345', 'HONDURAS'), ('351', 'HONGKONG'), ('355',
                                                                    'HUNGRIA'), ('361', 'INDIA'),
                         ('365', 'INDONESIA'), ('369', 'IRAK'), ('372',
                                                                 'IRAN'), ('375', 'IRLANDA-EIRE-'),
                         ('379', 'ISLANDIA'), ('383', 'ISRAEL'), ('386',
                                                                  'ITALIA'), ('391', 'JAMAICA'),
                         ('399', 'JAPON'), ('403', 'JORDANIA'), ('410',
                                                                 'KENIA'), ('413', 'KUWAIT'),
                         ('420', 'LAOS'), ('426', 'LESOTHO'), ('431',
                                                               'LIBANO'), ('434', 'LIBERIA'),
                         ('438', 'LIBIA'), ('445', 'LUXEMBURGO'), ('447',
                                                                   'MACAO'), ('450', 'MADAGASCAR'),
                         ('455', 'MALASIA'), ('458', 'MALAWI'), ('461',
                                                                 'MALDIVAS'), ('464', 'MALI'),
                         ('467', 'MALTA'), ('474', 'MARRUECOS'), ('477',
                                                                  'MARTINICA'), ('485', 'MAURICIO'),
                         ('488', 'MAURITANIA'), ('493', 'MEXICO'), ('497',
                                                                    'MONGOLIAREP.POPULAR'), ('501', 'MONTSERRAT,ISLA'),
                         ('504', 'MOYOTTE'), ('505', 'MOZAMBIQUE'), ('508',
                                                                     'NAURU'), ('511', 'NAVIDAD,ISLAS'),
                         ('517', 'NEPAL'), ('521', 'NICARAGUA'), ('525',
                                                                  'NIGER'), ('528', 'NIGERIA'),
                         ('531', 'NIUE,ISLA'), ('535', 'NORFOLK,ISLA'), ('538',
                                                                         'NORUEGA'), ('542', 'NUEVACALEDONIA'),
                         ('545', 'PAPUANUEVAGUINEA'), ('548',
                                                       'NUEVAZELANDIA'), ('551', 'NUEVASHEBRIDAS'), ('556', 'OMAN'),
                         ('563', 'PACIFICO,ISLAS-ADMIN'), ('566', 'PACIFICO,ISLAS-POSES'), ('569',
                                                                                            'PACIFICO,ISLAS-FIDEI'), ('573', 'HOLANDA'),
                         ('576', 'PAKISTAN'), ('580', 'PANAMA'), ('593',
                                                                  'PITCAIRN,ISLA'), ('599', 'POLINESIAFRANCESA'),
                         ('603', 'POLONIA'), ('607', 'PORTUGAL'), ('611',
                                                                   'PUERTORICO'), ('618', 'QATAR'),
                         ('628', 'REINOUNIDO'), ('640', 'REPUBLICACENTROAFRI'), ('647',
                                                                                 'REPUBLICADOMINICANA'), ('660', 'REUNION,ISLA'),
                         ('665', 'RODESIA'), ('670', 'RUMANIA'), ('675',
                                                                  'RWANDA'), ('690', 'SAMOAOCCIDENTAL,EDO'),
                         ('695', 'S.CRISTOBALNEVISY'), ('700', 'SANPEDROYMIQUELON'), ('705',
                                                                                      'SANVICENTE,ISLA'), ('710', 'SANTAELENA'),
                         ('715', 'SANTALUCIA,ISLA'), ('720',
                                                      'SANTOTOMEYPRINCIP'), ('728', 'SENEGAL'), ('731', 'SEYCHELLES'),
                         ('735', 'SIERRALEONA'), ('741',
                                                  'SINGAPUR'), ('744', 'SIRIA'), ('748', 'SOMALIA'),
                         ('750', 'SRILANKA'), ('756', 'SUDAFRICAYNAMIBIA'), ('759',
                                                                             'SUDAN'), ('764', 'SUECIA'),
                         ('767', 'SUIZA'), ('770', 'SURINAM'), ('776',
                                                                'TAILANDIA'), ('780', 'TANZANIA'),
                         ('783', 'DJIBOUTI'), ('785', 'TERRIT.ALTACOMIS.PA'), ('800',
                                                                               'TOGO'), ('810', 'REINODETONGA'),
                         ('815', 'TRINIDADYTOBAGO'), ('820', 'TUNEZ'), ('823',
                                                                        'TURCASYCAICOS,ISLA'), ('827', 'TURQUIA'),
                         ('833', 'UGANDA'), ('840', 'U.R.S.S.'), ('850',
                                                                  'VENEZUELA'), ('855', 'VIETNAM'),
                         ('863', 'VIRGENES,ISLAS-BRITA'), ('866', 'VISGENES,ISLAS-U.S.A'), ('870',
                                                                                            'FIDJI,ISLAS'), ('875', 'WALLISYFUTUNA,ISL'),
                         ('880', 'YEMENDELNORTE'), ('881', 'YEMENDELSUR'), ('885',
                                                                            'YUGOESLAVIA'), ('888', 'ZAIRE'),
                         ('890', 'ZAMBIA'), ('895', 'ZONADELCANALDEPA'), ('896', 'HOLANDA'), ('897', 'ESCOCIA')]

    def ws_valida_base_confiable(self, Pais, Tdoc, Ndoc, Nomb1, Nomb2, Apell1, Apell2, FecNac):
        from .ws_valida_base_confiable import ApiWsValidaBaseConfiable
        _api = ApiWsValidaBaseConfiable(self.base_url, self.authenticate, self.codigo_paises)
        return _api.ws_valida_base_confiable(Pais, Tdoc, Ndoc, Nomb1, Nomb2, Apell1, Apell2, FecNac)


    def ws_cliente_posee_cuenta(self, Pais, Tdoc, Ndoc, *args, **kwargs):
        from .ws_cliente_posee_cuenta import ApiWsClientePoseeCuenta
        _api = ApiWsClientePoseeCuenta(self.base_url, self.authenticate, self.codigo_paises)
        return _api.ws_cliente_posee_cuenta(Pais, Tdoc, Ndoc)
        