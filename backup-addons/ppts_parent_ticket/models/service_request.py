from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError


class ServiceRequest(models.Model):
    _inherit = 'service.request'

    child_ticket_id = fields.Many2one('child.ticket', string="Child Ticket ID", copy=False)
    parent_ticket_id = fields.Many2one('parent.ticket', string="Parent Ticket ID", copy=False)
    child_ticket_type_id = fields.Many2one('child.ticket.type', string="Child Ticket Type", copy=False)
    is_from_ct = fields.Boolean(string="SR from CT", copy=False)

    # with Approval
    # Convert to Parent Ticket Wizard
    def action_convert_parent_ticket_wizard(self):
        # Check for the asset and create the service request details on the asset ticket O2M fields
        rec = dict(self._fields['state'].selection).get(self.state)
        for record in self.customer_asset_ids:
            self.env['asset.lot.serial'].create({
                'service_request_id': self.id,
                'problem_description': self.reason,
                'ticket_type': 'sr',
                'stock_lot_id': record.stock_lot_id.id,
                'service_type_id': self.service_type_id.id,
                'service_category_id': self.service_category_id.id,
                'ct_user_id': self.ct_user.id if self.user_id.has_group(
                    'ppts_service_request.service_request_group_ct_user') else None,
                'engineer_id': self.user_id.id if not self.user_id.has_group(
                    'ppts_service_request.service_request_group_ct_user') else None,
                'ticket_create_date': self.create_date,
                'status': rec,
            })
        context = {
            "default_call_source_id": self.call_source_id.id,
            "default_service_category_id": self.service_category_id.id,
            "default_service_type_id": self.service_type_id.id,
            "default_request_type_id": self.request_type_id.id,
        }
        return {
            'name': _('Convert Parent Ticket'),
            'view_mode': 'form',
            'res_model': 'convert.parent.ticket',
            'type': 'ir.actions.act_window',
            'target': 'new',
            "context": context,
        }

    # Without Approval
    # Convert to Parent Ticket Wizard
    def action_convert_pt_without_approval_wizard(self):
        if not self.customer_asset_ids:
            raise UserError(_("Add Asset to proceed."))
        if not self.partner_id:
            raise UserError(_("Please map the customer to proceed."))
        context = {
            "default_call_source_id": self.call_source_id.id,
            "default_service_category_id": self.service_category_id.id,
            "default_service_type_id": self.service_type_id.id,
            "default_request_type_id": self.request_type_id.id,
        }
        return {
            'name': _('Convert Parent Ticket'),
            'view_mode': 'form',
            'res_model': 'convert.parent.ticket',
            'type': 'ir.actions.act_window',
            'target': 'new',
            "context": context,
        }

    # with Approval
    # Convert to Child Ticket Wizard
    def action_convert_child_ticket_wizard(self):
        return {
            'name': _('Convert Child Ticket'),
            'view_mode': 'form',
            'res_model': 'convert.child.ticket',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    # without Approval
    # Convert to Child Ticket Wizard
    def action_convert_ct_without_approval_wizard(self):
        return {
            'name': _('Convert Child Ticket'),
            'view_mode': 'form',
            'res_model': 'convert.child.ticket',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


class TasksMasterInherit(models.Model):
    _inherit = "tasks.master"

    service_type_id = fields.Many2one('service.type', string="Service Type", copy=False)
    service_category_id = fields.Many2one('service.category', string="Service Category", copy=False)
    parent_configuration_id = fields.Many2one('parent.ticket.configuration', string="Parent Configuration", copy=False)
    child_configuration_id = fields.Many2one('child.ticket.configuration', string='Child Configuration', copy=False)
    request_type_id = fields.Many2one('request.type', string="Approval Type", copy=False)

    @api.onchange('is_create_service_request', 'is_enable_child_ticket', 'is_create_ticket')
    def onchange_tickets(self):
        if self.is_create_ticket:
            self.is_enable_child_ticket = False
            self.is_create_service_request = False
        elif self.is_create_service_request:
            self.is_enable_child_ticket = False
            self.is_create_ticket = False
        elif self.is_enable_child_ticket:
            self.is_create_service_request = False
            self.is_create_ticket = False

    @api.onchange('service_type_id')
    def onchange_service_type_domain(self):
        category_ids = self.service_type_id.service_category_ids.mapped('id')
        domain = [('id', 'in', category_ids)]
        return {'domain': {'service_category_id': domain}}

    @api.onchange('service_type_id')
    def onchange_service_domain(self):
        request_ids = self.service_type_id.request_type_ids.mapped('id')
        domain = [('id', 'in', request_ids)]
        return {'domain': {'request_type_id': domain}}
