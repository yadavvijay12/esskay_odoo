# -*- coding: utf-8 -*-
#############################################################################
#
#    Point Perfect Technology Solutions.
#
#############################################################################
{
    'name': 'Parent Ticket',
    'version': '16.0.1.0.0',
    'summary': 'Module for managing Parent Ticket',
    'category': 'Services',
    'author': 'Point Perfect Technology Solutions',
    'company': 'Point Perfect Technology Solutions',
    'website': 'https://www.pptssolutions.com/',
    'depends': ['base', 'web', 'mail', 'product', 'stock', 'ppts_custom_masters', 'contract', 'base_automation'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/service_request_report.xml',
        'report/pi_sf_field_call_report.xml',
        'report/installation_child_ticket.xml',
        'report/Warranty_Replacement_Form.xml',
        'report/service_report_inhouse_child_ticket.xml',
        'data/email_template.xml',
        'views/ticket_configuration_view.xml',
        'views/parent_ticket_views.xml',
        'views/child_ticket_views.xml',
        'views/service_request_view.xml',
        'views/request_view.xml',
        'views/multi_level_approval_view.xml',
        'wizard/assign_engineer_views.xml',
        'wizard/convert_parent_ticket_views.xml',
        'wizard/convert_child_ticket_views.xml',
        'wizard/status_update_views.xml',
        'wizard/parent_ticket_approval_views.xml',
        'wizard/request_type_wizard_view.xml',
        'wizard/child_ticket_approval_views.xml',
        'wizard/exit_reason.xml',
        'wizard/reason_delete_engineer.xml',
        'data/base_automation.xml',
        'views/sla_policies_views.xml',
        'report/spares_sf_field_services_form.xml',
        'report/spare_indent.xml',
        'report/se_inhouse_repair_form.xml',
        'report/tsr_pm.xml',
        'report/loaner_report.xml',
        'views/stock_lot_view.xml',
        'views/stock_picking_views.xml',
        'views/res_partner_view.xml',
        'views/parent_ticket_menus.xml',  # Last because referencing actions defined in previous files
    ],
    # 'qweb': ['static/src/xml/relational_utils.xml'
    #          ],
    'assets': {
        'web.assets_backend': [
            'ppts_parent_ticket/static/src/xml/relational_utils.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
