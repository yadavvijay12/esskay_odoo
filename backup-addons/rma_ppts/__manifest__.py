# -*- coding: utf-8 -*-
#############################################################################
#
#    Point Perfect Technology Solutions.
#
#############################################################################
{
    'name': 'RMA (Return Merchandise Authorization)',
    'version': '16.0.1.0.0',
    'category': 'Sales',
    'license': 'LGPL-3',
    'summary': "Manage Return Merchandise Authorization (RMA). Allow users to manage Return Orders, Replacement, Refund & Repair in Odoo.",
    'author': 'Point Perfect Technology Solutions.',
    'website': 'https://www.pptssolutions.com/',
    'depends': ['delivery','crm','repair','ppts_parent_ticket'],
    'data': [
        'report/rma_report.xml',
        'data/rma_reason_ppts.xml',
        'data/mail_template_data.xml',
        'data/crm_claim_ppts_sequence.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'report/rma_report_template.xml',
        'views/view_account_invoice.xml',
        'views/crm_claim_ppts_view.xml',
        'views/view_stock_picking.xml',
        'views/rma_reason_ppts.xml',
        'views/view_stock_warehouse.xml',
        'views/sale_order_view.xml',
        'views/repair_order_view.xml',
        'views/claim_reject_message.xml',
        'views/child_ticket_view.xml',
        'wizard/view_claim_process_wizard.xml',
        'wizard/create_partner_delivery_address_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
