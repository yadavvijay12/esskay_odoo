# -*- coding: utf-8 -*-

{
    'name': 'Watsapp Sms',
    'version': '13.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'category': 'base',
    'depends': ['base','web','crm','sale_crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/watsapp_gateway_views.xml',
        'views/watsapp_sms_template.xml',
        'views/whatsapp_view.xml',
        'views/whatsapp_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
