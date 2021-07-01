# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import datetime
import logging, json, requests

_logger = logging.getLogger(__name__)

_TipoCobro = [('1', 'Sueldo'), ('2', 'Aguinaldo'), ('3', 'Anticipo de Sueldo'),
('4', 'Otras Remuneraciones'), ('7', 'Acreditación Tarjeta Prepaga'), ('8', 'Pago de Licencias')]

_Moneda = [('6900', 'Guaraníes'), ('1', 'Dólares Americanos')]

_ModalidadPago = [('20', 'Débito en Cta. Cte'), ('21', 'Débito Caja de Ahorro')]

_EstadoMovimiento = [('preliquidacion', 'Preliquidación'), ('aprobado', 'Aprobado'), ('enproceso', 'En Proceso'), ('cancelado', 'Cancelado'), ('liquidado', 'Liquidado')]

class sudameris_employee_salary_movement_wizard(models.TransientModel):
  _name = "sudameris_employee_salary_movement.wizard"
  _description = "Sudameris Employee Salary Movement wizard"
  message = fields.Text(readonly=True, store=False)


class sudameris_employee_salary_movement(models.Model):
  _name = 'sudameris_employee_salary_movement'
  _description = 'Movimientos de salario del funcionario'
  _rec_name = 'funcionario'

  identification_id = fields.Char(string='Nº identificación', required=True)
  funcionario = fields.Many2one(comodel_name='hr.employee', string='Funcionario', compute='_check_funcionario', store=True)
  moneda = fields.Selection(selection=_Moneda, strsng="Moneda", related='funcionario.tipo_moneda', readonly=True)
  salario_bruto_def = fields.Float(string="Salario del funcionario", digits=(18, 2), related='funcionario.salario_bruto', readonly=True)
  salario_importe = fields.Float(string="Salario a pagar", digits=(18, 2))
  tipo_cobro = fields.Selection(selection=_TipoCobro, string="Tipo de Cobro", default="1")
  fecha_pago = fields.Date(string="Fecha de pago", default=lambda s: fields.Date.context_today(s))
  modalidad_pago = fields.Selection(string="Modalidad de pago", selection=_ModalidadPago, default="21")
  codigo_operacion = fields.Char(string="Operación")
  codigo_suboperacion = fields.Char(string="Suboperación")
  tipo_operacion = fields.Char(string="Tipo de Operación")
  referencia = fields.Char(string="Referencia")
  state = fields.Selection(string="Estado", selection=_EstadoMovimiento, default='preliquidacion')

  def show_message(self, title, message):
    return {
      'name': title,
      'type': 'ir.actions.act_window',
      'res_model': 'sudameris_employee_salary_movement.wizard',
      'view_mode': 'form',
      'view_type': 'form',
      'context': {'default_message': message},
      'target': 'new'
    }

  @api.onchange('identification_id')
  def on_change_identification_id(self):
    _found = False
    if (self.identification_id):
      for funcionario in self.env['hr.employee'].search([('identification_id', '=', self.identification_id)]):
        _found = True
        self.funcionario = funcionario
        self.salario_importe = funcionario.salario_bruto
      if not _found:
        self.funcionario = None
        self.salario_importe = 0    
    
  @api.depends('identification_id', 'salario_importe')    
  def _check_funcionario(self):
    for rec in self:
      if rec.identification_id:
        for funcionario in self.env['hr.employee'].search([('identification_id', '=', rec.identification_id)]):
          rec.funcionario = funcionario
          rec.salario_importe = funcionario.salario_bruto
        
    
  def btn_aprobar(self):
    for rec in self:
      rec.state = 'aprobado'
      
  def btn_preliquidacion(self):
    for rec in self:
      rec.state = 'preliquidacion'

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

  def generar_pago(self):
    # Obtengo los movimientos seleccionados
    movimientos = self.env['sudameris_employee_salary_movement'].browse(self._context.get('active_ids'))
    _ids = []
    for rec in movimientos:
      if rec.state == 'aprobado':
        _ids.append('{}'.format(rec.id))
    if _ids:
      return {
        'type': 'ir.actions.act_url',
        'url': '/web/binary_text/crear_txt?ids={}'.format(','.join(_ids)),
        'target': 'self'
      }
    else:
      return self.show_message('Generar Pago', 'No se generó ningun pago')
