# -*- coding: utf-8 -*-
from odoo import http
from datetime import datetime
import logging
import tempfile

_logger = logging.getLogger(__name__)

class Sudameris_employee_salary_movement_controller(http.Controller):
    @http.route('/web/binary_text/crear_txt', type='http', auth="user")
    def index(self, req):        
        # Composición del nombre: ENTIDAD_SERVICIO_FECHA+HORA.TXT
        # Ejemplo: GESTION_PAGODESALARIOS_20200519103252.TXT
        # Tipo de dato: I: Entero, C: Caracter o Alfanumérico, D: Fecha, N: Numérico decimal con dos valores decimales
        ## CABECERA: Identificador de cabecera(C:1);Código de contrato(I:9);E-mail asociado al Servicio(C:50);Moneda(I:4);Importe(N:15.2);Cantidad de Documentos(I:5); \
        ## Fecha de Pago(D:8);Referencia(C:18);Tipo de Cobro(I:3);Debito Crédito(I:1);Cuenta Débito(I:9);Sucursal Débito(I:3);Módulo Débito(I:3); \ 
        ## Moneda Débito(I:4)Operación Débito(I:9);Sub Operación Débito(I:3);Tipo Operación Débito(I:3)
        # Ejemplo CABECERA: H;999;mail@entidad.com;6900;52000.00;1;19/05/20; 202005902952101999;1;1;1982073;10;20;6900;0;0;0
        ## DETALLE: Identificador del detalle(C:1);Concepto(C:30);Primer Apellido(C:15);Segundo Apellido(C:15);Primer Nombre(C:15);Segundo Nombre(C:15); \ 
        ## País(I:3);Tipo de Documento(I:2);Número de Documento(C:15);Moneda(I:4);Importe(N:15.2);Fecha de Pago(D:8);Modalidad de Pago(I:3); \ 
        ## Número de Cuenta(I:9);Sucursal Empleado(I:3);Moneda Empleado(I:4);Operación Empleado(I:9);Tipo de Operación Empleado(I:3);Suboperación Empleado(I:3); \ 
        ## Referencia(C:18);Tipo de Contrato(I:3);Sueldo Bruto(N:15.2);Fecha Fin de Contrato(D:8);
        # Ejemplo DETALLE: D;PAGO DE SALARIO VIA BANCO;APELLIDO 1;APELLIDO 2;NOMBRE 1;NOMBRE 2;586;1;111222;6900;52000.00;19/05/20;21;498154;10;6900;0;0;0;202005902952101999;1;528000.00;31/12/99
        # _txt = 'Token: {}\n'.format(get_token)
        # Obtengo los movimientos seleccionados
        if not req.params.get('ids'):
            return False
        movimientos = http.request.env['sudameris_employee_salary_movement'].search([('id', 'in', req.params.get('ids').split(','))])
        # Creo el TXT
        _txt_title = 'SUDAMERIS_ODOO_{}.txt'.format(datetime.strftime(datetime.now(), '%Y%m%d%H%M%S'))
        _txt_content_header = 'H;999;mail@entidad.com;6900;52000.00;1;19/05/20;202005902952101999;1;1;1982073;10;20;6900;0;0;0\n'
        _txt_content_detail = ''
        for movimiento in movimientos:
            if movimiento.state == 'aprobado':
                funcionario = movimiento.funcionario
                # Genero el detalle con los datos del funcionario
                #D;PAGO DE SALARIO VIA BANCO;APELLIDO 1;APELLIDO 2;NOMBRE 1;NOMBRE 2;586;1;111222;6900;52000.00;19/05/20;21;498154;10;6900;0;0;0;202005902952101999;1;528000.00;31/12/99
                _detalle = "D;SUDAMERIS_ODOO;{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10};{11};{12};{13};{14};{15};{16};{17};{18};{19};{20}\n".format(
                funcionario.apellido_1 or '', funcionario.apellido_2 or '', funcionario.nombre_1 or '', funcionario.nombre_2 or '',
                funcionario.country_id.name or '', funcionario.tipo_documento or '', funcionario.identification_id or '', movimiento.moneda or '',
                movimiento.salario_importe or '', movimiento.fecha_pago or '', movimiento.modalidad_pago or '', funcionario.numero_cuenta or '', 
                funcionario.numero_sucursal or '', funcionario.tipo_moneda or '', movimiento.codigo_operacion or '', 
                movimiento.tipo_operacion or '', movimiento.codigo_suboperacion or '', movimiento.referencia or '',
                funcionario.tipo_contrato or '', funcionario.salario_bruto or '', funcionario.fecha_fin_contrato or '',
                )
                _txt_content_detail += _detalle
        fp = tempfile.TemporaryFile()
        # Write data into your file respectively with your logic
        fp.write(str.encode(_txt_content_header + _txt_content_detail))
        fp.seek(0)
        file_data = fp.read()
        fp.close()
        return req.make_response(
            file_data, headers=[
                ('Content-Disposition', 'attachment; filename="{}"'.format(_txt_title)),
                ('Content-Type', 'text/plain')
            ])

    
#     @http.route('/hcs_sudameris/hcs_sudameris/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hcs_sudameris/hcs_sudameris/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hcs_sudameris.listing', {
#             'root': '/hcs_sudameris/hcs_sudameris',
#             'objects': http.request.env['hcs_sudameris.hcs_sudameris'].search([]),
#         })

#     @http.route('/hcs_sudameris/hcs_sudameris/objects/<model("hcs_sudameris.hcs_sudameris"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hcs_sudameris.object', {
#             'object': obj
#         })
