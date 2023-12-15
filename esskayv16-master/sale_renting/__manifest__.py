# -*- coding: utf-8 -*-
{
    'name': "PPTS : Loaner",

    'summary': "Manage rental contracts, deliveries and returns",

    'description': """
        Specify loaner of products (products, quotations, invoices, ...)
        Manage status of products, loaner, delays
        Manage user and manager notifications
    """,

    'category': 'Sales/Sales',
    'sequence': 160,
    'version': '1.0',

    'depends': ['sale_temporal','web_gantt','ppts_service_request'],

    'data': [
        'security/ir.model.access.csv',
        'security/ir_rules.xml',
        'data/rental_data.xml',
        'data/email_template.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/res_config_settings_views.xml',
        'views/stock_warehouse.xml',
        'views/service_request_sr_loaner_views.xml',

        'report/rental_order_report_templates.xml',
        'report/rental_report_views.xml',
        'report/rental_schedule_views.xml',

        'wizard/rental_configurator_views.xml',
        'wizard/rental_processing_views.xml',

        'views/sale_renting_menus.xml',
    ],
    'demo': [
        'data/rental_demo.xml',
    ],
    'application': True,
    'pre_init_hook': '_pre_init_rental',
    'assets': {
        'web.assets_backend': [
            'sale_renting/static/src/**/*',
        ],
    },

}
