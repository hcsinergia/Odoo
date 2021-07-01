from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import random

#import logging
#_logger = logging.getLogger(__name__)


class BM_OfficialApi(models.Model):
    _inherit = "bm.official"

    def valid_client_reliable_base(self, *args):
        # Checkeo que el usuario actual tiene el permiso del banco
        if not self.env.user.has_group('hcs_bm_sudameris.group_bm_bank_payroll') and not args:
            return self.show_message('Validar', 'Usted no tiene permiso para ejecutar esta accion')

        # Get officials in check and not reliable_base or ready, error and not reliable_base
        _search = ['&', ('state', 'in', ['check', 'ready', 'error']), ('reliable_base', '=', False)]
        
        # If are active_ids, search it only
        active_ids = self._context.get('active_ids')
        if active_ids:
            _search = ['&', '&', ('id', 'in', active_ids), ('state', 'in', ['check', 'ready', 'error']), ('reliable_base', '=', False)]

        func_result = {
            'validations': {
                'error': [],
                'message': ''
            },
            'count_ok': 0
        }
        for official in self.env['bm.official'].search(_search):
            for _ in range(2):
                official.reliable_base = bool(random.randint(0, 1))
            if official.reliable_base:
                official.state = 'ready' 
                func_result['count_ok'] += 1
            else:
                func_result['validations']['error'].append('{} ({})'.format(official.name, official.identification_id))

        if len(func_result['validations']['error']) > 0:
            func_result['validations']['message'] = '\nLos siguientes funcionarios no pudieron ser validados:\n\n{}'.format('\n'.join(func_result['validations']['error']))
        if not args:
            return self.show_message('Validar', 'Se validaron {} funcionarios.\n{}'.format(func_result['count_ok'], func_result['validations']['message']))

    def client_owns_account(self, *args):
        # Checkeo que el usuario actual tiene el permiso del banco
        if not self.env.user.has_group('hcs_bm.group_bm_bank_payroll') and not args:
            return self.show_message('Validar', 'Usted no tiene permiso para ejecutar esta accion')

        # Get officials in check and not reliable_base or ready, error and not reliable_base
        _search = ['&', '&', ('state', 'in', ['check', 'ready', 'error']), ('reliable_base', '=', True), ('account_number', '=', None)]
        
        # If are active_ids, search it only
        active_ids = self._context.get('active_ids')
        if active_ids:
            _search = ['&', '&', ('id', 'in', active_ids), ('state', 'in', ['check', 'ready', 'error']), '&', ('reliable_base', '=', True), ('account_number', '=', None)]

        func_result = {
            'validations': {
                'error': [],
                'message': ''
            },
            'count_ok': 0
        }
        for official in self.env['bm.official'].search(_search):
            for _ in range(2):
                _found = bool(random.randint(0, 1))
            if _found:
                official.account_number = random.randint(1704048, 3917590)
                official.account_name = random.choice(['CANCELADO', 'INACTIVO', 'NORMAL', 'PACON'])
                official.branch_number = random.choice([10, 24, 25])
                func_result['count_ok'] += 1
            else:
                func_result['validations']['error'].append('{} ({})'.format(official.name, official.identification_id))

        if len(func_result['validations']['error']) > 0:
            func_result['validations']['message'] = '\nLos siguientes funcionarios no poseen cuenta:\n\n{}'.format('\n'.join(func_result['validations']['error']))
        if not args:
            return self.show_message('Verificar cuenta', 'Se verificó la cuenta de {} funcionarios.\n{}'.format(func_result['count_ok'], func_result['validations']['message']))