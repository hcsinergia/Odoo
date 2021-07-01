# -*- coding: utf-8 -*-
from odoo import http
from datetime import datetime
import tempfile

#import logging
#_logger = logging.getLogger(__name__)

class BM_OfficialSalary_Controller(http.Controller):
    @http.route('/web/binary_text/create_file_txt', type='http', auth="user")
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


        if not req.params.get('ids'):
            return False
        # Get the selected official's salary movement
        officials_salary = http.request.env['bm.official.salary'].search([('id', 'in', req.params.get('ids').split(','))])
        # Creo el TXT
        file_title = 'BANKMANAGEMENT_{}.txt'.format(datetime.strftime(datetime.now(), '%Y%m%d%H%M%S'))
        file_content_header = 'H;999;mail@entidad.com;6900;52000.00;1;19/05/20;202005902952101999;1;1;1982073;10;20;6900;0;0;0\n'
        file_content_detail = ''
        for official_salary in officials_salary:
            if official_salary.state == 'aproved':
                #D;PAGO DE SALARIO VIA BANCO;APELLIDO 1;APELLIDO 2;NOMBRE 1;NOMBRE 2;586;1;111222;6900;52000.00;19/05/20;21;498154;10;6900;0;0;0;202005902952101999;1;528000.00;31/12/99
                file_content_detail += "D;PAGO DE SALARIO;{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}\n".format(
                    official_salary.official.surname_first or '',
                    official_salary.official.surname_second or '',
                    official_salary.official.name_first or '',
                    official_salary.official.name_second or '',
                    official_salary.official.country.name or '',
                    official_salary.official.identification_type or '',
                    official_salary.official.identification_id or '',
                    official_salary.currency_type or '',
                    official_salary.amount_to_pay or '',
                    official_salary.payment_date or '',
                    official_salary.payment_mode or '',
                    official_salary.official.account_number or '', 
                    official_salary.official.branch_number or '',
                    official_salary.official.currency_type or '',
                    official_salary.operation_code or '', 
                    official_salary.operation_type or '',
                    official_salary.suboperacion_code or '',
                    official_salary.reference or '',
                    official_salary.official.contract_type or '',
                    official_salary.official.gross_salary or '',
                    official_salary.official.contract_end_date or '',
                )
        file_content = str.encode(file_content_header + file_content_detail)
        # Create temporary file, write info and download
        tmp_file = tempfile.TemporaryFile()
        # Write data into your file respectively with your logic
        tmp_file.write(file_content)
        tmp_file.seek(0)
        file = tmp_file.read()
        tmp_file.close()
        
        return req.make_response(
            file, headers=[
                ('Content-Disposition', 'attachment; filename="{}"'.format(file_title)),
                ('Content-Type', 'text/plain')
            ])
