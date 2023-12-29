# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta
from datetime import datetime, date


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_rental_order = fields.Boolean("Created In App Loaner")
    rental_status = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('pickup', 'Confirmed'),
        ('return', 'Picked-up'),
        ('returned', 'Returned'),
        ('cancel', 'Cancelled'),
    ], string="Loaner Status", compute='_compute_rental_status', store=True)
    # loaner_status = next action to do basically, but shown string is action done.

    has_pickable_lines = fields.Boolean(compute="_compute_rental_status", store=True)
    has_returnable_lines = fields.Boolean(compute="_compute_rental_status", store=True)
    next_action_date = fields.Datetime(
        string="Next Action", compute='_compute_rental_status', store=True)
    has_late_lines = fields.Boolean(compute="_compute_has_late_lines")

    distributor_id = fields.Many2one('res.partner', string='Dealer / Distributor Name')
    request_id_alias = fields.Text('Request ID Alias')
    requested_by = fields.Many2one('res.users', string='Requested by')
    loaner_request = fields.Text('Reason for Loaner Request')
    remarks = fields.Text('Remarks')
    parent_ticket_id = fields.Many2one('parent.ticket', string="Parent Ticket ID")
    child_ticket_id = fields.Many2one('child.ticket', string="Child Ticket ID")
    # sr_id= fields.Many2one('service.request', string="SR ID")
    service_request_id = fields.Many2one('service.request', string="Service Request ID")
    lr_from_pt = fields.Boolean(string="Is Loaner From PT")

    def action_confirm(self):
        if any(not record.start_date and not record.return_date for record in self.order_line) and self.is_rental_order:
            raise UserError(_("Please set Product Start Date and Return Date."))
        res = super(SaleOrder, self).action_confirm()
        if self.lr_from_pt and self.parent_ticket_id:
            orders = self.env['stock.picking'].search([('origin', '=', self.name)])
            for order in orders:
                order.lr_from_pt = self.lr_from_pt
                order.parent_ticket_id = self.parent_ticket_id.id
        return res

    def before_return_notify(self):
        now = date.today()
        sale_order = self.env['sale.order'].sudo().search([('is_rental_order', '=', True)])
        for rec in sale_order:
            sale_order_line = self.env['sale.order.line'].search([('order_id', '=', rec.id)])
            for res in sale_order_line:
                if res.return_date:
                    previous_day = res.return_date - timedelta(days=1)
                    next_day = res.return_date + timedelta(days=1)
                    p_day = previous_day.strftime('%Y-%m-%d')
                    n_day = next_day.strftime('%Y-%m-%d')
                    pre_template_id = self.env.ref('sale_renting.email_template_loaner_return_notify')
                    exp_template_id = self.env.ref('sale_renting.email_template_loaner_return_expiry_notify')
                    partner_email = rec.partner_id.email
                    if p_day == now.strftime('%Y-%m-%d'):
                        if pre_template_id and partner_email:
                            mail_id = pre_template_id.with_context(email_to=partner_email).sudo().send_mail(
                                rec.id, force_send=True)
                    # if n_day == now.strftime('%Y-%m-%d'):
                    if n_day == now.strftime('%Y-%m-%d') or n_day < now.strftime('%Y-%m-%d'):
                        if exp_template_id and partner_email:
                            mail_id = exp_template_id.with_context(email_to=partner_email).sudo().send_mail(
                                rec.id, force_send=True)

    def request_approval(self):
        return True

    def approved(self):
        return True

    def _track_subtype(self, init_values):
        self.ensure_one()
        if self.is_rental_order:
            if 'state' in init_values and self.state == 'draft':
                return self.env.ref('sale_renting.mt_loaner_draf')
            elif 'state' in init_values and self.state == 'sale':
                return self.env.ref('sale_renting.mt_loaner_order_confirmed')
            # elif 'rental_status' in init_values and self.rental_status == 'return':
            #     return self.env.ref('sale_renting.mt_loaner_order_picked_up')
            # elif 'rental_status' in init_values and self.rental_status == 'returned':
            #     return self.env.ref('sale_renting.mt_loaner_order_returned')
            elif 'state' in init_values and self.state == 'cancel':
                return self.env.ref('sale_renting.mt_loaner_order_cancel')
        return super()._track_subtype(init_values)

    def sale_quotation_loaner_filter(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        sale_ids = self.env['sale.order'].search([('is_rental_order', '=', False), ])
        domain = "[('id', 'in', %s)]" % sale_ids.ids
        action['domain'] = domain
        return action

    def sale_order_loaner_filter(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        sale_ids = self.env['sale.order'].search(
            [('is_rental_order', '=', False), ('state', 'not in', ('draft', 'sent', 'cancel'))])
        domain = "[('id', 'in', %s)]" % sale_ids.ids
        action['domain'] = domain
        return action

    @api.depends('is_rental_order', 'next_action_date', 'rental_status')
    def _compute_has_late_lines(self):
        for order in self:
            order.has_late_lines = (
                    order.is_rental_order
                    and order.rental_status in ['pickup', 'return']  # has_pickable_lines or has_returnable_lines
                    and order.next_action_date and order.next_action_date < fields.Datetime.now())

    @api.depends('state', 'order_line', 'order_line.product_uom_qty', 'order_line.qty_delivered',
                 'order_line.qty_returned')
    def _compute_rental_status(self):
        for order in self:
            if order.state in ['sale', 'done'] and order.is_rental_order:
                rental_order_lines = order.order_line.filtered(lambda l: l.is_rental and l.start_date and l.return_date)
                pickeable_lines = rental_order_lines.filtered(lambda sol: sol.qty_delivered < sol.product_uom_qty)
                returnable_lines = rental_order_lines.filtered(lambda sol: sol.qty_returned < sol.qty_delivered)
                min_pickup_date = min(pickeable_lines.mapped('start_date')) if pickeable_lines else 0
                min_return_date = min(returnable_lines.mapped('return_date')) if returnable_lines else 0
                if min_pickup_date and pickeable_lines and (not returnable_lines or min_pickup_date <= min_return_date):
                    order.rental_status = 'pickup'
                    order.next_action_date = min_pickup_date
                elif returnable_lines:
                    order.rental_status = 'return'
                    order.next_action_date = min_return_date
                else:
                    order.rental_status = 'returned'
                    order.next_action_date = False
                order.has_pickable_lines = bool(pickeable_lines)
                order.has_returnable_lines = bool(returnable_lines)
            else:
                order.has_pickable_lines = False
                order.has_returnable_lines = False
                order.rental_status = order.state if order.is_rental_order else False
                order.next_action_date = False

    # PICKUP / RETURN : rental.processing wizard

    def open_pickup(self):
        status = "pickup"
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        lines_to_pickup = self.order_line.filtered(
            lambda r: r.state in ['sale', 'done'] and r.is_rental and float_compare(r.product_uom_qty, r.qty_delivered,
                                                                                    precision_digits=precision) > 0)
        return self._open_rental_wizard(status, lines_to_pickup.ids)

    def open_return(self):
        status = "return"
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        lines_to_return = self.order_line.filtered(
            lambda r: r.state in ['sale', 'done'] and r.is_rental and float_compare(r.qty_delivered, r.qty_returned,
                                                                                    precision_digits=precision) > 0)
        return self._open_rental_wizard(status, lines_to_return.ids)

    def _open_rental_wizard(self, status, order_line_ids):
        context = {
            'order_line_ids': order_line_ids,
            'default_status': status,
            'default_order_id': self.id,
        }
        return {
            'name': _('Validate a pickup') if status == 'pickup' else _('Validate a return'),
            'view_mode': 'form',
            'res_model': 'rental.order.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

    def _get_portal_return_action(self):
        """ Return the action used to display orders when returning from customer portal. """
        if self.is_rental_order:
            return self.env.ref('sale_renting.rental_order_action')
        else:
            return super()._get_portal_return_action()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_rental_order') and not vals.get('name'):
                sequence = self.env['ir.sequence'].next_by_code('loaner.order')
                vals['name'] = sequence
                if vals.get('parent_ticket_id'):
                    task_id = self.env.ref('ppts_custom_workflow.task_data_loaner_transfer_request')
                    pt_id = self.env["parent.ticket"].search([("id", "=", vals.get('parent_ticket_id'))])
                    pt_id.update({
                        'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                    })
                if vals.get('child_ticket_id'):
                    task_id = self.env.ref('ppts_custom_workflow.task_data_loaner_transfer_request')
                    ct_id = self.env["child.ticket"].search([("id", "=", vals.get('child_ticket_id'))])
                    ct_id.update({
                        'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                    })

        return super(SaleOrder, self).create(vals_list)

    def write(self, values):
        rec = super().write(values)
        task_id = None
        last_task_id = []
        pt_task_ids = self.parent_ticket_id.task_list_ids.mapped("task_id")
        for pt_task in pt_task_ids:
            last_task_id.append(pt_task.id)
        last_id = last_task_id.pop() if last_task_id else None
        if self.rental_status == 'pickup' and any(self.parent_ticket_id or self.child_ticket_id):
            task_id = self.env.ref('ppts_custom_workflow.task_data_loaner_transfer_approved')
        if self.rental_status == 'cancel' and any(self.parent_ticket_id or self.child_ticket_id):
            task_id = self.env.ref('ppts_custom_workflow.task_data_loaner_transfer_rejected')
        # Parent ticket Status Update
        if task_id and not task_id.id == last_id:
            pt_id = self.env["parent.ticket"].search([("id", "=", self.parent_ticket_id.id)])
            pt_id.update({
                'task_list_ids': [(0, 0, {'task_id': task_id.id})],
            })
        # Child Ticket Status Update
        ct_last_task_id = []
        ct_task_ids = self.child_ticket_id.task_list_ids.mapped("task_id")
        for ct_task in ct_task_ids:
            ct_last_task_id.append(ct_task.id)
        ct_last_id = ct_last_task_id.pop() if ct_last_task_id else None
        if task_id and not task_id.id == ct_last_id:
            ct_id = self.env["child.ticket"].search([("id", "=", self.child_ticket_id.id)])
            ct_id.update({
                'task_list_ids': [(0, 0, {'task_id': task_id.id})],
            })
        if 'rental_status' in values and self.parent_ticket_id or self.child_ticket_id and self.is_rental_order:
            # PT Configuration Notification
            if self.parent_ticket_id.parent_configuration_id and self.parent_ticket_id.parent_configuration_id.is_loaners:
                email = ''
                approver_email = ''
                send = False
                if self.parent_ticket_id.parent_configuration_id.alert_loaners == 'confirm' and self.rental_status == 'pickup':
                    send = True
                elif self.parent_ticket_id.parent_configuration_id.alert_loaners == 'done' and self.rental_status == 'returned':
                    send = True
                elif self.parent_ticket_id.parent_configuration_id.alert_loaners == 'both' and self.rental_status in [
                    'pickup', 'returned']:
                    send = True

                team_alert_template_id = self.parent_ticket_id.parent_configuration_id.alert_loaners_email_template_id
                customer_template_id = self.parent_ticket_id.parent_configuration_id.loaners_cust_email_template_id
                if team_alert_template_id and send:
                    teams = self.env['hr.employee'].search([('job_id', 'in',
                                                             self.parent_ticket_id.parent_configuration_id.alert_loaners_approval_team_ids.ids)]).mapped(
                        'work_email')
                    email += ', '.join(teams)
                    team_alert_template_id.with_context(email_to=email).sudo().send_mail(self.parent_ticket_id.id,
                                                                                         force_send=True)
                if customer_template_id and send:
                    customer_email = ",".join([str(self.parent_ticket_id.customer_account_id.email),
                                               str(self.parent_ticket_id.partner_id.email)])
                    customer_template_id.with_context(email_to=customer_email).sudo().send_mail(
                        self.parent_ticket_id.id, force_send=True)
                if team_alert_template_id and self.parent_ticket_id.parent_configuration_id.is_approval_required_loaners and send:
                    for teams in self.parent_ticket_id.parent_configuration_id.loaners_approval_team_ids:
                        teams = teams.mapped('line_ids.user_id.login')
                        approver_email += ', '.join(teams)
                    team_alert_template_id.with_context(email_to=approver_email).sudo().send_mail(
                        self.parent_ticket_id.id, force_send=True)
            # CT Configuration Notification
            if self.child_ticket_id.child_configuration_id and self.child_ticket_id.child_configuration_id.is_loaners:
                email = ''
                approver_email = ''
                send = False
                if self.child_ticket_id.child_configuration_id.alert_loaners == 'confirm' and self.rental_status == 'pickup':
                    send = True
                elif self.child_ticket_id.child_configuration_id.alert_loaners == 'done' and self.rental_status == 'returned':
                    send = True
                elif self.child_ticket_id.child_configuration_id.alert_loaners == 'both' and self.rental_status in [
                    'pickup', 'returned']:
                    send = True

                team_alert_template_id = self.child_ticket_id.child_configuration_id.alert_loaners_email_template_id
                customer_template_id = self.child_ticket_id.child_configuration_id.loaners_cust_email_template_id
                if team_alert_template_id and send:
                    teams = self.env['hr.employee'].search([('job_id', 'in',
                                                             self.child_ticket_id.child_configuration_id.alert_loaners_approval_team_ids.ids)]).mapped(
                        'work_email')
                    email += ', '.join(teams)
                    team_alert_template_id.with_context(email_to=email).sudo().send_mail(self.child_ticket_id.id,
                                                                                         force_send=True)
                if customer_template_id and send:
                    customer_email = ",".join([str(self.child_ticket_id.customer_account_id.email),
                                               str(self.child_ticket_id.partner_id.email)])
                    customer_template_id.with_context(email_to=customer_email).sudo().send_mail(self.child_ticket_id.id,
                                                                                                force_send=True)
                if team_alert_template_id and self.child_ticket_id.child_configuration_id.is_approval_required_loaners and send:
                    for teams in self.child_ticket_id.child_configuration_id.loaners_approval_team_ids:
                        teams = teams.mapped('line_ids.user_id.login')
                        approver_email += ', '.join(teams)
                    team_alert_template_id.with_context(email_to=approver_email).sudo().send_mail(
                        self.child_ticket_id.id, force_send=True)
        return rec

    def update_product_return_date(self):
        for line in self.order_line:
            return line.env.ref('sale_renting.rental_configurator_action')
