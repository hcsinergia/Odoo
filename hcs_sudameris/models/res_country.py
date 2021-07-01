from odoo import models, fields


class res_country_departament(models.Model):
  _name = "res.country.departament"
  
  name = fields.Char(string='Nombre del departamento', required=True)
  code = fields.Char(string='Código de departamento', required=True)
  state_id = fields.Many2one(string='Provincia', comodel_name='res.country.state')

  _sql_constraints = [
      ('name_code_uniq', 'unique(state_id, code)', 'The code of the department must be unique by state !')
  ]


class res_country_neighborhood(models.Model):
  _name = "res.country.neighborhood"
  
  name = fields.Char(string='Nombre del barrio', required=True)
  code = fields.Char(string='Código de barrio', required=True)
  departament_id = fields.Many2one(string='Departamento', comodel_name='res.country.departament')

  _sql_constraints = [
      ('name_code_uniq', 'unique(departament_id, code)', 'The code of the departament must be unique by neighborhood !')
  ]
