# -*- coding: utf-8 -*-
{
    "name": "PPTS : Spare Request",
    "summary": "Spare Request",
    "category": "Service",
    "version": "16.0",
    "sequence": 1,
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "https://www.pptssolutions.com",
    "description": """To Raise the Spare Request""",
    "depends": [
        'stock', 'sale_stock', 'ppts_parent_ticket'
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/spare_request_security.xml',
        'data/ir_sequence_data.xml',
        'data/task_data.xml',
        'data/email_template.xml',
        'views/department.xml',
        'views/spare_request_view.xml',
        'views/stock_move_views.xml',
        'views/stock_picking_views.xml',
        'views/parent_ticket_view.xml',
        'views/child_ticket_view.xml',
        'views/multi_level_approval_view.xml',
        'wizard/spare_approval_views.xml',
    ],
    "application": True,
    "installable": True,
    "auto_install": False,

}
