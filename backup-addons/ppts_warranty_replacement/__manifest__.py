{
    'name': "PPTS Warranty Replacement (RMA)",
    'version': '16.0',
    'summary': """ This module provides Warranty Replacement Process """,
    'author': "PPTS India Pvt Ltd",
    'website': "https://www.pptssolutions.com",
    'category': 'masters',
    'depends': ['base','product','sale','stock','sale_stock','ppts_custom_masters','ppts_service_request','ppts_parent_ticket','spare_request'],
    'data': [
        'data/ir_sequence_data.xml',
        'data/mail_template.xml',
        'data/task_data.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/warranty_replacement_view.xml',
        'views/service_request_sr_wr_views.xml',
        'views/multi_level_approval_view.xml',
        'views/parent_ticket_view.xml',
        'wizard/reason_reason_view.xml',
        'wizard/wr_sr_wizard_views.xml',
        'wizard/wr_approval_views.xml',
        'views/wr_report_template.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
    'assets': {
            'web.assets_backend': [
                'ppts_warranty_replacement/static/src/**/*',
            ],
        },
}
