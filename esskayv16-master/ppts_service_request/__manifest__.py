# -*- coding: utf-8 -*-
#############################################################################
#
#    Point Perfect Technology Solutions.
#
#############################################################################
{
    'name': 'PPST : Service Request',
    'version': '16.0.1.0.0',
    'summary': 'Module for managing service request and service request web form',
    'category': 'Services',
    'author': 'Point Perfect Technology Solutions',
    'company': 'Point Perfect Technology Solutions',
    'website': 'https://www.pptssolutions.com/',
    'depends': ['base', 'mail', 'sale', 'survey', 'website', 'product', 'stock', 'multi_level_approval','sales_team'],
    'data': ['security/security.xml',
             'security/ir.model.access.csv',
             'views/master_list_views.xml',
            'views/res_users.xml',
             'views/service_request_views.xml',
             'views/service_request_website_form.xml',
             'data/email_template.xml',
             'wizard/reason_reason_view.xml',
             'views/stock_production_lot_view.xml',
             'views/crm_team_view.xml',
             'views/service_request_menus.xml',  # Last because referencing actions defined in previous files
             'views/service_request_sr_factory_request_views.xml',
             'views/service_request_sr_fsm_views .xml',
             'views/service_request_sr_remote_support_views.xml',
             'views/service_request_sr_loaner_views.xml',
             'views/service_request_sr_wr_views.xml',
             'views/service_request_maintenance_views.xml',
             'views/service_request_sr_installation_views.xml',
             'views/service_request_check_stock_view.xml',
             'views/multi_level_approval_view.xml',
             'views/so_call_views.xml',
             ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {
            'web.assets_backend': [
                'ppts_service_request/static/src/notebook.xml',
            ],
            'web.assets_frontend': [
                'ppts_service_request/static/src/js/website_portal_form.js',
                'ppts_service_request/static/src/js/country.js',
            ],
        },
}
