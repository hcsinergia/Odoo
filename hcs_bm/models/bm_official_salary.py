# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import datetime
import logging, json, requests

_logger = logging.getLogger(__name__)


class BM_OfficialSalary(models.Model):
  _name = 'bm.official.salary'
  _description = 'Movimiento de salario del funcionaro'
  _rec_name = 'official'

  identification_id = fields.Char(string='Nº identificación', required=True)
  official = fields.Many2one('bm.official', 'Funcionario', compute='_check_official', store=True)
  currency_type = fields.Selection([
      ('6900', 'Guaraníes'),
      ('1', 'Dólares Americanos')], strsng="Moneda", related='official.currency_type', readonly=True)
  official_gross_salary = fields.Float("Salario del funcionario", digits=(18, 2), related='official.gross_salary', readonly=True)
  amount_to_pay = fields.Float(string="Salario a pagar", digits=(18, 2))
  charge_type = fields.Selection([
      ('1', 'Sueldo'),
      ('2', 'Aguinaldo'),
      ('3', 'Anticipo de Sueldo'),
      ('4', 'Otras Remuneraciones'),
      ('7', 'Acreditación Tarjeta Prepaga'),
      ('8', 'Pago de Licencias')], string="Tipo de Cobro", default="1")
  payment_date = fields.Date(string="Fecha de pago", default=lambda s: fields.Date.context_today(s))
  payment_mode = fields.Selection([
      ('20', 'Débito en Cta. Cte'),
      ('21', 'Débito Caja de Ahorro')], string="Modalidad de pago", default="21")
  operation_type = fields.Char(string="Tipo de Operación")
  operation_code = fields.Char(string="Operación")
  company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
  suboperacion_code = fields.Char(string="Suboperación")
  reference = fields.Char(string="Referencia")
  state = fields.Selection([
      ('draft', 'Preliquidación'),
      ('aproved', 'Aprobado'),
      ('check', 'En Proceso'),
      ('cancel', 'Cancelado'),
      ('done', 'Liquidado')], string="Estado", default='draft')

  def show_message(self, title, message):
    return {
      'name': title,
      'type': 'ir.actions.act_window',
      'res_model': 'bm.official.salary.wizard',
      'view_mode': 'form',
      'view_type': 'form',
      'context': {'default_message': message},
      'target': 'new'
    }

  @api.onchange('identification_id')
  def on_change_identification_id(self):
    _found = False
    if (self.identification_id):
      for official in self.env['bm.official'].search([('identification_id', '=', self.identification_id)]):
        _found = True
        self.official = official
        self.amount_to_pay = official.gross_salary
      if not _found:
        self.official = None
        self.amount_to_pay = 0    
    
  @api.depends('identification_id', 'amount_to_pay')    
  def _check_official(self):
    for official_salary in self:
      if official_salary.identification_id:
        for official in self.env['bm.official'].search([('identification_id', '=', official_salary.identification_id)]):
          official_salary.official = official
          official_salary.amount_to_pay = official.gross_salary        
    
  def btn_aprobar(self):
    for official_salary in self:
      official_salary.state = 'aproved'
      
  def btn_draft(self):
    for official_salary in self:
      official_salary.state = 'draft'

  # Hacer funcion async para obtener la respuesta
  def obtener_token(self):
    #import wdb
    #wdb.set_trace()
    config_parameter = self.env['ir.config_parameter'].sudo()
    sudameris_auth = json.loads(config_parameter.get_param('sudameris.auth'))
    # Si la fecha de hoy es mayor a la fecha de expiración
    if datetime.now() > datetime.strptime(sudameris_auth['expiration'], '%Y-%m-%d %H:%M:%S'):
      r = requests.post('https://alertaseg.com.ar:8089/api/alerta_gps/check', data={})
      return r.content
      # raise ValidationError(json.dumps(r, indent=4))
      ### Me contecto al banco y espero respuesta del mismo *CREAR CONEXION VIA POST
      #
      # Guardo los nuevos datos en el parametro
      sudameris_auth = '{"token": "TOKEN_TEST","expiration":"2021-02-01 00:00:00"}'
      config_parameter.set_param('sudameris.auth', sudameris_auth)
      sudameris_auth = json.loads(sudameris_auth)
      #
      ### Finalizo la configuración del banco
    # Siempre retorno el token valido
    return sudameris_auth

  def create_file_txt(self):
    _ids = []
    # Obtengo los movimientos seleccionados
    for official_salary in self.env['bm.official.salary'].browse(self._context.get('active_ids')):
      if official_salary.state == 'aproved':
        _ids.append('{}'.format(official_salary.id))
    if _ids:
      return {
        'type': 'ir.actions.act_url',
        'url': '/web/binary_text/create_file_txt?ids={}'.format(','.join(_ids)),
        'target': 'self'
      }
    else:
      return self.show_message('Generar Pago', 'No se generó ningun pago')
