{
    'name': "PPTS Custom Workflow",

    'summary': """
        This module provides custom workflow features.""",

    'author': "PPTS",
    'website': "https://www.pptssolutions.com",
    'category': 'Customizations',
    'version': '16.0',
    'depends': ['base', 'hr', 'survey', 'ppts_service_request','quality_assurance'],
    'data': [
        'security/ir.model.access.csv',
        'data/task_data.xml',
        'views/workflow_views.xml',
        'views/task_master_views.xml',
        'views/hr_employee_views.xml',
    ],
}
