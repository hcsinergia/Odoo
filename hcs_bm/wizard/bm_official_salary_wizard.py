# -*- coding: utf-8 -*-
from odoo import models, fields


class BM_OfficialSalary_Wizard(models.TransientModel):
  _name = "bm.official.salary.wizard"
  _description = "Wizard: Movimiento de salario del funcionaro"
  message = fields.Text(readonly=True, store=False)
