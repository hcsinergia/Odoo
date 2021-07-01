# -*- coding: utf-8 -*- | , api, _
from odoo import models, fields

_TipoProducto = [('producto', 'Producto'), ('kit', 'Welcome Kit')]

class sudameris_employee_products(models.Model):
  _name = 'sudameris_employee_products'
  _description = 'Paquete/productos del funcionario'

  name = fields.Char(index=True)
  tipo = fields.Selection(string="Tipo de producto", selection=_TipoProducto, default='producto', store=True, required=True)
  parent_id = fields.Many2one('sudameris_employee_products', index=True, ondelete='cascade')
  child_ids = fields.One2many('sudameris_employee_products', 'parent_id', string='Productos del kit')
  salario_minimo = fields.Integer(string="Salario minimo", default='0')
