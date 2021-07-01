# -*- coding: utf-8 -*-
import base64
from odoo import fields, models, api, _
from odoo.modules.module import get_module_resource
from datetime import datetime, date
from odoo.exceptions import ValidationError

#import logging
#_logger = logging.getLogger(__name__)


class BM_Official(models.Model):
    _name = "bm.official"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Tabla de funcionarios"

    @api.model
    def _default_image(self):
        image_path = get_module_resource('hcs_bm', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    # Basic info
    name = fields.Char(string="Nombre", compute="_on_change_name", required=False)
    name_first = fields.Char(string="Primer Nombre", required=True)
    name_second = fields.Char(string="Segundo Nombre")
    surname_first = fields.Char(string="Primer Apellido", required=True)
    surname_second = fields.Char(string="Segundo Apellido")
    gender = fields.Selection([
        ('male', 'Hombre'),
        ('female', 'Mujer'),
        ('other', 'Otro')
    ], "Sexo", default="male", tracking=True)
    marital = fields.Selection([
        ('single', 'Soltero(a)'),
        ('married', 'Casado(a)'),
        ('cohabitant', 'Cohabitante Legal'),
        ('widower', 'Viudo(a)'),
        ('divorced', 'Divorciado(a)')
    ], string='Estado Civil', default='single', tracking=True)
    identification_id = fields.Char(string='N° de cedula', tracking=True)
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
        ('20', 'REPRES.DIPLOMATICAS')], string="Tipo de Documento", digits=(2), default="1")
    identification_expiry = fields.Date(string="Vencimiento de Cedula")
    country = fields.Many2one('res.country', 'Nacionalidad', tracking=True)
    city = fields.Many2one('res.country.state', 'Ciudad', domain="[('country_id', '=?', country)]", required=True)
    department = fields.Many2one('res.country.departament', 'Departamento', domain="[('state_id', '=?', city)]", required=True)
    neighborhood = fields.Many2one('res.country.neighborhood', 'Barrio', domain="[('departament_id', '=?', department)]", required=True)
    real_address = fields.Char(string="Dirección", digits=(50), required=True)
    house_no = fields.Integer(string="N° Casa", digits=(3), required=True)
    street_transversal = fields.Char(string="Calle Transversal", digits=(35))
    address_code = fields.Integer(default=1, digits=(3))
    birthday = fields.Date('Fecha de nacimiento', tracking=True)
    country_of_birth = fields.Many2one('res.country', 'País de Nacimiento', tracking=True)
    place_of_birth = fields.Many2one('res.country.state', 'Lugar de nacimiento', domain="[('country_id', '=?', country_of_birth)]", tracking=True)

    # contact
    email = fields.Char('E-mail')
    work_phone = fields.Char('Telefono Laboral', compute="_compute_phones", store=True, readonly=False)
    particular_phone = fields.Char('Telefono Particular')
    mobile_phone = fields.Char('Telefono Celular')
    idenfitication_image_front = fields.Binary(
        string="Cédula de Identidad (Frente)", max_width=100, max_height=100)
    idenfitication_image_back = fields.Binary(
        string="Cédula de Identidad (Dorso)", max_width=100, max_height=100)
    idenfitication_image_pdf = fields.Binary(string="Cédula de Identidad (PDF)")
    idenfitication_image_pdf_name = fields.Char(string="Nombre de cédula de identidad (PDF)")
    reference = fields.Text('Referencia')
    image_1920 = fields.Image(default=_default_image)

    # Bank info
    contract_type = fields.Selection([
        ('1', 'Contrato Por Tiempo Indefinido'),
        ('2', 'Contrato Por Tiempo Definido')], string="Tipo de Contrato", digits=(1), default="2")
    currency_type = fields.Selection([
        ('6900', 'Guaraníes'),
        ('1', 'Dólares Americanos')], string="Tipo de moneda", default="6900")
    gross_salary = fields.Float(string="Salario Bruto", digits=(18, 2))
    group_type = fields.Selection([
        ('90', 'Payroll'),
        ('94', 'Proveedores')], string="Tipo de Grupo", digits=(3), default="90")
    executive = fields.Integer(string="Ejecutivo")
    admission_date = fields.Date(string="Fecha de ingreso", required=True)
    contract_end_date = fields.Date(string="Fecha de fin de contrato")
    branch_number = fields.Char(string="Sucursal del Funcionario")
    account_number = fields.Char(string="Número de la Cuenta", digits=(9))
    account_name = fields.Char(string="Descripción de la Cuenta", digits=(30))
    sub_segmentation = fields.Selection([
        ('S', 'Crear'),
        ('N', 'No crear')], string="Sub segmentación", digits=(1), default="N")
    welcome_kit = fields.Many2one('bm.product', 'Welcome Kit')

    # misc
    notes = fields.Text('Notas')
    color = fields.Integer('Color Index', default=0)
    # pin = fields.Char(string="PIN", copy=False, help="PIN used to Check In/Out in Kiosk Mode (if enabled in Configuration).")
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    department_id = fields.Many2one('bm.department', 'Departmento', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    job_id = fields.Many2one('bm.job', 'Puesto de trabajo', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    job_title = fields.Char("Titulo del trabajo", compute="_compute_job_title", store=True, readonly=False)
    parent_id = fields.Many2one('bm.official', 'Gerente', compute="_compute_parent_id", store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    coach_id = fields.Many2one('bm.official', 'Supervisor', compute='_compute_coach', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help='Seleccione el "funcionario" que es el supervisor de este funcionario.\n'
             'El "Supervisor" no tiene derechos o responsabilidades específicos por defecto.')
    km_home_work = fields.Integer(string="Km Trabajo desde casa", tracking=True)

    # officials in company
    child_ids = fields.One2many('bm.official', 'parent_id', string='Direct subordinates')
    category_ids = fields.Many2many('bm.official.category', 'official_category_rel', 'official_id', 'category_id', string='Etiquetas')
    active = fields.Boolean("Active", default=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('check', 'En proceso de alta'),
        ('error', 'Revisar'),
        ('ready', 'Listo')],
        string="Estado", default='draft')
    reliable_base = fields.Boolean(
        string="Validación", default=False, readonly=True)
    departured = fields.Many2one('bm.official.departure', 'Licencia', compute="_compute_departured")

    def show_message(self, title, message, *args):
        return {
            'name': title,
            'type': 'ir.actions.act_window',
            'res_model': 'bm.official.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {'default_message': message},
            'target': 'new'
        }

    def show_warning(self, title, message):
        return {
            'warning': {
                'title': title,
                'message': message,
            },
        }

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

    @api.depends('departured')
    def _compute_departured(self):
        for official in self:
            official.departured = self.env['bm.official.departure'].search(['&', ('identification_id', '=', official.identification_id), ('state', '=', 'active')], order='id desc', limit=1)
                        
    @api.onchange('name_first', 'name_second', 'surname_first', 'surname_second', 'account_number', 'state', 'reliable_base')
    def _on_change_name(self):
        for official in self:
            if official.account_number:
                official.state = 'ready'

            _nombre = official.name_first
            if (official.name_second):
                _nombre = "{} {}".format(
                    official.name_first, official.name_second)

            _apellido = official.surname_first
            if (official.surname_second):
                _apellido = "{} {}".format(
                    official.surname_first, official.surname_second)

            if _nombre and _apellido:
                official.name = '{} {}'.format(_nombre, _apellido)

    # check
    @api.onchange('identification_id')
    def _on_change_identification_id(self):
        if (self.identification_id):
            for official in self.env['bm.official'].search([('identification_id', '=', self.identification_id)]):
                self.identification_id = self._origin.identification_id
                return self.show_warning('Número de identificación del funcionario', 'El funcionario {} ya posee este Número de Identificación.'.format(official.name))

    @api.onchange('gross_salary')
    def _on_change_gross_salary(self):
        if self.state != 'ready':  # Solo si el funcionario no está listo, obtengo los kits y le asigno el kit minimo
            _welcome_kit_selected = False
            for kit in self.env['bm.product'].search([('product_type', '=', 'kit')], order='minimum_salary desc'):
                if self.gross_salary >= kit.minimum_salary:
                    self._origin.welcome_kit = self.welcome_kit = kit.id
                    _welcome_kit_selected = True
                    break
            if not _welcome_kit_selected:
                self._origin.welcome_kit = None

    @api.onchange('country')
    def _on_change_country(self):
        self.country_of_birth = self.country
        self.city = None

    @api.onchange('city')
    def _on_change_city(self):
        self.department = None

    @api.onchange('department')
    def _on_change_department(self):
        self.neighborhood = None

    @api.onchange('identification_expiry')
    def _on_change_identification_expiry(self):
        if self.identification_expiry:
            if date.today() > self.identification_expiry:
                self.identification_expiry = None
                return self.show_warning('Vencimiento de identificación', 'El documento se encuentra vencido')

    @api.onchange('birthday')
    def _on_change_birthday(self):
        if self.birthday:
            if self.birthday < date(1900, 5, 10):
                self.birthday = None
                return self.show_warning('Fecha de nacimiento', 'La fecha de nacimiento debe ser mayór')

    @api.onchange('admission_date')
    def _on_change_admission_date(self):
        if self.admission_date:
            if self.admission_date < date(1900, 5, 10):
                self.admission_date = None
                return self.show_warning('Fecha de ingreso', 'La fecha de ingreso debe ser mayór')
            if self.admission_date > date.today():
                self.admission_date = None
                return self.show_warning('Fecha de ingreso', 'La fecha de ingreso no puede ser mayór al dia actual')

    @api.onchange('contract_end_date')
    def _on_change_contract_end_date(self):
        if self.contract_end_date:
            if self.contract_end_date < date(1900, 5, 10):
                self.contract_end_date = None
                return self.show_warning('Fecha de fin de contrato', 'La fecha fin de contrato debe ser mayór')

    def button_aprove(self):
        # get officials selected
        officials = self.env['bm.official'].browse(self._context.get('active_ids')) or self
        _ready_count = 0
        # loop officials
        for official in officials:
            # if official has account, validate next one
            if official.reliable_base:
                continue
            # if official is already checked or ready
            if official.state in ['check', 'ready']:
                continue
            # if official has not idenfitication_image or idenfitication_image_pdf, store error and go to next one
            #if not (official.idenfitication_image_front or official.idenfitication_image_back or official.idenfitication_image_pdf):
            #    _errors.append(
            #        '{}: Falta cargar la imagen de la cedula de identidad'.format(official.name))
            #    continue
            # if its ok, change state
            if official.state == 'draft':
                official.state = 'check'
                _ready_count += 1
        if _ready_count > 1:
            return self.show_message('Aprobar', 'Se aprobaron {} funcionarios'.format(_ready_count))


    def button_draft(self):
        for official in self:
            if official.state == 'check':
                official.state = 'draft'
                official.reliable_base = False

    def button_reset(self):
        for official in self:
            if official.state == 'ready':
                official.numero_cuenta = None
                official.numero_sucursal = None
                official.nombre_cuenta = None
                official.reliable_base = False
                official.state = 'check'

    def create_officials_salary(self):                
        func_result = {
            'has_payment': [],
            'payment': '',
            'count_ok': 0
        }
        officials_salary = self.env['bm.official.salary']
        # Obtengo los funcionarios seleccionados
        for official in self.env['bm.official'].search([
                '&',
                '&', 
                ('id', 'in', self._context.get('active_ids')), 
                ('state', 'in', ['ready']),
                '&', 
                ('account_number', '!=', False),
                ('account_name', '!=', False),
                '&', 
                ('gross_salary', '>', 0),
                ('reliable_base', '=', True)
            ]):
            _create_official_salary = True
            #Get the last movement and check if in 35 range and is paid
            for official_salary in officials_salary.search([('official.id', '=', official.id)], order='id desc', limit=1):
                #if exist official salary for las 35 day
                diference_days = (datetime.now().date() - official_salary.payment_date).days
                if diference_days <= 35:
                    func_result['has_payment'].append('{}: {} dias'.format(official.name, diference_days))
                    #_changes.append('{} ya posee registro'.format(official.name))
                    _create_official_salary = False
            if _create_official_salary:
                officials_salary.create({
                    'identification_id': official.identification_id
                })
                func_result['count_ok'] += 1
        #if _ready_count > 0:
        if len(func_result['has_payment']) > 0:
            func_result['payment'] = '\nLos siguientes funcionarios ya poseen registros validos:\n{}'.format('\n'.join(func_result['has_payment']))
        return self.show_message('Movimiento de salarios', 'Se crearon {} movimientos.\n{}'.format(func_result['count_ok'], func_result['payment']))