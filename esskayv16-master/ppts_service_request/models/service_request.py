# -*- coding: utf-8 -*-
#############################################################################
#
#    Point Perfect Technology Solutions.
#
#############################################################################
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError, ValidationError
from lxml import etree
import re


class ServiceRequest(models.Model):
    _name = 'service.request'
    _rec_name = 'name'
    _description = "Service Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Service Request ID', copy=False, default="New", required=True)
    service_request_id_alias = fields.Char(string='Service Request ID Alias', copy=False)
    service_request_date = fields.Datetime(string="System Generate Date", required=True, default=fields.Datetime.now)
    customer_name = fields.Char(string='Customer Name', copy=True)
    dealer_distributor_name = fields.Char(string='Customer Dealer/Distributor Name', copy=True
                                          )
    state = fields.Selection(
        [('draft', 'Draft'), ('new', 'New'), ('in_review', 'In Review'),
         ('waiting_for_approval', 'Waiting for approval'),
         ('approved', 'Approved'), ('check_availability_request', 'Check Availability Request'),
         ('external_stock', 'Check External Stock'),
         ('rejected', 'Rejected'), ('hold', 'On Hold'), ('available', 'Available'), ('not_available', 'Not available'),
         ('partial_available', 'Partial Available'), ('converted_to_ticket', 'Converted to Ticket'),
         ('closed', 'Closed'), ('resumed', 'Resumed'), ('reopened', 'Ticket Reopened'), ('cancelled', 'Cancelled')],
        string='Status', default='draft')
    call_source_id = fields.Many2one('call.source', string="Call Source/Type", copy=True)
    service_category_id = fields.Many2one('service.category', string="Service Category", copy=True, required=True)
    service_type_id = fields.Many2one('service.type', string="Service Type", copy=True, required=True)
    request_type_id = fields.Many2one('request.type', string="Approval Type", copy=True, required=True)
    # is_required_approval = fields.Boolean(string="Request Type", copy=True, compute='compute_approval')
    is_required_approval = fields.Boolean(string="Approval Type", copy=True,
                                          related="request_type_id.is_required_approval")
    problem_reported = fields.Text(string='Problem Reported', copy=True)
    product_name = fields.Char(string="Product Name", copy=True)
    custom_product_serial = fields.Char(string="Serial Number", copy=True)
    model = fields.Char(string="Model", copy=True)
    product_category_id = fields.Char(string='Product Category ID', copy=True)
    product_category_alias = fields.Char(string='Product Category Alias', copy=True, help='Cat No')
    requested_by_name = fields.Char(string='Requested by - Name', copy=True)
    requested_by_contact_number = fields.Char(string='Requested by - Contact number', copy=True)
    requested_by_email = fields.Char(string='Requested by - Email', copy=True)
    requested_by_title = fields.Char(string='Requested by - Title', copy=True)
    call_received_id = fields.Many2one('call.received', string="Call Received by", copy=True)
    call_received_on = fields.Datetime(string='Call Received On')
    external_reference = fields.Char(string='External Reference', copy=True, help='JDE Call Ref')
    remarks = fields.Text(string='Remarks', copy=True)
    issue_noticed = fields.Char(string='How was the issue noticed', copy=True)
    case_completed_successfully_id = fields.Many2one('case.completed.successfully',
                                                     string="Was the case completed successfully", copy=True)
    medical_intervention_id = fields.Many2one('medical.intervention', string="Was medical intervention needed",
                                              copy=True)
    patient_involved_id = fields.Many2one('patient.involved', string="Was a patient involved", copy=True)
    surgical_delay_id = fields.Many2one('surgical.delay', string="Was there a surgical delay", copy=True)
    bio_medical_engineer_id = fields.Text(string="Bio Medical Engineer", copy=True,
                                          required=True)
    service_request_status_id = fields.Many2one('service.request.status', string="Service Request Status", copy=True,
                                                help='Upto by Both Manual & By Odoo')
    user_team_ids = fields.Many2many('crm.team', string="User Allowed Teams", store=True, copy=True)
    team_id = fields.Many2one('crm.team', string="Team", compute='_compute_team_id', store=True, readonly=False,
                              precompute=True, copy=True, change_default=True, check_company=True, tracking=True,
                              domain="[('id', 'in', user_team_ids)]")
    dispatch_location_id = fields.Many2one('dispatch.location', string="Dispatch location", copy=True)
    oem_warranty_status_id = fields.Many2one('oem.warranty.status', string="OEM Warranty Status (As per customer)",
                                             copy=True)
    repair_warranty_status_id = fields.Many2one('repair.warranty.status',
                                                string="Repair Warranty Status (As per customer)", copy=True)
    oem_warranty_status = fields.Selection(
        [('in_oem_warranty', 'In OEM Warranty'), ('out_oem_warranty', 'Out Of OEM Warranty'),
         ('not_available', 'Not available')], string='OEM Warranty Status (As per customer)')
    oem_repair_status = fields.Selection(
        [('in_repair_warranty', 'In Repair Warranty'), ('out_repair_warranty', 'Out Of Repair Warranty'),
         ('not_available', 'Not available')], string='Repair Warranty Status (As per customer)')
    survey_id = fields.Many2one('survey.survey', string='Worksheet', copy=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('service.request'),
                                 required=True)
    # Customer Selection address fields
    partner_id = fields.Many2one(comodel_name='res.partner', string="Customer", copy=True)
    street = fields.Char(copy=True)
    street2 = fields.Char(copy=True)
    zip = fields.Char(change_default=True, copy=True)
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]", copy=True)
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', copy=True)
    country_code = fields.Char(related='country_id.code', string="Country Code", copy=True)
    phone = fields.Char(string='Phone', copy=True)
    mobile = fields.Char(string='Mobile', copy=True)
    email = fields.Char(string='Email', copy=True)
    # End Customer Selection
    description = fields.Html("Description", translate=True, sanitize=False)
    # From Service Request
    customer_email = fields.Char(string='Customer Email', copy=True)
    customer_street = fields.Char(copy=True)
    customer_street2 = fields.Char(copy=True)
    customer_zip = fields.Char(change_default=True, copy=True)
    customer_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', copy=True)
    customer_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', copy=True)
    customer_country_code = fields.Char(related='customer_country_id.code', string="Country Code", copy=True)
    parent_count = fields.Integer(compute='compute_parent_count')
    child_count = fields.Integer(compute='compute_child_count')
    user_id = fields.Many2one('res.users', string='Responsible', required=False, default=lambda self: self.env.user.id)
    service_properties = fields.Properties('Properties', definition='partner_id.service_ticket_properties', copy=True)
    dealer_distributor_id = fields.Many2one('res.partner', string="Dealer/Distributor Name", copy=True,
                                            compute='_compute_dealer_check')
    child_ticket_id = fields.Many2one('child.ticket', string="Child Ticket ID", copy=True)
    parent_ticket_id = fields.Many2one('parent.ticket', string="Parent Ticket ID", copy=True)
    approver_id = fields.Many2one('multi.approval.type', string="Approval Level", copy=True)
    # Fields to hide the ticket buttons
    is_parent_ticket_created = fields.Boolean('Parent Ticket Created?')
    is_child_ticket_created = fields.Boolean('Child Ticket Created?')
    approver_ids = fields.One2many('service.ticket.approval', 'service_request_id', string="Approvars")
    close_reason = fields.Text('Close Reason', help="While close the ticket this field will have the details.")
    is_check_available = fields.Boolean('Check the available stock')
    # By Wilbert SR-Loaner
    product_part_number = fields.Char(string='Product Part', copy=True, help="CAT No")
    product_part_code = fields.Char(string="Product Part Code", copy=True, help='Provide Product Code as Model No')
    location_contact_person = fields.Char(string='Location Contact person', copy=True)
    installation_date = fields.Date(string='Installation date')
    customer_po_number = fields.Char(string="Customer PO Ref", copy=True)
    order_number = fields.Char(string="Order Number", copy=True)
    customer_po_date = fields.Date(string="Customer PO Date")
    invoice_number = fields.Char(string="Invoice Number", copy=True)
    invoice_date = fields.Date(string="Invoice Date")
    tender_refer_number = fields.Char(string="Tender Refer Number", copy=True)
    extended_invoice_number = fields.Char(string="Extended Invoice Number", copy=True)
    extended_invoice_date = fields.Date(string="Extended Invoice Date")
    # SR Installation
    install_addr_street = fields.Char(copy=True)
    install_addr_street2 = fields.Char(copy=True)
    install_addr_zip = fields.Char(change_default=True, copy=True)
    install_addr_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', copy=True)
    install_addr_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', copy=True)
    install_addr_country_code = fields.Char(related='customer_country_id.code', string="Country Code", copy=True)
    # Sheet Field
    reason = fields.Char(string="Reason")
    request_hold_date = fields.Date('Hold On')
    request_hold_reason = fields.Char('Hold Reason')
    attachment_ids = fields.Many2many('ir.attachment', 'service_request_attachment_rel', 'service_request_id',
                                      'attachment_id', 'Attachments',
                                      help="You may attach files to this service request, to be added to all ")
    is_auto_approval = fields.Boolean(string="Auto Approval", copy=True, related="request_type_id.is_auto_approval")
    is_approval_lr_from_pt = fields.Boolean(string="Approval Required From Loaner", copy=True)
    is_lr_from_pt = fields.Boolean(string="Approval Required From Loaner", copy=True)
    service_ticket_count = fields.Integer(compute='compute_service_ticket_count')
    event_date = fields.Date(string='Event date', default=fields.Date.context_today)
    adverse_consequences = fields.Text(string="Were there adverse consequences ? ", copy=True)
    # New Fields
    select_adverse_consequences = fields.Selection(
        [('complainant_not_aware', 'Complainant Not Aware'), ('no', 'No '), ('yes', 'Yes'),
         ('not_reported', 'Not Reported')],
        string="Were there adverse consequences")
    complaint_type = fields.Selection(
        [('service_facility', 'Service Facility'), ('user_facility', 'User Facility')], string='Complaint type')
    is_website_order = fields.Boolean(string="Is Website Order", copy=True)
    request_count = fields.Integer(string="Request Count", compute='compute_request_count')
    assign_engineer_ids = fields.Many2many(comodel_name='res.users', relation='assign_engineer_rel', string="Engineer",
                                           readonly=True)
    ct_user = fields.Many2one('res.users', string='User Level 2')
    # PM - Fields
    customer_contract_count = fields.Integer(string="Customer Contract", compute='compute_request_count')
    event_description = fields.Char(string="Event Description (be specific)", copy=True)
    date_of_event = fields.Date(string="Date of Event", copy=True)
    awareness_date = fields.Date(string="Awareness Date", copy=True)
    repair_location_id = fields.Many2one('stock.warehouse', string="Repair Center Location")
    action_taken_at_site = fields.Char(string='Action taken at Site')
    alternate_contact_name = fields.Char(string='Alternate Contact name')
    alternate_contact_number = fields.Char(string='Alternate Contact number')
    alternate_contact_email = fields.Char(string='Alternate Contact Email')
    is_oem_warranty = fields.Boolean('OEM Warranty Check', compute='_compute_service_category_id_check_visible')
    is_repair_warranty = fields.Boolean('Repair Warranty Check', compute='_compute_service_category_id_check_visible')
    warranty_start_dates = fields.Date(string="Warranty Start Date", compute='_compute_warranty_start_end_date')
    warranty_end_dates = fields.Date(string="Warranty End Date", compute='_compute_warranty_start_end_date')

    repair_warranty_start_date = fields.Date(string="Repair Warranty Start Date",
                                             help='Manual / Updated by system end of Ticket & Warranty certificate Generation',
                                             compute='_compute_warranty_start_end_date')
    repair_warranty_end_date = fields.Date(string="Repair Warranty End Date",
                                           help='Manual / Updated by system end of Ticket & Warranty certificate Generation',
                                           compute='_compute_warranty_start_end_date')

    def _compute_warranty_start_end_date(self):
        for rec in self:
            if rec.customer_asset_ids:
                asset = rec.customer_asset_ids[-1]
                if asset:
                    rec.warranty_start_dates = asset.stock_lot_id.warranty_start_date
                else:
                    rec.warranty_start_dates = False
                if asset:
                    rec.warranty_end_dates = asset.stock_lot_id.warranty_end_date
                else:
                    rec.warranty_end_dates = False
                if asset:
                    rec.repair_warranty_start_date = asset.stock_lot_id.repair_warranty_start_date
                else:
                    rec.repair_warranty_start_date = False
                if asset:
                    rec.repair_warranty_end_date = asset.stock_lot_id.repair_warranty_end_date
                else:
                    rec.repair_warranty_end_date = False
            else:
                rec.warranty_start_dates = False
                rec.warranty_end_dates = False
                rec.repair_warranty_start_date = False
                rec.repair_warranty_end_date = False

    @api.depends('service_category_id')
    def _compute_service_category_id_check_visible(self):
        # When u select the service category based on these fields will be show.
        for rec in self:
            if rec.service_category_id.code == 'WR':
                rec.is_oem_warranty = True
            elif rec.service_category_id.code == 'WRT':
                rec.is_oem_warranty = True
            else:
                rec.is_oem_warranty = False
            if rec.service_category_id.code == 'RW':
                rec.is_repair_warranty = True
            else:
                rec.is_repair_warranty = False

    @api.depends('partner_id')
    def _compute_dealer_check(self):
        # The customer master dealer name will appear in the dealer distributer name field when you pick the customer.
        for rec in self:
            partner_check = self.env['res.partner'].search(
                [('name', '=', rec.partner_id.name)])
            if partner_check:
                rec.dealer_distributor_id = partner_check.dealer_distributer_ids.dealer_id.id
            else:
                rec.dealer_distributor_id = False

    def customer_address_check(self):
        if self.partner_id:
            self.customer_street = self.partner_id.street
            self.customer_street2 = self.partner_id.street2
            self.customer_state_id = self.partner_id.state_id
            self.customer_zip = self.partner_id.zip
            self.customer_country_id = self.partner_id.country_id

    @api.onchange('customer_email')
    # When you enter the wrong (proper) email through the validation error.
    def validate_email_id(self):
        if self.customer_email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                             self.customer_email)
            if match == None:
                raise ValidationError('Not a valid E-mail ID')

    @api.onchange('country_id')
    # When you select a county, it automatically changes to a matching county state.
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange('state_id')
    # When you select a state, it automatically changes to a matching state county.
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

    @api.onchange('customer_state_id')
    # When you select a state, it automatically changes to a matching state county.
    def _onchange_customer_state_id(self):
        if self.customer_state_id:
            self.customer_country_id = self.customer_state_id.country_id.id

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            if record.partner_id.is_block_partner == 'blocked':
                raise UserError('The customer has been blocked. Please change the customer.')
        return res

    @api.model
    def get_view(self, view_id=None, view_type=None, **options):
        res = super(ServiceRequest, self).get_view(view_id, view_type, **options)
        if (res) and (view_type in ('form', 'tree')) and not self.env.user.has_group(
                'ppts_service_request.service_request_group_ct_user'):
            tree_view = self.env.ref("ppts_service_request.so_call_tree_view").id
            form_view = self.env.ref("ppts_service_request.so_call_form_view").id
            doc = etree.XML(res['arch'])
            if view_type == 'tree' and view_id == tree_view:
                nodes = doc.xpath("//tree")
                for node in nodes:
                    node.set('create', '0')
                res['arch'] = etree.tostring(doc)
            if view_type == 'form' and view_id == form_view:
                nodes = doc.xpath("//form")
                for node in nodes:
                    node.set('create', '0')
                res['arch'] = etree.tostring(doc)
        return res

    @api.onchange('service_type_id')
    def onchange_service_type_domain(self):
        category_ids = self.service_type_id.service_category_ids.mapped('id')
        approval_type_ids = self.service_type_id.request_type_ids.mapped('id')
        request_domain = [('id', 'in', approval_type_ids)]
        domain = [('id', 'in', category_ids)]
        return {'domain': {'service_category_id': domain, 'request_type_id': request_domain}}

    @api.onchange('requested_by_email')
    def validate_email_id_check(self):
        # When you enter the wrong (proper) email through the validation error.
        if self.requested_by_email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                             self.requested_by_email)
            if match == None:
                raise ValidationError('Not a valid E-mail ID')

    # Priya
    @api.onchange('request_type_id')
    def onchange_request_type_domain(self):
        domain = [('ticket_type', '=', self.request_type_id.ticket_type)]
        return {'domain': {'request_type_id': domain}}

    # def write(self, vals):
    #     result = super(ServiceRequest, self).write(vals)
    #     last_task_id = []
    #     pt_task_ids = self.parent_ticket_id.task_list_ids.mapped("task_id")
    #     for pt_task in pt_task_ids:
    #         last_task_id.append(pt_task.id)
    #     last_id = last_task_id.pop() if last_task_id else None
    #     if 'state' in vals:
    #         if self.is_lr_from_pt:
    #             task_id = None
    #             if self.state == 'approved' and self.parent_ticket_id:
    #                 task_id = self.env.ref('ppts_custom_workflow.task_data_loaner_transfer_approved')
    #             elif self.state == 'rejected' and self.parent_ticket_id:
    #                 task_id = self.env.ref('ppts_custom_workflow.task_data_loaner_transfer_rejected')
    #             elif self.state == 'available' and self.parent_ticket_id:
    #                 task_id = self.env.ref('ppts_custom_workflow.task_data_loaner_available')
    #             elif self.state == 'not_available' and self.parent_ticket_id:
    #                 task_id = self.env.ref('ppts_custom_workflow.task_data_loaner_not_available')
    #
    #             if task_id and not task_id.id == last_id:
    #                 pt_id = self.env["parent.ticket"].search([("id", "=", self.parent_ticket_id.id)])
    #                 pt_id.update({
    #                     'task_list_ids': [(0, 0, {'task_id': task_id.id})],
    #                 })
    #     return result

    # def compute_approval(self):
    #     for rec in self:
    #         if rec.request_type_id.is_required_approval or rec.is_approval_lr_from_pt:
    #             rec.is_required_approval = True
    #         else:
    #             rec.is_required_approval = False

    # Acknowledgment
    def action_send_acknowledgment_from_pt(self):
        email = self.partner_id.email
        teams = self.env['hr.employee'].search([('job_id', 'in',
                                                 self.parent_ticket_id.parent_configuration_id.alert_loaners_approval_team_ids.ids)]).mapped(
            'work_email')
        approval_mails = ', '.join(teams)
        if self.parent_ticket_id.parent_configuration_id and self.parent_ticket_id.parent_configuration_id.is_loaners:
            cust_template_id = self.parent_ticket_id.parent_configuration_id.loaners_cust_email_template_id
            approval_template_id = self.parent_ticket_id.parent_configuration_id.alert_loaners_email_template_id
            if self.parent_ticket_id.parent_configuration_id.alert_loaners == 'confirm' and self.state == 'approved':
                if cust_template_id:
                    cust_template_id.with_context(email_to=email).sudo().send_mail(self.parent_ticket_id.id,
                                                                                   force_send=True)
                if approval_template_id:
                    approval_template_id.with_context(email_to=approval_mails).sudo().send_mail(
                        self.parent_ticket_id.id, force_send=True)
            elif self.parent_ticket_id.parent_configuration_id.alert_loaners == 'done' and self.state == 'closed':
                if cust_template_id:
                    cust_template_id.with_context(email_to=email).sudo().send_mail(self.parent_ticket_id.id,
                                                                                   force_send=True)
                if approval_template_id:
                    approval_template_id.with_context(email_to=approval_mails).sudo().send_mail(
                        self.parent_ticket_id.id, force_send=True)
            elif self.parent_ticket_id.parent_configuration_id.alert_loaners == 'both' and self.state in (
                    'approved', 'closed'):
                if cust_template_id:
                    cust_template_id.with_context(email_to=email).sudo().send_mail(self.parent_ticket_id.id,
                                                                                   force_send=True)
                if approval_template_id:
                    approval_template_id.with_context(email_to=approval_mails).sudo().send_mail(
                        self.parent_ticket_id.id, force_send=True)

    @api.onchange('email')
    # When you enter the wrong (proper) email through the validation error.
    def email_validate_check(self):
        if self.email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
            if match == None:
                raise ValidationError('Not a valid E-mail ID')

    # @api.model
    # def default_get(self, fields_list):
    #     res = super().default_get(fields_list)
    #     if self.env.context.get('request_type') == 'factory_repair':
    #         factory_id = self.env['request.type'].search([('ticket_type', '=', 'sr_factory_repair')], limit=1)
    #         res['request_type_id'] = factory_id.id
    #     elif self.env.context.get('request_type') == 'fsm':
    #         fsm_id = self.env['request.type'].search([('ticket_type', '=', 'sr_fsm')], limit=1)
    #         res['request_type_id'] = fsm_id.id
    #     elif self.env.context.get('request_type') == 'installation':
    #         installation_id = self.env['request.type'].search([('ticket_type', '=', 'sr_installation')], limit=1)
    #         res['request_type_id'] = installation_id.id
    #     elif self.env.context.get('request_type') == 'loaner':
    #         loaner_id = self.env['request.type'].search([('ticket_type', '=', 'sr_loaner')], limit=1)
    #         res['request_type_id'] = loaner_id.id
    #     elif self.env.context.get('request_type') == 'remote_support':
    #         remote_support_id = self.env['request.type'].search([('ticket_type', '=', 'sr_remote_support')], limit=1)
    #         res['request_type_id'] = remote_support_id.id
    #     elif self.env.context.get('request_type') == 'maintenance':
    #         maintenance_id = self.env['request.type'].search([('ticket_type', '=', 'sr_maintenance')], limit=1)
    #         res['request_type_id'] = maintenance_id.id
    #     elif self.env.context.get('request_type') == 'wr':
    #         wr_id = self.env['request.type'].search([('ticket_type', '=', 'sr_wr')], limit=1)
    #         res['request_type_id'] = wr_id.id
    #     elif self.env.context.get('request_type') == 'so_call':
    #         so_id = self.env['request.type'].search([('ticket_type', '=', 'so_call')], limit=1)
    #         res['request_type_id'] = so_id.id
    #     return res

    def action_open_request_view(self):
        view = None
        for request in self:
            if request.request_type_id.ticket_type == 'sr_loaner':
                view = self.env.ref('ppts_service_request.service_request_sr_loaner_form_view')
            elif request.request_type_id.ticket_type == 'sr_wr':
                view = self.env.ref('ppts_service_request.service_request_sr_wr_form_view')
            elif request.request_type_id.ticket_type == 'sr_factory_repair':
                view = self.env.ref('ppts_service_request.service_request_sr_factory_form_view')
            elif request.request_type_id.ticket_type == 'sr_fsm':
                view = self.env.ref('ppts_service_request.service_request_sr_fsm_form_view')
            elif request.request_type_id.ticket_type == 'sr_installation':
                view = self.env.ref('ppts_service_request.service_request_sr_installation_form_view')
            elif request.request_type_id.ticket_type == 'sr_maintenance':
                view = self.env.ref('ppts_service_request.service_request_maintenance_form_view')
            elif request.request_type_id.ticket_type == 'sr_remote_support':
                view = self.env.ref('ppts_service_request.service_request_sr_remote_support_form_view')
            elif request.request_type_id.ticket_type == 'so_call':
                view = self.env.ref('ppts_service_request.so_call_form_view')
            else:
                view = self.env.ref('ppts_service_request.service_request_form_view')
            return {
                'type': 'ir.actions.act_window',
                'name': 'Service Request',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view.id,
                'res_model': 'service.request',
                'res_id': request.id,
                'target': 'current',
            }

    # Open Based on Request Type
    def action_open_request_based_type(self):
        action_id = None
        for request in self:
            if request.request_type_id.ticket_type == 'sr_loaner':
                action_id = self.env.ref('ppts_service_request.action_service_request_sr_loaner')
            elif request.request_type_id.ticket_type == 'sr_wr':
                action_id = self.env.ref('ppts_service_request.action_service_request_sr_wr')
            elif request.request_type_id.ticket_type == 'sr_factory_repair':
                action_id = self.env.ref('ppts_service_request.action_service_request_sr_factory')
            elif request.request_type_id.ticket_type == 'sr_fsm':
                action_id = self.env.ref('ppts_service_request.action_service_request_sr_fsm')
            elif request.request_type_id.ticket_type == 'sr_installation':
                action_id = self.env.ref('ppts_service_request.action_service_request_sr_installation')
            elif request.request_type_id.ticket_type == 'sr_maintenance':
                action_id = self.env.ref('ppts_service_request.action_service_request_maintenance')
            elif request.request_type_id.ticket_type == 'sr_remote_support':
                action_id = self.env.ref('ppts_service_request.action_service_request_sr_remote_support')
            elif request.request_type_id.ticket_type == 'so_call':
                action_id = self.env.ref('ppts_service_request.action_so_call')
            else:
                action_id = self.env.ref('ppts_service_request.action_service_request')
        return action_id.id

    @api.depends('user_id')
    def _compute_team_id(self):
        for order in self:
            team_ids = self.env.user.team_ids
            if team_ids:
                order.team_id = team_ids[0].id
                order.user_team_ids = team_ids.ids
            else:
                order.team_id = False

    # @api.onchange('request_type_id')
    # def _onchange_request_type(self):
    #     team_ids = self.env.user.team_ids.ids
    #     if team_ids and self.request_type_id.sudo().team_id.id in team_ids and self.request_type_id.team_id:
    #         self.team_id = self.request_type_id.team_id.id
    #         return {'domain': {'team_id': [('id', '=', self.request_type_id.team_id.id)]}}
    #     else:
    #         self.team_id = False

    def action_submit(self):
        # When you click the submit button, the state moves to a new stage.
        self.state = 'new'
        # Whoever clicks the submit button will see the user name and the Responsible name.
        self.user_id = self.env.user.id
        mail_list = []
        for members in self.team_id.member_ids:
            if members.has_group('ppts_service_request.service_request_group_ct_user'):
                mail_list.append(members.login)
        mails = ', '.join(mail_list)
        get_action = self.action_open_request_based_type()
        template_id = self.env.ref('ppts_service_request.email_template_service_request_submit')
        base_url = '/web#id=%d&action=%r&model=service.request&view_type=form' % (self.id, get_action)
        if template_id:
            template_id.with_context(rec_url=base_url, email_to=mails).sudo().send_mail(self.id, force_send=True)
        if not self.team_id:
            raise UserError('Map the team to submit the request.')
        # Update the status on the child ticket
        if self.child_ticket_id:
            service_request_submitted_task_id = self.env['tasks.master'].search(
                [('python_code', '=', 'service_request_submitted')])
            if not service_request_submitted_task_id:
                raise UserError(
                    "Create Service Request Submitted with python code as 'service_request_submitted' to proceed further.")
            self.child_ticket_id.task_list_ids = [(0, 0, {'task_id': service_request_submitted_task_id.id})]

    def action_for_review(self):
        self.ct_user = self.env.user.id
        # Check for the ticket type whether its warranty replacement or not, if its warranty then check for the contract and if not do not allow to proceed further
        if self.service_type_id.ticket_type == 'sr_wr':
            today_date = fields.Date.today()
            is_exist = False
            for record in self.env['contract.contract'].search(
                    [('state', '=', 'started'), ('partner_id', '=', self.partner_id.id),
                     ('date_start', '<=', today_date), ('date_end', '>=', today_date)]):
                for contract_lines in record.contract_line_fixed_ids:
                    for service_request in self.customer_asset_ids:
                        if contract_lines.stock_lot_id.id == service_request.stock_lot_id.id:
                            is_exist = True
                            break
            if not is_exist:
                raise ValidationError(_("There is no any contract for this customer '%s'", self.partner_id.name))
        if self.child_ticket_id:
            service_request_submitted_task_id = self.env['tasks.master'].search(
                [('python_code', '=', 'service_request_inreview')])
            if not service_request_submitted_task_id:
                raise UserError(
                    "Create Service Request In Review with python code as 'service_request_inreview' to proceed further.")
            self.child_ticket_id.task_list_ids = [(0, 0, {'task_id': service_request_submitted_task_id.id})]
        self.state = 'in_review'

    def action_ticket_close(self):
        user_exist = self._check_user_exist()
        if user_exist and self.approver_ids:
            return {
                'name': "Reason",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'reason.reason',
                'target': 'new',
                'context': {'default_reason_type': 'close'}
            }
        elif not self.approver_ids:
            return {
                'name': "Reason",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'reason.reason',
                'target': 'new',
                'context': {'default_reason_type': 'close'}
            }
        else:
            return self._show_notification('You are not allowed to Close this Service Request' + ' ' + self.name)

    def action_for_approval(self):
        values = []
        attachments = []
        '''
        1. If the ticket type is installation then the asset will be mapped after completing the installation process,
            and need to check while close the parent ticket, if the asset is not mapped then should not allow to clsoe the installation parent ticket.
        '''
        if not self.customer_asset_ids:
            raise UserError(_("Please Add the Assets to send for an approval."))
        if not self.partner_id:
            raise UserError(_("Please map the customer to send for an approval."))
        # for record in self.approver_id.line_ids:
        #     vals = (0, 0, {
        #         "sequence": record.sequence,
        #         "user_id": record.user_id.id,
        #         "require_opt": record.require_opt,
        #         "state": 'new',
        #     })
        #     values.append(vals)
        # if values:
        #     self.approver_ids = values
        if self.request_type_id.is_required_approval and self.request_type_id.is_auto_approval:
            for approval_user in self.approver_ids:
                approval_user.state = 'approved'
                approval_user.approved_on = fields.Date.today()
            self.state = 'approved'
        elif self.request_type_id.is_required_approval and not self.request_type_id.is_auto_approval:
            # CTwork on factory repair SR and sends
            # for approval, the supporting information that to be sent is, equipment details, warranty/contract details,
            # problem reported and engineer comment/reason for movement and attachment of service report
            self.state = 'waiting_for_approval'
            # Create the approval list under the approval process module
            if self.attachment_ids:
                for service_attachment in self.attachment_ids:
                    ir_values = {
                        'name': str(service_attachment.name) + "Copy",
                        'type': service_attachment.type,
                        'datas': service_attachment.datas,
                        'store_fname': service_attachment.store_fname,
                        'mimetype': service_attachment.mimetype,
                        'res_model': 'multi.approval',
                        'public': True,
                    }
                    report_attachment_id = self.env['ir.attachment'].sudo().create(ir_values)
                    attachments.append(report_attachment_id.id)
            approval_id = self.env['multi.approval'].create({
                'name': self.name,
                'user_id': self.env.user.id,
                'type_id': self.approver_id.id,
                'service_request_id': self.id,
                'attachment_ids': attachments
            })
            approval_id.action_submit()
            if self.child_ticket_id:
                service_request_submitted_task_id = self.env['tasks.master'].search(
                    [('python_code', '=', 'service_request_approval')])
                if not service_request_submitted_task_id:
                    raise UserError(
                        "Create Service Request Sent for Approval with python code as 'service_request_approval' to proceed further.")
                self.child_ticket_id.task_list_ids = [(0, 0, {'task_id': service_request_submitted_task_id.id})]
            action_id = self.env.ref('ppts_service_request.action_service_request_approval', raise_if_not_found=False)
            template_id = self.env.ref('ppts_service_request.mail_template_notify_approvers')
            for approver in self.approver_id.line_ids:
                base_url = '/web#id=%d&action=%r&model=service.request&view_type=form' % (self.id, action_id.id)
                oem_warranty_status = dict(self._fields['oem_warranty_status'].selection).get(self.oem_warranty_status)
                oem_repair_status = dict(self._fields['oem_repair_status'].selection).get(self.oem_repair_status)

                if template_id:
                    template_id.with_context(rec_url=base_url, warranty=oem_warranty_status,
                                             repair=oem_repair_status).sudo().send_mail(approver.id, force_send=True)
        else:
            self.state = 'approved'
        return True

    def _check_user_exist(self):
        if self.env['service.ticket.approval'].search(
                [('user_id', '=', self.env.user.id), ('service_request_id', '=', self.id)]):
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

    def action_approved(self):
        user_exist = self._check_user_exist()
        if user_exist:
            for approver_id in self.env['service.ticket.approval'].search(
                    [('user_id', '=', self.env.user.id), ('service_request_id', '=', self.id)]):
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
                self.action_send_acknowledgment_from_pt()
        else:
            return self._show_notification('You are not allowed to approve this service request' + ' ' + self.name)

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
            return self._show_notification('You are not allowed to reject this service request' + ' ' + self.name)

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
            return self._show_notification('You are not allowed to hold this service request' + ' ' + self.name)

    # Service Request Sequences
    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            vals['name'] = self.env['ir.sequence'].with_context(force_company=self.env.user.company_id.id).next_by_code(
                'service.request') or _('New')
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('service.request') or _('New')
        return super(ServiceRequest, self).create(vals)

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id.is_block_partner == 'blocked':
            raise UserError('The customer has been blocked. Please change the customer.')
        if self.partner_id:
            self.street = self.partner_id.street or ''
            self.street2 = self.partner_id.street2 or ''
            self.city_id = self.partner_id.city_id.id or False
            self.state_id = self.partner_id.state_id.id or False
            self.country_id = self.partner_id.country_id.id or False
            self.zip = self.partner_id.zip or ''
            self.phone = self.partner_id.phone or ''
            self.mobile = self.partner_id.mobile or ''
            self.email = self.partner_id.email or ''
            self.customer_type_id = self.partner_id.customer_type.id or False
            self.customer_region_id = self.partner_id.customer_region.id or False
            self.gst_no = self.partner_id.gst_no or ''
            self.tier_tier_id = self.partner_id.tier_tier.id or False
            self.hospital_name = self.partner_id.hospital_name or ''
            self.surgeon_name = self.partner_id.surgeon_name or ''
            self.customer_group_id = self.partner_id.customer_group or ''
            self.customer_id_alias = self.partner_id.customer_id_alias or ''
            self.d_number = self.partner_id.d_number or ''
            self.customer_id = self.partner_id.id

    def customer_selection(self):
        if self.customer_name:
            partner_obj = self.env['res.partner'].search([('name', '=', self.customer_name)], limit=1)
            if partner_obj:
                self.partner_id = partner_obj.id or False
                self.street = partner_obj.street or ''
                self.street2 = partner_obj.street2 or ''
                self.zip = partner_obj.zip or ''
                self.city = partner_obj.city or ''
                self.state_id = partner_obj.state_id.id or False
                self.country_id = partner_obj.country_id.id or False
                self.country_code = partner_obj.country_code or ''
                self.phone = partner_obj.phone or ''
                self.mobile = partner_obj.mobile or ''
                self.email = partner_obj.email or ''
            else:
                raise UserError(_("Customer does not Exists! "))
        else:
            raise UserError(_("Please Enter the Customer Name "))

    # Send By Email
    def action_send_mail(self):
        '''
        This function opens a window to compose an email, with the service request template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup('ppts_service_request.email_template_service_request')[2]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
        except ValueError:
            compose_form_id = False
        if not self.partner_id.email:
            return self._show_notification('Please Enter Customer Email')
        ctx = {
            'default_model': 'service.request',
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

    @api.onchange('customer_asset_ids')
    def onchange_customer_asset_ids(self):
        for order in self.customer_asset_ids:
            line = self.customer_asset_ids.filtered(lambda l: l.stock_lot_id == order.stock_lot_id)
            if len(line) > 1:
                raise UserError(_('You cannot have multiple lines with same Serial Number - %s') % (
                        line[1].stock_lot_id.name or ''))

    # Parent Count
    def compute_parent_count(self):
        for record in self:
            record.parent_count = self.env['parent.ticket'].search_count([('service_request_id', '=', record.id)])

    # Parent Count
    def compute_child_count(self):
        for record in self:
            record.child_count = self.env['child.ticket'].search_count([('service_request_id', '=', record.id)])

    def compute_service_ticket_count(self):
        for record in self:
            record.service_ticket_count = self.env['multi.approval'].search_count(
                [('service_request_id', '=', record.id)])

    # Smart Button - Action view Parent Tickets
    def action_view_parent_tickets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Parent Ticket',
            'view_mode': 'tree,form',
            'res_model': 'parent.ticket',
            'domain': [('service_request_id', '=', self.id)],
            'context': "{'create': False}"
        }

    # Smart Button - Action view Parent Tickets
    def action_view_child_tickets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Child Ticket',
            'view_mode': 'tree,form',
            'res_model': 'child.ticket',
            'domain': [('service_request_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def action_view_service_request_approval(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Approvals',
            'view_mode': 'tree,form',
            'res_model': 'multi.approval',
            'domain': [('service_request_id', '=', self.id)],
            'context': "{'create': False}"
        }

    # Smart Button - requests
    def action_view_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Request',
            'view_mode': 'tree,form',
            'res_model': 'request',
            'domain': [('service_request_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_request_count(self):
        for record in self:
            record.request_count = self.env['request'].search_count([('service_request_id', '=', self.id)])

    def check_availability_request(self):
        # Stock Check is External Or Internal
        if self.partner_id.customer_account_id and self.customer_asset_ids:
            loaner = self.partner_id.customer_account_id.stock_checking_process_ids.filtered(
                lambda l: l.request_type == 'loaner')
            warranty = self.partner_id.customer_account_id.stock_checking_process_ids.filtered(
                lambda l: l.request_type == 'warranty_replacement')
            if loaner.stock_request_type == 'external' and self.request_type_id.ticket_type == 'sr_loaner' or warranty.stock_request_type == 'external' and self.request_type_id.ticket_type == 'sr_wr':
                # Creates Request for External Stock Check
                request_data = {
                    'name': self.name + " External Stock Check",
                    'service_request_id': self.id,
                    'team_id': self.team_id.id,
                    'user_id': self.env.user.id,
                    'is_external_service': True,
                    'asset_ids': [(0, 0, {
                        'stock_lot_id': line.stock_lot_id.id,
                        'product_id': line.product_id.id,
                        'description': line.product_id.name,
                        'quantity': 1,
                        'product_uom_id': line.product_id.uom_id.id,
                    }) for line in self.customer_asset_ids],
                }
                request = self.env['request'].create(request_data)

                # Send Mail to Respective Customer Account
                action_id = self.env.ref('ppts_parent_ticket.action_request', raise_if_not_found=False)
                template_id = self.env.ref('ppts_service_request.mail_template_external_stock_check')
                base_url = '/web#id=%d&cids=1&action=%r&model=request&view_type=form' % (request.id, action_id.id)
                if template_id:
                    template_id.with_context(rec_url=base_url).sudo().send_mail(self.id, force_send=True)
                self.state = 'external_stock'
            elif loaner.stock_request_type == 'internal' and self.request_type_id.ticket_type == 'sr_loaner' or warranty.stock_request_type == 'internal' and self.request_type_id.ticket_type == 'sr_wr':
                self.is_check_available = True
                self.state = 'check_availability_request'
            else:
                UserError(_("There is no stock check options for customer account %s") % (
                        self.partner_id.customer_account_id.name or ''))
        else:
            raise UserError(_("There is no product in Asset Selection "))

    def check_available_stock(self):
        if self.customer_asset_ids:
            for asset in self.customer_asset_ids:
                qty = sum(asset.product_id.stock_quant_ids.filtered(lambda l: l.location_id.usage == 'internal').mapped(
                    'available_quantity'))
                if qty > 0:
                    asset.is_available = True
            if all(x.is_available for x in self.customer_asset_ids):
                self.state = 'available'
            elif any(x.is_available for x in self.customer_asset_ids):
                self.state = 'partial_available'
            else:
                self.state = 'not_available'
        else:
            raise UserError(_("There is no product in Asset Selection "))

    def service_request_reopen(self):
        self.approver_ids = False
        self.approver_id = False
        self.state = 'new'

    # Button - Resume
    def service_request_resume(self):
        # When you click the Resume button, the state moves to a Resumed stage.
        self.state = 'resumed'

    def action_request_hold(self):
        return {
            'name': "Reason",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'reason.reason',
            'target': 'new',
            'context': {'default_reason_type': 'request_hold'}
        }

    def service_request_in_review(self):
        self.state = 'in_review'

    def action_request_cancel(self):
        self.state = 'cancelled'


class ServiceTicketApproval(models.Model):
    _name = 'service.ticket.approval'

    service_request_id = fields.Many2one('service.request', string="Service Request", ondelete="cascade")
    sequence = fields.Integer(string='Sequence')
    user_id = fields.Many2one(string='User', comodel_name="res.users")
    require_opt = fields.Selection(
        [('Required', 'Required'),
         ('Optional', 'Optional'),
         ], string="Type of Approval", default='Required')
    state = fields.Selection(
        [('new', 'New'), ('approved', 'Approved'),
         ('rejected', 'Rejected'), ('hold', 'Hold'),
         ], string="Status", default='new')
    reject_reason = fields.Char('Reject Reason')
    approved_on = fields.Date('Approved On')
    rejected_on = fields.Date('Rejected On')
    hold_on = fields.Date('Hold On')
    hold_reason = fields.Char('Hold Reason')


class MultiApproval(models.Model):
    _inherit = 'multi.approval'

    service_request_id = fields.Many2one('service.request', string='Service Ticket')

    def action_approve(self):
        values = super().action_approve()
        if self.service_request_id and self.state == 'Approved':
            if self.service_request_id.child_ticket_id:
                service_request_submitted_task_id = self.env['tasks.master'].search(
                    [('python_code', '=', 'service_request_approved')])
                if not service_request_submitted_task_id:
                    raise UserError(
                        "Create Service Request Approved with python code as 'service_request_approved' to proceed further.")
                self.service_request_id.child_ticket_id.task_list_ids = [
                    (0, 0, {'task_id': service_request_submitted_task_id.id})]
            self.service_request_id.sudo().state = 'approved'
        return values
