# -*- coding: utf-8 -*-
import base64
import re
from odoo import fields, models, api, _
from odoo.modules.module import get_module_resource
from odoo.exceptions import Warning
from datetime import datetime, date

import logging
logger = logging.getLogger(__name__)


class BM_Official(models.Model):
    _name = "bm.official"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Tabla de funcionarios"

    _ACCOUNT_STATUS = [
        ('0', 'Cuenta Activa'),
        ('4', 'Cuenta Inactiva'),
        ('71', 'Bloqueo de Saldo Permanente'),
        ('74', 'WK Pendiente de Entrega'),
        ('75', 'Variación de firma'),
        ('76', 'Falta firma formulario'),
        ('77', 'Cedula ilegible'),
        ('99', 'Cuenta Cancelada'),
        ('999', 'Sin información')]

    # region _DEFAULT_
    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'hcs_bm_sudameris', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    @api.model
    def _default_country(self):
        return self.env['res.country'].search([('code_number', '=', '586')], limit=1).id

    @api.model
    def _domain_country(self):
        return [('country_id', '=', self.env.ref('base.py').id)]
    # endregion

    # region COMPUTE
    @api.depends('job_id')
    def _compute_job_title(self):
        for official in self.filtered('job_id'):
            official.job_title = official.job_id.name

    @api.depends('department_id')
    def _compute_parent_id(self):
        for official in self.filtered('department_id.manager_id'):
            official.parent_id = official.department_id.manager_id

    @api.depends('parent_id')
    def _compute_coach(self):
        for official in self:
            manager = official.parent_id
            previous_manager = official._origin.parent_id
            if manager and (official.coach_id == previous_manager or not official.coach_id):
                official.coach_id = manager
            elif not official.coach_id:
                official.coach_id = False

    @api.depends('name')
    @api.onchange('name_first', 'name_second', 'surname_first', 'surname_second')
    def _compute_name(self):
        for official in self:
            _nombre = official.name_first or ''
            if (official.name_second):
                _nombre = "{} {}".format(
                    official.name_first, official.name_second)
            _apellido = official.surname_first or ''
            if (official.surname_second):
                _apellido = "{} {}".format(
                    official.surname_first, official.surname_second)
            official.name = '{} {}'.format(_nombre.upper(), _apellido.upper())
            # Compruebo la sucursal del funcionario
            for account in official.company_id.account_ids:
                if account.currency_type == official.currency_type:
                    # seteo la sucursal
                    if not official.branch_id:
                        official.branch_id = account.branch_id
                    if not official.account_module:
                        official.account_module = account.module


    @api.depends('departured')
    def _compute_departured(self):
        for official in self:
            official_departured = self.env['bm.official.departure'].search(
                ['&', ('official', '=', official.id), ('state', '=', 'active')], order='id desc', limit=1)
            official.departured = official_departured
            if official_departured['departure_reason'] == 'medical':
                official.departure_medical = True

    @api.depends('company_code_imp')
    def _inverse_company_code(self):
        for official in self:
            official.company_id = self.env['res.company'].sudo().search([('company_code', '=', official.company_code_imp)])

    @api.depends('welcome_kit', 'gross_salary')
    def _compute_welcome_kit(self):
        # Se computa solo si está en borrador
        # Solo si el funcionario no está listo, obtengo los kits y le asigno el kit minimo
        if self.state in ['draft']:
            # Remuevo el Kit y le asigno el correspondiente
            self.welcome_kit = None
            for kit in self.env['bm.product'].search([('product_type', '=', 'kit')], order='minimum_salary desc'):
                if self.gross_salary >= kit.minimum_salary:
                    self.welcome_kit = [(4, kit.id)]
                    break
            # Asigno la segmentacion segun documentacion
            if self.gross_salary > 0 and self.gross_salary < 5000000:
                self.segmentation = 'sudameris'
            elif self.gross_salary >= 5000000 and self.gross_salary < 35000000:
                self.segmentation = 'sudameris_plus'
            elif self.gross_salary >= 35000000:
                self.segmentation = 'sudameris_elite'
            else:
                self.segmentation = None
        # elif self.state in ['check']:  # Solo si el funcionario no está listo, obtengo los kits y le asigno el kit minimo
        #    if not (self._origin.segmentation == self.segmentation):
        #        self.segmentation_check = True

    @api.constrains('reference', 'gross_salary', 'work_phone', 'mobile_phone')
    def constrains_fields(self):
        for record in self:
            # Contrains campo referencia
            if (record.reference):
                if len(record.reference) < 50 or len(record.reference) > 100:
                    raise Warning(
                        'El campo Referencia debe tener entre 50 y 100 caracteres')
            # Contrains campo salario bruto
            if (not record.gross_salary):
                # if int(record.gross_salary.split(',')[0]) <= 0:
                raise Warning('El campo Salario bruto debe ser mayor a 0')
            # Constrains campo work_phone
            if (record.work_phone):
                # if not re.match('^[0-9]\d{10}$', record.work_phone):
                if not re.match('^[0-9]*$', record.work_phone):
                    raise Warning(
                        'El campo Teléfono Laboral no tiene un formato valido')
            # Constrains campo mobile_phone
            if (record.mobile_phone):
                if not re.match('^[0-9]*$', record.mobile_phone):
                    raise Warning(
                        'El campo Teléfono Celular no tiene un formato valido')

    # endregion

    # region FIELDS
    name = fields.Char(
        string="Nombre", compute="_compute_name", required=False)
    name_first = fields.Char(string="Primer Nombre", required=True)
    name_second = fields.Char(string="Segundo Nombre")
    surname_first = fields.Char(string="Primer Apellido", required=True)
    surname_second = fields.Char(string="Segundo Apellido")
    gender = fields.Selection([
        ('M', 'Masculino'),
        ('F', 'Femenino')
    ], "Sexo", default="M", tracking=True)
    marital = fields.Selection([
        ('S', 'Soltero(a)'),
        ('C', 'Casado(a)'),
        ('L', 'Cohabitante Legal'),
        ('V', 'Viudo(a)'),
        ('D', 'Divorciado(a)')
    ], string='Estado Civil', default='S', tracking=True)
    identification_id = fields.Char(
        string='Cédula de identidad', tracking=True)
    identification_type = fields.Selection([
        ('1', 'CEDULA DE IDENTIDAD'),
        ('2', 'CREDENCIAL CIVICA'),
        ('3', 'R.U.C.'),
        ('4', 'PASAPORTE'),
        ('5', 'DNI-DOC.NAC.IDENTID.'),
        ('6', 'REGISTRO DE COMERCIO'),
        ('7', 'LIB.DE ENROLAMIENTO'),
        ('10', 'GARANTIA'),
        ('15', 'Entidades Públicas'),
        ('16', 'CARNET-INMIGRACIONES'),
        ('98', 'No Registra'),
        ('99', 'Inst. Financieras'),
        ('20', 'REPRES.DIPLOMATICAS')], string="Tipo de Cédula", digits=(2), default="1")
    identification_expiry = fields.Date(
        string="Vencimiento de Cédula", required=True)
    country = fields.Many2one('res.country', 'Nacionalidad (País)',
                              default=_default_country, required=True, tracking=True)
    city = fields.Many2one('res.country.state', 'Departamento',
                           domain=_domain_country, required=True)
    # domain="[('state_id', '=?', city)]",
    location = fields.Many2one(
        'res.country.location', 'Localidad', required=True)
    # , domain="[('location_id', '=?', location)]"
    neighborhood = fields.Many2one(
        'res.country.neighborhood', 'Barrio', required=True)
    real_address = fields.Char(string="Dirección", digits=(50), required=True)
    house_no = fields.Char(string="Nro. Casa", digits=(3),
                           required=True, default="0")
    street_transversal = fields.Char(string="Calle Transversal", digits=(35))
    reference = fields.Char(string="Referencia")
    address_code = fields.Integer(default=1, digits=(3))
    birthday = fields.Date('Fecha de nacimiento', tracking=True, required=True)
    country_of_birth = fields.Many2one(
        'res.country', 'País de Nacimiento', required=True, tracking=True)
    place_of_birth = fields.Many2one(
        'res.country.state', 'Lugar de nacimiento', domain="[('country_id', '=?', country_of_birth)]", required=True, tracking=True)

    email = fields.Char('E-mail')
    work_phone = fields.Char('Teléfono Laboral', required=True)
    particular_phone = fields.Char('Teléfono particular')
    mobile_phone = fields.Char('Teléfono celular', required=True)
    idenfitication_image_front = fields.Binary(
        string="Cédula de Identidad (Frente)", max_width=100, max_height=100)
    idenfitication_image_back = fields.Binary(
        string="Cédula de Identidad (Dorso)", max_width=100, max_height=100)
    idenfitication_image_pdf = fields.Binary(
        string="Cédula de Identidad (PDF)")
    idenfitication_image_pdf_name = fields.Char()
    authorization_image_pdf = fields.Binary(
        string="Autorización Extranjero (PDF)")
    authorization_image_pdf_name = fields.Char()

    image_1920 = fields.Image(default=_default_image)

    contract_type = fields.Selection([
        ('I', 'Contrato Por Tiempo Indefinido'),
        ('D', 'Contrato Por Tiempo Definido')], string="Tipo de Contrato", required=True, digits=(1), default="D")
    currency_type = fields.Selection([
        ('6900', 'Guaraníes'),
        ('1', 'Dólares Americanos')], string="Tipo de moneda", default="6900")
    gross_salary = fields.Float(
        string="Salario Bruto", digits=(18, 2), required=True)
    group_type = fields.Selection([
        ('90', 'Payroll'),
        ('94', 'Proveedores')], string="Tipo de Grupo", digits=(3), default="90")
    executive = fields.Integer(string="Ejecutivo", default="730")
    admission_date = fields.Date(string="Fecha de ingreso", required=True)
    contract_end_date = fields.Date(string="Fecha de fin de contrato")
    branch_id = fields.Many2one('bm.branch', 'Sucursal del Funcionario')
    account_registration = fields.Date(string="Fecha de Alta de cuenta")
    account_number = fields.Char(string="Número de la Cuenta", digits=(9))
    account_name = fields.Char(string="Descripción de la Cuenta", digits=(30))
    account_status = fields.Selection(
        _ACCOUNT_STATUS, string="Estado de la Cuenta")
    account_module = fields.Char("Modulo")
    segmentation_aproved = fields.Boolean("Aprobar segmento")
    segmentation = fields.Selection([
        ('sudameris', 'SUDAMERIS'),
        ('sudameris_plus', 'SUDAMERIS PLUS'),
        ('sudameris_elite', 'SUDAMERIS ELITE')], size=1, string="Recomendación Segmentación")
    segmentation_check = fields.Boolean(
        "Verificar recomendación", default=False)
    cam_check = fields.Boolean(default=False)
    reject_reason = fields.Text('Motivo de rechazo')
    sub_segmentation = fields.Selection([
        ('S', 'Crear'),
        ('N', 'No crear')], string="Sub segmentación", digits=(1), default="N")
    welcome_kit = fields.Many2many('bm.product', 'official_welcome_kit_rel', 'official_id',
                                   string='Welcome Kit', compute='_compute_welcome_kit', store=True)
    refer_cam_date = fields.Char(string="Fecha de Movimiento")

    notes = fields.Text('Notas')
    color = fields.Integer('Color Index', default=0)
    #pin = fields.Char(string="PIN", copy=False, help="PIN used to Check In/Out in Kiosk Mode (if enabled in Configuration).")
    company_id = fields.Many2one(
        'res.company', 'Nombre de la empresa', required=True, default=lambda self: self.env.company)

    company_code_imp = fields.Integer("Cod Empresa", inverse="_inverse_company_code", store=True)
    company_code = fields.Char("Código de Empresa", related='company_id.company_code', readonly=True)
    department_id = fields.Many2one('bm.department', 'Departamento de la empresa',
                                    domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    job_id = fields.Many2one(
        'bm.job', 'Cargo', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    job_title = fields.Char(
        "Titulo del trabajo", compute="_compute_job_title", store=True, readonly=False)
    parent_id = fields.Many2one('bm.official', 'Gerente', compute="_compute_parent_id", store=True, readonly=False,
                                domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    coach_id = fields.Many2one('bm.official', 'Supervisor', compute='_compute_coach', store=True, readonly=False,
                               domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                               help='Seleccione el "funcionario" que es el supervisor de este funcionario.\n'
                               'El "Supervisor" no tiene derechos o responsabilidades específicos por defecto.')
    km_home_work = fields.Integer(
        string="Km Trabajo desde casa", tracking=True)

    # officials in company
    child_ids = fields.One2many(
        'bm.official', 'parent_id', string='Direct subordinates')
    category_ids = fields.Many2many(
        'bm.official.category', 'official_category_rel', 'official_id', 'category_id', string='Etiquetas')
    active = fields.Boolean("Active", default=True)
    unlinked = fields.Boolean("Desvinculado", default=False)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('error', 'Revisar'),
        ('check_payroll', 'En proceso de alta'),
        ('check_cam', 'En proceso de alta'),
        ('check_cpe', 'En proceso de alta'),
        ('pending', 'Pendiente a Confirmar'),
        ('departured', 'Licencia'),
        ('ready', 'Listo')],
        string="Estado", default='draft')
    reliable_base = fields.Boolean(
        string="Validación", default=False, readonly=True)
    departured = fields.Many2one(
        'bm.official.departure', 'Licencia', compute="_compute_departured")
    departure_medical = fields.Boolean(string='Licencia Medica', default=False)

    _sql_constraints = [
        ('identification_id_company_uniq', 'unique(identification_id,company_id)',
         'Ya existe otro funcionario con la misma cédula de identidad'),
        ('account_number_company_id_uniq', 'unique(account_number,company_id)',
         'Ya existe otro funcionario con el mismo número de cuenta'),
        ('mobile_phone_company_uniq', 'unique(mobile_phone,company_id)',
         'Ya existe otro funcionario con el mismo número de telefono celular'),
        ('email_company_uniq', 'unique(email,company_id)',
         'Ya existe otro funcionario con el mismo E-Mail'),
        ('real_address_house_no_company_uniq', 'unique(real_address,house_no,company_id)',
         'Ya existe otro funcionario con la misma dirección'),
    ]
    # endregion

    # region OVERRIDES
    def write(self, vals):
        res = super(BM_Official, self).write(vals)
        # Primer horario: 8:30
        time_first = datetime.now().replace(hour=8, minute=30, second=0, microsecond=0)
        # Segundo horario: 16:00
        time_last = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)
        # Si se realizaron cambios fuera de los horarios estipulados, se notifican
        if datetime.now() < time_first or datetime.now() > time_last:
            print('Se realizaron cambios fuera de horario')
            #self.notify_to_channel('bm_mail_channel_group_bm_bank_payroll', 'Cambios fuera de horario', 'Se realizaron cambios fuera de horario: {}'.format(vals))
            # if self.segmentation_aproved and not self.state == 'check_cam':
            #    self.state = 'check_cam'
        # Motivo de rechazo
        # if not self.reject_reason:
        #    if self.account_status in ['75', '76', '77']:
        #        # Guardo el texto del selection
        #        self.reject_reason = dict(self._fields['account_status'].selection).get(self.account_status)
        #    else:
        #        self.reject_reason = None
        return res
    # endregion

    # region POPUPS
    def show_message(self, title, message, *args):
        return {
            'name': title,
            'type': 'ir.actions.act_window',
            'res_model': 'bm.official.wizard',
            'view_mode': 'form',
            'context': {'default_message': message},
            'target': 'new'
        }

    def notify_to_channel(self, _channel, _subject, _message):
        channel_obj = self.env.ref('hcs_bm_sudameris.{}'.format(_channel))
        if channel_obj:
            self.env['mail.message'].sudo().create({
                'email_from': '"Sudameris BOT" <info@sudameris.com.py>',  # Email
                # Odoo bot ID
                'author_id': self.env['res.users'].search(['&', ('active', '=', False), ('id', '=', 1)]).id,
                'model': 'mail.channel',
                'subject': _subject,
                'message_type': 'comment',
                'subtype_id': self.env.ref('mail.mt_comment').id,
                'body': _message,
                # This is the channel where you want to send the message and all the users of this channel will receive message
                'channel_ids': [(4, channel_obj.id)],
                'res_id': channel_obj.id,  # here add the channel you created.
            })

    def notify_to_users(self, _company, _subject, _message):
        # Obtengo a todos los usuarios
        users = self.env['res.users'].search([('company_ids', 'in', _company)])
        bot = self.env['res.users'].search(['&', ('active', '=', False), ('id', '=', 1)])
        channel_obj = self.env['mail.channel'].sudo()
        if users.ids:
            for user in users:
                channel_name = '%s, %s' % (bot.name, user.name)
                channel_id = channel_obj.search([('name', 'like', channel_name)])
                # Si no existe el canal, lo creo
                if not channel_id:
                    channel_id = channel_obj.create({
                        'name': channel_name,
                        'email_send': False,
                        'channel_type': 'chat',
                        'public': 'private'
                    })
                    # Reescribo los usuarios subscriptos y agrego solo al bot y al usuario
                    channel_id.channel_partner_ids = [(6, 0, [bot.partner_id.id, user.partner_id.id])]
                    #(0, 0, {'partner_id': bot.partner_id.id})
                channel_id.message_post(
                    subject=_subject,
                    body=_message,
                    message_type='comment',
                    subtype='mail.mt_comment',
                )
    # endregion

    # region ONCHANGE
    def onchange_warning(self, title, message):
        return {
            'warning': {
                'title': title,
                'message': message,
            },
        }

    @api.onchange('segmentation', 'welcome_kit')
    def _on_change_segmentation_welcome_kit(self):
        if (self.state in ['check_payroll']):
            products = {
                'origin': [],
                'new': []
            }
            for product in self._origin.welcome_kit:
                products['origin'].append(product.id)
            for product in self.welcome_kit:
                products['new'].append(product.id.origin)
            self._origin.segmentation_check = self.segmentation_check = (
                products['origin'] != products['new'] or self._origin.segmentation != self.segmentation)

    @api.onchange('identification_id')
    def _on_change_identification_id(self):
        if (self.identification_id):
            for official in self.env['bm.official'].search([('identification_id', '=', self.identification_id)]):
                self.identification_id = self._origin.identification_id
                return self.onchange_warning('Número de identificación del funcionario', 'El funcionario {} ya posee este Número de Identificación.'.format(official.name))

    @api.onchange('city')
    def _on_change_city(self):
        self.location = None

    @api.onchange('location')
    def _on_change_location(self):
        self.neighborhood = None

    @api.onchange('identification_expiry')
    def _on_change_identification_expiry(self):
        if self.identification_expiry:
            if date.today() > self.identification_expiry:
                return self.onchange_warning('Vencimiento de identificación', 'El documento se encuentra vencido')

    @api.onchange('birthday')
    def _on_change_birthday(self):
        if self.birthday:
            if self.birthday < date(1900, 5, 10):
                self.birthday = None
                return self.onchange_warning('Fecha de nacimiento', 'La fecha de nacimiento debe ser mayór')

    @api.onchange('admission_date')
    def _on_change_admission_date(self):
        if self.admission_date:
            if self.admission_date < date(1900, 5, 10):
                self.admission_date = self._origin.admission_date
                return self.onchange_warning('Fecha de ingreso', 'La fecha de ingreso debe ser mayor')
            if self.admission_date > date.today():
                self.admission_date = self._origin.admission_date
                return self.onchange_warning('Fecha de ingreso', 'La fecha de ingreso no puede ser posterior a la fecha actual')

    @api.onchange('contract_end_date')
    def _on_change_contract_end_date(self):
        if self.contract_end_date:
            if self.contract_end_date < date(1900, 5, 10):
                self.contract_end_date = None
                return self.onchange_warning('Fecha de fin de contrato', 'La fecha fin de contrato debe ser mayór')
    # endregion

    # region ACTIONS API
    def action_verificar_cuenta(self):
        """
        # Action: Verificar Cuenta
        # - Verifica Base Confiable | Desactivo porque no se requiere para verificar cuenta
        - Cliente Posee Cuenta
        - Estado de Caja de Ahorro

        # Observaciones
        - official: Si paso el parametro, va a verificar solo el funcionario que le pasé
        """
        result = {
            'message': '',
            #'vbc': {
            #    'ok': [],
            #    'pass': [],
            #    'error': []
            #},
            'cpc': {
                'ok': [],
                'pass': [],
                'error': []
            },
            'eca': {
                'ok': [],
                'pass': [],
                'error': []
            }
        }

        # Verifico cada funcionario seleccionado o self = funcionario seleccionado
        for official in self.env['bm.official'].browse(self._context.get('active_ids')) or self:
            # Valida Base Confiable
            #vbc_result = self.ws_valida_base_confiable(official)
            #if vbc_result['ok']:
            #    result['vbc']['ok'].append(official.name)
            #elif vbc_result['pass']:
            #    result['vbc']['pass'].append(official.name)
            #elif vbc_result['error']:
            #    result['vbc']['error'].append('{}: {}'.format(official.name, vbc_result['message']))

            # Cliente Posee Cuenta
            cpc_result = self.ws_cliente_posee_cuenta(official)
            if cpc_result['ok']:
                result['cpc']['ok'].append(official.name)
            elif cpc_result['pass']:
                result['cpc']['pass'].append(official.name)
            elif cpc_result['error']:
                result['cpc']['error'].append('{}: {}'.format(official.name, cpc_result['message']))

            # Estado de Caja de Ahorro
            if cpc_result['ok'] or cpc_result['pass']:
                eca_result = self.ws_estado_ca(official)
                if eca_result['ok']:
                    result['eca']['ok'].append(official.name)
                elif eca_result['pass']:
                    result['eca']['pass'].append(official.name)
                elif eca_result['error']:
                    result['eca']['error'].append('{}: {}'.format(official.name, eca_result['message']))

        #result['message'] = 'Se validaron {} funcionarios\n'.format(len(result['vbc']['ok']))
        result['message'] = 'Se obtuvo la cuenta de {} funcionarios\n'.format(len(result['cpc']['ok']))
        result['message'] += 'Se actualizaron {} estados de Cuentas\n'.format(len(result['eca']['ok']))


        #if len(result['vbc']['pass']) > 0:
        #    result['message'] += 'Funcionarios no encontrados:\n{}\n\n'.format(
        #        '\n'.join(result['vbc']['pass']))
        if len(result['cpc']['pass']) > 0:
            result['message'] += 'Ya poseia Cuenta:\n{}\n\n'.format(
                '\n'.join(result['cpc']['pass']))

        #if len(result['vbc']['error']) > 0:
        #    result['message'] += 'Errores al validar:\n{}\n\n'.format(
        #        '\n'.join(result['vbc']['error']))
        if len(result['cpc']['error']) > 0:
            result['message'] += 'Errores al obtener la Cuenta:\n{}\n\n'.format(
                '\n'.join(result['cpc']['error']))
        if len(result['eca']['error']) > 0:
            result['message'] += 'Errores al obtener el estado de Cuenta:\n{}\n\n'.format(
                '\n'.join(result['eca']['error']))

        return self.show_message('Verificar cuenta', result['message'])

    def action_create_account(self):
        """
        # Action: Crear Cuenta
        - Alta de Cuenta
        - Alta de Caja de Ahorro
        - Alta de Tarjeta Débito (VISA-MASTERCARD)
        - Estado de CA
        """
        result = {
            'message': '',
            'ac': {
                'ok': [],
                'pass': [],
                'error': []
            },
            'aca': {
                'ok': [],
                'pass': [],
                'error': []
            },
            'eca': {
                'ok': [],
                'pass': [],
                'error': []
            },
            'atd': {
                'ok': [],
                'error': []
            }
        }
        # Verifico cada funcionario seleccionado
        for official in self.env['bm.official'].browse(self._context.get('active_ids')) or self:
            # Alta de cuenta
            ac_result = self.ws_alta_cuenta(official)
            if ac_result['ok']:
                result['ac']['ok'].append(official.name)
            elif ac_result['pass']:
                result['ac']['pass'].append(official.name)
            elif ac_result['error']:
                result['ac']['error'].append('{}: {}'.format(official.name, ac_result['message']))

            # Alta de Caja de Ahorro
            if ac_result['ok'] or ac_result['pass']:
                aca_result = self.ws_alta_ca(official)
                if aca_result['ok']:
                    result['aca']['ok'].append(official.name)
                elif aca_result['pass']:
                    result['aca']['pass'].append(official.name)
                elif aca_result['error']:
                    result['aca']['error'].append('{}: {}'.format(official.name, ac_result['message']))

                # Estado de Caja de Ahorro
                if aca_result['ok'] or aca_result['pass']:
                    eca_result = self.ws_estado_ca(official)
                    if eca_result['ok']:
                        result['eca']['ok'].append(official.name)
                    elif eca_result['pass']:
                        result['eca']['pass'].append(official.name)
                    elif eca_result['error']:
                        result['eca']['error'].append('{}: {}'.format(official.name, eca_result['message']))

                # Alta de Tarjeta de Débito
                if ac_result['ok'] or ac_result['pass'] and aca_result['ok'] or aca_result['pass']:
                    atd_result = self.ws_alta_td(official)
                    if atd_result['ok']:
                        result['atd']['ok'].append(official.name)
                    elif atd_result['error']:
                        result['atd']['error'].append('{}: {}'.format(official.name, atd_result['message']))


        result['message'] = 'Se crearon {} Cuentas\n'.format(len(result['ac']['ok']))
        result['message'] += 'Se crearon {} Cajas de Ahorro\n'.format(len(result['aca']['ok']))
        result['message'] += 'Se actualizaron {} estados de Cuentas\n'.format(len(result['eca']['ok']))
        result['message'] += 'Se crearon {} Tarjetas de Débito\n\n'.format(len(result['atd']['ok']))

        if len(result['ac']['pass']) > 0:
            result['message'] += 'Ya poseia Cuenta:\n{}\n\n'.format(
                '\n'.join(result['ac']['pass']))
        if len(result['ac']['pass']) > 0:
            result['message'] += 'Ya poseia Caja de Ahorro:\n{}\n\n'.format(
                '\n'.join(result['aca']['pass']))

        if len(result['ac']['error']) > 0:
            result['message'] += 'Errores al crear Cuenta:\n{}\n\n'.format(
                '\n'.join(result['ac']['error']))
        if len(result['ac']['error']) > 0:
            result['message'] += 'Errores al crear Caja de Ahorro:\n{}\n\n'.format(
                '\n'.join(result['aca']['error']))
        if len(result['eca']['error']) > 0:
            result['message'] += 'Errores al obtener el estado de Cuenta:\n{}\n\n'.format(
                '\n'.join(result['eca']['error']))
        if len(result['atd']['error']) > 0:
            result['message'] += 'Errores al crear Tarjeta de Débito:\n{}\n\n'.format(
                '\n'.join(result['atd']['error']))

        return self.show_message('Alta de cuentas', result['message'])
    # endregion

    # region ACTIONS
    def action_refer_cp(self):
        """# Action: Remitir al banco (Centro Payroll)
        Accion relacionada: action_verificar_cuenta
        """
        result = {
            'message': '',
            'count_ok': 0,
            'errors': {
                'not_id': [],
                'gross_salary': [],
                'has_account': []
            },
            'vbc': None
        }

        for official in self.env['bm.official'].browse(self._context.get('active_ids')) or self:

            # Chequeo si tiene cuenta
            # if official.reliable_base and official.account_number:
            if official.account_number:
                result['errors']['has_account'].append(
                    '{}'.format(official.name))

            # Solo verifico los funcionarios que esten en borrador o en error
            if official.state in ['check_payroll', 'check_cam', 'check_cpe', 'pending', 'departured', 'ready']:
                continue

            # Tiene que tener el documento cargado en imagen o pdf
            if not ((official.idenfitication_image_front and official.idenfitication_image_back) or official.idenfitication_image_pdf):
                result['errors']['not_id'].append('{}'.format(official.name))
                continue

            # Tiene que tener el salario asignado
            if not (official.gross_salary > 0):
                result['errors']['gross_salary'].append(
                    '{}'.format(official.name))
                continue

            # Si está en borrador, pasa a estar en proceso de alta (Centro Payroll)
            account_result = None
            if official.state in ['draft']:
                # Verifico la cuenta del funcionario
                account_result = self.action_verificar_cuenta()
                official.state = 'check_payroll'

            # Si está en 'Revisar', se envía al CAM (es porque se rechazo el alta)
            if official.state in ['error']:
                official.state = 'check_cam'

            if official.state in ['check_payroll', 'check_cam']:
                if not official.refer_cam_date : official.refer_cam_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                result['count_ok'] += 1

        result['message'] = 'Se remitieron {} funcionarios\n'.format(
            result['count_ok'])
        # Si obtengo info de la cuenta, la muestro
        if account_result:
            result['message'] += '{}\n'.format(
                account_result['context']['default_message'])

        if len(result['errors']['not_id']) > 0:
            result['message'] += 'NO poseen "Cédula de identidad":\n{}\n\n'.format(
                '\n'.join(result['errors']['not_id']))

        if len(result['errors']['gross_salary']) > 0:
            result['message'] += 'NO poseen "Salario Bruto" asignado:\n{}\n\n'.format(
                '\n'.join(result['errors']['gross_salary']))

        if len(result['errors']['has_account']) > 0:
            result['message'] += 'Ya poseen numero de cuenta:\n{}\n\n'.format(
                '\n'.join(result['errors']['has_account']))

        if result['count_ok'] > 0:
            # Notifica a los usuarios de Centro Payroll que tiene altas
            self.notify_to_channel('bm_mail_channel_group_bm_bank_payroll',
                                   'Funcionarios a aprobar',
                                   'Tiene {} nuevas solicitudes de {} para alta de cuentas.'.format(
                                       result['count_ok'], self.env.company.name))

        return self.show_message('Remitir al Banco', result['message'])

    def action_create_officials_salary(self):
        """# Action: Crear movimiento de salario"""
        result = {
            'message': '',
            'count_ok': 0,
            'errors': {
                'not_ready': [],
                'gross_salary': [],
                'not_account': [],
                'account_status': [],
                'has_payment': [],
                'has_departured': []
            }
        }

        officials_salary = self.env['bm.official.salary'].sudo()

        for official in self.env['bm.official'].browse(self._context.get('active_ids')) or self:
            # Si el funcionario NO está listo,
            # con salario asignado, validado
            # con cuenta y con estado de cuenta diferente a 74 (PACON).
            # lo ignoro
            if not official.state in ['ready']:
                result['errors']['not_ready'].append(
                    '{}'.format(official.name))
                continue
            if not official.gross_salary > 0:
                result['errors']['gross_salary'].append(
                    '{}'.format(official.name))
                continue
            # if not official.reliable_base:
            #    continue
            if not official.account_number:
                result['errors']['not_account'].append(
                    '{}'.format(official.name))
                continue
            if official.account_status in ['74']:
                result['errors']['account_status'].append(
                    '{}'.format(official.name))
                continue

            # Obtengo el ultimo movimiento de salario
            for official_salary in officials_salary.search([('official.id', '=', official.id)], order='id desc', limit=1):
                # Verifico que el funcionario no tenga registros en los 35 días
                diference_days = (datetime.now().date()
                                  - official_salary.payment_date).days
                if diference_days <= 35:
                    result['errors']['has_payment'].append(
                        '{}'.format(official.name))
                if diference_days > 35 and official.departured:
                    result['errors']['has_departured'].append(
                        '{}'.format(official.name))
                    #official.account_status = '71'

            officials_salary.create({
                'official': official.id,
            })
            result['count_ok'] += 1

        # Crear movimientos de salarios
        result['message'] = 'Se crearon {} movimientos de salarios\n\n'.format(
            result['count_ok'])

        if len(result['errors']['not_ready']) > 0:
            result['message'] += 'No están listos:\n{}\n\n'.format(
                '\n'.join(result['errors']['not_ready']))

        if len(result['errors']['gross_salary']) > 0:
            result['message'] += 'Error de Salario:\n{}\n\n'.format(
                '\n'.join(result['errors']['gross_salary']))

        if len(result['errors']['not_account']) > 0:
            result['message'] += 'No posee cuenta:\n{}\n\n'.format(
                '\n'.join(result['errors']['not_account']))

        if len(result['errors']['account_status']) > 0:
            result['message'] += 'En proceso de apertura de cuenta:\n{}\n\n'.format(
                '\n'.join(result['errors']['account_status']))

        if len(result['errors']['has_payment']) > 0:
            result['message'] += 'Ya poseen registros en los ultimos 35 dias:\n{}\n\n'.format(
                '\n'.join(result['errors']['has_payment']))

        if len(result['errors']['has_departured']) > 0:
            result['message'] += 'Licencia mayor a 35 dias:\n{}\n\n'.format(
                '\n'.join(result['errors']['has_departured']))

        return self.show_message('Movimiento de salarios', result['message'])

    def action_refer_cam(self):
        """# Action: Remitir al banco (Centro de Altas Masivas)"""
        result = {
            'message': '',
            'count_ok': 0,
            'errors': {
                'not_ready': [],
                'not_id_auth': [],
                'not_segmentation_aproved': []
            }
        }

        for official in self.env['bm.official'].browse(self._context.get('active_ids')) or self:
            if official.state in ['check_payroll']:
                # Es extranjero o cobra en moneda extranjera y no tiene autorización
                _country_py_id = self.env['res.country'].search([('id', '=', self.env.ref('base.py').id)])
                if official.country != _country_py_id or official.currency_type != '6900':
                    if not official.authorization_image_pdf:
                        result['errors']['not_id_auth'].append('{}'.format(official.name))
                        continue

                if official.segmentation_check and not official.segmentation_aproved:
                    result['errors']['not_segmentation_aproved'].append(
                        '{}'.format(official.name))
                else:
                    official.segmentation_aproved = True
                    official.state = 'check_cam'
                    result['count_ok'] += 1
            else:
                result['errors']['not_ready'].append(
                    '{}'.format(official.name))

        # Remitir al banco (Centro de Altas Masivas)
        result['message'] = 'Se remitieron {} funcionarios\n\n'.format(
            result['count_ok'])

        if len(result['errors']['not_segmentation_aproved']) > 0:
            result['message'] += 'Esperan aprobación de segmentación:\n{}\n\n'.format(
                '\n'.join(result['errors']['not_segmentation_aproved']))

        if len(result['errors']['not_id_auth']) > 0:
            result['message'] += 'NO poseen "Autorización Extranjero (PDF)":\n{}\n\n'.format(
                '\n'.join(result['errors']['not_id_auth']))

        if len(result['errors']['not_ready']) > 0:
            result['message'] += 'No están en proceso de alta o ya se encuentra remitidos al CAM:\n{}\n\n'.format(
                '\n'.join(result['errors']['not_ready']))

        return self.show_message('Remitir al CAM', result['message'])

    def action_aprove(self):
        """# Action: Aprobar funcionario"""
        result = {
            'message': '',
            'count_ok': 0,
            'errors': {
                'reject_reason': [],
                'not_valid': []
            }
        }
        for official in self.env['bm.official'].browse(self._context.get('active_ids')) or self:
            if official.state in ['check_cam', 'pending']:
                # Actualizo los datos de la cuenta
                self.action_verificar_cuenta()

                # Desactivo la opcion reliable_base porque no se necesita para verificar
                # Si no tiene la cuenta activa
                if official.account_status:
                    if official.account_status not in ['0']:
                        # Si tiene cuenta en estado WK Pendiente de entrega
                        if official.account_status in ['74']:
                            official.state = 'check_cpe'
                            if official.reject_reason and official.reject_reason != 'Pendiente de Activación':
                                # Agrego Pendiente de activación si viaja a payroll entregas
                                official.reject_reason = 'Pendiente de Activación: ' + official.reject_reason
                            else:
                                official.reject_reason = 'Pendiente de Activación'
                        else:
                            official.state = 'pending'

                        official.reject_reason = dict(
                            official._fields['account_status'].selection).get(official.account_status)
                        result['errors']['reject_reason'].append(
                            '{}: {}'.format(official.name, official.reject_reason))
                    else:
                        official.state = 'ready'
                        official.reject_reason = None
                        result['count_ok'] += 1
                else:
                    result['errors']['reject_reason'].append(
                        '{}: {}'.format(official.name, 'Pendiente de Activación: Sin cuenta'))

                # if official.reliable_base:
                #    Lo anterior
                # else:
                #    official.state = 'pending'
                #    result['errors']['not_valid'].append(official.name)
                #    #official.reject_reason = 'Persona No Encontrada.'
                #    #official.reject_reason = dict(official._fields['account_status'].selection).get(official.account_status)
                #    # return self.show_message('Aprobar', 'Falta información bancaria, ')

        # Crear movimientos de salarios
        result['message'] = 'Se aprobaron {} funcionarios\n\n'.format(
            result['count_ok'])

        if len(result['errors']['reject_reason']) > 0:
            result['message'] += 'No se aprobaron:\n{}\n\n'.format(
                '\n'.join(result['errors']['reject_reason']))

        if len(result['errors']['not_valid']) > 0:
            result['message'] += 'No se validaron todavia:\n{}\n\n'.format(
                '\n'.join(result['errors']['not_valid']))

        return self.show_message('Aprobar', result['message'])

    def action_departure_report(self, sac='1'):
        # Obtengo solo los ID de los que están en proceso y si hay alguno, genero el archivo de pago
        officials = self.search(['&', '&', ('id', 'in', self._context.get('active_ids')), ('state', 'in', ['departured']), ('departure_medical', '=', False)]) or self.search(['&', ('state', 'in', ['departured']), ('departure_medical', '=', False)])
        if officials:
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/binary_file/create_departure_report?ids={}'.format(','.join([str(_id) for _id in officials.ids])),
                'target': 'self'
            }
        else:
            return self.show_message('Informe de desvinculados', 'No se encontraron desvinculados.')

    def action_account_report(self):
        _ids = self.search(['&', ('id', 'in', self._context.get(
            'active_ids')), ('account_registration', '!=', None)]).ids
        if _ids:
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/binary_file/create_account_report/{}'.format(','.join([str(_id) for _id in _ids])),
                'target': 'self'
            }
        else:
            return self.show_message('Informe de Altas', 'No se encontraron altas, verifique los filtros')
    # endregion

    # region TEM_PACTIONS
    def action_reset(self):
        for official in self.env['bm.official'].browse(self._context.get('active_ids')) or self:
            official.account_number = None
            official.account_name = None
            official.account_status = None
            official.branch_id = None
            official.reliable_base = False
            official.segmentation_aproved = False
            official.segmentation_check = False
            official.unlinked = False
            official.refer_cam_date = False
            official.state = 'draft'
            official.reject_reason = ''
    # endregion
