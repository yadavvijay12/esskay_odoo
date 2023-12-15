# -*- coding: utf-8 -*-
#############################################################################
#
#    Point Perfect Technology Solutions.
#
#############################################################################
from datetime import date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import pytz
import re
import datetime


class ChildTicket(models.Model):
    _name = 'child.ticket'
    _rec_name = 'name'
    _description = "Child Ticket"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_next_task_ids(self):
        tasks_all_ids = self.env["tasks.master"].search([])
        return tasks_all_ids.ids

    name = fields.Char(string='Child Ticket ID', copy=False, default="New")
    child_ticket_id_alias = fields.Char(string='Child Ticket ID Alias', copy=False)
    child_configuration = fields.Char(string='Child Configuration', copy=False)
    child_ticket_type_id = fields.Many2one('child.ticket.type', string="Child Ticket Type", copy=False,
                                           compute='_child_ticket_type_check')
    partner_id = fields.Many2one('res.partner', string="Customer", copy=False)
    customer_street = fields.Char(copy=False)
    customer_street2 = fields.Char(copy=False)
    customer_zip = fields.Char(change_default=True, copy=False)
    customer_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', copy=False)
    customer_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', copy=False)
    customer_country_code = fields.Char(related='customer_country_id.code', string="Country Code", copy=False)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('child.ticket'))
    call_source_id = fields.Many2one('call.source', string="Call Source", copy=False)
    call_date = fields.Datetime(string="Call Date", default=fields.Datetime.now)
    service_category_id = fields.Many2one('service.category', string="Parent Service Category", copy=False)
    service_type_id = fields.Many2one('service.type', string="Parent Service Type", copy=False)
    product_id = fields.Many2one('product.product', string="Product", copy=False)
    product_part_number = fields.Char(string='Product Part No')
    product_code_no = fields.Char(string='Product Code No', related="product_id.product_code")
    # asset_serial_number = fields.Char(string='Asset Serial No')
    stock_lot_id = fields.Many2one('stock.lot', string="Asset Serial No", required=True)
    categ_id = fields.Many2one('product.category', 'Product Category', copy=False)
    product_category_id_alias = fields.Char(string='Product Category ID Alias', copy=False)
    problem_description = fields.Text(string='Problem Description', copy=False)
    requested_by_name_child = fields.Char(string='Requested by - Name', copy=False, help='Contact/Text')
    requested_by_contact_number = fields.Char(string='Requested by - Contact number', copy=False, help='Contact/Text')
    requested_by_email_ct = fields.Char(string='Requested by - Email')
    requested_by_title_ct = fields.Char(string='Requested by - Title')
    remarks = fields.Text(string='Remarks', copy=False, tracking=True)
    installation_date = fields.Datetime(string="Installation Start Date")
    installation_end_date = fields.Datetime(string="Installation Start Date")
    dealer_distributor_id = fields.Many2one('res.partner', string="Dealer / Distributor Name", copy=False,
                                            compute='_compute_partner_dealer_check', compute_sudo=True)
    call_received_id = fields.Many2one('call.received', string="Call Received by", copy=False)
    alternate_contact_name = fields.Char(string='Alternate Contact name', copy=False)
    alternate_contact_number = fields.Char(string='Alternate Contact number', copy=False)
    alternate_contact_email = fields.Char(string='Alternate Contact Email')

    # team_id = fields.Many2one('crm.team', string="Team", copy=False)
    customer_account_id = fields.Many2one('res.partner', string="Customer Account", copy=False)
    service_request_id = fields.Many2one('service.request', string="Service Request ID", copy=False)
    faulty_section = fields.Char(string='Faulty Section', copy=False)
    sow = fields.Char(string='SOW', copy=False)
    webdelata_id = fields.Char(string='Webdelta ID', copy=False)
    webdelata = fields.Char(string='Webdelta', copy=False)
    mc_stk = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='MC-STK')
    state = fields.Selection(
        [('new', 'New'), ('in_review', 'In Review'), ('waiting_for_approval', 'Waiting for approval'),
         ('approved', 'Approved'), ('rejected', 'Rejected'), ('closed', 'Closed'), ('re_open', 'Re Opened'),
         ('cancel', 'Cancel')],
        string='Status', default='new')
    description = fields.Html("Description", translate=True, sanitize=False)
    parent_ticket_id = fields.Many2one('parent.ticket', string="Parent Ticket ID", readonly=True)
    child_ticket_attachments = fields.Many2many(comodel_name="ir.attachment",
                                                relation='child_ticket_ir_attachments_rel', string="Attachments")
    child_assign_engineer_ids = fields.Many2many(comodel_name='res.users', relation='child_ticket_assign_engineer_rel',
                                                 string="Engineer")
    child_ticket_asset_ids = fields.One2many('child.ticket.asset.line', 'child_ticket_id', string='Assets')
    child_ticket_properties = fields.Properties('Properties',
                                                definition='product_id.child_ticket_properties_definition', copy=True)

    current_asset_location = fields.Many2one('stock.location', string='Current Asset Location', copy=False,
                                             compute='_compute_stock_lot_id_check')
    service_request_count = fields.Integer(compute='compute_service_count')
    task_list_ids = fields.One2many('tasks.master.line', 'child_ticket_id', string="Task Lists")
    child_configuration_id = fields.Many2one('child.ticket.configuration', string='Child Configuration', copy=False,
                                             required=True)
    approver_id = fields.Many2one('multi.approvalmulti.type', string="Approval Level", copy=False)
    approver_ids = fields.One2many('service.ticket.approval', 'child_ticket_id', string="Approvers")
    close_reason = fields.Text('Close Reason', help="While close the ticket this field will have the details.")
    close_date = fields.Datetime('Closed Date', readonly=True, copy=False)
    request_type_id = fields.Many2one('request.type', string="Approval Type", copy=False, required=True)
    is_required_approval = fields.Boolean(string="Approval Type", copy=False,
                                          related="request_type_id.is_required_approval")
    user_id = fields.Many2one('res.users', string='Responsible', required=False, default=lambda self: self.env.user.id)
    team_id = fields.Many2one('crm.team', string="Team", store=True, required=True, copy=False, check_company=True,
                              tracking=True)
    is_assign_to_user = fields.Boolean(string="Is Assign to User", copy=False)
    is_request_reassign = fields.Boolean(string="Is Request Reassign", copy=False, default=True)
    next_task_ids = fields.Many2many('tasks.master', string="Next Tasks", default=_default_next_task_ids)
    request_count = fields.Integer(compute='compute_request_count')
    origin = fields.Char('Origin', default=False, readonly=True,
                         help="This field will be updated, if any child ticket is creating from the the parent ticket.")

    # SLA
    sla_polices_ids = fields.One2many('sla.policies', 'child_ticket_id', string="SLA Status", compute='_sla_apply')
    sla_deadline = fields.Datetime("SLA Deadline", compute_sudo=True, store=True)
    sla_deadline_date = fields.Date("SLA Deadline Date", compute_sudo=True, store=True)
    is_send_for_approvals = fields.Boolean(string="Is Send for Approvals")
    transfer_count = fields.Integer(string="Transfer Count", compute='_compute_transfer_count')
    approvals_count = fields.Integer(string='Approval Count', compute='_compute_approvals_count')

    is_create_loaner = fields.Boolean(string="Is Create Loaner")
    is_create_installation = fields.Boolean(string="Is Create Installation")
    is_installation_created = fields.Boolean(string="Is Installation Created")
    installation_id = fields.Many2one('project.task', string="Installation ID")
    installation_count = fields.Integer(compute='_count_total_installation')

    request_type = fields.Char(compute='get_request_ticket_type', string="Request Ticket Type")
    is_auto_approval = fields.Boolean(string="Auto Approval", copy=False, related="request_type_id.is_auto_approval")
    is_ar_hold_tick = fields.Boolean(string="Is AR Hold/Release")
    is_ar_hold = fields.Boolean(string="Is AR Hold")
    is_pt_ticket = fields.Boolean(string="Is Create Tickets")
    active = fields.Boolean(string='active', default=True)

    is_pi_true = fields.Boolean(string="PI Required True", copy=False)
    version = fields.Char(string="Version", default='00')

    historical_data_line = fields.One2many(comodel_name='assets.historical.data', inverse_name='ref_ticket_id',
                                           string="Asset Historical Data", copy=True, auto_join=True)

    inward_order_count = fields.Integer(compute='count_inward_order')
    cancel_reason = fields.Char(string="Reason")
    alternate_contact_id = fields.Many2one('res.partner', string="Alternate Contact")
    price_available_in_contract = fields.Char(string='Price available in Contract')
    re_repair = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Re-Repair')
    repair_center_location_id = fields.Char(string="Repair Center Location")
    repair_location_id = fields.Many2one('stock.warehouse', string="Repair Center Location")
    parent_ticket_id_alias = fields.Char(string='Ticket ID Alias')
    parent_ticket_id_alias_date = fields.Date(string='Ticket ID Alias Date')
    action_taken_at_site = fields.Char(string='Action taken at Site', copy=False)
    parent_child_ticket_id = fields.Many2one('child.ticket', string='Parent Child Ticket', copy=False)
    task_value_notify = fields.Many2one('tasks.master', string="Notify Task")
    parent_count = fields.Integer(compute='_compute_parent_count')
    new_create_child_ticket = fields.Char(string='Id', related='parent_ticket_id.child_ticket_ids.name',
                                          order='id desc')
    is_inventory_checks = fields.Boolean(string="Inventory Check")
    is_spare_checks = fields.Boolean(string="Spare Check")
    is_loaners_checks = fields.Boolean(string="Spare Check")
    is_disable_status_update = fields.Boolean(string="Disable Status update", copy=False)
    job_closed_date = fields.Datetime(string="Job Closed Date")
    engineer_reason = fields.Char(string='Engineer Reason', copy=False, tracking=True)
    customer_region_id = fields.Many2one('customer.region', string="Customer Region")
    present_engineer_id = fields.Many2one('res.users', string='Current Enginner', copy=False)
    approved_date = fields.Datetime(string="Approved Date", compute='action_approved_approver')

    # Warranty

    oem_warranty_status_id = fields.Many2one('oem.warranty.status', string="OEM Warranty Status (As per customer)",
                                             copy=False)
    repair_warranty_status_id = fields.Many2one('repair.warranty.status',
                                                string="Repair Warranty Status (As per customer)", copy=False)
    oem_warranty_status = fields.Selection(
        [('in_oem_warranty', 'In OEM Warranty'), ('out_oem_warranty', 'Out Of OEM Warranty'),
         ('not_available', 'Not available')], string='OEM Warranty Status')
    oem_repair_status = fields.Selection(
        [('in_repair_warranty', 'In Repair Warranty'), ('out_repair_warranty', 'Out Of Repair Warranty'),
         ('not_available', 'Not available')], string='Repair Warranty Status')
    extended_warranty_status = fields.Selection(
        [('in_repair_warranty', 'In Warranty'), ('out_repair_warranty', 'Out Of Warranty'),
         ('not_available', 'Not available')], string='Extended Warranty Status')
    cmc_status = fields.Selection([('in_warranty', 'In Warranty'), ('out_warranty', 'Out Of Warranty')],
                                  string='CMC Status', copy=False)
    amc_status = fields.Selection([('in_warranty', 'In Warranty'), ('out_warranty', 'Out Of Warranty')],
                                  string='AMC Status', copy=False)
    warranty_start_date = fields.Datetime(string="Warranty Start Date", readonly=True)
    warranty_end_date = fields.Datetime(string="Warranty End Date", readonly=True)
    is_ew_status_mailsent = fields.Boolean('Extended Warranty Mail Sent?',
                                           help='If the Extended Warranty mail is sent once then should not send mail again. so marking this field as true not to send mail more than once.')
    is_amc = fields.Boolean('AMC Check', compute='_compute_service_category_id_check')
    is_cmc = fields.Boolean('CMC Check', compute='_compute_service_category_id_check')
    is_oem_warranty = fields.Boolean('OEM Warranty Check', compute='_compute_service_category_id_check')
    is_repair_warranty = fields.Boolean('Repair Warranty Check', compute='_compute_service_category_id_check')
    is_extend_warranty = fields.Boolean('Repair Warranty Check', compute='_compute_service_category_id_check')
    warranty_start_dates = fields.Date(string="Warranty Start Date", related='stock_lot_id.warranty_start_date')
    warranty_end_dates = fields.Date(string="Warranty End Date", related='stock_lot_id.warranty_end_date')
    extended_warranty_start_date = fields.Date(string="Extended Warranty Start Date",
                                               related='stock_lot_id.extended_warranty_start_date')
    extended_warranty_end_date = fields.Date(string="Extended Warranty End Date",
                                             related='stock_lot_id.extended_warranty_end_date')
    repair_warranty_start_date = fields.Date(string="Repair Warranty Start Date",
                                             help='Manual / Updated by system end of Ticket & Warranty certificate Generation',
                                             related='stock_lot_id.repair_warranty_start_date')
    repair_warranty_end_date = fields.Date(string="Repair Warranty End Date",
                                           help='Manual / Updated by system end of Ticket & Warranty certificate Generation',
                                           related='stock_lot_id.repair_warranty_end_date')
    is_status_reassign=fields.Boolean(string="Status Ressign")

    def action_check_availability_engineer(self):
        # Search for users who belong to a specific group but not another group and are part of the current team
        res_users = self.env['res.users'].search(
            [('groups_id', 'in', self.env.ref('ppts_service_request.service_request_group_user').id),
             ('groups_id', 'not in', self.env.ref('ppts_service_request.service_request_group_ct_user').id),
             ('id', 'in', self.team_id.member_ids.ids)])
        vals = []
        for rec in res_users:
            # Search for child tickets assigned to the engineer excluding specific states
            engineer_count = self.env['child.ticket'].search([('child_assign_engineer_ids.name', '=', rec.name), (
                'state', '!=',
                ('closed', 'cancel', 'waiting_for_approval', 'rejected', 'esc_new', 'esc_inprogress', 'esc_closed'))])
            # Prepare values to create records in 'check.availability.engineer' model
            vals.append((0, 0, {'user_assign_id': rec.id, 'engineer_tickets_count': len(engineer_count),
                                'child_tickets_ids': [(4, rec.id, False) for rec in engineer_count]}))
            # Create a new record in 'check.availability.engineer' model
        check_availability_engineer_id = self.env['check.availability.engineer'].create(
            {'check_engineer_ids': vals, 'name': self.name})
        # Return an action to open the created record in a new window
        return {
            'name': "Check Engineer Availability",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'check.availability.engineer',
            'target': 'new',
            'res_id': check_availability_engineer_id.id
        }

    @api.depends('state')
    def action_approved_approver(self):
        for rec in self:
            # Check if the state of the record is 'approved'
            if rec.state == 'approved':
                # If approved, set the 'approved_date' field to the current write date
                rec.sudo().approved_date = rec.write_date
            else:
                # If not approved, set the 'approved_date' field to False
                rec.sudo().approved_date = False

    @api.depends('service_category_id')
    def _compute_service_category_id_check(self):
        # When u selet the category based on these fields will be show
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
            if rec.service_category_id.code == 'WR':
                rec.is_oem_warranty = True
            else:
                rec.is_oem_warranty = False
            if rec.service_category_id.code == 'RW':
                rec.is_repair_warranty = True
            else:
                rec.is_repair_warranty = False
            if rec.service_category_id.code == 'EW':
                rec.is_extend_warranty = True
            else:
                rec.is_extend_warranty = False

    @api.onchange('requested_by_email_ct')
    def validate_requested_by_email(self):
        # When you enter the wrong (not proper email) email through the validation error.
        if self.requested_by_email_ct:
            # Validate the entered email using a regular expression pattern
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                             self.requested_by_email_ct)
            # If the entered email doesn't match the pattern, raise a validation error
            if match == None:
                raise ValidationError('Not a valid E-mail ID')

    @api.onchange('action_taken_at_site', 'repair_location_id', 'problem_description')
    def _onchange_alternate_(self):
        # When you enter these fields values in the parent ticket, auto-create the child ticket fields.
        self.service_request_id.action_taken_at_site = self.action_taken_at_site
        self.service_request_id.repair_location_id = self.repair_location_id
        self.service_request_id.problem_reported = self.problem_description

    # Smart button - parent ticket count
    def _compute_parent_count(self):
        # Parent ticket ids counts
        for record in self:
            record.parent_count = self.env['parent.ticket'].search_count([('child_ticket_id', '=', record.id)])

    @api.depends('child_configuration_id')
    # When you selct the child configuration, automattically fill the child ticket type based on configuration
    def _child_ticket_type_check(self):
        for rec in self:
            if rec.child_configuration_id:
                rec.child_ticket_type_id = rec.child_configuration_id.child_ticket_type.id
            else:
                rec.child_ticket_type_id = False

    @api.depends('stock_lot_id')
    def _compute_stock_lot_id_check(self):
        # When you select the asset, the asset loaction will be fetched the current asset location field
        for rec in self:
            location_check = self.env['stock.quant'].search(
                [('lot_id', '=', rec.stock_lot_id.name)], limit=1)
            if location_check:
                rec.current_asset_location = location_check.location_id.id
            else:
                rec.current_asset_location = False  # Handle case when no location is found

    @api.depends('partner_id')
    def _compute_partner_dealer_check(self):
        # When you select the customer, the customer master dealer name will be show the dealer distributer name field
        for rec in self:
            partner_check = self.env['res.partner'].search(
                [('name', '=', rec.partner_id.name)])
            if partner_check:
                rec.customer_region_id = partner_check.customer_region
                rec.dealer_distributor_id = partner_check.dealer_distributer_ids.dealer_id.id
            else:
                rec.dealer_distributor_id = False
                rec.customer_region_id = False

    @api.onchange('alternate_contact_email', 'alternate_contact_name', 'alternate_contact_number')
    def _onchange_alternate_contacts(self):
        # When you enter these fields values in the parent ticket, auto-create the child ticket fields.
        self.parent_ticket_id.alternate_contact_name = self.alternate_contact_name
        self.parent_ticket_id.alternate_contact_number = self.alternate_contact_number
        self.parent_ticket_id.alternate_contact_email = self.alternate_contact_email

    # Alternate contact -> create customer(button)
    def action_open_customer_contacts_ct(self):
        partner_mobile = self.env['res.partner'].search(
            [('mobile', '=', self.alternate_contact_number)], limit=1)
        partner = self.env['res.partner'].search(
            ['|', ('name', '=', self.alternate_contact_name), ('mobile', '=', self.alternate_contact_number)], limit=1)
        if not partner_mobile:
            partner = self.env['res.partner'].create({
                'name': self.alternate_contact_name,
                'mobile': self.alternate_contact_number,
                'email': self.alternate_contact_email,
                'parent_id': self.partner_id.id,
            })
            self.alternate_contact_id = partner.id

        elif not partner:
            partner = self.env['res.partner'].create({
                'name': self.alternate_contact_name,
                'mobile': self.alternate_contact_number,
                'parent_id': self.partner_id.id,
                'email': self.alternate_contact_email,
            })
        self.alternate_contact_id = partner.id

    @api.onchange('alternate_contact_email')
    def validate_alternate_email_check(self):
        # When you enter the wrong (proper) email through the validation error.
        if self.alternate_contact_email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                             self.alternate_contact_email)
            if match == None:
                raise ValidationError("Please enter a valid email address.")

    # Priya
    def cancel(self):
        view = self.env.ref('ppts_parent_ticket.exit_reasons_wizard_form')
        return {
            'name': "Cancel Reason",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'reason.reason',
            'target': 'new',
        }

        # inward_order_count

    def count_inward_order(self):
        for record in self:
            record.inward_order_count = self.env['stock.picking'].sudo().search_count(
                [('child_ticket_id', '=', record.id)])  # Set count to 0 if there's no child_ticket_id

    def action_view_inward_transfer(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Transfer',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('child_ticket_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def action_view_parent_ticket_ct(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Parent Ticket',
            'view_mode': 'tree,form',
            'res_model': 'parent.ticket',
            'domain': [('child_ticket_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def create_parent_ticket(self):
        latest = self.task_list_ids[-1].task_id
        if latest.is_create_ticket:
            self.sudo().parent_ticket_id.with_context(repairs_required=True, sr_type=latest.sudo().service_type_id.id,
                                                      sr_categ=latest.sudo().service_category_id.id,
                                                      pt_conf=latest.sudo().parent_configuration_id.id,
                                                      rq_type=latest.sudo().request_type_id.id).copy()
            self.is_pt_ticket = False

    def field_service_report_values(self):
        user_tz = self.env.user.tz or 'UTC'
        local_tz = pytz.timezone(user_tz)

        job_started_ref = self.env.ref('ppts_custom_workflow.job_start_time').id
        job_end_ref = self.env.ref('ppts_custom_workflow.job_end_time').id
        started_for_site_ref = self.env.ref('ppts_custom_workflow.engineer_started_for_site').id
        reached_site_ref = self.env.ref('ppts_custom_workflow.engineer_reached_site').id
        work_site_ref = self.env.ref('ppts_custom_workflow.job_end_time').id
        received_by_engineer_ref = self.env.ref('ppts_custom_workflow.received_by_engineer').id

        if job_started_ref:
            job_started = self.env['tasks.master.line'].search(
                [('task_id', '=', job_started_ref), ('child_ticket_id', '=', self.id)], limit=1)
            job_start = (job_started.create_date.astimezone(local_tz).replace(tzinfo=None)) if job_started else ''
        if job_end_ref:
            job_end = self.env['tasks.master.line'].search(
                [('task_id', '=', job_end_ref), ('child_ticket_id', '=', self.id)], limit=1)
            job_end_time = (job_end.create_date.astimezone(local_tz).replace(tzinfo=None)) if job_end else ''
        if started_for_site_ref:
            started_for_site = self.env['tasks.master.line'].search(
                [('task_id', '=', started_for_site_ref), ('child_ticket_id', '=', self.id)], limit=1)
            start_for_site = (
                started_for_site.create_date.astimezone(local_tz).replace(tzinfo=None)) if started_for_site else ''
        if reached_site_ref:
            reached_site = self.env['tasks.master.line'].search(
                [('task_id', '=', reached_site_ref), ('child_ticket_id', '=', self.id)], limit=1)
            reach_site = (reached_site.create_date.astimezone(local_tz).replace(tzinfo=None)) if reached_site else ''
        if work_site_ref:
            work_end = self.env['tasks.master.line'].search(
                [('task_id', '=', work_site_ref), ('child_ticket_id', '=', self.id)], limit=1)
            job_end_time = (work_end.create_date.astimezone(local_tz).replace(tzinfo=None)) if work_end else ''
        if received_by_engineer_ref:
            received_engineer = self.env['tasks.master.line'].search(
                [('task_id', '=', received_by_engineer_ref), ('child_ticket_id', '=', self.id)], limit=1)
            received_by_engineer = (
                received_engineer.create_date.astimezone(local_tz).replace(tzinfo=None)) if received_engineer else ''

        docargs = {
            'job_started': job_start.strftime("%d-%b-%Y %I:%M %p") if job_started else '',
            'job_end': job_end_time.strftime("%d-%b-%Y %I:%M %p") if job_end else '',
            'started_for_site': start_for_site.strftime("%d-%b-%Y %I:%M %p") if started_for_site else '',
            'reached_site': reach_site.strftime("%d-%b-%Y %I:%M %p") if reached_site else '',
            'work_end': job_end_time.strftime("%d-%b-%Y %I:%M %p") if work_end else '',
            'received_engineer': received_by_engineer.strftime("%d-%b-%Y %I:%M %p") if received_engineer else '',
        }
        return docargs

    def request_raise_invoice(self):
        request_data = {
            'name': self.name + " Invoice Request",
            'child_ticket_id': self.id,
            'team_id': self.team_id.id,
            'user_id': self.env.user.id,
            'is_create_invoice': True,
        }
        self.env['request'].create(request_data)

        title = _("Invoice Request!")
        message = _("The request for an Invoice was submitted successfully.")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'next': {'type': 'ir.actions.act_window_close'}

            }
        }

    def request_quotation(self):
        request_data = {
            'name': self.name + " Quotation Request",
            'child_ticket_id': self.id,
            'team_id': self.team_id.id,
            'user_id': self.env.user.id,
            'is_create_quote': True,
        }
        self.env['request'].create(request_data)

        title = _("Quotation Request!")
        message = _("successfully submitted a request for a quote.")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'next': {'type': 'ir.actions.act_window_close'}

            }
        }

    def action_view_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('child_ticket_id', '=', self.id)],
            'context': "{'create': False}"
        }

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id.is_block_partner == 'blocked':
            raise UserError('The customer has been blocked. Please change the customer.')

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            if record.partner_id.is_block_partner == 'blocked':
                raise UserError('The customer has been blocked. Please change the customer.')
        return res

    def ar_hold(self):
        ar_hold = self.task_list_ids.task_id.filtered(lambda r: r.python_code == 'ar_hold')
        task_ar_hold = self.task_list_ids.filtered(lambda r: r.task_id.name == 'AR Hold')
        for status_update in task_ar_hold or ar_hold:
            status_update.write({'status': 'Hold'})
            self.write({'is_ar_hold_tick': True})

    def ar_release(self):
        self.is_ar_hold_tick = False

    # Smart Button - Contract
    def action_view_contract(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contract',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.partner_id.id)],
            'res_model': 'contract.contract',
        }

    @api.onchange('service_type_id')
    def onchange_service_type_domain(self):
        category_ids = self.service_type_id.service_category_ids.mapped('id')
        domain = [('id', 'in', category_ids)]
        return {'domain': {'service_category_id': domain}}

    def reset_to_new(self):
        # When you click the Reset button, the state moves to a Re Opened stage.
        self.state = 're_open'

    def write(self, vals):
        result = super(ChildTicket, self).write(vals)
        mails = ''
        if vals.get('state') == 'closed':
            task_line_job_end = self.task_list_ids.filtered(lambda r: r.is_end_task == True)
            if len(task_line_job_end) > 1:
                raise UserError('You Are Not Allowed To Add Multiple Job Close')
            task_line_work_end = self.task_list_ids.filtered(lambda r: r.is_work_end == True)
            data = {
                'ref_id': self.stock_lot_id.id,
                'service_request_id': self.service_request_id.id or self.sudo().parent_ticket_id.service_request_id.id,
                'parent_ticket_id': self.sudo().parent_ticket_id.id,
                'child_ticket_id': self.id,
                'problem_description': task_line_work_end.maintenance_problem_description if task_line_work_end else 'No Data',
                'recommendation_customer': task_line_job_end.recommendation_customer if task_line_job_end else 'No Data',
                'customer_remarks': task_line_job_end.customer_remarks if task_line_job_end else 'No Data',
                'action_taken': task_line_work_end.action_taken if task_line_work_end else 'No Data',
                'final_report_comments': task_line_work_end.final_report_comments if task_line_work_end else 'No Data',
            }
            self.env['assets.historical.data'].create(data)
            if self.request_type_id.ticket_type == 'sr_fsm':
                childs_template_id = self.env.ref('ppts_parent_ticket.fsm_child_ticket_closed_mail_template')
                teams = self.team_id.mapped('member_ids.login')
                mails += ', '.join(teams)
                if childs_template_id:
                    childs_template_id.with_context(email_to=mails).sudo().send_mail(self.id, force_send=True)
            elif self.request_type_id.ticket_type == 'sr_installation':
                child_template_id = self.env.ref('ppts_parent_ticket.mail_template_installation_completed_child_ticket')
                teams = self.team_id.mapped('member_ids.login')
                mails += ', '.join(teams)
                if child_template_id:
                    child_template_id.with_context(email_to=mails).sudo().send_mail(self.id, force_send=True)
            elif self.request_type_id.ticket_type == 'sr_factory_repair':
                sr_factory_repair_template_id = self.env.ref(
                    'ppts_parent_ticket.mail_template_fr_factory_repair_child_ticket')
                teams = self.team_id.mapped('member_ids.login')
                mails += ', '.join(teams)
                if sr_factory_repair_template_id:
                    sr_factory_repair_template_id.with_context(email_to=mails).sudo().send_mail(self.id,
                                                                                                force_send=True)
            # Auto close parent ticket when all child tickets have closed
            open_tickets = self.env['child.ticket'].sudo().search(
                [('parent_ticket_id', '=', self.sudo().parent_ticket_id.id)])
            if all(x.state == 'closed' for x in open_tickets) and self.company_id.auto_close_pt:
                self.sudo().parent_ticket_id.state = 'closed'

        if 'task_list_ids' in vals and self.present_engineer_id and self.user_has_groups(
                'ppts_service_request.service_request_group_user') and not self.user_has_groups(
            'ppts_service_request.service_request_national_head'):
            # print(self.user_has_groups('ppts_service_request.service_request_group_user'),'jjjjjjjjjjjjjjjj')
            if self.present_engineer_id.id != self.env.user.id:
                raise UserError(_('You are not authorized engineer to modify this ticket. Ticket enginner is %s',
                                  self.present_engineer_id.name))
        return result

    @api.onchange('request_type_id')
    def _onchange_request_type_id(self):
        if self.request_type_id and not self.request_type_id.is_required_approval:
            self.is_send_for_approvals = True

    @api.depends('request_type_id')
    def get_request_ticket_type(self):
        for record in self:
            # This method store the request type's ticket type to hide the buttons based on types
            record.request_type = record.request_type_id.ticket_type

    # Smart Button - Installation
    def action_view_installation(self):
        view = self.env.ref('ppts_project_sr_installation.view_task_tree2_sr_installation')
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Installation',
            'view_mode': 'tree',
            'views': [(self.env.ref('ppts_project_sr_installation.view_task_tree2_sr_installation').id, 'tree'),
                      (self.env.ref('ppts_project_sr_installation.view_task_form2_sr_installation').id, 'form')],
            'res_model': 'project.task',
            'domain': [('installation_child_ticket_id', '=', self.sudo().id)],
            'context': "{'create': False}"
        }

    def _count_total_installation(self):
        for record in self:
            record.installation_count = self.env['project.task'].sudo().search_count(
                [('installation_child_ticket_id', '=', record.id)])

    def action_create_installation(self):
        for record in self:
            installation = {
                'is_project_installation': True,
                'installation_service_category_id': record.service_category_id.id or False,
                'installation_service_type_id': record.service_type_id.id or False,
                'installation_child_ticket_id': record.id or False,
                'installation_parent_ticket_id': record.parent_ticket_id.id or False,
                'installation_customer_id': record.partner_id.id or False,
                'installation_customer_account_id': record.customer_account_id.id or False,
                'team_id': record.team_id.id or False,
                'installation_stock_lot_id': record.stock_lot_id.id or False,
                'installation_categ_id': record.categ_id.id or False,
                'installation_origin': record.name or '',
                'description': record.description or '',
                # New
                'installation_process_alias': record.child_ticket_id_alias or '',
                'installation_child_ticket_type': record.child_ticket_type_id.id or False,
                'installation_title': record.remarks or '',
                'installation_reported_fault': record.faulty_section or '',
                'installation_external_reference': record.remarks or '',
                'installation_customer_po_number': record.service_request_id.customer_po_number or '',
                'installation_customer_po_date': record.service_request_id.customer_po_date,
            }
            installation_id = self.env['project.task'].create(installation)
            record.installation_id = installation_id.id
            # Add the engineer to the installation process to see the orders
            installation_id.user_ids = [(4, p.id) for p in record.team_id.mapped('member_ids')]
            installation_id.action_start_installation()
            record.write({'is_installation_created': True})
            view = self.env.ref('ppts_project_sr_installation.view_task_form2_sr_installation')
            return {
                'type': 'ir.actions.act_window',
                'name': 'Installation',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view.id,
                'res_model': 'project.task',
                'res_id': installation_id.id,
                'target': 'current',
                'domain': [('is_project_installation', '=', True)],
            }

    loaner_count = fields.Integer(compute='_compute_loaner_count', string="Loaner Count")

    def _compute_loaner_count(self):
        for record in self:
            record.loaner_count = self.env['sale.order'].search_count(
                [('is_rental_order', '=', True), ('child_ticket_id', '=', self.id)])

    def action_view_loaner_order(self):
        sale_order = self.env['sale.order'].search([('is_rental_order', '=', True), ('child_ticket_id', '=', self.id)])
        field_ids = sale_order.ids
        domain = [('id', 'in', field_ids), ('is_rental_order', '=', True)]
        view_form_id = self.env.ref('sale_renting.rental_order_primary_form_view').id
        view_kanban_id = self.env.ref('sale_renting.rental_order_view_kanban').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'kanban,form',
            'target': 'current',
            'domain': domain,
            'context': "{'create': False}"
        }
        if len(sale_order) == 1:
            action.update({'views': [(view_form_id, 'form')], 'res_id': sale_order.id})
        else:
            action['views'] = [(view_kanban_id, 'kanban'), (view_form_id, 'form')]
        return action

    def action_process_loaner(self):
        if self.request_type_id.ticket_type != 'sr_loaner':
            raise UserError(_('You need to select request type as Loaner !'))
        sr_order = {
            'is_rental_order': True,
            'lr_from_pt': True,
            'partner_id': self.partner_id.id or False,
            'parent_ticket_id': self.parent_ticket_id.id or False,
            'child_ticket_id': self.id or False,
            'team_id': self.team_id.id or False,
            'service_request_id': self.service_type_id.id or False,
            'order_line': [(0, 0, {
                'product_id': self.product_id.id,
                'is_rental': True,
                'product_uom_qty': 1,
                'product_uom': self.product_id.uom_id.id,
            })],
        }
        sale_order = self.env['sale.order'].create(sr_order)
        template_id_pi = self.env.ref('sale_renting.mail_template_loaner_created')
        if template_id_pi:
            template_id_pi.sudo().send_mail(self.id, force_send=True)
        return {
            'type': 'ir.actions.act_window',
            'name': 'SR Loaner Order',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'sale.order',
            'res_id': sale_order and sale_order.id,
            'target': 'current',
            'domain': [('is_rental_order', '=', True)],
            'context': {'default_is_rental_order': 1, 'search_default_filter_today': 1,
                        'search_default_filter_to_return': 1}
        }

    def _compute_approvals_count(self):
        for record in self:
            record.approvals_count = self.env['multi.approval'].search_count([('child_ticket_id', '=', record.id)])

    def _compute_transfer_count(self):
        for record in self:
            record.transfer_count = self.env['stock.picking'].search_count([('origin', '=', self.name)])

    def action_view_send_for_approvals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send for Approvals',
            'view_mode': 'tree,form',
            'res_model': 'multi.approval',
            'domain': [('child_ticket_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def _sla_apply(self):
        for ticket in self:
            now = fields.Datetime.now()
            min_deadline = False
            slas = self.env['sla.policies'].search(
                ['|', '|', '|', ('customer_id', '=', ticket.partner_id.id), ('product_id', '=', ticket.product_id.id),
                 ('start_stage_id', 'in', ticket.task_list_ids.task_id.ids),
                 ('reach_stage_id', 'in', ticket.task_list_ids.task_id.ids)])
            if slas:
                for status in slas:
                    if status:
                        if not status.duration:
                            ticket.sudo().sla_polices_ids = False
                        if not min_deadline or status.duration < min_deadline:
                            min_deadline += status.duration
                    if status.interval_unit == 'hours':
                        remaining_days = now + timedelta(hours=min_deadline)
                    else:
                        remaining_days = now + timedelta(min_deadline)
                    ticket.sudo().sla_deadline = remaining_days
                    ticket.sudo().sla_deadline_date = remaining_days.date()
                    ticket.sudo().sla_polices_ids = slas.ids
            else:
                ticket.sudo().sla_deadline = False
                ticket.sudo().sla_deadline_date = False
                ticket.sudo().sla_polices_ids = False

    # @api.depends('user_id')
    # def _compute_team_id(self):
    #     cached_teams = {}
    #     for order in self:
    #         default_team_id = self.env.context.get('default_team_id', False) or order.team_id.id
    #         user_id = order.user_id.id
    #         company_id = order.company_id.id
    #         key = (default_team_id, user_id, company_id)
    #         if key not in cached_teams:
    #             cached_teams[key] = self.env['crm.team'].with_context(
    #                 default_team_id=default_team_id)._get_default_team_id(user_id=user_id, domain=[
    #                 ('company_id', 'in', [company_id, False])])
    #         order.team_id = cached_teams[key]

    @api.onchange('request_type_id')
    def _onchange_request_type(self):
        team_ids = self.env.user.read_user_teams()
        if team_ids and self.request_type_id.sudo().team_id.id in team_ids and self.request_type_id.team_id:
            self.team_id = self.request_type_id.team_id.id
        else:
            self.team_id = False

    @api.onchange('parent_ticket_id')
    def _onchange_parent_ticket_id(self):
        if self.parent_ticket_id:
            self.partner_id = self.parent_ticket_id.partner_id.id or False,
            self.call_source_id = self.parent_ticket_id.call_source_id.id or False,
            self.service_category_id = self.parent_ticket_id.service_category_id.id or False,
            self.request_type_id = self.parent_ticket_id.request_type_id.id or False,
            self.service_type_id = self.parent_ticket_id.service_type_id.id or False,
            self.product_id = self.parent_ticket_id.product_id.id or False,
            self.stock_lot_id = self.parent_ticket_id.stock_lot_id.id or False,
            self.categ_id = self.parent_ticket_id.categ_id.id or False,
            self.dealer_distributor_id = self.parent_ticket_id.dealer_distributor_id.id or False,
            self.call_received_id = self.parent_ticket_id.call_received_id.id or False,
            self.oem_warranty_status_id = self.parent_ticket_id.oem_warranty_status_id.id,
            self.repair_warranty_status_id = self.parent_ticket_id.repair_warranty_status_id.id or False,
            self.customer_account_id = self.parent_ticket_id.customer_account_id.id or False,
            self.team_id = self.parent_ticket_id.team_id.id or False,
            self.write({
                'problem_description': self.parent_ticket_id.problem_description,
                'requested_by_name_child': self.parent_ticket_id.requested_by_name,
                'requested_by_contact_number': self.parent_ticket_id.requested_by_contact_number,
                'remarks': self.parent_ticket_id.remarks,
                'alternate_contact_name': self.parent_ticket_id.alternate_contact_name,
                'alternate_contact_number': self.parent_ticket_id.alternate_contact_number,

                'faulty_section': self.parent_ticket_id.faulty_section,
                'sow': self.parent_ticket_id.sow,
                'webdelata_id': self.parent_ticket_id.webdelata_id,
                'webdelata': self.parent_ticket_id.webdelata,
            })

    def action_ticket_close(self):
        user_exist = self._check_user_exist()
        return {
            'name': "Reason",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'reason.reason',
            'target': 'new',
            'context': {'default_reason_type': 'close'}
        }

    # Child Ticket Sequences
    @api.model
    def create(self, vals):
        if vals.get('child_configuration_id'):
            child_config = self.env['child.ticket.configuration'].search(
                [('id', '=', vals.get('child_configuration_id'))], limit=1)
            if child_config.is_inward_receipts or child_config.is_outward_delivery_order or child_config.is_material_movement:
                if not vals.get('repair_location_id'):
                    parent_ticket_id = self.env['parent.ticket'].browse(vals.get('parent_ticket_id'))
                    if parent_ticket_id.repair_center_location_id:
                        vals['repair_location_id'] = parent_ticket_id.repair_center_location_id.id
                    if not parent_ticket_id.repair_center_location_id:
                        raise UserError(
                            _('Map the repair center location on the this ticket (%s) to create internal transfer to receive the products.') % parent_ticket_id.name)
                repair_location = self.env['stock.warehouse'].search([('id', '=', vals.get('repair_location_id'))],
                                                                     limit=1)
                transit_location_id = self.env['stock.location'].search(
                    [('wh_id', '=', repair_location.id), ('name', '=', 'Transit'),
                     ('usage', '=', 'transit'), ('company_id', '=', self.env.user.company_id.id)], limit=1)
                if not transit_location_id:
                    raise UserError(
                        _('There is no Transit location in this warehouse- %s . Create new location called "Transit" and map location type as "Transit Location" to create an Inward order') % (
                            repair_location.name))
                customer_location_id = self.env['stock.location'].search(
                    [('wh_id', '=', repair_location.id), ('name', '=', 'Customers'),
                     ('usage', '=', 'customer')], limit=1)
                if not customer_location_id:
                    raise UserError(
                        _('There is no Customer location in this warehouse- %s . Create new location called "Customers" and map location type as "Customer Location" to create an Inward order') % (
                            repair_location.name))

        if 'company_id' in vals:
            vals['name'] = self.env['ir.sequence'].with_context(force_company=self.env.user.company_id.id).next_by_code(
                'child.ticket') or _('New')
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('child.ticket') or _('New')
        vals['state'] = 'new'
        rec = super(ChildTicket, self).create(vals)
        if rec.child_configuration_id.is_create_alert:
            email = ''
            if rec.child_configuration_id.customer_type == 'oem':
                email = rec.customer_account_id.email
            elif rec.child_configuration_id.customer_type == 'end_customer':
                email = rec.partner_id.email
            elif rec.child_configuration_id.customer_type == 'both':
                email = ",".join([str(rec.customer_account_id.email), str(rec.partner_id.email)])
            template_id = rec.child_configuration_id.notification_template_id
            if template_id:
                template_id.with_context(email_to=email).sudo().send_mail(rec.id, force_send=True)
        if not rec.child_configuration_id.is_inventory and rec.request_type_id.ticket_type == 'sr_wr':
            raise ValidationError(
                _('Kindly Enable Inventory on %s Configuration', rec.child_configuration_id.child_config_name))
        if not rec.child_configuration_id.is_outward_delivery_order and not rec.child_configuration_id.delivery_operation_type_id and rec.request_type_id.ticket_type == 'sr_wr':
            raise ValidationError(
                _('Kindly Enable Delivery on %s Configuration', rec.child_configuration_id.child_config_name))
        # If the receipt is enabled on the child ticket configuration, create internal transfer
        # Create Return Order Alternate for Taking Receipts
        if rec.child_configuration_id.is_inward_receipts and rec.child_configuration_id.receipts_operation_type_id:
            do_order = self.env['stock.picking'].sudo().search(
                [('origin', '=', rec.stock_lot_id.name), ('picking_type_id.code', '=', 'outgoing'),
                 ('state', '=', 'done')])
            # GET Return Order
            return_of = "Return of " + do_order[-1].name if do_order else False
            return_order = self.env['stock.picking'].sudo().search(
                [('origin', '=', return_of), ('picking_type_id.code', '=', 'incoming'), ('state', '=', 'done')])
            if do_order and not return_order:
                returns = self.env['stock.return.picking'].create({
                    'picking_id': do_order[-1].id,
                })
                returns._onchange_picking_id()
                new_picking_id, pick_type_id = returns._create_returns()
                # Override the context to disable all the potential filters that could have been set previously
                ctx = dict(self.env.context)
                ctx.update({
                    'default_partner_id': rec.partner_id.id,
                    'search_default_picking_type_id': pick_type_id,
                    'search_default_draft': False,
                    'search_default_assigned': False,
                    'search_default_confirmed': False,
                    'search_default_ready': False,
                    'search_default_planning_issues': False,
                    'search_default_available': False,
                })
                new_pick = self.env['stock.picking'].sudo().search([('id', '=', new_picking_id)])
                new_pick.child_ticket_id = rec.id
            elif return_order:
                pass
            else:
                raise ValidationError(
                    _('There is not Transfer for this %s serial number',
                      rec.stock_lot_id.name))
        # Create Delivery Order
        if rec.child_configuration_id.is_outward_delivery_order and rec.child_configuration_id.delivery_operation_type_id:
            if rec.request_type_id.ticket_type == 'sr_wr' and rec.parent_child_ticket_id:
                draft_order = self.env['stock.picking'].sudo().search(
                    [('child_ticket_id', '=', rec.parent_child_ticket_id.id), ('picking_type_id.code', '=', 'outgoing'),
                     ('state', '=', 'draft')], limit=1)
                draft_order.child_ticket_id = rec.id
            else:
                return_order = self.env['stock.picking'].sudo().search(
                    [('child_ticket_id', '=', rec.id), ('picking_type_id.code', '=', 'incoming'),
                     ('is_return', '=', True)], limit=1)
                customer_location_id = self.env['stock.location'].sudo().search([('usage', '=', 'customer')], limit=1)
                vals = {
                    "picking_type_id": rec.child_configuration_id.delivery_operation_type_id.id,
                    "location_id": rec.child_configuration_id.delivery_operation_type_id.default_location_src_id.id,
                    "location_dest_id": rec.child_configuration_id.delivery_operation_type_id.default_location_dest_id.id or customer_location_id.id,
                    "partner_id": rec.partner_id.id,
                    'child_ticket_id': rec.id,
                    'origin': return_order.name,
                    'is_inward_transfer': True
                }
                if vals:
                    picking_id = self.env['stock.picking'].sudo().create(vals)
                    line_vals = {
                        'product_id': rec.product_id.id,
                        'product_uom': rec.product_id.uom_id.id,
                        'name': rec.product_id.name,
                        'product_uom_qty': 1,
                        # 'quantity_done': 1,
                        'picking_id': picking_id.id,
                        "location_id": rec.child_configuration_id.delivery_operation_type_id.default_location_src_id.id,
                        "location_dest_id": rec.child_configuration_id.delivery_operation_type_id.default_location_dest_id.id or customer_location_id.id,
                    }
                    self.env['stock.move'].sudo().create(line_vals)
        # Material Movement
        if rec.child_configuration_id.is_material_movement and rec.child_configuration_id.transfer_operation_type_ids:
            customer_location_id = self.env['stock.location'].sudo().search([('usage', '=', 'customer')], limit=1)
            vals = {
                "picking_type_id": rec.child_configuration_id.transfer_operation_type_ids[-1].id,
                "location_id": customer_location_id.id,
                "location_dest_id": transit_location_id.id,
                "partner_id": rec.partner_id.id,
                'child_ticket_id': rec.id,
                'is_inward_transfer': True
            }
            if vals:
                picking_id = self.env['stock.picking'].sudo().create(vals)
                line_vals = {
                    'product_id': rec.product_id.id,
                    'product_uom': rec.product_id.uom_id.id,
                    'name': rec.product_id.name,
                    'quantity_done': 1,
                    'picking_id': picking_id.id,
                    "location_id": customer_location_id.id,
                    "location_dest_id": transit_location_id.id,
                }
                self.env['stock.move'].sudo().create(line_vals)
        return rec

    # Open Wizard Child Assign Engineer
    def action_child_assign_engineer_wizard(self):
        # Check for the asset and create the child ticket details on the asset ticket O2M fields
        rec = dict(self._fields['state'].selection).get(self.state)
        self.env['asset.lot.serial'].create({
            'child_ticket_id': self.id,
            'problem_description': self.problem_description,
            'ticket_type': 'ct',
            'stock_lot_id': self.stock_lot_id.id,
            'service_type_id': self.service_type_id.id,
            'service_category_id': self.service_category_id.id,
            'ticket_create_date': self.create_date,
            'ct_user_id': self.user_id.id,
            'engineer_id': self.child_assign_engineer_ids.id,
            'status': rec,
        })
        context = {
            'default_is_assign_to_user': self.is_assign_to_user,
            'default_is_request_reassign': self.is_request_reassign,
        }

        return {
            'name': _('Assign User'),
            'view_mode': 'form',
            'res_model': 'child.assign.engineer',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

    def action_child_reassign_engineer_wizard(self):
        context = {
            'default_is_assign_to_user': self.is_assign_to_user,
            'default_is_request_reassign': self.is_request_reassign,
        }
        return {
            'name': _('Re-assign User'),
            'view_mode': 'form',
            'res_model': 'child.assign.engineer',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

    # Installation Report

    def show_warning_messages(self):
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

    def action_generate_report_installation_child_ticket(self):
        if self.request_type_id.ticket_type == "sr_installation":
            return self.env.ref('ppts_parent_ticket.report_esskay_config').report_action(self)
        else:
            return self.show_warning_messages()

    # Send By Email
    def action_send_mail(self):
        '''
        This function opens a window to compose an email, with the child ticket template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup('ppts_parent_ticket.email_template_child_ticket')[2]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
        except ValueError:
            compose_form_id = False
        if not self.partner_id.email:
            return self._show_notification('Please Enter Customer Email')
        ctx = {
            'default_model': 'child.ticket',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        }
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.onchange('stock_lot_id')
    def _onchange_stock_lot_id(self):
        for record in self:
            record.product_id = record.stock_lot_id.product_id.id or False
            stock_lot_obj = self.env['stock.lot'].search([('name', '=', record.stock_lot_id.name)])
            # warranty
            warranty_check_false = stock_lot_obj.filtered(lambda x: x.oem_warranty_check == False)
            warranty_check_true = stock_lot_obj.filtered(lambda x: x.oem_warranty_check == True)
            # repair
            repair_check_false = stock_lot_obj.filtered(lambda x: x.oem_repair_warranty_check == False)
            repair_check_true = stock_lot_obj.filtered(lambda x: x.oem_repair_warranty_check == True)

            if record.stock_lot_id:
                record.historical_data_line = [(0, 0, {'ref_ticket_id': record.id,
                                                       'service_request_id': x.service_request_id.id,
                                                       'parent_ticket_id': x.parent_ticket_id.id,
                                                       'child_ticket_id': x.child_ticket_id.id,
                                                       'problem_description': x.problem_description,
                                                       'recommendation_customer': x.recommendation_customer,
                                                       'customer_remarks': x.customer_remarks,
                                                       'action_taken': x.action_taken,
                                                       'final_report_comments': x.final_report_comments}) for x in
                                               record.stock_lot_id.historical_data_line]
                if warranty_check_false:
                    record.oem_warranty_status = 'not_available'
                if repair_check_false:
                    record.oem_repair_status = 'not_available'
                if warranty_check_true:
                    oem_warranty = warranty_check_true.search(
                        [('name', '=', record.stock_lot_id.name), ('warranty_start_date', '<=', date.today()),
                         ('warranty_end_date', '>=', date.today())])
                    if oem_warranty:
                        record.oem_warranty_status = 'in_oem_warranty'
                    else:
                        record.oem_warranty_status = 'out_oem_warranty'
                if repair_check_true:
                    oem_repair = repair_check_true.search(
                        [('name', '=', record.stock_lot_id.name), ('repair_warranty_start_date', '<=', date.today()),
                         ('repair_warranty_end_date', '>=', date.today())])
                    if oem_repair:
                        record.oem_repair_status = 'in_repair_warranty'
                    else:
                        record.oem_repair_status = 'out_repair_warranty'
                if record.stock_lot_id and record.stock_lot_id.extended_warranty_start_date and record.stock_lot_id.extended_warranty_end_date:
                    if record.stock_lot_id.extended_warranty_end_date >= date.today():
                        record.extended_warranty_status = 'in_repair_warranty'
                    else:
                        record.extended_warranty_status = 'out_repair_warranty'
                else:
                    record.extended_warranty_status = 'not_available'
            else:
                record.oem_warranty_status = ''
                record.oem_repair_status = ''

    def action_service_request(self):
        self.ensure_one()
        context = {'default_child_ticket_id': self.id}
        return {
            'name': _('Select Approval Type'),
            'view_mode': 'form',
            'res_model': 'request.type.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            "context": context,
        }

    # Smart Button - Service Request
    def action_view_service_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Request',
            'view_mode': 'tree,form',
            'views': [(self.env.ref('ppts_service_request.service_request_tree_view').id, 'tree')],
            'res_model': 'service.request',
            'domain': [('child_ticket_id', 'in', self.ids)],
            'context': "{'create': False}"
        }

    # Service Request Count
    def compute_service_count(self):
        for record in self:
            record.service_request_count = self.env['service.request'].search_count(
                [('child_ticket_id', '=', record.id)])

    def compute_request_count(self):
        for record in self:
            record.request_count = self.env['request'].search_count([('child_ticket_id', '=', record.id)])

    # Acknowledgment Button
    def action_send_acknowledgment(self):
        email = ''
        if self.child_configuration_id:
            if not self.child_configuration_id.is_create_alert:
                return self._show_notification(
                    'Please Enable On Ticket Create Alert / Notification in Child Configuration')
            if not self.child_configuration_id.notification_template_id:
                return self._show_notification('Please Select Notification Template')
            if not self.child_configuration_id.customer_type:
                return self._show_notification('Please Select Customer Type')
            if self.child_configuration_id.is_create_alert:
                if self.child_configuration_id.customer_type == 'oem':
                    if not self.customer_account_id.email:
                        return self._show_notification('Please Select Customer Account')
                    else:
                        email = self.customer_account_id.email
                elif self.child_configuration_id.customer_type == 'end_customer':
                    if not self.partner_id.email:
                        return self._show_notification('Please Select Customer')
                    else:
                        email = self.partner_id.email
                elif self.child_configuration_id.customer_type == 'both':
                    if not (self.customer_account_id.email and self.partner_id.email):
                        return self._show_notification('Please Select Both Customer and Customer Account')
                    else:
                        email = ",".join([str(self.customer_account_id.email), str(self.partner_id.email)])
                template_id = self.child_configuration_id.notification_template_id
                if template_id:
                    template_id.with_context(email_to=email).sudo().send_mail(self.id, force_send=True)
                    return self._show_success_notification('Acknowledgment Sent Successfully')
        else:
            return self._show_notification('Please Enter Child Configuration')

    def _show_success_notification(self, message):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'success',
                'sticky': False,
            },
        }
        return notification

    # Button - Send for Review
    def action_for_review(self):
        # When you click the Send for Review button, the state moves to a In Review stage.
        self.state = 'in_review'

    # Send for Approval - Button
    def send_for_approval(self):
        return {
            'name': _('Send for Approval'),
            'view_mode': 'form',
            'res_model': 'child.ticket.approval',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_for_approval(self):
        values = []
        for record in self.approver_id.line_ids:
            vals = (0, 0, {
                "sequence": record.sequence,
                "user_id": record.user_id.id,
                "require_opt": record.require_opt,
                "state": 'new',
            })
            values.append(vals)
        if values:
            self.approver_ids = values
        self.state = 'waiting_for_approval'
        action_id = self.env.ref('ppts_service_request.action_service_request_approval', raise_if_not_found=False)
        template_id = self.env.ref('ppts_service_request.mail_template_notify_approvers')
        for approver in self.approver_id.line_ids:
            base_url = '/web#id=%d&action=%r&model=service.request&view_type=form' % (self.id, action_id.id)
            if template_id:
                template_id.with_context(rec_url=base_url).sudo().send_mail(approver.id, force_send=True)
        return True

    def action_approved(self):
        user_exist = self._check_user_exist()
        if user_exist:
            for approver_id in self.env['service.ticket.approval'].search(
                    [('user_id', '=', self.env.user.id), ('child_ticket_id', '=', self.id)]):
                if approver_id.state == 'approved':
                    raise UserError(_("Already this has been approved on %s" % approver_id.create_date.date()))
                else:
                    approver_id.state = 'approved'
                    approver_id.approved_on = fields.Date.today()
            # Check whether all are approved if not then should not change the service request status
            if any(record.state != 'approved' for record in self.approver_ids):
                pass
            else:
                self.state = 'approved'
        else:
            return self._show_notification('You are not allowed to approve this Child Ticket' + ' ' + self.name)

    def action_rejected(self):
        user_exist = self._check_user_exist()
        if user_exist:
            if self.approver_ids.filtered(
                    lambda record: record.state == 'approved' and record.user_id.id == self.env.user.id):
                raise UserError(_('You have approved the ticket already !'))
            return {
                'name': "Reason",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'reason.reason',
                'target': 'new',
                'context': {'default_reason_type': 'reject'}
            }
        else:
            return self._show_notification('You are not allowed to reject this Child Ticket' + ' ' + self.name)

    def action_hold(self):
        user_exist = self._check_user_exist()
        if user_exist:
            if self.approver_ids.filtered(
                    lambda record: record.state == 'approved' and record.user_id.id == self.env.user.id):
                raise UserError(_('You have approved the ticket already !'))
            return {
                'name': "Reason",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'reason.reason',
                'target': 'new',
                'context': {'default_reason_type': 'hold'}
            }
        else:
            return self._show_notification('You are not allowed to hold this Child Ticket' + ' ' + self.name)

    def _check_user_exist(self):
        if self.env['service.ticket.approval'].search(
                [('user_id', '=', self.env.user.id), ('child_ticket_id', '=', self.id)]):
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

    @api.onchange('task_list_ids')
    def _onchange_task_list_ids(self):
        for record in self:
            if self.child_configuration_id.work_flow_id:
                pro = []
                for task_line in record.task_list_ids:
                    work_flow = self.env["tasks.master.line"].search(
                        [("workflow_id", "=", self.child_configuration_id.work_flow_id.id),
                         ("task_id", "=", task_line.task_id.id)])
                    if work_flow:
                        for wk in work_flow:
                            if wk.next_task_ids:
                                pro_ids = [(6, 0, wk.next_task_ids.ids)]
                                task_line.next_task_ids = pro_ids
                                self.next_task_ids = [(6, 0, wk.next_task_ids.ids)]
            create_installation = record.task_list_ids.task_id.filtered(
                lambda r: r.python_code == 'create_installation')
            # Create Installation
            if create_installation:
                record.is_create_installation = True
            else:
                record.is_create_installation = False

            create_loaner = record.task_list_ids.task_id.filtered(lambda r: r.python_code == 'create_loaner')
            if create_loaner:
                record.is_create_loaner = True
            else:
                record.is_create_loaner = False

            # AR Hold
            ar_hold = record.task_list_ids.task_id.filtered(lambda r: r.python_code == 'ar_hold')
            if ar_hold:
                record.is_ar_hold = True
            else:
                record.is_ar_hold = False

            # Create Ticket
            pt_ticket = record.task_list_ids.task_id.filtered(lambda r: r.is_create_ticket == True)
            if pt_ticket:
                record.is_pt_ticket = True
            else:
                record.is_pt_ticket = False

            re_assign = record.task_list_ids.task_id.filtered(lambda r: r.description == 'Request Re-assign')
            if re_assign:
                record.is_status_reassign = True
            else:
                record.is_status_reassign = False

    def action_status_update(self):
        return {
            'name': _('Status Update'),
            'view_mode': 'form',
            'res_model': 'child.ticket',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('ppts_parent_ticket.child_ticket_status_update_form_view').id,
            'target': 'new',
            'res_id': self.id
        }

    # Smart Button - Engineer
    def action_view_engineer(self):
        self.ensure_one()
        return {
            'name': 'Engineer',
            'view_mode': 'tree,form',
            'res_model': 'res.users',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': [('id', 'in', self.child_assign_engineer_ids.ids)],
            'context': "{'create': False}"
        }

    # Smart Button - Approvals
    def action_view_approvals(self):
        self.ensure_one()
        return {
            'name': 'Approvals',
            'view_mode': 'tree,form',
            'res_model': 'service.ticket.approval',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': [('id', 'in', self.approver_ids.ids)],
            'context': "{'create': False}"
        }

    # Smart Button - Returns
    def action_view_returns(self):
        self.ensure_one()
        return {
            'name': 'Returns',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('child_ticket_id', '=', self.id), ('is_return', '=', True)],
            'context': "{'create': False}"
        }

    return_count = fields.Integer(string="Return", compute='_compute_return_order_ids')
    return_order_ids = fields.Many2many('stock.picking', string="Return Orders", compute='_compute_return_order_ids')

    def _compute_return_order_ids(self):
        for rec in self:
            return_order_ids = self.env['stock.picking'].search(
                [('child_ticket_id', '=', self.id), ('is_return', '=', True)])
            rec.return_count = len(return_order_ids)
            rec.return_order_ids = return_order_ids.ids

    # Smart Button - Schedule
    def action_view_schedule(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Activities',
            'view_mode': 'tree,form',
            'res_model': 'mail.activity',
            'domain': [('res_id', '=', self.id), ('res_model', '=', 'child.ticket')],
        }

    # Smart Button - requests
    def action_view_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Request',
            'view_mode': 'tree,form',
            'res_model': 'request',
            'domain': [('child_ticket_id', '=', self.id)],
            'context': "{'create': False}"
        }

    # Smart Button - Reports
    def action_view_reports(self):
        return True

    # Smart Button - Expenses
    def action_view_expenses(self):
        return True

    # Smart Button - Timesheet
    def action_view_timesheet(self):
        return True

    # Smart Button - Purchase Request
    def action_view_purchase_request(self):
        return True

    def action_view_transfers(self):
        tree_id = self.env.ref('stock.vpicktree').id
        form_id = self.env.ref('stock.view_picking_form').id
        return {
            'name': _('Internal Transfers'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'stock.picking',
            'view_id': tree_id,
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'type': 'ir.actions.act_window',
            'domain': [('origin', '=', self.name)],
            'context': "{'create': False}",
        }

    def action_delete_status(self):
        if self.task_list_ids:
            if len(self.task_list_ids.ids) <= 1:
                raise UserError(_('It is not possible to delete the lines since it has single line.'))
            else:
                task_list_id = self.env['tasks.master.line'].search([('child_ticket_id', '=', self.id)], limit=1,
                                                                    order='id desc')
                if task_list_id and not task_list_id.is_end_task:
                    related_ct = self.env['child.ticket'].search([('name', '=', task_list_id.ref_value)], limit=1)
                    related_ct_pickings = self.env['stock.picking'].search(
                        [('child_ticket_id', '=', related_ct.id), ('child_ticket_id', '!=', False)])
                    for ct in related_ct_pickings:
                        ct.action_cancel()
                    related_ct.unlink()
                    # Check for the SR anyting be created from this task, if yes delete and delete thet task
                    for existing_service_request_id in self.env['service.request'].sudo().search(
                            [('child_ticket_id', '=', self.id), ('state', '=', ('draft', 'new'))]):
                        existing_service_request_id.unlink()
                    task_list_id.meeting_ids.unlink()
                    task_list_id.unlink()
                elif task_list_id and task_list_id.is_end_task:
                    context = {
                        'child_task_line_id': task_list_id.id
                    }
                    return {
                        'name': _('Send for Approval'),
                        'view_mode': 'form',
                        'res_model': 'child.ticket.approval',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context': context
                    }
                self._onchange_task_list_ids()
        return True


class ChildTicketAssetLine(models.Model):
    _name = 'child.ticket.asset.line'

    child_ticket_id = fields.Many2one('child.ticket', string='Child Ticket')
    product_id = fields.Many2one('product.product', string="Product")
    name = fields.Text(string="Description")


class ServiceTicketApproval(models.Model):
    _inherit = 'service.ticket.approval'

    child_ticket_id = fields.Many2one('child.ticket', string="Child Ticket", ondelete="cascade")


class ReasonReason(models.TransientModel):
    _inherit = 'reason.reason'
    _description = 'Reason'

    cancel_reason = fields.Char(string="Reason")

    def action_cancel_ct(self):
        child_ticket_id = self.env['child.ticket'].browse(self.env.context.get('active_id'))
        stock = self.env['stock.picking'].search(
            [('child_ticket_id', '=', child_ticket_id.id), ('state', '!=', 'done')])
        for res in stock:
            if res.picking_type_id.code == "outgoing":
                res.state = "cancel"
        child_ticket_id.state = 'cancel'
        child_ticket_id.cancel_reason = self.cancel_reason

    def action_confirm(self):
        res = super(ReasonReason, self).action_confirm()
        if self.env.context.get('active_model') == 'child.ticket':
            child_ticket_id = self.env['child.ticket'].browse(self.env.context.get('active_id'))
            for approve_id in self.env['service.ticket.approval'].search(
                    [('user_id', '=', self.env.user.id), ('child_ticket_id', '=', child_ticket_id.id)]):
                if self.reason_type == 'hold':
                    approve_id.state = 'hold'
                    approve_id.hold_reason = self.name
                    approve_id.hold_on = fields.Date.today()
                elif self.reason_type == 'reject':
                    approve_id.state = 'rejected'
                    approve_id.reject_reason = self.name
                    approve_id.rejected_on = fields.Date.today()
            if self.reason_type == 'close':
                child_ticket_id.state = 'closed'
                child_ticket_id.close_reason = self.name
                child_ticket_id.close_date = fields.Datetime.today()
                if child_ticket_id.state == 'closed':
                    child_ticket_id.job_closed_date = child_ticket_id.write_date

        return True


class TasksMasterLine(models.Model):
    _inherit = 'tasks.master.line'

    is_request_approval = fields.Boolean(string="Request Approval", related='task_id.is_request_approval')
    is_check_attachment = fields.Boolean(string='Attachment Check')

    @api.onchange('task_id')
    def onchange_ct_task_list(self):

        if self.is_wk and self.child_ticket_id and not self.child_ticket_id.child_assign_engineer_ids:
            raise ValidationError(_('Assign engineer before creating work order'))

    def write(self, vals):
        result = super().write(vals)
        if self.env.user.has_group(
                'ppts_service_request.service_request_group_user') and not self.user_has_groups(
            'ppts_service_request.service_request_group_ct_user') and not self.user_has_groups(
            'ppts_service_request.service_request_group_manager') and not self.user_has_groups(
            'ppts_service_request.service_request_national_head') and not self.user_has_groups(
            'ppts_service_request.service_request_administrator'):
            if self.child_ticket_id.child_assign_engineer_ids.id != self.env.user.id:
                raise UserError('You are not authorized engineer to modify this ticket')
        return result

    @api.model
    def create(self, vals):
        """This method sets a checks whether PI Task Updated or Not"""
        result = super().create(vals)
        if result.approval_type_id:
            if not result.Commants:
                raise ValidationError(
                    _('Please Enter the Comments'))

        if result.child_ticket_id:
            ct_pi_true = self.env['tasks.master.line'].search(
                [('is_pi_required', '=', True), ('child_ticket_id', '=', result.child_ticket_id.id)], limit=1)
            pi_not_id = self.env['tasks.master'].search([('name', '=', 'PI Not Required')], limit=1)
            ct_pi_not_true = self.env['tasks.master.line'].search(
                [('task_id', '=', pi_not_id.id), ('child_ticket_id', '=', result.child_ticket_id.id)], limit=1)
            workflow_pi_required = result.child_ticket_id.child_configuration_id.work_flow_id.task_list_ids.mapped(
                'is_pi_required')
            if any(workflow_pi_required) and ct_pi_true or ct_pi_not_true:
                result.child_ticket_id.is_pi_true = True  # Visible
            elif any(workflow_pi_required) and not ct_pi_true:
                result.child_ticket_id.is_pi_true = False  # Invisible
            elif not any(workflow_pi_required):
                result.child_ticket_id.is_pi_true = True  # Visible

            # PI Required Check in CT
            # pi_req_id = self.env['tasks.master'].search([('is_pi_required', '=', True)], limit=1)
            # if (
            #         pi_not_id.id in result.child_ticket_id.next_task_ids.ids or pi_req_id.id in result.child_ticket_id.next_task_ids.ids) \
            #         and result.task_id.id not in result.child_ticket_id.next_task_ids.ids and not result.task_id.name == 'New':
            #     raise UserError(_("Update PI Required or PI Not Required status"))
        return result

    def create_inventory_ct(self):
        for rec in self.child_ticket_id:
            move_lines = []
            move_vals = {}
            move_vals.update({
                'product_id': rec.product_id.id,
                'product_uom_qty': 1,
                'product_uom': rec.product_id.uom_id.id,
                'name': rec.product_id.default_code or rec.product_id.name,
                'location_id': self.task_id.source_location_id.id,
                'location_dest_id': self.task_id.destination_location_id.id,
                'lot_ids': [(4, rec.stock_lot_id.id)],
            })
            move_lines.append((0, 0, move_vals))
            values = {
                'location_id': self.task_id.source_location_id.id,
                'location_dest_id': self.task_id.destination_location_id.id,
                'picking_type_id': self.task_id.operation_type_id.id,
                'move_type': 'one',
                'move_ids': move_lines,
                # 'move_line_ids': move_lines,
                'origin': rec.name,
            }
            if move_lines:
                stock_id = self.env['stock.picking'].create(values)
                stock_id.action_confirm()
                stock_id.button_validate()

    def button_tasks_update(self):
        values = super().button_tasks_update()
        for record in self:
            template_id = False
            employee = self.env['hr.employee'].sudo().search(
                [('job_id', 'in', record.task_id.sudo().job_ids.ids)]).mapped('work_email')
            employee_cc = self.env['hr.employee'].sudo().search(
                [('job_id', 'in', record.task_id.sudo().job_cc_ids.ids)]).mapped('work_email')
            mails = ', '.join(employee)
            mails_cc = ', '.join(employee_cc)
            # if record.task_id.is_create_ticket and record.child_ticket_id:
            #     record.child_ticket_id.create_parent_ticket()
            if record.is_end_task and record.child_ticket_id:
                if not employee and not employee_cc:
                    raise UserError("There is no Email configured on these employees")
                record.child_ticket_id.state = 'closed'
                if record.child_ticket_id.request_type_id.ticket_type == 'sr_fsm':
                    template_id = self.env.ref('ppts_parent_ticket.fsm_child_ticket_closed_mail_template')
                if template_id:
                    template_id.with_context(email_to=mails, email_cc=mails_cc).sudo().send_mail(
                        record.child_ticket_id.id, force_send=True)
            if record.is_check_oem_warranty and record.child_ticket_id:
                # child_ticket = self.env['parent.ticket'].search([('id', '=', record.child_ticket_id.id)])
                stock_lot_obj = self.env['stock.lot'].search([('name', '=', record.child_ticket_id.stock_lot_id.name)])
                # warranty
                warranty_check_false = stock_lot_obj.filtered(lambda x: x.oem_warranty_check == False)
                warranty_check_true = stock_lot_obj.filtered(lambda x: x.oem_warranty_check == True)

                if record.child_ticket_id.stock_lot_id:
                    if warranty_check_false:
                        record.child_ticket_id.oem_warranty_status = 'not_available'
                    if warranty_check_true:
                        oem_warranty = warranty_check_true.search(
                            [('name', '=', record.child_ticket_id.stock_lot_id.name),
                             ('warranty_start_date', '<=', date.today()),
                             ('warranty_end_date', '>=', date.today())])
                        if oem_warranty:
                            record.child_ticket_id.oem_warranty_status = 'in_oem_warranty'
                        else:
                            record.child_ticket_id.oem_warranty_status = 'out_oem_warranty'
                else:
                    record.child_ticket_id.oem_warranty_status = ''
                oem_warranty_status = dict(record.child_ticket_id._fields['oem_warranty_status'].selection).get(
                    record.child_ticket_id.oem_warranty_status)
                template_id_check_oem_warranty = self.env.ref(
                    'ppts_parent_ticket.mail_template_check_oem_warranty_child_ticket')
                if template_id_check_oem_warranty:
                    template_id_check_oem_warranty.with_context(email_to=mails, email_cc=mails_cc, task=record.id,
                                                                oem_warranty_status=oem_warranty_status).sudo().send_mail(
                        record.child_ticket_id.id, force_send=True)

            if record.is_check_oem_repair_status and record.child_ticket_id:
                # child_ticket = self.env['parent.ticket'].search([('id', '=', record.child_ticket_id.id)])
                stock_lot_obj = self.env['stock.lot'].search([('name', '=', record.child_ticket_id.stock_lot_id.name)])
                # repair
                repair_check_false = stock_lot_obj.filtered(lambda x: x.oem_repair_warranty_check == False)
                repair_check_true = stock_lot_obj.filtered(lambda x: x.oem_repair_warranty_check == True)

                if record.child_ticket_id.stock_lot_id:
                    if repair_check_false:
                        record.child_ticket_id.oem_repair_status = 'not_available'

                    if repair_check_true:
                        oem_repair = repair_check_true.search(
                            [('name', '=', record.child_ticket_id.stock_lot_id.name),
                             ('repair_warranty_start_date', '<=', date.today()),
                             ('repair_warranty_end_date', '>=', date.today())])
                        if oem_repair:
                            record.child_ticket_id.oem_repair_status = 'in_repair_warranty'
                        else:
                            record.child_ticket_id.oem_repair_status = 'out_repair_warranty'
                else:
                    record.child_ticket_id.oem_repair_status = ''

                oem_repair_status = dict(record.child_ticket_id._fields['oem_repair_status'].selection).get(
                    record.child_ticket_id.oem_repair_status)
                template_id_check_oem_repair_warranty = self.env.ref(
                    'ppts_parent_ticket.mail_template_check_oem_repair_status_child_ticket')
                if template_id_check_oem_repair_warranty:
                    template_id_check_oem_repair_warranty.with_context(email_to=mails, email_cc=mails_cc,
                                                                       task=record.id,
                                                                       oem_repair_status=oem_repair_status).sudo().send_mail(
                        record.child_ticket_id.id, force_send=True)

        return values

    def action_send_mail_ct(self):
        '''
        This function opens a window to compose an email, with the child ticket template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup('ppts_parent_ticket.email_template_child_ticket')[2]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
        except ValueError:
            compose_form_id = False
        # if not self.partner_id.email:
        #     return self._show_notification('Please Enter Customer Email')
        ticket_ids = self.env["child.ticket"].search([("id", "=", self.child_ticket_id.id)], limit=1).id
        ctx = {
            'default_model': 'child.ticket',
            'default_res_id': ticket_ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        }
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class MultiApproval(models.Model):
    _inherit = 'multi.approval'

    child_ticket_id = fields.Many2one('child.ticket', string='Child Ticket')
    child_task_line_id = fields.Many2one('tasks.master.line', string="Child's Task Line",
                                         help="while delete thet task and if has end task, it needs an approval so this will be the refernece field, once approved then the line will be deleted automatically.")
    stock_id = fields.Many2one('stock.picking', string="Stock Orders")

    attachment_ids = fields.Many2many('ir.attachment', string='Documents', related='child_task_line_id.attachment_ids')

    def dummy(self):
        pass

    def action_approve(self):
        values = super().action_approve()
        child_ticket = self.env['child.ticket'].sudo().browse(self.child_ticket_id.id)
        if self.child_ticket_id.id and self.child_task_line_id:
            if self.state == 'Approved' and not self.child_task_line_id.is_request_approval:
                self.child_task_line_id.sudo().unlink()
                values = {
                    'res_id': self.child_ticket_id.id,
                    'model': 'child.ticket',
                    'body': 'As per the request the status has been deleted.',
                    'author_id': self.env.user.partner_id.id
                }
                self.env['mail.message'].create(values)
                self.child_ticket_id.sudo().message_post(body='As per the request the status has been deleted.')
            else:
                approved_task = self.child_ticket_id.child_configuration_id.work_flow_id.task_list_ids.task_id.filtered(
                    lambda r: r.name == 'Approved')
                if approved_task:
                    self.child_ticket_id.sudo().write(
                        {'state': 'approved', 'task_list_ids': [(0, 0, {'task_id': approved_task.id})]})
                else:
                    raise UserError('There is no Approval Task available on workflow to update on ticket status')
                values = {
                    'res_id': self.child_ticket_id.id,
                    'model': 'child.ticket',
                    'body': 'As per the request the status has been approved.',
                    'author_id': self.env.user.partner_id.id
                }
                self.env['mail.message'].create(values)
                # self.child_ticket_id.sudo().message_post(body='As per the request the status has been approved.')
                self.child_ticket_id.sudo().write({'state': 'approved'})
        elif self.child_ticket_id.id:
            if self.state != 'Approved':

                pass
            else:
                child_ticket.sudo().write({'state': 'approved'})
        return values
