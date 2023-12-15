# -*- coding: utf-8 -*-
#############################################################################
#                                                                           #
#    Point Perfect Technology Solutions.                                    #
#                                                                           #
#############################################################################
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError
import base64


class ProjectTask(models.Model):
    _inherit = 'project.task'

    name = fields.Char(string='Title', tracking=True, required=True, index='trigram', default="New")
    is_project_installation = fields.Boolean('Project Installation')
    installation_process_alias = fields.Char(string='Installation Process ID Alias')
    installation_start_date = fields.Date(string='Installation Start date', default=fields.Date.context_today)
    installation_end_date = fields.Date(string='Installation End date', default=fields.Date.context_today)
    installation_title = fields.Char(string='Title')
    installation_reported_fault = fields.Char(string='Reported Fault')
    installation_parent_ticket_id = fields.Many2one('parent.ticket', string="Parent Ticket ID", copy=False)
    installation_child_ticket_id = fields.Many2one('child.ticket', string="Child Ticket ID", copy=False)
    installation_external_reference = fields.Char(string='External Reference', copy=False)
    installation_service_category_id = fields.Many2one('service.category', string="Service Category", copy=False)
    installation_service_type_id = fields.Many2one('service.type', string="Service Type", copy=False)
    installation_child_ticket_type = fields.Many2one('child.ticket.type', string='Child Ticket Type', copy=False)
    installation_stock_lot_id = fields.Many2one('stock.lot', string="Products/Assets", tracking=True,
                                                track_visibility='onchange')
    installation_categ_id = fields.Many2one('product.category', string='Product Categories')
    installation_customer_id = fields.Many2one('res.partner', string="Customer", help='Customer Group')
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        index=True,
        default=lambda self: self.env.user,
    )
    installation_customer_account_id = fields.Many2one('res.partner', string="Customer Account", copy=False)
    installation_tags = fields.Many2many('sla.tags', string="Tags", copy=False)
    # installation_stock_lot_id = fields.Many2one('stock.lot', string="Serial Number", required=True)
    installation_product_code_no = fields.Char(string="Product Code No")
    installation_product_part = fields.Char(string="Product Part No")
    installation_origin = fields.Char(string='Source Document', readonly=True)
    installation_customer_po_number = fields.Char(string="Customer PO number", copy=False)
    installation_customer_po_date = fields.Date(string="Customer PO Date", default=fields.Date.context_today)
    installation_invoice_number = fields.Char(string="Invoice Number", copy=False)
    installation_invoice_date = fields.Date(string="Invoice Date", default=fields.Date.context_today)
    installation_delivery_number = fields.Many2one('stock.picking', string="Delivery Order Number", copy=False)
    installation_order_date = fields.Datetime('Delivery Order Date')
    service_request_id = fields.Many2one('service.request', string="Service Request")
    installation_state = fields.Selection(
        selection=[("new", "New"), ("asset_update", "Asset Details Updated"), ("asset_update", "Asset Details Updated"),
                   ("started", "Installation Started"), ("in_progress", "Installation In Progress"),
                   ("on_hold", "Installation On hold"), ("waiting_for_approval", "Waiting for Approval"),
                   ("approved", "Approved"), ("rejected", "Rejected"), ("cancelled", "Installation Cancelled"),
                   ("completed", "Installation Completed")], default="new", index=True)
    approver_id = fields.Many2one('multi.approval.type', string="Approval Level", copy=False)
    approver_ids = fields.One2many('installation.approval', 'installation_id', string="Approvers")
    install_status = fields.Selection([('new', 'New'), ('done', 'Done')], string="Installation Status", default='new')
    worksheet_id = fields.Many2one('survey.survey', string="Worksheet")
    team_id = fields.Many2one('crm.team', string="Team", compute='_compute_team_id', store=True, required=True,
                              readonly=False, precompute=True, copy=False, change_default=True, check_company=True,
                              tracking=True,
                              domain="['|', ('company_id', '=', False), ('company_id', '=', company_id),('is_service_request', '=', True)]")
    # request_type_id = fields.Many2one('request.type', string="Request Type", copy=False, required=True)
    is_required_approval = fields.Boolean(string="Approval Required", copy=False)
    image_1920 = fields.Image("Image", copy=False)
    installation_product_serial = fields.Char(string="Serial Number", copy=False)
    install_attachment_ids = fields.Many2many(comodel_name="ir.attachment", relation='installation_ir_attachments_rel',
                                              string="Attachments")
    is_send_for_approvals = fields.Boolean(string="Is Send for Approvals", copy=False)
    approvals_count = fields.Integer(string='Approval Count', compute='_compute_approvals_count')
    expense_count = fields.Integer(string='Expense Count', compute='_compute_expense_count')
    warranty_start_date = fields.Datetime(string="Warranty Start Date")
    warranty_end_date = fields.Datetime(string="Warranty End Date")
    feed_back_end_task_1 = fields.Selection(
        [('5', 'Excellent'), ('4', 'Very Good'), ('3', 'Good'),
         ('2', 'Average'), ('1', 'Poor')],
        string="Call Registration / Co-ordination Process")
    feed_back_end_task_2 = fields.Selection(
        [('5', 'Excellent'), ('4', 'Very Good'), ('3', 'Good'),
         ('2', 'Average'), ('1', 'Poor')],
        string="Response to Service Request")
    feed_back_end_task_3 = fields.Selection(
        [('5', 'Excellent'), ('4', 'Very Good'), ('3', 'Good'),
         ('2', 'Average'), ('1', 'Poor')],
        string="Engineer was equipped for solving time problem")
    feed_back_end_task_4 = fields.Selection(
        [('5', 'Excellent'), ('4', 'Very Good'), ('3', 'Good'),
         ('2', 'Average'), ('1', 'Poor')],
        string="Analysis / explanation by Service Engineer")
    feed_back_end_task_5 = fields.Selection(
        [('5', 'Excellent'), ('4', 'Very Good'), ('3', 'Good'),
         ('2', 'Average'), ('1', 'Poor')],
        string="Overall satisfaction about Stryker products and Service")
    on_hold_reason = fields.Char('On Hold Reason')
    stock_picking_ids = fields.Many2many('stock.picking', string="Domain Delivery Orders",
                                         compute='compute_alternate_stock_ids', store=True)
    spare_request_ids = fields.Many2many('spare.request', string="Spare Request", compute='_compute_spare_request')
    department = fields.Char(string="Department", copy=False)
    tender_ref_number = fields.Char(string="Tender Ref Number", copy=False)
    warranty_invoice_number = fields.Char(string="Warranty Invoice Number", copy=False)
    warranty_invoice_date = fields.Date(string="Warranty Invoice Date", copy=False)
    is_state_close = fields.Boolean(string='Close State')

    # @api.onchange('stock_picking_ids')
    # def onchange_stock_picking_ids_domain(self):
    #     if self.stock_picking_ids == None:
    #         stock_picking = self.stock_picking_ids.mapped('id')
    #         domain = [('id', 'in', stock_picking)]
    #         return {'domain': {'installation_delivery_number': domain}}

    def _compute_spare_request(self):
        lists = []
        for record in self:
            spare_ids = self.env["spare.request"].search(
                [("child_ticket_id", "=", record.installation_child_ticket_id.id)])
            if spare_ids:
                record.spare_request_ids = spare_ids.ids
            else:
                record.spare_request_ids = None

    @api.depends('installation_child_ticket_id')
    def compute_alternate_stock_ids(self):
        for rec in self:
            rec.stock_picking_ids = False
            if rec.installation_child_ticket_id:
                rec.stock_picking_ids = rec.installation_child_ticket_id.replacement_picking_ids.ids
            else:
                rec.stock_picking_ids = None
        if rec .installation_child_ticket_id.state == 'closed':
            rec.is_state_close = True

    @api.onchange('installation_delivery_number')
    def onchange_delivery_order(self):
        if self.installation_delivery_number and self.installation_delivery_number.move_line_ids_without_package:
            new_serial_order = self.installation_delivery_number.move_line_ids_without_package[0]
            self.installation_product_serial = new_serial_order.lot_id.name
            self.installation_product_code_no = new_serial_order.product_id.product_tmpl_id.custom_product_serial
            self.installation_product_part = new_serial_order.product_id.product_tmpl_id.product_part
            self.installation_order_date = self.installation_delivery_number.date_done
        else:
            self.installation_product_serial = self.installation_product_code_no = self.installation_product_part = False

    def action_resume(self):
        self.installation_state = 'in_progress'

    def update_serial_number(self):
        if self.installation_stock_lot_id:
            available_stock = self.env['stock.lot'].search([('name', '=', self.installation_product_serial)])
            if available_stock:
                raise UserError(_("Serial Number is already available"))
            self.installation_stock_lot_id.name = self.installation_product_serial
            self.message_post(body=_("New Serial Number: %s", self.installation_product_serial))

    def action_create_expense(self):
        self.ensure_one()
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Expense',
            'view_mode': 'form',
            'res_model': 'hr.expense',
            'target': 'current',
            'context': {'default_installation_id': self.id, 'default_name': self.name + ' Expense',
                        'default_user_id': employee_id.id if employee_id else None}
        }

    def show_warning_message(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("This process will be released in phase 2!"),
                'type': 'warning',
                'sticky': False,  # True/False will display for few seconds if false
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def action_view_approvals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send for Approvals',
            'view_mode': 'tree,form',
            'res_model': 'multi.approval',
            'domain': [('installation_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def action_view_expense(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Expenses',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense',
            'domain': [('installation_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def _compute_approvals_count(self):
        for record in self:
            record.approvals_count = self.env['multi.approval'].search_count([('installation_id', '=', record.id)])

    def _compute_expense_count(self):
        for record in self:
            record.expense_count = self.env['hr.expense'].search_count([('installation_id', '=', record.id)])

    # Smart Button - Reports
    def action_view_reports(self):
        return True

    # Smart Button - Survey
    def action_view_survey(self):
        return True

    @api.depends('user_id')
    def _compute_team_id(self):
        cached_teams = {}
        for order in self:
            default_team_id = self.env.context.get('default_team_id', False) or order.team_id.id
            user_id = order.user_id.id
            company_id = order.company_id.id
            key = (default_team_id, user_id, company_id)
            if key not in cached_teams:
                cached_teams[key] = self.env['crm.team'].with_context(
                    default_team_id=default_team_id
                )._get_default_team_id(
                    user_id=user_id, domain=[('company_id', 'in', [company_id, False])])
            order.team_id = cached_teams[key]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_project_installation') is True and not vals.get('name') or vals['name'] == _('New'):
                sequence = self.env['ir.sequence'].next_by_code('sr.installation')
                vals['name'] = sequence
        return super(ProjectTask, self).create(vals_list)

    def action_start_installation(self):
        self.installation_state = 'started'

    def action_in_progress_installation(self):
        self.installation_state = 'in_progress'

    def action_complete_installation(self):
        return {
            'name': _('Installation Feedback'),
            'view_mode': 'form',
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('ppts_project_sr_installation.view_complete_installation_feedback').id,
            'target': 'new',
            'res_id': self.id
        }

    def action_complete_installation_wiz(self):
        # mails = ''
        # # Update the below fields value on the parent form.
        # #Product Code No, Installation Date
        # template_id = self.env.ref('ppts_parent_ticket.mail_template_installation_completed_child_ticket')
        # child_template_id = self.env.ref('ppts_parent_ticket.mail_template_closed_child_ticket')
        # for team_ids in self.installation_child_ticket_id.child_configuration_id.alert_installation_approval_team_ids:
        #     teams = team_ids.mapped('member_ids.login')
        #     mails += ', '.join(teams)
        # if template_id:
        #     template_id.with_context(email_to=mails).sudo().send_mail(self.installation_child_ticket_id.id, force_send=True)
        # if child_template_id:
        #     child_template_id.with_context(email_to=mails).sudo().send_mail(self.installation_child_ticket_id.id, force_send=True)
        if self.installation_stock_lot_id and self.installation_end_date and self.installation_start_date:
            self.installation_stock_lot_id.installation_date = self.installation_start_date
            self.installation_stock_lot_id.installation_end_date = self.installation_end_date
            self.installation_child_ticket_id.installation_date = self.installation_start_date
            self.installation_child_ticket_id.installation_end_date = self.installation_end_date
        else:
            raise UserError(_("Installation dates is not available !"))
        self.installation_parent_ticket_id.sudo().product_code_no = self.installation_product_code_no
        self.installation_parent_ticket_id.sudo().installation_date = self.installation_start_date
        self.installation_parent_ticket_id.sudo().installation_end_date = self.installation_end_date
        self.installation_parent_ticket_id.sudo().warranty_start_date = self.warranty_start_date
        self.installation_parent_ticket_id.sudo().warranty_end_date = self.warranty_end_date
        self.installation_child_ticket_id.warranty_start_date = self.warranty_start_date
        self.installation_child_ticket_id.warranty_end_date = self.warranty_end_date
        self.installation_state = 'completed'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Request',
            'view_mode': 'tree,form',
            'res_model': 'child.ticket',
            'domain': [('id', '=', self.installation_child_ticket_id.id)],
            'context': "{'create': False}"
        }

    def action_ready_for_testing_installation(self):
        return self.show_warning_message()

    def action_ready_for_qc_installation(self):
        return self.show_warning_message()

    def action_return_installation(self):
        return self.show_warning_message()

    # Need to remove after discussing with customer
    # def action_request_approval_installation(self):
    #     self.ensure_one()
    #     return {
    #         'name': _('Send for Approval'),
    #         'view_mode': 'form',
    #         'res_model': 'installation.approval',
    #         'type': 'ir.actions.act_window',
    #         'target': 'new',
    #     }

    def action_return_spares_installation(self):
        return self.show_warning_message()

    def action_update_asset_installation(self):
        return self.show_warning_message()

    def action_generate_report_installation(self):
        return self.env.ref('ppts_parent_ticket.report_esskay_config').report_action(self.installation_child_ticket_id)



    def action_send_mail(self):
        return self.show_warning_message()

    def action_cancel_installation(self):
        self.installation_state = 'cancelled'

    def _check_user_exist(self):
        if self.env['installation.approval'].search(
                [('user_id', '=', self.env.user.id), ('installation_id', '=', self.id)]):
            return True
        else:
            return False

    def _show_notification(self, message):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ('Pay attention'),
                'message': message,
                'type': 'danger',
                'sticky': False,
            },
        }
        return notification

    def write(self, vals):
        result = super(ProjectTask, self).write(vals)
        if 'installation_state' in vals:
            if self.is_project_installation:
                description = ''
                task_id = None
                if self.installation_parent_ticket_id or self.installation_child_ticket_id:
                    if self.installation_state == 'started':
                        task_id = self.env.ref('ppts_custom_workflow.task_data_create_installation')
                    elif self.installation_state == 'in_progress':
                        task_id = self.env.ref('ppts_custom_workflow.task_data_installation_inprogress')
                    elif self.installation_state == 'waiting_for_approval':
                        task_id = self.env.ref('ppts_custom_workflow.task_data_installation_waiting_for_approval')
                    elif self.installation_state == 'approved':
                        task_id = self.env.ref('ppts_custom_workflow.task_data_installation_approved')
                    elif self.installation_state == 'rejected':
                        task_id = self.env.ref('ppts_custom_workflow.task_data_installation_rejected')
                    elif self.installation_state == 'completed':
                        task_id = self.env.ref('ppts_custom_workflow.task_data_installation_completed')
                    elif self.installation_state == 'cancelled':
                        task_id = self.env.ref('ppts_custom_workflow.task_data_installation_cancelled')
                    elif self.installation_state == 'asset_update':
                        task_id = self.env.ref('ppts_custom_workflow.task_data_installation_asset_details_updated')
                    elif self.installation_state == 'on_hold':
                        task_id = self.env.ref('ppts_custom_workflow.task_data_installation_installation_on_hold')
                        description = self.on_hold_reason
                if task_id:
                    ticket_id = None
                    if self.installation_child_ticket_id:
                        ticket_id = self.env["child.ticket"].search([("id", "=", self.installation_child_ticket_id.id)])
                    elif self.installation_parent_ticket_id:
                        ticket_id = self.env["parent.ticket"].search(
                            [("id", "=", self.installation_parent_ticket_id.id)])
                    if ticket_id:
                        ticket_id.update({
                            'task_list_ids': [(0, 0, {'task_id': task_id.id,
                                                      'status': description})],
                        })
            # CT Configuration Notification
            if self.installation_child_ticket_id.child_configuration_id:
                approver_email = ''
                if self.installation_child_ticket_id.child_configuration_id.is_auto_send_report_installation and self.installation_child_ticket_id.child_configuration_id.is_installation:
                    if self.installation_state in ['completed',
                                                   'cancelled'] and self.installation_child_ticket_id.child_configuration_id.alert_installation_approval_team_ids:
                        invoice_report = self.env.ref('ppts_parent_ticket.report_esskay_config')
                        data_record = base64.b64encode(
                            self.env['ir.actions.report'].sudo()._render_qweb_pdf(invoice_report, [
                                self.installation_child_ticket_id.id], data=None)[0])
                        ir_values = {
                            'name': self.name,
                            'type': 'binary',
                            'datas': data_record,
                            'store_fname': data_record,
                            'mimetype': 'application/pdf',
                            'res_model': 'child.ticket',
                        }
                        report_attachment_id = self.env['ir.attachment'].sudo().create(ir_values)
                        alert_installation_email_template_id = self.installation_child_ticket_id.child_configuration_id.alert_installation_email_template_id
                        alert_installation_email_template_id.attachment_ids.unlink()
                        alert_installation_email_template_id.attachment_ids = [(4, report_attachment_id.id)]
                        if alert_installation_email_template_id:
                            teams = self.env['hr.employee'].search([('job_id', 'in',
                                                                     self.installation_child_ticket_id.child_configuration_id.alert_installation_approval_team_ids.ids)]).mapped(
                                'work_email')
                            approver_email += ', '.join(teams)
                            alert_installation_email_template_id.with_context(email_to=approver_email).sudo().send_mail(
                                self.installation_child_ticket_id.id, force_send=True)
        return result


class MultiApproval(models.Model):
    _inherit = 'multi.approval'

    installation_id = fields.Many2one('project.task', string="Installation ID", copy=False)

    def action_approve(self):
        values = super(MultiApproval, self).action_approve()
        installation_id = self.env['project.task'].sudo().search([('id', '=', self.installation_id.id)])
        if all(x.state == 'Approved' for x in self.line_ids):
            installation_id.installation_state = 'approved'
        return values

    def action_refuse(self, reason=''):
        values = super(MultiApproval, self).action_refuse(reason='')
        installation_id = self.env['project.task'].sudo().search([('id', '=', self.installation_id.id)])
        if all(x.state == 'Refused' for x in self.line_ids):
            installation_id.installation_state = 'rejected'
        return values
