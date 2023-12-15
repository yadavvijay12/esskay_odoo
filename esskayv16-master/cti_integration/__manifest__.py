# -*- coding: utf-8 -*-
#############################################################################
#
#    Point Perfect Technology Solutions.
#
#############################################################################
{
    'name': 'PPTS Call Integration',
    'version': '16.0.1.0.0',
    'summary': 'Module for managing calls from odoo to phones and mobiles',
    'category': 'Services',
    'author': 'Point Perfect Technology Solutions',
    'company': 'Point Perfect Technology Solutions',
    'website': 'https://www.pptssolutions.com/',
    'depends': ['base','web', 'bus', 'mail', 'survey'],
    'data': [
        'data/api_configuration_data.xml',
        'data/call_history_sequence.xml',
        'security/ir.model.access.csv',
        'views/ppts_res_partner_inherited_views.xml',
        'views/cti_integration_views.xml',
        'views/call_history_views.xml',
        'views/outbound_call_list_views.xml',
        'wizard/outbound_wizard_views.xml'
    ],
    "assets": {
        "web.assets_backend": [
            "cti_integration/static/src/js/notification_popup.js",
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
