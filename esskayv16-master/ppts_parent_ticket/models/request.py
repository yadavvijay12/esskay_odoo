# -*- coding: utf-8 -*-
#############################################################################
#
#    Point Perfect Technology Solutions.
#
#############################################################################
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError
from odoo.exceptions import UserError, ValidationError


class Request(models.Model):
    _name = 'request'
    _description = "Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', copy=False, )
    parent_ticket_id = fields.Many2one('parent.ticket', string='Parent Ticket')
    child_ticket_id = fields.Many2one('child.ticket', string='Child Ticket')
    team_id = fields.Many2one('crm.team', string="Team", copy=False, help="Should inherit from user & Edit")
    user_id = fields.Many2one('res.users', string='Requested by')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('request'))
    is_create_invoice = fields.Boolean(string='Create Invoice')
    service_request_id = fields.Many2one('service.request', string="Service Request ID", copy=False)
    asset_ids = fields.One2many('request.asset.line', 'request_id', string='Assets')
    return_ids = fields.One2many('request.asset.line', 'request_id', string='Assets')
    is_stock_checked = fields.Boolean(string="Is Stock Checked?")
    spare_request_id = fields.Many2one('spare.request', string="Spare Request", copy=False)
    external_state = fields.Selection(
        [('new', 'Draft'), ('draft', 'Draft'), ('available', 'Available'), ('not_available', 'Not available'),
         ('partial_available', 'Partial Available'), ('confirm', 'Confirmed'), ('issued', 'Issued'),
         ('partial_issued', 'Partially Issued'), ('internal', 'Internal')],
        string='Status', default='new')
    partner_id = fields.Many2one('res.partner', string="Customer", copy=False)
    customer_account_id = fields.Many2one('res.partner', string="Customer Account",
                                          related='partner_id.customer_account_id')
    is_spare_request = fields.Boolean(string="Is Spare Request?")
    is_external = fields.Boolean(string="Is Spare External")
    is_external_service = fields.Boolean(string="Is Stock External From Service")
    is_create_quote = fields.Boolean(string="Is Quotations")
    spare_request_ids = fields.Many2many('spare.request', string="Spare Requests", copy=False, compute='_compute_spare')
    spare_count = fields.Integer(string="Spare Requests", copy=False, compute='_compute_spare')
    is_return_table=fields.Boolean(string="Return")

    @api.model
    def create(self, vals):
        res = super(Request, self).create(vals)
        if res.name != 'Assigned to User':
            template_id = self.env.ref('ppts_parent_ticket.mail_template_requests')
            amc = dict(res.parent_ticket_id._fields['amc_status'].selection).get(
                res.parent_ticket_id.amc_status) or dict(
                res.child_ticket_id._fields['amc_status'].selection).get(res.child_ticket_id.amc_status) or ''
            cmc = dict(res.parent_ticket_id._fields['cmc_status'].selection).get(
                res.parent_ticket_id.cmc_status) or dict(
                res.child_ticket_id._fields['cmc_status'].selection).get(res.child_ticket_id.cmc_status) or ''
            warranty = dict(res.parent_ticket_id._fields['oem_warranty_status'].selection).get(
                res.parent_ticket_id.oem_warranty_status) or dict(
                res.child_ticket_id._fields['oem_warranty_status'].selection).get(
                res.child_ticket_id.oem_warranty_status) or ''
            repair = dict(res.parent_ticket_id._fields['oem_repair_status'].selection).get(
                res.parent_ticket_id.oem_repair_status) or dict(
                res.child_ticket_id._fields['oem_repair_status'].selection).get(
                res.child_ticket_id.oem_repair_status) or ''
            extended = dict(res.parent_ticket_id._fields['extended_warranty_status'].selection).get(
                res.parent_ticket_id.extended_warranty_status) or dict(
                res.child_ticket_id._fields['extended_warranty_status'].selection).get(
                res.child_ticket_id.extended_warranty_status) or ''
            if vals.get('is_spare_request') == True:
                if not vals.get('asset_ids'):
                    raise ValidationError(_("Please select the Spare Parts."))

            stock=res.child_ticket_id.partner_id.customer_account_id.stock_checking_process_ids.filtered(lambda l: l.request_type == 'spare_parts')
            if res.child_ticket_id and stock:
                if stock.stock_request_type == 'internal':
                    res.is_return_table=True

            team = res.team_id.id or vals.get('team_id')
            if team:
                team_id = self.env['crm.team'].browse(int(team))
                # Get the parent ticket assign engineer's to send an email
                email_ids = None;
                parent_ticket_user_name = None
                if res.child_ticket_id.parent_ticket_id:
                    for parent_ticket_users in res.child_ticket_id.parent_ticket_id.assign_engineer_ids:
                        if email_ids:
                            email_ids += ',' + parent_ticket_users.email
                        else:
                            email_ids = parent_ticket_users.email
                            parent_ticket_user_name = parent_ticket_users.name
                if email_ids:
                    action_id = self.env.ref('ppts_parent_ticket.action_request', raise_if_not_found=False)
                    base_url = '/web#id=%d&cids=1&action=%r&model=request&view_type=form' % (res.id, action_id.id)
                    # if rec.has_group('ppts_service_request.service_request_group_ct_user') and not rec.has_group(
                    #         'ppts_service_request.service_request_group_manager'):
                    mail_id = template_id.with_context(email_to=email_ids, amc=amc, cmc=cmc, warranty=warranty,
                                                       repair=repair, extended=extended,
                                                       parent_ticket_user_name=parent_ticket_user_name,
                                                       rec_ur=base_url).sudo().send_mail(res.id,
                                                                                         force_send=True)
        return res

    def _compute_spare(self):
        lists = []
        for record in self:
            spare_ids = self.env["spare.request"].search([("request_id", "=", record.id)])
            if spare_ids:
                record.spare_request_ids = spare_ids.ids
                record.spare_count = len(spare_ids)
            else:
                record.spare_request_ids = None
                record.spare_count = 0

    def view_spare_request(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Spare Request',
            'view_mode': 'tree,form',
            'res_model': 'spare.request',
            'domain': [('request_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def request_spare_order(self):
        if self.is_spare_request and self.customer_account_id:
            spare = self.customer_account_id.stock_checking_process_ids.filtered(
                lambda l: l.request_type == 'spare_parts')
            if not spare:
                raise UserError(_("There is no Stock Checking Process for customer account !"))
            elif spare.stock_request_type == 'external':
                self.is_external = True
                self.external_state = 'draft'
            elif spare.stock_request_type == 'internal':
                context = {
                    "default_request_id": self.id,
                    "default_indent_date": datetime.now(),
                    "default_requirement": '1',
                    "default_type": 'stock',
                    "default_parent_ticket_id": self.parent_ticket_id.id or False,
                    "default_child_ticket_id": self.child_ticket_id.id or False,
                    "default_state": 'draft',
                    "default_partner_id": self.partner_id.id or self.partner_id.id,
                    "default_team_id": self.parent_ticket_id.team_id.id or self.child_ticket_id.team_id.id,
                    "default_spare_request_line": [(0, 0, {
                        'description': line.description,
                        'product_uom_qty': line.quantity,
                        'product_uom_id': line.product_uom_id.id,
                    }) for line in self.asset_ids],
                }
                context.update(self.env.context)
                view_id = self.env.ref("spare_request.view_spare_request_form").id
                return {
                    "type": "ir.actions.act_window",
                    "name": "Spare Request",
                    "res_model": "spare.request",
                    "view_mode": "form",
                    "views": [(view_id, "form")],
                    "target": "new",
                    "context": context,
                }

    def acton_confirm(self):
        if self.is_spare_request:
            self.external_state = 'confirm'
            task_id = self.env.ref('spare_request.task_data_spare_delivery_approved')
            # PT # Task Update For External Process
            if self.parent_ticket_id:
                self.parent_ticket_id.update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })

            # CT # Task Update For External Process
            if self.child_ticket_id:
                self.child_ticket_id.update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })

    def acton_process_external_transfer(self):
        task_id = None
        if self.is_spare_request:
            if all(a.stock_availability == 'available' for a in self.asset_ids):
                self.external_state = 'issued'
                task_id = self.env.ref('spare_request.task_data_spare_delivery_done')
            else:
                self.external_state = 'partial_issued'
                task_id = self.env.ref('spare_request.task_data_spare_delivery_done')
            # PT # Task Update For External Process
            if self.parent_ticket_id:
                self.parent_ticket_id.update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })

            # CT # Task Update For External Process
            if self.child_ticket_id:
                self.child_ticket_id.update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })

    def raise_invoice(self):
        if self.is_create_invoice:
            if self.parent_ticket_id:
                ticket = self.parent_ticket_id
            else:
                ticket = self.child_ticket_id
            invoice_data = {
                'partner_id': ticket.partner_id.id,
                'move_type': 'out_invoice',
                'team_id': self.team_id.id,
                'parent_ticket_id': self.parent_ticket_id.id,
                'child_ticket_id': self.child_ticket_id.id,
                'invoice_line_ids': [(0, 0, {
                    'product_id': ticket.product_id.id,
                })],
            }
            invoice = self.env['account.move'].sudo().create(invoice_data)
            self.is_create_invoice = False


class RequestAssetLine(models.Model):
    _name = 'request.asset.line'
    _description = 'Request Asset Line'

    name = fields.Char(string="Description")
    product_id = fields.Many2one('product.product', string="Product")
    description = fields.Char(string="Description")
    stock_lot_id = fields.Many2one('stock.lot', string="Asset Lot/Serial Number")
    notes = fields.Char('Notes')
    request_id = fields.Many2one('request', string='Request', ondelete='cascade')
    quantity = fields.Integer(string="Demand Quantity", default=1)
    available = fields.Integer(string="Done Quantity")
    product_uom_id = fields.Many2one('uom.uom', string="UOM")
    stock_availability = fields.Selection(
        [('available', 'Available'), ('partial', 'Partially Available'),
         ('not_available', 'Not Available')], string='Stock Availability')
    part_number = fields.Char(string="Part No")
    serial_number = fields.Char(string="Serial No")
    return_quantity = fields.Integer(string="Return Quantity", compute='compute_spare_return_status')

    @api.onchange('available')
    def _onchange_available_qty(self):
        for rec in self:
            if rec.available:
                if rec.quantity < rec.available:
                    raise UserError('Enter the Done Quantity Correctly!!')

    @api.depends('quantity', 'available')
    def compute_spare_return_status(self):
        for rec in self:
            if rec.available and rec.quantity:
                rec.return_quantity = rec.quantity - rec.available
            else:
                rec.return_quantity = 0

    def action_mark_stock_status(self):
        task_id = None
        if self.request_id.service_request_id:
            if 'is_available' in self.env.context:
                self.stock_availability = 'available'
                self.request_id.service_request_id.sudo().state = 'available'
            elif 'is_partial' in self.env.context:
                self.stock_availability = 'partial'
                self.request_id.service_request_id.sudo().state = 'partial_available'
            elif 'is_not_available' in self.env.context:
                self.stock_availability = 'not_available'
                self.request_id.service_request_id.sudo().state = 'not_available'
        if self.request_id.is_spare_request:
            if 'is_available' in self.env.context:
                self.stock_availability = 'available'
                self.available = self.quantity
            elif 'is_partial' in self.env.context:
                if self.quantity > self.available > 0:
                    self.stock_availability = 'partial'
                # if self.quantity - self.available:

                else:
                    return self._show_notification('Enter Available Quantity Correctly')
            elif 'is_not_available' in self.env.context:
                self.available = 0
                self.stock_availability = 'not_available'

            if self.request_id and self.request_id.external_state != 'confirm':
                if all(a.stock_availability == 'available' for a in self.request_id.asset_ids):
                    self.request_id.external_state = 'available'
                    task_id = self.env.ref('spare_request.task_data_spare_available')
                elif all(a.stock_availability == 'not_available' for a in self.request_id.asset_ids):
                    self.request_id.external_state = 'not_available'
                    task_id = self.env.ref('spare_request.task_data_spare_not_available')
                else:
                    self.request_id.external_state = 'partial_available'
                    task_id = self.env.ref('spare_request.task_data_spare_partially_available')

                # PT # Task Update For External Process
                if self.request_id.parent_ticket_id:
                    self.request_id.parent_ticket_id.update({
                        'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                    })

                # CT # Task Update For External Process
                if self.request_id.child_ticket_id:
                    self.request_id.child_ticket_id.update({
                        'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                    })

    def _show_notification(self, message):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'warning',
                'sticky': False,
            },
        }
        return notification

    @api.onchange('stock_lot_id')
    def _onchange_stock_lot_id(self):
        if self.stock_lot_id:
            self.product_id = self.stock_lot_id.product_id.id
        else:
            self.product_id = False

    @api.onchange('product_id')
    def _onchange_product_uom_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
            self.description = self.product_id.name
        else:
            self.product_uom_id = False
            self.description = ''

    def action_open_product_template(self):
        self.ensure_one()
        return {
            'name': 'Product',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.template',
            'res_id': self.product_id.product_tmpl_id.id,
        }
