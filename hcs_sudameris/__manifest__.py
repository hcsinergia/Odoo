# -*- coding: utf-8 -*-
{
    'name': "Sudameris",

    'summary': "Control de empleados y salarios",

    'description': """
        Modulo para el control de empleados y salarios por compañias asociadas al banco
    """,

    'author': "HC Sinergia",
    'website': "http://www.hcsinergia.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Administration',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['hr', 'contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/website_templates.xml',
        'views/webclient_templates.xml',
        'views/templates.xml',
        'views/assets.xml',
        'views/res_country_views.xml',
        'views/employee.xml',
        'views/salary_movement.xml',
        'views/products.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
