{
    'name': 'ESSKAY MOBILE API For Odoo',
    'version': '0.1.0',
    'category': 'API',
    'author': "PPTS India Pvt Ltd",
    'summary': 'RESTFUL API For Odoo',
    'description': """
RESTFUL API For Odoo
====================
With use of this module user can enable REST API in any Odoo applications/modules order from costco

""",
    'depends': ['base'],
    "external_dependencies": {"python": ["beautifulsoup4"]},
    'data': [
        'security/ir.model.access.csv',
        'views/res_users.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
