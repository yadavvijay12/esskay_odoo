{
    'name': "PPTS Maintenance",
    'version': '16.0',
    'summary': """ This module provides SR-Maintenance Process """,
    'author': "PPTS India Pvt Ltd",
    'website': "https://www.pptssolutions.com",
    'category': 'masters',
    'depends': ['base','maintenance','ppts_service_request','ppts_parent_ticket'],
    'data': [
        'data/ir_sequence_data.xml',
        'data/task_data.xml',
        # 'data/mail_template.xml',
        'security/ir.model.access.csv',
        'views/maintenance_view.xml',
        'views/service_request_sr_maintenance.xml',
        'views/multi_level_approval_view.xml',
        'views/child_ticket_view.xml',
        'wizard/reason_reason_view.xml',
        'wizard/maintenance_approval_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
    'assets': {
            'web.assets_backend': [
                'ppts_maintenanace/static/src/**/*',
            ],
        },
}
