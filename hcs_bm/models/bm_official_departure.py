# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime

DEPARTURE_REASONS = [('medical', 'Medica'), ('fired', 'Despido'), ('resigned', 'Renuncia'), ('retired', 'Retirado')]


class BM_OfficialDeparture(models.Model):
    _name = 'bm.official.departure'
    _description = 'Movimiento de salario del funcionaro'

    name = fields.Char(compute='_compute_name')
    identification_id = fields.Char(string='Nº identificación', required=True)
    official = fields.Many2one('bm.official', 'Funcionario', compute='_check_official', copy=False, store=True)
    departure_reason = fields.Selection(DEPARTURE_REASONS, string="Motivo de salida", copy=False, tracking=True, required=True, default="medical")
    departure_description = fields.Text(string="Salida: Información adicional", copy=False, tracking=True)
    departure_start = fields.Date(string="Fecha de Salida", default=lambda self: datetime.now().date(), copy=False, required=True)
    departure_end = fields.Date(string="Fecha de Retorno", copy=False)
    state = fields.Selection([
        ('active', 'Activo'),
        ('finish', 'Finalizado')],
        string="Estado", default='active')

    @api.depends('identification_id')    
    def _check_official(self):
        for official_departure in self:
            if official_departure.identification_id:
                for official in self.env['bm.official'].search([('identification_id', '=', official_departure.identification_id)]):
                    official_departure.official = official

    @api.depends('official', 'departure_reason', 'departure_end')
    def _compute_name(self):
        for official_departure in self:
            official_departure.name = '#{}: {}'.format(official_departure.id, dict(DEPARTURE_REASONS)[official_departure.departure_reason])
            # active by default
            official_departure.state = 'active'
            if official_departure.departure_reason == 'medical' :
                # if departure_end is less from today, means is not departured
                if official_departure.departure_end < datetime.now().date():
                    official_departure.state = 'finish'

    @api.onchange('departure_reason')
    def on_change_departure_reason(self):
        if self.departure_reason == 'medical':
            self.departure_end = self._origin.departure_end
        else:
            self.departure_end = None