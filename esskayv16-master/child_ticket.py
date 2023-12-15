# -*- coding: utf-8 -*-
#############################################################################
#
#    Point Perfect Technology Solutions.
#
#############################################################################
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError


class ChildTicket(models.Model):
    _inherit = 'child.ticket'
    _description = "Child Ticket"

    is_create_maintenance = fields.Boolean(string="Is Create Maintenance")
    is_maintenance_created = fields.Boolean(string="Is Maintenance Created")
    maintenance_id = fields.Many2one('maintenance.request', string="Maintenance ID")
    maintenance_count = fields.Integer(compute='_count_total_maintenance')
    maintenance_ids = fields.Many2many('maintenance.request', string="Maintenance", compute='_compute_maintenance_line')

    def _compute_maintenance_line(self):
        for record in self:
            maintenance_ids = self.env["maintenance.request"].search([("child_ticket_id", "=", record.id)])
            if maintenance_ids:
                record.maintenance_ids = maintenance_ids.ids
            else:
                record.maintenance_ids = None

    # Smart Button - Maintenance
    def action_view_maintenance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance',
            'view_mode': 'tree',
            'views': [(self.env.ref('ppts_maintenanace.sr_maintenance_request_view_tree').id, 'tree'),
                      (self.env.ref('ppts_maintenanace.sr_maintenance_request_view_form').id, 'form')],
            'res_model': 'maintenance.request',
            'domain': [('child_ticket_id', '=', self.sudo().id)],
            'context': "{'create': False}"
        }

    def _count_total_maintenance(self):
        for record in self:
            record.maintenance_count = self.env['maintenance.request'].sudo().search_count([('child_ticket_id', '=', record.id)])

    def action_create_maintenance(self):
        if not self.stock_lot_id:
            raise UserError(_("Please Select Asset Serial No"))
        record = {
            'is_sr_maintenance': True,
            'maintenance_process_alias_id': self.child_ticket_id_alias or '',
            'title': self.problem_description or '',
            'stock_lot_id': self.stock_lot_id.id,
            'product_id': self.product_id.id,
            'partner_id': self.partner_id.id or False,
            'customer_account_id': self.customer_account_id.id or False,
            'service_category_id': self.service_category_id.id or False,
            'service_type_id': self.service_type_id.id or False,
            # 'request_type_id': order.request_type_id.id or False,
            'team_id': self.team_id.id or False,
            # 'parent_ticket_id': order.parent_ticket_id.id or False,
            'child_ticket_id': self.id or False,
            'external_reference': self.remarks,
            'reported_fault': self.faulty_section or '',
            'categ_id': self.product_id.categ_id.id or False,
            'service_request_id': self.service_request_id.id or False,
            'custom_product_serial': self.product_id.custom_product_serial,
            'product_code_no': self.product_id.product_code,
            'cat_no': self.product_id.product_part,
            'worksheet_id': self.survey_id.id or False,
            'origin': self.name,
            'warranty_end_date': self.stock_lot_id.warranty_end_date,
            'extended_warranty_end_date': self.stock_lot_id.extended_warranty_end_date,
            'user_id': self.env.user.id,
        }
        record = self.env['maintenance.request'].create(record)
        record._onchange_stock_lot_id()
        view = self.env.ref('ppts_maintenanace.sr_maintenance_request_view_form')
        self.is_maintenance_created = True
        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Request',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view.id,
            'res_model': 'maintenance.request',
            'res_id': record.id,
            'target': 'current',
            'domain': [('is_sr_maintenance', '=', True)],
        }

    @api.onchange('task_list_ids')
    def _onchange_task_list_ids(self):
        res = super(ChildTicket, self)._onchange_task_list_ids()
        for record in self:
            mr = record.task_list_ids.task_id.filtered(lambda r: r.python_code == 'maintenance_request')
            if mr:
                record.is_create_maintenance = True
            else:
                record.is_create_maintenance = False
        return res