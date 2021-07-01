from odoo import models, fields

class BMResCompany(models.Model):
  _inherit = 'res.company'

  company_code = fields.Integer('Código de la Empresa', required=True)

  _sql_constraints = [
      ('company_code_uniq', 'unique(company_code)', 'No puden existir 2 empresas con el mismo código'),
  ]