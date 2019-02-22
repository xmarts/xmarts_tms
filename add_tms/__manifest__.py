# -*- coding: utf-8 -*-
{
    'name': "add_tms",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Victor Manuel Alonso Soto",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','x_tms'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/tms_operations.xml',
        'views/type_vehicle_procedures.xml',
        'views/tms_event_actions.xml',
        'views/tms_categories_events.xml',
        'views/tms_odometro_vehicle.xml',
        'views/tms_tall_low.xml',
        'views/tms_type_vehicle.xml',
        'views/tms_reason_state.xml',
        'views/tms_motor_types.xml',
        'views/tms_validity.xml',
        'views/tms_tires.xml',
        'views/tms_categories_empresa.xml',
        'views/tms_employee_category.xml',
        'views/tms_plazas.xml',
        'views/tms_categories_letter_porte.xml',
        'views/tms_transportable_product.xml',
        'views/tms_procedure_vehicle.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}