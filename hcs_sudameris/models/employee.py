# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
from .API.ws_base import SudamerisApiBase
from datetime import datetime, date
import logging
import json

_logger = logging.getLogger(__name__)

# Referencia de códigos de datos
_TipoGrupo = [('90', 'Payroll'), ('94', 'Proveedores')]

_Moneda = [('6900', 'Guaraníes'), ('1', 'Dólares Americanos')]

_TipoDocumento = [('1', 'CEDULA DE IDENTIDAD'), ('2', 'CREDENCIAL CIVICA'), ('3', 'R.U.C.'),
                  ('4', 'PASAPORTE'), ('5',
                                       'DNI-DOC.NAC.IDENTID.'), ('6', 'REGISTRO DE COMERCIO'),
                  ('7', 'LIB.DE ENROLAMIENTO'), ('10',
                                                 'GARANTIA'), ('15', 'Entidades Públicas'),
                  ('16', 'CARNET-INMIGRACIONES'), ('98',
                                                   'No Registra'), ('99', 'Inst. Financieras'),
                  ('20', 'REPRES.DIPLOMATICAS')]

_TipoContrato = [('1', 'Contrato Por Tiempo Indefinido'),
                 ('2', 'Contrato Por Tiempo Definido')]

_EstadosFuncionario = [('borrador', 'Borrador'),
                       ('enproceso', 'En proceso de alta'), ('listo', 'Listo')]


class hr_employee_wizard(models.TransientModel):
    _name = "hr.employee.wizard"
    _description = "HR employee wizard"
    message = fields.Text(readonly=True, store=False)


class hr_employee_sudameris_inherit(models.Model):
    _inherit = 'hr.employee'

    nombre_1 = fields.Char(string="Primer Nombre", required=True)
    nombre_2 = fields.Char(string="Segundo Nombre")
    apellido_1 = fields.Char(string="Primer Apellido", required=True)
    apellido_2 = fields.Char(string="Segundo Apellido")
    tipo_documento = fields.Selection(
        selection=_TipoDocumento, string="Tipo de identificación", digits=(2), default="5")
    vencimiento_documento = fields.Date(string="Vencimiento de identificación")
    tipo_contrato = fields.Selection(
        selection=_TipoContrato, string="Tipo de Contrato", digits=(1), default="2")
    tipo_moneda = fields.Selection(
        string="Tipo de moneda", selection=_Moneda, default="6900")
    salario_bruto = fields.Float(string="Salario", digits=(18, 2))
    codigo_direccion = fields.Integer(default=1, digits=(3))
    ciudad = fields.Many2one(string='Ciudad', comodel_name='res.country.state',
                             domain="[('country_id', '=?', country_id)]", required=True)
    barrio = fields.Many2one(string='Barrio', comodel_name='res.country.neighborhood',
                             domain="[('departament_id', '=?', departamento)]", required=True)
    departamento = fields.Many2one(string='Departamento', comodel_name='res.country.departament',
                                   domain="[('state_id', '=?', ciudad)]", required=True)
    calle_transversal = fields.Char(string="Calle Transversal", digits=(35))
    domicilio_real = fields.Char(
        string="Domicilio real", digits=(50), required=True)
    nro_casa = fields.Integer(string="Numero de Casa",
                              digits=(3), required=True)
    tipo_grupo = fields.Selection(
        selection=_TipoGrupo, string="Tipo de Grupo", digits=(3), default="90")
    ejecutivo = fields.Integer(string="Ejecutivo")
    fecha_ingreso = fields.Date(string="Fecha de ingreso", required=True)
    fecha_fin_contrato = fields.Date(string="Fecha de fin de contrato")
    numero_sucursal = fields.Char(string="Sucursal del Funcionario")
    numero_cuenta = fields.Char(
        string="Número de la Cuenta", digits=(9), readonly=True)
    nombre_cuenta = fields.Char(
        string="Descripción de la Cuenta", digits=(30), readonly=True)
    sub_segmentacion = fields.Selection(selection=[(
        'S', 'Crear'), ('N', 'No crear')], string="Sub segmentación", digits=(1), default="N")
    wk = fields.Many2one(string='Welcome Kit',
                         comodel_name='sudameris_employee_products')
    state = fields.Selection(
        string="Estado", selection=_EstadosFuncionario, default='borrador')
    cedula_image = fields.Binary(
        string="Cédula de Identidad (imagen)", max_width=100, max_height=100)
    cedula_document = fields.Binary(string="Cédula de Identidad (PDF)")
    cedula_name = fields.Char(string="Nombre de la cedula")
    base_confiable = fields.Boolean(
        string="Validación", default=False, readonly=True)

    _sql_constraints = [
        ('user_uniq', 'unique (user_id, company_id)',
         "A user cannot be linked to multiple employees in the same company."),
        ('phone_uniq', 'unique (phone)',
         "The Phone must be unique, this one is already assigned to another employee."),
        ('identification_id_uniq', 'unique (identification_id)',
         "The identification_id must be unique, this one is already assigned to another employee."),
        ('domicilio_real_uniq', 'unique (domicilio_real)',
         "The Direction must be unique, this one is already assigned to another employee."),
        ('work_email_uniq', 'unique (work_email)',
         "The Email must be unique, this one is already assigned to another employee."),
    ]

    # Mostrar mensaje

    def show_message(self, title, message, *args):
        return {
            'name': title,
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.wizard',
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

    # Check nombre del funcionario
    @api.onchange('nombre_1', 'nombre_2', 'apellido_1', 'apellido_2')
    def _on_change_name(self):
        for funcionario in self:
            _nombre = funcionario.nombre_1
            if (funcionario.nombre_2):
                _nombre = "{} {}".format(
                    funcionario.nombre_1, funcionario.nombre_2)

            _apellido = funcionario.apellido_1
            if (funcionario.apellido_2):
                _apellido = "{} {}".format(
                    funcionario.apellido_1, funcionario.apellido_2)

            if _nombre and _apellido:
                funcionario.name = '{} {}'.format(_nombre, _apellido)

    # check
    @api.onchange('identification_id')
    def _on_change_identification_id(self):
        if (self.identification_id):
            for funcionario in self.env['hr.employee'].search([('identification_id', '=', self.identification_id)]):
                self.identification_id = self._origin.identification_id
                return self.show_warning('Número de identificación del funcionario', 'El funcionario {} ya posee este Número de Identificación.'.format(funcionario.name))

    @api.onchange('salario_bruto')
    def _on_change_salario_bruto(self):
        if self.state != 'listo':  # Solo si el funcionario no está listo, obtengo los kits y le asigno el kit minimo
            _kit_selected = False
            for kit in self.env['sudameris_employee_products'].search([('tipo', '=', 'kit')], order='salario_minimo desc'):
                if self.salario_bruto >= kit.salario_minimo:
                    self._origin.wk = self.wk = kit.id
                    _kit_selected = True
                    break
            if not _kit_selected:
                self._origin.wk = None

    @api.onchange('country_id')
    def _on_change_country_id(self):
        self.ciudad = None

    @api.onchange('ciudad')
    def _on_change_ciudad(self):
        self.departamento = None

    @api.onchange('departamento')
    def _on_change_barrio(self):
        self.barrio = None

    @api.onchange('vencimiento_documento')
    def _on_change_vencimiento_documento(self):
        if self.vencimiento_documento:
            if date.today() > self.vencimiento_documento:
                self.vencimiento_documento = None
                return self.show_warning('Vencimiento de identificación', 'El documento se encuentra vencido')

    @api.onchange('birthday')
    def _on_change_birthday(self):
        if self.birthday:
            if self.birthday < date(1900, 5, 10):
                self.birthday = None
                return self.show_warning('Fecha de nacimiento', 'La fecha de nacimiento debe ser mayór')

    @api.onchange('fecha_ingreso')
    def _on_change_fecha_ingreso(self):
        if self.fecha_ingreso:
            if self.fecha_ingreso < date(1900, 5, 10):
                self.fecha_ingreso = None
                return self.show_warning('Fecha de ingreso', 'La fecha de ingreso debe ser mayór')
            if self.fecha_ingreso > date.today():
                self.fecha_ingreso = None
                return self.show_warning('Fecha de ingreso', 'La fecha de ingreso no puede ser mayór al dia actual')

    @api.onchange('fecha_fin_contrato')
    def _on_change_fecha_fin_contrato(self):
        if self.fecha_fin_contrato:
            if self.fecha_fin_contrato < date(1900, 5, 10):
                self.fecha_fin_contrato = None
                return self.show_warning('Fecha de fin de contrato', 'La fecha fin de contrato debe ser mayór')

    def btn_aprobar(self):
        # Obtengo la lista de funcionarios seleccionados
        funcionarios = self.env['hr.employee'].browse(
            self._context.get('active_ids')) or self
        # raise ValidationError(funcionarios)
        for funcionario in funcionarios:
            if funcionario.state == 'borrador' and (funcionario.cedula_image or funcionario.cedula_document):
                funcionario.state = 'enproceso'

    def btn_borrador(self):
        for funcionario in self:
            if funcionario.state == 'enproceso':
                funcionario.state = 'borrador'
                funcionario.base_confiable = False

    def btn_reiniciar(self):
        for funcionario in self:
            if funcionario.state == 'listo':
                funcionario.numero_cuenta = None
                funcionario.numero_sucursal = None
                funcionario.nombre_cuenta = None
                funcionario.base_confiable = False
                funcionario.state = 'enproceso'

    def crear_movimientos(self):
        _count_ok = 0
        _errors = []
        # Obtengo el context de movimientos de salarios
        movimientos = self.env['sudameris_employee_salary_movement']
        # Obtengo los funcionarios seleccionados
        for funcionario in self.env['hr.employee'].browse(self._context.get('active_ids')):
            _create = True
            if funcionario.salario_bruto == 0:
                return self.show_message('Movimiento de salarios', 'El funcionario {} no tiene salario'.format(funcionario.name))
            if funcionario.state == 'listo':
                list_movimientos = movimientos.search(
                    [('funcionario.id', '=', funcionario.id)])
                for movimiento in list_movimientos:
                    if datetime.now().month == movimiento.fecha_pago.month:
                        _errors.append(
                            '{} ya posee registro'.format(funcionario.name))
                        _create = False
                # Si no hay un registro, lo crea
                if _create:
                    movimientos.create({
                        'identification_id': funcionario.identification_id
                    })
                    # _changes.append('[OK]: Se creó el movimiento de {}'.format(funcionario.name))
                    _count_ok += 1
            # else:
            #  _changes.append('[ATENCION]: {} no está listo para crear movimiento de salario'.format(funcionario.name))
        if _count_ok > 0:
            return self.show_message('Movimiento de salarios', 'Se crearon {} movimientos'.format(_count_ok))

    def cliente_valida_base_confiable(self):
        # Checkeo que el usuario actual
        if not self.env.user.company_id.id == 1:
            return self.show_message('Validar usuario', 'Cuando todo esté listo, un representante del banco Sudameris podrá verificar el estado del funcionario.')
        _changes = []
        # Creo la clase y le paso como parametro ir.config_parameter como sudo
        _config_parameter = self.env['ir.config_parameter'].sudo()
        sudamerisApi = SudamerisApiBase(_config_parameter)
        # Obtengo la lista de funcionarios seleccionados
        funcionarios = self.env['hr.employee'].browse(
            self._context.get('active_ids')) or self
        for funcionario in funcionarios:
            # Hago la consulta a la API
            result = sudamerisApi.ws_valida_base_confiable(
                funcionario.country_id.name,
                funcionario.tipo_documento,
                funcionario.identification_id,
                funcionario.nombre_1,
                funcionario.nombre_2,
                funcionario.apellido_1,
                funcionario.apellido_2,
                funcionario.birthday
            )
            funcionario.base_confiable = result[0]
            if result[0] == False:
                _changes.append('{}: {}'.format(funcionario.name, result[1]))
        if len(_changes) > 0:
            return self.show_message('Cliente Valida Base Confiable', 'Se encontraron los siguientes errores: \n{}'.format('\n'.join(_changes)))

    def cliente_posee_cuenta(self):
        # Checkeo que el usuario actual
        if not self.env.user.company_id.id == 1:
            return self.show_message('Cliente posee cuenta', 'Cuando todo esté listo, un representante del banco Sudameris podrá verificar el estado del funcionario.')

        _changes=[]
        # Creo la clase y le paso como parametro ir.config_parameter como sudo
        _config_parameter=self.env['ir.config_parameter'].sudo()
        sudamerisApi=SudamerisApiBase(_config_parameter)
        # Obtengo los funcionarios seleccionados y verifco cada uno
        for funcionario in self.env['hr.employee'].browse(self._context.get('active_ids')):
            if funcionario.state == 'borrador':
                _changes.append(
                    '{} todavia no está aprobado, debe estar En Proceso de Alta'.format(funcionario.name))
                continue
            if funcionario.state == 'listo' and funcionario.numero_cuenta != '':
                _changes.append(
                    '{} ya posee una cuenta en el banco'.format(funcionario.name))
                continue
            # Hago la consulta a la API
            result=sudamerisApi.ws_cliente_posee_cuenta(
                funcionario.country_id.name, funcionario.tipo_documento, funcionario.identification_id)
            for res in result:
                _valor = res["Filas"]["RepFilas.Fila"][0]["Valor"]
                if res['Descripcion'] == "CTNRO":  # Número de cuenta
                    funcionario.numero_cuenta = _valor
                if res['Descripcion'] == "Cttfir":  # Sucursal
                    funcionario.numero_sucursal = 1
                if res['Descripcion'] == "Observacion":  # Descripción de la cuenta
                    funcionario.nombre_cuenta = _valor
            # Guardo la respuestas correspondientes y marco el funcionario como listo
            funcionario.state = 'listo'
            _changes.append(
                '{} obtuvo su cuenta correctamente'.format(funcionario.name))
        return self.show_message('Cliente Posee Cuenta', '\n'.join(_changes))
