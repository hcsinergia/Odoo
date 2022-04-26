# -*- coding: utf-8 -*-
from odoo import api, fields, models

REJECT_REASONS = [
    ('1', 'CI ILEGIBLE O DAÑADA'),
    ('2', 'CI VENCIDA'),
    ('3', 'FALTA ANVERSO/REVERSO'),
    ('4', 'NO COINCIDE'),
    ('5', 'CEDULA ADULTERADA'),
    ('6', 'OTRO')]

CPE_STATUS = [
    ('1', 'WK PENDIENTE DE ENTREGA'),
    ('2', 'VARIACION DE FIRMA'),
    ('3', 'FALTA FIRMA FORMULARIO'),
    ('4', 'CÉDULA ILEGIBLE'),
    ('5', 'PENDIENTE DE ACTIVACION')]

class BMOfficialWizard(models.TransientModel):
    _name = "bm.official.wizard"
    _description = "BM Official Wizard"

    message = fields.Text(readonly=True, store=False)


class BMOfficialWizardRejectCAM(models.TransientModel):
    _name = 'bm.official.wizard.rejectcam'
    _description = "BM Official Wizard Rechazar CAM"

    def button_save(self):
        official = self.env['bm.official'].browse(self.env.context.get('active_id'))
        if self.reject_reason != '6':
            official.reject_reason = dict(self._fields['reject_reason'].selection).get(self.reject_reason)
        else:
            official.reject_reason = self.reject_reason_description
        official.state = 'error'

        # Notifica a los usuarios de Centro Payroll que tiene altas
        notify_title = 'Rechazo de funcionarios'
        notify_body = 'Se rechazo el alta del Funcionario: {} ({}).<br>Motivo: {}'.format(official.name, official.identification_id, official.reject_reason)
        official.notify_to_company_users(official.company_id.id, notify_title, notify_body)
        return True
    
    reject_reason = fields.Selection(REJECT_REASONS, string="Motivo de rechazo", required=True, default='1')
    reject_reason_description = fields.Text('Descripción del rechazo')


class BMOfficialWizardStatusCPE(models.TransientModel):
    _name = "bm.official.wizard.statuscpe"
    _description = "BM Official Wizard Status CPE"

    def button_save(self):
        official = self.env['bm.official'].browse(self.env.context.get('active_id'))
        official.reject_reason = dict(self._fields['cpe_status'].selection).get(self.cpe_status)
        if self.cpe_status == '5':
            official.state = 'pending'

    cpe_status = fields.Selection(CPE_STATUS, string="Estado del funcionario")
