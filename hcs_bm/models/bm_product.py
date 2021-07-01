# -*- coding: utf-8 -*- | , api, _
from odoo import models, fields


class BM_Products(models.Model):
  _name = 'bm.product'
  _description = 'Welcome Kit'

  name = fields.Char(index=True)
  product_type = fields.Selection([
      ('producto', 'Producto'),
      ('kit', 'Welcome Kit')], string="Tipo de producto", default='producto', store=True, required=True)
  parent_id = fields.Many2one('bm.product', index=True, ondelete='cascade')
  child_ids = fields.One2many('bm.product', 'parent_id', string='Productos del kit')
  minimum_salary = fields.Integer(string="Salario minimo", default='0')
