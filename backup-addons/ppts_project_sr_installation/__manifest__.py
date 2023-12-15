{
    'name': "Installation",
    'version': '16.0',
    'summary': """
        This module provides the below masters.
        1. SR Installation
        """,
    'author': "PPTS India Pvt Ltd",
    'website': "https://www.pptssolutions.com",
    'category': 'masters',
    'depends': ['base','project','ppts_service_request','ppts_parent_ticket','hr_expense','spare_request','ppts_warranty_replacement'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'data/ir_sequence_data.xml',
        'wizard/installation_reason.xml',
        'views/project_sr_installation_views.xml',
        'views/service_request_sr_installation_views.xml',
        'views/multi_level_approval_view.xml',
        'wizard/reason_reason_view.xml',
        'wizard/installation_approval_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
