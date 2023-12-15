from odoo import models, fields, api, _
from datetime import datetime, date, timedelta

from odoo.exceptions import UserError


class SRMaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    name = fields.Char(string="Subject", required=True, copy=False, readonly=True, default=lambda self: _('New'))
    is_sr_maintenance = fields.Boolean('Is SR-Maintenance', help='Segregate SR Maintenance Orders')
    maintenance_process_alias_id = fields.Char(string="Maintenance Process ID Alias", copy=False)
    maintenance_install_start_date = fields.Date(string="Maintenance Installation Start date",
                                                 default=fields.Date.context_today)
    maintenance_install_end_date = fields.Date(string="Maintenance Installation End date",
                                               default=fields.Date.context_today)
    title = fields.Char(string="Title", required=True)
    reported_fault = fields.Char(string="Reported Fault", copy=False)
    parent_ticket_id = fields.Many2one('parent.ticket', string="Parent Ticket ID", copy=False)
    child_ticket_id = fields.Many2one('child.ticket', string="Child Ticket ID", copy=False)
    external_reference = fields.Char(string="External Reference")
    service_category_id = fields.Many2one('service.category', string="Service Category", copy=False)
    service_type_id = fields.Many2one('service.type', string="Service Type", copy=False)
    child_ticket_type_id = fields.Many2one('child.ticket.type', string="Child Ticket Type", copy=False)
    product_id = fields.Many2one('product.product', 'Products/Assets', copy=False)
    categ_id = fields.Many2one('product.category', 'Product Categories', copy=False)
    # Customer Details
    partner_id = fields.Many2one('res.partner', string="Customer", copy=False)
    customer_account_id = fields.Many2one('res.partner', string="Customer Account",
                                          related='partner_id.customer_account_id')
    team_id = fields.Many2one('crm.team', string='Team', copy=False)
    #
    asset_tag_ids = fields.Many2many('asset.tag', string="Tags")
    stock_lot_id = fields.Many2one('stock.lot', string="Asset Lot/Serial Number", copy=False)
    product_code_no = fields.Char(string='Product Code No.', copy=False)
    cat_no = fields.Char(string='Product Part No', copy=False)
    worksheet_id = fields.Many2one('survey.survey', string="Worksheet", copy=False)
    image_1920 = fields.Image("Image", copy=False)
    origin = fields.Char("Source Document", copy=False, readonly=True)
    po_number = fields.Char(string="PO Number", copy=False)
    po_date = fields.Datetime(string="PO Date", copy=False)
    invoice_number = fields.Datetime(string="Invoice Number", copy=False)
    invoice_date = fields.Datetime(string="Invoice Date", copy=False)
    warranty_status = fields.Selection([('in_oem_warranty', 'In OEM Warranty'), ('out_oem_warranty', 'OO OEM Warranty'),
                                        ('not_available', 'Not available')], string='Warranty Status')
    warranty_end_date = fields.Date(string="Warranty End Date", copy=False)
    extended_warranty_status = fields.Selection(
        [('in_repair_warranty', 'In Warranty'), ('out_repair_warranty', 'OO Warranty'),
         ('not_available', 'Not available')], string='Extended Warranty Status')
    extended_warranty_end_date = fields.Date(string="Extended Warranty End Date", copy=False)
    amc_status = fields.Char(string='AMC Status', copy=False)
    amc_end_date = fields.Date(string="AMC End Date", copy=False)
    cmc_status = fields.Char(string='CMC Status', copy=False)
    cmc_end_date = fields.Date(string="CMC End Date", copy=False)
    is_amc = fields.Boolean('AMC Check', compute='_compute_service_category_id_check')
    is_cmc = fields.Boolean('CMC Check', compute='_compute_service_category_id_check')
    maintenance_properties_definition = fields.Properties('Properties',
                                                          definition='partner_id.service_ticket_properties', copy=True)
    # Extra
    # approver_id = fields.Many2one('multi.approval.type', string="Approval Level", copy=False)
    approver_ids = fields.One2many('maintenance.approval', 'maintenance_id', string="Approvers")
    # request_type_id = fields.Many2one('request.type', string="Request Type", copy=False, required=True)
    # is_required_approval = fields.Boolean(string="Request Type", copy=False, related="request_type_id.is_required_approval")
    service_request_id = fields.Many2one('service.request', string="Service Request")
    maintenance_state = fields.Selection(
        [('new', 'New Request'), ('started', 'Maintenance Started'), ('in_progress', 'Maintenance In Progress'),
         ('waiting_for_approval', 'Waiting for Approval'),
         ('approved', 'Approved'), ('rejected', 'Rejected'), ('spare_requested', 'Spare Requested'),
         ('spare_received', 'Spare Parts Received'), ('spare_returned', 'Spare Parts Returned'),
         ('warranty_void', 'Warranty Void'), ('worksheet_completed', 'Worksheet Completed'),
         ('rescheduled', 'Maintenance Rescheduled'), ('on_hold', 'Maintenance  On hold'),
         ('cancelled', 'Maintenance  Cancelled'), ('completed', 'Maintenance Completed')], default='new',
        string="Status")
    service_request_count = fields.Integer(compute='compute_service_count')
    custom_product_serial = fields.Char(string="Serial Number", copy=False)
    action_taken_site = fields.Char(string="Action Taken at Site", copy=False)
    maintenance_attachment_ids = fields.Many2many(comodel_name="ir.attachment",
                                                  relation='maintenance_ir_attachments_rel',
                                                  string="Attachments")
    is_send_for_approvals = fields.Boolean(string="Is Send for Approvals", copy=False, compute='_get_approval')
    approvals_count = fields.Integer(string='Approval Count', compute='_compute_approvals_count')
    text_customer_observations = fields.Html(string='Text')
    text_engineer_observations = fields.Html(string='Text')
    text_recommend_observations = fields.Html(string='Text')
    maintenance_asset_ids = fields.Many2many('stock.lot', string="Maintenance Assets")


    @api.depends('service_category_id')
    def _compute_service_category_id_check(self):
        # When you select the category based on these fields will be shown.
        for rec in self:
            # If the service category code is 'AMC', set is_amc to True, otherwise set it to False
            if rec.service_category_id.code == 'AMC':
                rec.is_amc = True
            else:
                rec.is_amc = False
            if rec.service_category_id.code == 'CMC':
                rec.is_cmc = True
            else:
                rec.is_cmc = False

    @api.onchange('partner_id', 'service_category_id', 'stock_lot_id')
    def partner_amc_cmc_status_check(self):
        contract_ids = self.env['contract.contract'].search(
            [('partner_id', '=', self.partner_id.id), ('date_start', '<=', date.today()), ('state', '=', 'started'),
             ('date_end', '>=', date.today())])
        if contract_ids:
            for contract in contract_ids:
                if contract.custom_contract_type == 'amc':
                    self.cmc_status = 'out_warranty'
                    self.amc_status = 'in_warranty'
                elif contract.custom_contract_type == 'cmc':
                    self.cmc_status = 'in_warranty'
                    self.amc_status = 'out_warranty'
                if contract:
                    self.amc_end_date=contract.date_end
                    self.cmc_end_date=contract.date_end
                    self.po_number=contract.ccc_ref.name
                    self.po_date=contract.ccc_ref.date_order
                    self.invoice_number=contract.ccc_ref.invoice_ids.name
                    self.invoice_date=contract.ccc_ref.invoice_ids.invoice_date
                else:
                    self.cmc_status = 'out_warranty'
                    self.amc_status = 'out_warranty'
                    self.amc_end_date= False
                    self.cmc_end_date = False
                    self.po_number = False
                    self.po_date=False
                    self.invoice_number = False
                    self.invoice_date = False



        else:
            self.amc_status = False
            self.cmc_status = False

    def _get_approval(self):
        for record in self:
            record.is_send_for_approvals = False
            if record.sudo().child_ticket_id:
                if record.sudo().child_ticket_id.child_configuration_id.is_approval_required_maintenance:
                    record.is_send_for_approvals = True

    def action_cancel(self):
        self.archive_equipment_request()
        self.maintenance_state = 'cancelled'

    def action_reset_maintenance(self):
        self.reset_equipment_request()
        self.maintenance_state = 'rescheduled'

    def action_view_approvals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send for Approvals',
            'view_mode': 'tree,form',
            'res_model': 'multi.approval',
            'domain': [('maintenance_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def _compute_approvals_count(self):
        for record in self:
            record.approvals_count = self.env['multi.approval'].search_count([('maintenance_id', '=', record.id)])

    # Smart Button - Reports
    def action_view_reports(self):
        return True

    # Smart Button - Survey
    def action_view_survey(self):
        return True

    @api.onchange('stock_lot_id')
    def _onchange_stock_lot_id(self):
        for record in self:
            stock_lot_obj = self.env['stock.lot'].search([('name', '=', record.stock_lot_id.name)])
            # warranty
            warranty_check_false = stock_lot_obj.filtered(lambda x: x.oem_warranty_check == False)
            warranty_check_true = stock_lot_obj.filtered(lambda x: x.oem_warranty_check == True)
            # repair
            repair_check_false = stock_lot_obj.filtered(lambda x: x.oem_repair_warranty_check == False)
            repair_check_true = stock_lot_obj.filtered(lambda x: x.oem_repair_warranty_check == True)

            if record.stock_lot_id:
                if warranty_check_false:
                    record.warranty_status = 'not_available'
                if repair_check_false:
                    record.extended_warranty_status = 'not_available'
                if warranty_check_true:
                    oem_warranty = warranty_check_true.search(
                        [('name', '=', record.stock_lot_id.name), ('warranty_start_date', '<=', date.today()),
                         ('warranty_end_date', '>=', date.today())])
                    if oem_warranty:
                        record.warranty_status = 'in_oem_warranty'
                    else:
                        record.warranty_status = 'out_oem_warranty'
                if repair_check_true:
                    oem_repair = repair_check_true.search(
                        [('name', '=', record.stock_lot_id.name), ('extended_warranty_start_date', '<=', date.today()),
                         ('extended_warranty_end_date', '>=', date.today())])
                    if oem_repair:
                        record.extended_warranty_status = 'in_repair_warranty'
                    else:
                        record.extended_warranty_status = 'out_repair_warranty'
            else:
                record.warranty_status = ''
                record.extended_warranty_status = ''

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New') and vals.get('is_sr_maintenance') is True:
                sequence = self.env['ir.sequence'].next_by_code('sr.maintenance')
                vals['name'] = sequence
        rec = super(SRMaintenanceRequest, self).create(vals_list)
        for vals in vals_list:
            if 'maintenance_state' in vals and rec.child_ticket_id:
                task_id = None
                if rec.maintenance_state == 'started':
                    task_id = self.env.ref('ppts_maintenanace.task_data_maintenance_started')
                if task_id:
                    rec.child_ticket_id.sudo().update({
                        'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                    })
            return rec

    # @api.model_create_multi
    def write(self, vals_list):
        rec = super(SRMaintenanceRequest, self).write(vals_list)
        if 'maintenance_state' in vals_list:
            if self.child_ticket_id.child_configuration_id:
                email = ''
                approver_email = ''
                if self.child_ticket_id.child_configuration_id.is_auto_send_report_maintenance and self.child_ticket_id.child_configuration_id.is_maintenance:
                    if self.maintenance_state in ['completed',
                                                  'cancelled'] and self.child_ticket_id.child_configuration_id.alert_maintenance_approval_team_ids:
                        alert_email_template_id = self.child_ticket_id.child_configuration_id.alert_maintenance_email_template_id
                        if alert_email_template_id:
                            teams = self.env['hr.employee'].search([('job_id', 'in',
                                                                     self.child_ticket_id.child_configuration_id.alert_maintenance_approval_team_ids.ids)]).mapped(
                                'work_email')
                            email += ', '.join(teams)
                            alert_email_template_id.with_context(email_to=email).sudo().send_mail(
                                self.child_ticket_id.id, force_send=True)
                        if alert_email_template_id and self.child_ticket_id.child_configuration_id.is_approval_required_maintenance and self.maintenance_state == 'waiting_for_approval':
                            for teams in self.child_ticket_id.child_configuration_id.maintenance_approval_team_ids:
                                teams = teams.mapped('line_ids.user_id.login')
                                approver_email += ', '.join(teams)
                            alert_email_template_id.with_context(email_to=approver_email).sudo().send_mail(
                                self.child_ticket_id.id, force_send=True)

            # Task Update for Child Ticket
            task_id = None
            last_task_id = []
            task_ids = self.child_ticket_id.task_list_ids.mapped("task_id")
            for task in task_ids:
                last_task_id.append(task.id)
            last_id = last_task_id.pop() if last_task_id else None
            if 'maintenance_state' in vals_list and self.parent_ticket_id or self.child_ticket_id:
                if self.maintenance_state == 'started':
                    task_id = self.env.ref('ppts_maintenanace.task_data_maintenance_started')
                elif self.maintenance_state == 'in_progress':
                    task_id = self.env.ref('ppts_maintenanace.task_data_maintenance_in_progress')
                elif self.maintenance_state == 'completed':
                    task_id = self.env.ref('ppts_maintenanace.task_data_maintenance_completed')
                elif self.maintenance_state == 'on_hold':
                    task_id = self.env.ref('ppts_maintenanace.task_data_maintenance_on_hold')
                elif self.maintenance_state == 'cancelled':
                    task_id = self.env.ref('ppts_maintenanace.task_data_maintenance_cancelled')
                elif self.maintenance_state == 'rescheduled':
                    task_id = self.env.ref('ppts_maintenanace.task_data_maintenance_rescheduled')

                if task_id and not task_id.id == last_id and self.child_ticket_id:
                    self.child_ticket_id.sudo().update({
                        'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                    })

        return rec

    def action_start_process(self):
        self.maintenance_state = 'started'

    def action_in_progress(self):
        self.maintenance_state = 'in_progress'

    def action_complete(self):
        self.maintenance_state = 'completed'

    def action_ready_for_testing(self):
        pass

    def action_ready_for_qc(self):
        pass

    def action_return(self):
        pass

    def action_on_hold(self):
        user_exist = self._check_user_exist()
        if user_exist:
            if self.approver_ids.filtered(
                    lambda record: record.state == 'approved' and record.user_id.id == self.env.user.id):
                raise UserError(_('You have approved the ticket already !'))
            return {
                'name': "Reason",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'maintenance.reason',
                'target': 'new',
                'context': {'default_reason_type': 'hold'}
            }
        else:
            return self._show_notification('You are not allowed to hold this Maintenance' + ' ' + self.name)

    def action_request_approval(self):
        if self.sudo().child_ticket_id:
            if self.sudo().child_ticket_id.child_configuration_id.is_approval_required_maintenance and self.sudo().child_ticket_id.child_configuration_id.maintenance_approval_team_ids:
                approval_type_id = self.sudo().child_ticket_id.child_configuration_id.maintenance_approval_team_ids[
                    -1].id
                request = {
                    'name': self.name,
                    'type_id': approval_type_id or False,
                    'maintenance_id': self.id,
                }
                requests = self.env['multi.approval'].create(request)
                requests.action_submit()
                self.maintenance_state = 'waiting_for_approval'
        return True

    def action_approved(self):
        user_exist = self._check_user_exist()
        if user_exist:
            for approver_id in self.env['maintenance.approval'].search(
                    [('user_id', '=', self.env.user.id), ('maintenance_id', '=', self.id)]):
                if approver_id.state == 'approved':
                    raise UserError(_("Already this has been approved on %s" % approver_id.create_date.date()))
                else:
                    approver_id.state = 'approved'
                    approver_id.approved_on = fields.Date.today()
            # Check whether all are approved if not then should not change the service request status
            if any(record.state != 'approved' for record in self.approver_ids):
                pass
            else:
                self.maintenance_state = 'approved'
        else:
            return self._show_notification('You are not allowed to approve this Maintenance' + ' ' + self.name)

    def action_reject(self):
        user_exist = self._check_user_exist()
        if user_exist:
            if self.approver_ids.filtered(
                    lambda record: record.state == 'approved' and record.user_id.id == self.env.user.id):
                raise UserError(_('You have approved the ticket already !'))
            return {
                'name': "Reason",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'maintenance.reason',
                'target': 'new',
                'context': {'default_reason_type': 'reject'}
            }
        else:
            return self._show_notification('You are not allowed to reject this Maintenance' + ' ' + self.name)

    def action_return_spares(self):
        pass

    def action_request_spares(self):
        pass

    def action_generate_report(self):
        pass

    def _check_user_exist(self):
        if self.env['maintenance.approval'].search(
                [('user_id', '=', self.env.user.id), ('maintenance_id', '=', self.id)]):
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

    def action_service_request_maintenance(self):
        context = {
            'maintenance_id': self.id,
            'customer_name': self.partner_id.name,
            'partner_id': self.partner_id.id or False,
            # 'customer_account_id': self.partner_id.customer_account_id.id or False,
            'service_category_id': self.service_category_id.id or False,
            'service_type_id': self.service_type_id.id or False,
            'product_name': self.product_id.name,
            'custom_product_serial': self.product_id.custom_product_serial,
            'product_category_id': self.categ_id.name,
            # 'request_type_id': self.request_type_id.id or False,
            'child_ticket_id': self.child_ticket_id.id or False,
            'parent_ticket_id': self.parent_ticket_id.id or False,
            'team_id': self.team_id.id or False,
            'external_reference': self.external_reference,
            'problem_reported': self.reported_fault or '',
            'survey_id': self.worksheet_id.id or False,
            'customer_asset_ids': [(0, 0, {
                'stock_lot_id': self.stock_lot_id.id,
                'product_id': self.product_id.id,
            })],
        }
        order = self.env['service.request'].create(context)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Request',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'service.request',
            'res_id': order.id,
            'target': 'current',
        }

    def action_view_service_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Request',
            'view_mode': 'tree,form',
            'res_model': 'service.request',
            'domain': [('maintenance_id', '=', self.id)],
            'context': "{'create': False}"
        }

    # Service Request Count
    def compute_service_count(self):
        for record in self:
            record.service_request_count = self.env['service.request'].search_count(
                [('maintenance_id', '=', record.id)])

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


class ServiceRequest(models.Model):
    _inherit = 'service.request'

    maintenance_id = fields.Many2one('maintenance.request', string="Maintenance ID")


class MultiApproval(models.Model):
    _inherit = 'multi.approval'

    maintenance_id = fields.Many2one('maintenance.request', string="Maintenance ID", copy=False)

    def action_approve(self):
        values = super(MultiApproval, self).action_approve()
        maintenance = self.env['maintenance.request'].sudo().search([('id', '=', self.maintenance_id.id)])
        if all(x.state == 'Approved' for x in self.line_ids):
            maintenance.maintenance_state = 'approved'
        return values

    def action_refuse(self, reason=''):
        values = super(MultiApproval, self).action_refuse(reason='')
        maintenance = self.env['maintenance.request'].sudo().search([('id', '=', self.maintenance_id.id)])
        if all(x.state == 'Refused' for x in self.line_ids):
            maintenance.maintenance_state = 'rejected'
        return values
