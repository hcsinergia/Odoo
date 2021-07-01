# -*- coding: utf-8 -*-
from odoo import api, fields, models


class BM_OfficialWizard(models.TransientModel):
    _name = "bm.official.wizard"
    _description = "BM Official Wizard"

    message = fields.Text(readonly=True, store=False)
