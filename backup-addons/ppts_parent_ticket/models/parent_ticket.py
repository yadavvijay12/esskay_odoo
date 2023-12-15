# -*- coding: utf-8 -*-
#############################################################################
#                                                                           #
#    Point Perfect Technology Solutions.                                    #
#                                                                           #
#############################################################################
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import Warning, UserError, ValidationError
import base64


class ParentTicket(models.Model):
    _name = 'parent.ticket'
    _rec_name = 'name'
    _description = "Parent Ticket"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_next_task_ids(self):
        tasks_all_ids = self.env["tasks.master"].search([])
        return tasks_all_ids.ids

    name = fields.Char(string='Parent Ticket ID', copy=False, default="New", help='Job No')
    parent_ticket_id_alias = fields.Char(string='Ticket ID Alias', help='External Reference ex.JDE', required=True)
    parent_ticket_id_alias_date = fields.Date(string='Ticket ID Alias Date')
    parent_configuration = fields.Char(string='Parent Configuration')
    parent_configuration_id = fields.Many2one('parent.ticket.configuration', string="Parent Configuration",
                                              required=True, )
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('parent.ticket'))
    call_source_id = fields.Many2one('call.source', string="Call Source")
    call_date = fields.Datetime(string="Call Date", default=fields.Datetime.now)
    service_category_id = fields.Many2one('service.category', string="Service Category")
    service_category_code = fields.Char(string="Service Category Code", related="service_category_id.code")
    remarks_service_category = fields.Text(string='Remarks')
    service_type_id = fields.Many2one('service.type', string="Service Type")
    service_type_code = fields.Char(string="Service Type Code", related="service_type_id.code")
    remarks_service_type = fields.Text(string='Remarks')
    request_type_id = fields.Many2one('request.type', string="Approval Type", required=True)
    request_type = fields.Char(compute='get_request_ticket_type', string="Request Ticket Type")
    product_id = fields.Many2one('product.product', string="Product")
    # product_serial_no = fields.Many2one('stock.lot',string="Product Serial No")
    serial_number_id = fields.Many2one('asset.model', string="Asset Serial No")
    stock_lot_id = fields.Many2one('stock.lot', string="Asset Serial No", required=True)
    categ_id = fields.Many2one('product.category', 'Product Category')
    product_category_id_alias = fields.Char(string='Product Category ID Alias')
    problem_description = fields.Text(string='Problem Reported')
    requested_by_name = fields.Char(string='Requested by - Name', help='Contact/Text')
    requested_by_contact_number = fields.Char(string='Requested by - Contact number', help='Contact/Text')
    requested_by_email = fields.Char(string='Requested by - Email')
    requested_by_title = fields.Char(string='Requested by - Title')
    remarks = fields.Text(string='Remarks')
    installation_date = fields.Datetime(string="Installation Start Date")
    installation_end_date = fields.Datetime(string="Installation End Date")
    installation_date_pt = fields.Datetime(string="Installation Date", related='stock_lot_id.installation_date')
    dealer_distributor_id = fields.Many2one('res.partner', string="Dealer / Distributor Name")
    call_received_id = fields.Many2one('call.received', string="Call Received by")
    external_work_order_date = fields.Date(string="External Work Order Date")
    alternate_contact_name = fields.Char(string='Alternate Contact name')
    alternate_contact_number = fields.Char(string='Alternate Contact number')
    alternate_contact_email = fields.Char(string='Alternate Contact Email')

    oem_warranty_status_id = fields.Many2one('oem.warranty.status', string="OEM Warranty Status (As per customer)",
                                             copy=False)
    repair_warranty_status_id = fields.Many2one('repair.warranty.status',
                                                string="Repair Warranty Status (As per customer)")
    team_id = fields.Many2one('crm.team', string="Team", help="Should inherit from user & Edit", required=True)
    repair_center_location_id = fields.Many2one('stock.warehouse', string="Repair Center Location",
                                                help="Map the warehouse based on this only need to take the transit location to create inward and the product needs to be moved from customer location to transit location.")
    price_available_in_contract = fields.Selection(
        [('yes', 'Yes'), ('no', 'No'), ('not_verified', 'Not Verified'), ('not_applicable', 'Not Applicable')],
        string='Price available in Contract')
    customer_account_id = fields.Many2one('res.partner', string="Customer Account",
                                          related='partner_id.customer_account_id')
    service_request_id = fields.Many2one('service.request', string="Service Request ID")
    product_code_no = fields.Char(string='Product Code No.')
    cat_no = fields.Char(string='Product Part No')
    franchise_id = fields.Many2one('res.partner', string="Franchise")
    re_repair = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Re-Repair')
    faulty_section = fields.Char(string='Faulty Section')
    sow = fields.Char(string='SOW')
    webdelata_id = fields.Char(string='Webdelta ID')
    webdelata = fields.Char(string='Webdelta')
    mc_stk = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='MC-STK')
    pi_no = fields.Char(string='PI No')
    exp_no = fields.Char(string='Exp No')
    last_action_date = fields.Date(string="Last Action Date", tracking=True)
    state = fields.Selection(
        [('new', 'New'), ('warranty_check', 'OEM Warranty Approval'),
         ('repair_warranty_check', 'Repair Warranty Approval'), ('confirm', 'Confirm'),
         ('waiting_for_approval', 'Waiting for approval'),
         ('approved', 'Approved'), ('closed', 'Closed'), ('rejected', 'Rejected')], string='Status',
        default='new', tracking=3)
    description = fields.Html("Description", translate=True, sanitize=False)
    assign_engineer_ids = fields.Many2many(comodel_name='res.users', relation='parent_ticket_assign_engineer_rel',
                                           string="Engineer")
    child_count = fields.Integer(compute='compute_child_count')
    child_ticket_id = fields.Many2one('child.ticket', string="Child Ticket Id")
    parent_ticket_properties = fields.Properties('Properties',
                                                 definition='product_id.parent_ticket_properties_definition', copy=True)
    contract_ids = fields.One2many('contract.contract', 'parent_ticket_id', string='Contract')
    parent_ticket_asset_ids = fields.One2many('parent.ticket.asset.line', 'parent_ticket_id', string='Assets')
    parent_ticket_inventory_ids = fields.One2many('parent.ticket.inventory.line', 'parent_ticket_id',
                                                  string='Inventory')
    # Customer Selection
    partner_id = fields.Many2one('res.partner', string="Customer")
    customer_street = fields.Char(copy=False)
    customer_street2 = fields.Char(copy=False)
    customer_zip = fields.Char(change_default=True, copy=False)
    customer_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', copy=False)
    customer_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', copy=False)
    customer_country_code = fields.Char(related='customer_country_id.code', string="Country Code", copy=False)
    street = fields.Char(copy=False)
    street2 = fields.Char(copy=False)
    zip = fields.Char(change_default=True)
    city = fields.Char(copy=False)
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    country_code = fields.Char(related='country_id.code', string="Country Code")
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')
    oem_warranty_status = fields.Selection(
        [('in_oem_warranty', 'In OEM Warranty'), ('out_oem_warranty', 'OO OEM Warranty'),
         ('not_available', 'Not available')], string='OEM Warranty Status')
    oem_repair_status = fields.Selection(
        [('in_repair_warranty', 'In Repair Warranty'), ('out_repair_warranty', 'OO Repair Warranty'),
         ('not_available', 'Not available')], string='Repair Warranty Status')
    extended_warranty_status = fields.Selection(
        [('in_repair_warranty', 'In Warranty'), ('out_repair_warranty', 'Out Of Warranty'),
         ('not_available', 'Not available')], string='Extended Warranty Status')
    cmc_status = fields.Selection([('in_warranty', 'In Warranty'), ('out_warranty', 'Out Of Warranty')],
                                  string='CMC Status')
    amc_status = fields.Selection([('in_warranty', 'In Warranty'), ('out_warranty', 'Out Of Warranty')],
                                  string='AMC Status')
    pm_warranty_status = fields.Selection(
        [('in_warranty', 'In Warranty'), ('out_warranty', 'OO Warranty'),
         ('not_available', 'Not available')], string='PM Warranty Status', default='not_available')
    inventory_reference = fields.Char(string='Inventory Reference')
    packaging = fields.Char(string='Packaging')
    packaging_id = fields.Many2one("stock.quant.package", string='Packaging')
    packaging_alias = fields.Char(string='Packaging Alias')
    stock_production_lot_id = fields.Many2one("stock.lot", string='Stock Lot')
    task_list_ids = fields.One2many('tasks.master.line', 'parent_ticket_id', string="Task Lists")
    is_assigned_user = fields.Boolean(string="Assigned User")
    is_send_acknowledgement = fields.Boolean(string="Is Send Acknowledgement")
    is_ar_hold = fields.Boolean(string="Is AR Hold")
    is_ar_hold_tick = fields.Boolean(string="Is AR Hold/Release")
    is_child_ticket_auto = fields.Boolean(related='parent_configuration_id.is_child_ticket_auto',
                                          string="Is Child Ticket Auto")
    status_count = fields.Integer(compute='compute_status_count')
    inward_picking_ids = fields.One2many('stock.picking', 'parent_id', string='Inward',
                                         domain="[('is_inward_transfer', '=',True)]")
    inward_count = fields.Integer(string='Internal Transfers', compute='_compute_inward_picking_ids')
    outward_count = fields.Integer(string='Outward Transfers', compute='_compute_outward_picking_ids')
    quality_count = fields.Integer(string='Quality', compute='_compute_quality_line_ids')
    quality_line_ids = fields.One2many('quality.alert', 'parent_id', string='Quality')
    is_child_ticket_created = fields.Boolean(string="Is Child Ticket Created")
    approvals_count = fields.Integer(string='Approval Count', compute='_compute_approvals_count')
    is_send_for_approvals = fields.Boolean(string="Is Send for Approvals")
    is_assign_to_user = fields.Boolean(string="Is Assign to User")
    is_request_reassign = fields.Boolean(string="Is Request Reassign")
    is_create_loaner = fields.Boolean(string="Is Create Loaner")
    is_create_installation = fields.Boolean(string="Is Create Installation")
    is_installation_created = fields.Boolean(string="Is Installation Created")
    installation_id = fields.Many2one('project.task', string="Installation ID")

    close_reason = fields.Text('Close Reason', help="While close the ticket this field will have the details.")
    close_date = fields.Datetime('Closed Date', readonly=True, copy=False)
    next_task_ids = fields.Many2many('tasks.master', string="Next Tasks", default=_default_next_task_ids)

    # SLA
    sla_polices_ids = fields.One2many('sla.policies', 'ticket_id', string="SLA Status", compute='_sla_apply')
    sla_deadline = fields.Datetime("SLA Deadline", compute_sudo=True, store=True)
    sla_deadline_date = fields.Date("SLA Deadline Date", compute_sudo=True, store=True)
    sr_count = fields.Integer(compute='compute_sr_count')
    installation_count = fields.Integer(compute='_compute_installation_count')
    loaner_count = fields.Integer(compute='_compute_loaner_count', string="Loaner Count")

    # Extra
    attachment_ids = fields.Many2many('ir.attachment', 'parent_ticket_attachment_rel', 'parent_ticket_id',
                                      'attachment_id', 'Attachments',
                                      help="You may attach files to this parent ticket, to be added to all ")
    pt_conf_ids = fields.Many2many('parent.ticket.configuration', compute='_compute_pt_conf_ids',
                                   string="Parent Ticket Configuration IDS", store=True, precompute=True, )
    request_count = fields.Integer(compute='compute_request_count')
    loaner_request_ids = fields.Many2many('service.request', string="Loaner Requests",
                                          compute='_compute_loaner_request_ids')
    is_inventory = fields.Boolean(string="Inventory", related='parent_configuration_id.is_inventory')
    child_ticket_ids = fields.Many2many('child.ticket', string="Child Ticket's", compute='_compute_child_tickets_ids')
    transfer_count = fields.Integer(string="Transfer Count", compute='_compute_transfer_count')
    price_total = fields.Float('Total')
    warranty_start_date = fields.Datetime(string="Warranty Start Date", readonly=True)
    warranty_end_date = fields.Datetime(string="Warranty End Date", readonly=True)
    is_warranty_approval_required = fields.Boolean(string='OEM Warranty Approval', copy=False)
    is_repair_warranty_approval_required = fields.Boolean(string='Repair Warranty Approval', copy=False)
    warranty_approval_created = fields.Boolean(string='Warranty Approval Created', copy=False)
    is_warranty_approval_done = fields.Boolean(string='Warranty Approval Done', copy=False)
    is_auto_approval = fields.Boolean(string="Auto Approval", copy=False, related="request_type_id.is_auto_approval")
    active = fields.Boolean(string='active', default=True)
    is_ew_status_mailsent = fields.Boolean('Extended Warranty Mail Sent?',
                                           help='If the Extended Warranty mail is sent once then should not send mail again. so marking this field as true not to send mail more than once.')
    check_status = fields.Boolean(string="Check Status")
    is_paid = fields.Boolean(string="Is Paid Service", copy=False)
    contact_id = fields.Many2one('res.partner', string="Contact")
    origin = fields.Char('Origin', default=False, readonly=True,
                         help="This field will be updated, if any child ticket is creating from the the parent ticket.")
    is_confirm_assign_user = fields.Boolean(string="Confirm", default=True)
    return_count = fields.Integer(string="Return", compute='_compute_return_order_ids')
    return_order_ids = fields.Many2many('stock.picking', string="Return Orders", compute='_compute_return_order_ids')
    is_inventory_check = fields.Boolean(string="Inventory Check")
    is_spare_check = fields.Boolean(string="Spare Check")
    is_loaners_check = fields.Boolean(string="Spare Check")

    # is_required_approval = fields.Boolean(string="Approval Type", copy=False,
    #                                       related="request_type_id.is_required_approval")
    # task_value_notify = fields.Many2one('tasks.master', string="Notify Task")
    # new_parent_child_ticket = fields.Char(string='Id', related='child_ticket_ids.name',
    #                                       order='id desc')
    is_disable_status_update = fields.Boolean(string="Disable Status update", copy=False)

    @api.onchange('requested_by_contact_number')
    def _onchange_requested_contact_check(self):
        if self.requested_by_contact_number:
            contact = self.env['res.partner'].search(
                [('mobile', '=', self.requested_by_contact_number)], limit=1)
            if contact:
                self.requested_by_email = contact.email
                self.requested_by_title = contact.title.name
                self.requested_by_name = contact.name

    @api.onchange('requested_by_email')
    def _onchange_requested_email_check(self):
        contact_check = self.env['res.partner'].search(
            [('email', '=', self.requested_by_email)], limit=1)
        if contact_check:
            self.requested_by_contact_number = contact_check.mobile

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.customer_street = self.partner_id.street or ''
            self.customer_street2 = self.partner_id.street or ''
            self.customer_zip = self.partner_id.zip or ''
            self.customer_state_id = self.partner_id.state_id.id or False
            self.customer_country_id = self.partner_id.country_id.id or False

    # Priya
    @api.onchange('stock_lot_id')
    def checking_stock_lot_id(self):
        if self.stock_lot_id:
            value = self.env['parent.ticket'].search(
                [('stock_lot_id', '=', self.stock_lot_id.id), ('state', '!=', 'closed')])
            # Load installation date from the asset
            self.installation_date_pt = self.stock_lot_id.installation_date
            for rec in value:
                raise ValidationError(
                    _("This lot number (%s) is already has a ticket and the reference number is (%s).",
                      self.stock_lot_id.name, rec.name))

    def _compute_return_order_ids(self):
        for rec in self:
            return_order_ids = self.env['stock.picking'].search(
                [('child_ticket_id', 'in', self.child_ticket_ids.ids), ('is_return', '=', True)])
            rec.return_count = len(return_order_ids)
            rec.return_order_ids = return_order_ids.ids

    def action_view_returns(self):
        self.ensure_one()
        return {
            'name': 'Returns',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('child_ticket_id', 'in', self.child_ticket_ids.ids), ('is_return', '=', True)],
            'context': "{'create': False}"
        }

    def action_open_customer_contacts(self):
        if not self.partner_id:
            raise UserError("Select the customer to create the contact.")
        title_id = self.env['res.partner.title'].search([('name', '=', self.requested_by_title)], limit=1)
        partner_email_id = self.env['res.partner'].search([('email', '=', self.requested_by_email)], limit=1)
        if partner_email_id:
            self.contact_id = partner_email_id.id
            return True
        partner_mobile_id = self.env['res.partner'].search(
            ['|', ('phone', '=', self.requested_by_contact_number), ('mobile', '=', self.requested_by_contact_number)],
            limit=1)
        if partner_mobile_id:
            self.contact_id = partner_mobile_id.id
            return True
        if not title_id:
            title_id = self.env['res.partner.title'].create({'name': self.requested_by_title})
        if title_id:
            contact = self.env['res.partner'].create({
                'name': self.requested_by_name,
                'mobile': self.requested_by_contact_number,
                'email': self.requested_by_email,
                'title': title_id.id,
                'ex_customer_type': 'create_customer',
                'parent_id': self.partner_id.id,
            })
            self.contact_id = contact.id

    @api.returns('self', lambda value: value.id)
    def copy(self, defaults=None):
        if not defaults:
            defaults = {}
        if self.env.context.get('repairs_required'):
            # Assign default values for views
            defaults.update({'service_type_id': self.env.context.get('sr_type'),
                             'service_category_id': self.env.context.get('sr_categ'),
                             'parent_configuration_id': self.env.context.get('pt_conf'),
                             'request_type_id': self.env.context.get('rq_type')})
        return super(ParentTicket, self).copy(defaults)

    def request_raise_invoice(self):
        request_data = {
            'name': self.name + " Invoice Request",
            'parent_ticket_id': self.id,
            'team_id': self.team_id.id,
            'user_id': self.env.user.id,
            'is_create_invoice': True,
        }
        self.env['request'].create(request_data)

    def request_quotation(self):
        request_data = {
            'name': self.name + " Quotation Request",
            'parent_ticket_id': self.id,
            'team_id': self.team_id.id,
            'user_id': self.env.user.id,
            'is_create_quote': True,
        }
        self.env['request'].create(request_data)

    def action_create_sale(self):
        for order in self:
            if not order.stock_lot_id:
                raise UserError(_("Please Select Asset"))
            else:
                order_data = {
                    'partner_id': order.partner_id.id or False,
                    'team_id': order.team_id.id or False,
                    'parent_ticket_id': order.id or False,
                    'origin': order.name or '',
                    'order_line': [(0, 0, {
                        'product_id': order.product_id.id,
                        'stock_lot_id': order.stock_lot_id.id,
                        'product_uom_qty': 1,
                        'product_uom': order.product_id.uom_id.id,
                    })],
                }
                self.env['sale.order'].create(order_data)

    @api.onchange('partner_id', 'service_category_id')
    def partner_amc_cmc_status_check(self):
        contract_ids = self.env['contract.contract'].search(
            [('partner_id', '=', self.partner_id.id), ('date_start', '<=', date.today()), ('state', '=', 'started'),
             ('date_end', '>=', date.today())])
        if contract_ids:
            self.contract_ids = [(6, 0, [contract.id for contract in contract_ids])]
            for contract in contract_ids:
                if contract.custom_contract_type == 'amc':
                    self.cmc_status = 'out_warranty'
                    self.amc_status = 'in_warranty'
                elif contract.custom_contract_type == 'cmc':
                    self.cmc_status = 'in_warranty'
                    self.amc_status = 'out_warranty'
                elif contract.custom_contract_type == 'both':
                    self.cmc_status = 'in_warranty'
                    self.amc_status = 'in_warranty'
                elif contract.custom_contract_type == 'warranty':
                    self.pm_warranty_status = 'in_warranty'
                else:
                    self.cmc_status = 'out_warranty'
                    self.amc_status = 'out_warranty'
        else:
            self.contract_ids = None
            self.amc_status = False
            self.cmc_status = False
        # Check if the order is warranty type, if yes then check the warranty data on the asset master and update the status as in_oem_warranty as available
        if self.service_category_id.category_type == 'is_warranty':
            if self.stock_lot_id and self.stock_lot_id.warranty_start_date and self.stock_lot_id.warranty_end_date:
                if fields.Date.today() <= self.stock_lot_id.warranty_end_date:
                    # self.update({'oem_warranty_status': 'in_oem_warranty'})
                    self.oem_warranty_status = 'in_oem_warranty'
                else:
                    raise ValidationError(
                        _('Kindly check this asset (%s) whether has correct warranty start and end date.',
                          self.stock_lot_id.name))
        elif self.service_category_id.category_type == 'is_extended_warranty':
            if self.stock_lot_id and self.stock_lot_id.extended_warranty_start_date and self.stock_lot_id.extended_warranty_end_date:
                if fields.Date.today() <= self.stock_lot_id.extended_warranty_end_date:
                    # self.update({'extended_warranty_status': 'in_repair_warranty'})
                    self.extended_warranty_status = 'in_repair_warranty'
                else:
                    raise ValidationError(
                        _('Kindly check this asset (%s) whether has correct extended warranty start and end date.',
                          self.stock_lot_id.name))
        elif self.service_category_id.category_type == 'is_repair_warranty':
            if self.stock_lot_id and self.stock_lot_id.repair_warranty_start_date and self.stock_lot_id.repair_warranty_end_date:
                if fields.Date.today() <= self.stock_lot_id.repair_warranty_end_date:
                    self.oem_repair_status = 'in_repair_warranty'
                else:
                    raise ValidationError(
                        _('Kindly check this asset (%s) whether has correct repair warranty start and end date.',
                          self.stock_lot_id.name))
        if self.amc_status == 'in_warranty' and self.service_category_id.category_type == 'is_amc':
            self.check_status = True
        elif self.cmc_status == 'in_warranty' and self.service_category_id.category_type == 'is_cmc':
            self.check_status = True
        elif self.service_category_id.category_type == 'is_warranty' and self.oem_warranty_status == 'in_oem_warranty':
            self.check_status = True
        elif self.service_category_id.category_type == 'is_extended_warranty' and self.extended_warranty_status == 'in_repair_warranty':
            self.check_status = True
        elif self.service_category_id.category_type == 'is_repair_warranty' and self.oem_repair_status == 'in_repair_warranty':
            self.check_status = True
        elif self.service_category_id.category_type == 'is_paid':
            self.check_status = True
            self.is_paid = True
        elif self.service_category_id.category_type == 'is_billable':
            self.check_status = True
            self.is_paid = True
        elif self.service_category_id.category_type == 'is_installable':
            self.check_status = True
            self.is_paid = True
        elif self.pm_warranty_status == 'in_warranty':
            self.check_status = True
        else:
            self.check_status = False

    @api.onchange('stock_lot_id')
    def _onchange_stock_lot_id_domain(self):
        if self.partner_id:
            stock_lot_ids = self.env['stock.lot'].search([('customer_id', '=', self.partner_id.id)])
            domain = [('id', 'in', stock_lot_ids.ids)]
        else:
            domain = [('id', 'in', None)]
        return {'domain': {'stock_lot_id': domain}}

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

    @api.onchange('service_type_id')
    def onchange_service_domain(self):
        request_ids = self.service_type_id.request_type_ids.mapped('id')
        domain = [('id', 'in', request_ids)]
        return {'domain': {'request_type_id': domain}}

    def action_confirm(self):
        # 'default_is_confirm_assign_user': self.is_confirm_assign_user,
        # Check for the asset and create the Parent ticket details on the asset ticket O2M fields
        rec = dict(self._fields['state'].selection).get(self.state)
        contract = self.env['contract.contract'].search([('name', '=', self.contract_ids.name)])
        print("contract", contract)
        self.env['asset.lot.serial'].create({
            'parent_ticket_id': self.id,
            'problem_description': self.problem_description,
            'stock_lot_id': self.stock_lot_id.id,
            'ticket_type': 'pt',
            'service_type_id': self.service_type_id.id,
            'service_category_id': self.service_category_id.id,
            'ticket_create_date': self.create_date,
            'ct_user_id': self.assign_engineer_ids[0].id,
            'contract_details': contract.ids,
            'status': rec,
        })
        if self.is_warranty_approval_required:
            self.state = 'warranty_check'
        elif self.is_repair_warranty_approval_required:
            self.state = 'repair_warranty_check'
        else:
            self.state = 'confirm'

    @api.onchange('parent_configuration_id', 'oem_repair_status', 'oem_warranty_status')
    def get_repair_warranty_approval_required(self):
        if self.parent_configuration_id.repair_warranty_check == 'yes':
            if self.parent_configuration_id.repair_inwarranty_approval == 'yes' and self.oem_repair_status == 'in_repair_warranty':
                self.is_repair_warranty_approval_required = True
            if self.parent_configuration_id.repair_outwarranty_approval == 'yes' and self.oem_repair_status == 'out_repair_warranty':
                self.is_repair_warranty_approval_required = True
        if self.parent_configuration_id.oem_warranty_check == 'yes':
            if self.parent_configuration_id.oem_inwarranty_approval == 'yes' and self.oem_warranty_status == 'in_oem_warranty':
                self.is_warranty_approval_required = True
            if self.parent_configuration_id.oem_outwarranty_approval == 'yes' and self.oem_warranty_status == 'out_oem_warranty':
                self.is_warranty_approval_required = True

    def warranty_send_for_approval(self):
        if self.parent_configuration_id.oem_inwarranty_approval or self.parent_configuration_id.oem_outwarranty_approval:
            if not self.parent_configuration_id.oem_approval_team_ids:
                raise UserError(_("There is no approval teams for OEM warranty approval"))
            for warranty_approval in self.parent_configuration_id.oem_approval_team_ids:
                request = {
                    'name': "OEM Warranty Approval " + self.name,
                    'type_id': warranty_approval.id or False,
                }
                requests = self.env['multi.approval'].create(request)
                requests.action_submit()
                requests.parent_ticket_id = self.id
        if self.parent_configuration_id.repair_inwarranty_approval or self.parent_configuration_id.repair_outwarranty_approval:
            if not self.parent_configuration_id.repair_approval_team_ids:
                raise UserError(_("There is no approval teams for Repair warranty approval"))
            for repair_approval in self.parent_configuration_id.repair_approval_team_ids:
                request = {
                    'name': "Repair Warranty Approval " + self.name,
                    'type_id': repair_approval.id or False,
                }
                requests = self.env['multi.approval'].create(request)
                requests.action_submit()
                requests.parent_ticket_id = self.id

        self.warranty_approval_created = True
        # parent_ticket_id.write({'state': 'waiting_for_approval', 'is_send_for_approvals': True})

    @api.onchange('request_type_id')
    def _onchange_request_type_id(self):
        if self.request_type_id and not self.request_type_id.is_required_approval:
            self.is_send_for_approvals = True

    def action_view_loaner_order(self):
        sale_order = self.env['sale.order'].search([('is_rental_order', '=', True), ('parent_ticket_id', '=', self.id)])
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

    @api.depends('request_type_id')
    def get_request_ticket_type(self):
        # This method store the request type's ticket type to hide the buttons based on types
        for record in self:
            record.request_type = record.request_type_id.ticket_type

    def _compute_transfer_count(self):
        for record in self:
            record.transfer_count = self.env['stock.picking'].search_count([('origin', '=', self.name)])

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

    def _compute_child_tickets_ids(self):
        lists = []
        for record in self:
            ticket_ids = self.env["child.ticket"].search([("parent_ticket_id", "=", record.id)])
            if ticket_ids:
                record.child_ticket_ids = ticket_ids.ids
            else:
                record.child_ticket_ids = None

    def _compute_loaner_request_ids(self):
        lists = []
        for record in self:
            request_ids = self.env["service.request"].search(
                [("parent_ticket_id", "=", record.id), ("is_lr_from_pt", "=", True)])
            if request_ids:
                record.loaner_request_ids = request_ids.ids
            else:
                record.loaner_request_ids = None

    @api.depends('service_category_id', 'service_type_id')
    def _compute_pt_conf_ids(self):
        conf_ids = []
        for record in self:
            pt_conf_ids = self.env['parent.ticket.configuration'].search(
                [('service_category_id', '=', record.service_category_id.id),
                 ('service_type_id', '=', record.service_type_id.id)])
            if record.service_category_id and record.service_type_id:
                if pt_conf_ids:
                    for each in pt_conf_ids:
                        conf_ids.append(each.id)
                    record.pt_conf_ids = conf_ids
                else:
                    record.pt_conf_ids = False

    @api.onchange('request_type_id')
    def _onchange_request_type(self):
        team_ids = self.env.user.team_ids
        if team_ids:
            self.team_id = team_ids[0].id
            return {'domain': {'team_id': [('id', 'in', team_ids.ids)]}}
        else:
            self.team_id = False

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_code_no = self.product_id.product_code
            self.cat_no = self.product_id.product_part
            self.categ_id = self.product_id.categ_id.id or False

    def _sla_apply(self):
        for ticket in self:
            # SLA
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
                            # ticket.write({'sla_polices_ids': False})
                        if not min_deadline or status.duration < min_deadline:
                            min_deadline += status.duration
                    if status.interval_unit == 'hours':
                        remaining_days = now + timedelta(hours=min_deadline)
                    else:
                        remaining_days = now + timedelta(min_deadline)
                    ticket.sudo().sla_deadline = remaining_days
                    ticket.sudo().sla_deadline_date = remaining_days.date()
                    ticket.sudo().sla_polices_ids = slas.ids
                    # ticket.write({
                    #     'sla_deadline': remaining_days,
                    #     'sla_deadline_date': remaining_days.date(),
                    #     'sla_polices_ids': slas.ids,
                    # })
            else:
                ticket.sudo().sla_deadline = False
                ticket.sudo().sla_deadline_date = False
                ticket.sudo().sla_polices_ids = False
                # ticket.write({'sla_polices_ids': False, 'sla_deadline': False, 'sla_deadline_date': False})

    @api.depends('quality_line_ids')
    def _compute_quality_line_ids(self):
        for order in self:
            order.quality_count = len(order.quality_line_ids)

    @api.depends('inward_picking_ids')
    def _compute_inward_picking_ids(self):
        for order in self:
            order.inward_count = len(order.inward_picking_ids.filtered(lambda r: r.is_inward_transfer))

    @api.depends('inward_picking_ids')
    def _compute_outward_picking_ids(self):
        for order in self:
            order.outward_count = len(order.inward_picking_ids.filtered(lambda r: r.is_outward_transfer))

    def write(self, vals):

        if vals.get('task_list_ids'):
            for record in self:
                if self.parent_configuration_id.is_child_ticket_auto:
                    for task in vals.get('task_list_ids'):
                        mapped_task_id = self.parent_configuration_id.task_id
                        if task[2] and 'task_id' in task[2]:
                            if task[2] != False and task[2]['task_id'] == mapped_task_id.id:
                                # if mapped task in parent.ticket.confirguration and the task selected or added on the status is equal then create child
                                # ticket automatically.
                                child_ticket_id = self.action_child_ticket_create()
                                # Make this field hide to hide the Create Child Ticket button automatically.
        return super().write(vals)

    # Parent Ticket Sequences
    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            vals['name'] = self.env['ir.sequence'].with_context(force_company=self.env.user.company_id.id).next_by_code(
                'parent.ticket') or _('New')
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('parent.ticket') or _('New')
        vals['state'] = 'new'
        rec = super(ParentTicket, self).create(vals)
        if vals.get('task_list_ids'):
            for record in rec:
                if rec.parent_configuration_id.is_child_ticket_auto:
                    for task in vals.get('task_list_ids'):
                        mapped_task_id = rec.parent_configuration_id.task_id
                        if task[2] and 'task_id' in task[2]:
                            if task[2] != False and task[2]['task_id'] == mapped_task_id.id:
                                # if mapped task in parent.ticket.confirguration and the task selected or added on the status is equal then create child
                                # ticket automatically.
                                rec.action_child_ticket_create()
                                # Make this field hide to hide the Create Child Ticket button automatically.
        if rec.parent_configuration_id.is_create_alert:
            email = ''
            if rec.parent_configuration_id.customer_type == 'oem':
                email = rec.customer_account_id.email
            elif rec.parent_configuration_id.customer_type == 'end_customer':
                email = rec.partner_id.email
            elif rec.parent_configuration_id.customer_type == 'both':
                email = ",".join([str(rec.customer_account_id.email), str(rec.partner_id.email)])
            template_id = rec.parent_configuration_id.notification_template_id
            if template_id:
                template_id.with_context(email_to=email).sudo().send_mail(rec.id, force_send=True)
        if rec.parent_configuration_id.is_inward_receipts and rec.parent_configuration_id.receipts_operation_type_id:
            customer_location_id = self.env['stock.location'].sudo().search([('usage', '=', 'customer')], limit=1)
            vals = {
                "picking_type_id": rec.parent_configuration_id.receipts_operation_type_id.id,
                "location_id": rec.parent_configuration_id.receipts_operation_type_id.default_location_src_id.id or customer_location_id.id,
                "location_dest_id": rec.parent_configuration_id.receipts_operation_type_id.default_location_dest_id.id,
                "partner_id": rec.partner_id.id,
                'parent_id': rec.id,
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
                    'location_id': rec.parent_configuration_id.receipts_operation_type_id.default_location_src_id.id or customer_location_id.id,
                    'location_dest_id': rec.parent_configuration_id.receipts_operation_type_id.default_location_dest_id.id
                }
                self.env['stock.move'].sudo().create(line_vals)
        if rec.parent_configuration_id.is_outward_delivery_order and rec.parent_configuration_id.delivery_operation_type_id:
            customer_location_id = self.env['stock.location'].sudo().search([('usage', '=', 'customer')], limit=1)
            vals = {
                "picking_type_id": rec.parent_configuration_id.delivery_operation_type_id.id,
                "location_id": rec.parent_configuration_id.delivery_operation_type_id.default_location_src_id.id,
                "location_dest_id": rec.parent_configuration_id.delivery_operation_type_id.default_location_dest_id.id or customer_location_id.id,
                "partner_id": rec.partner_id.id,
                'parent_id': rec.id,
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
                    'location_id': rec.parent_configuration_id.delivery_operation_type_id.default_location_src_id.id,
                    'location_dest_id': rec.parent_configuration_id.delivery_operation_type_id.default_location_dest_id.id or customer_location_id.id,
                }
                self.env['stock.move'].sudo().create(line_vals)

        return rec

    # Open Wizard Assign Engineer
    def action_assign_engineer_wizard(self):
        view = self.env.ref('ppts_parent_ticket.view_assign_engineer_wiz')
        context = {
            'default_is_assign_to_user': self.is_assign_to_user,
            'default_is_request_reassign': self.is_request_reassign,
            'default_assign_engineer_id': self.env.user.id,

        }
        return {
            'name': _('Assign User'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'assign.engineer',
            'view_id': view.id,
            'target': 'new',
            'context': context
        }

    def action_reassign_engineer_wizard(self):
        context = {
            'default_is_assign_to_user': self.is_assign_to_user,
            'default_is_request_reassign': self.is_request_reassign,
        }
        view = self.env.ref('ppts_parent_ticket.view_assign_engineer_wiz')
        return {
            'name': _('Re-assign User'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'assign.engineer',
            'view_id': view.id,
            'target': 'new',
            'context': context
        }

    # Create Child Ticket Automatically - Using Write Method
    def action_child_ticket_create(self):
        for record in self:
            child_tick = {
                'partner_id': record.partner_id.id or False,
                'call_source_id': record.call_source_id.id or False,
                'call_date': record.call_date or False,
                'service_category_id': record.service_category_id.id or False,
                'service_type_id': record.service_type_id.id or False,
                'product_id': record.product_id.id or False,
                'stock_lot_id': record.stock_lot_id.id or False,
                'categ_id': record.categ_id.id or False,
                'product_category_id_alias': record.product_category_id_alias or '',
                'problem_description': record.problem_description or '',
                'requested_by_name_child': record.requested_by_name or '',
                'requested_by_contact_number': record.requested_by_contact_number or '',
                'remarks': record.remarks or '',
                'installation_date': record.installation_date or False,
                'dealer_distributor_id': record.dealer_distributor_id.id or False,
                'call_received_id': record.call_received_id.id or False,
                'alternate_contact_name': record.alternate_contact_name or '',
                'alternate_contact_number': record.alternate_contact_number or '',
                'alternate_contact_email': record.alternate_contact_email or '',
                'oem_warranty_status_id': record.oem_warranty_status_id.id or False,
                'repair_warranty_status_id': record.repair_warranty_status_id.id or False,
                'customer_account_id': record.customer_account_id.id or False,
                'team_id': record.team_id.id,
                'faulty_section': record.faulty_section or '',
                'sow': record.sow or '',
                'webdelata_id': record.webdelata_id or '',
                'webdelata': record.webdelata or '',
                'mc_stk': record.mc_stk or False,
                'child_configuration_id': record.parent_configuration_id.child_ticket_type_id.id or False
            }
            part_no = {
                'product_part_no': record.cat_no
            }
            child_ticket = self.env['child.ticket'].sudo().create(child_tick)
            if record.parent_configuration_id.child_ticket_type_id.work_flow_id:
                status = record.parent_configuration_id.child_ticket_type_id.work_flow_id.task_list_ids[0]
                status_data = [(0, 0, {
                    'task_id': status.task_id.id,
                    'next_task_ids': [(6, 0, status.next_task_ids.ids)],
                    'status': status.status,
                    'child_ticket_id': child_ticket.id,
                })]
                child_ticket.sudo().write({'task_list_ids': status_data})

            # part = self.env['asset.model'].create(part_no)
            child_ticket.parent_ticket_id = record.id
            child_ticket._onchange_stock_lot_id()
            child_ticket._onchange_task_list_ids()
            record.child_ticket_id = child_ticket.id
            record.sudo().action_confirm()

    def action_create_child_ticket_wizard(self):
        open_child_tickets = self.env['child.ticket'].search(
            [('parent_ticket_id', '=', self.id), ('state', 'not in', ('closed', 'cancel'))])
        open_tickets = ', '.join(open_child_tickets.mapped('name'))
        if open_child_tickets:
            raise ValidationError(_('There is already [ %s ] are not yet closed'
                                    '\n Kindly close the Child Ticket to create new!', open_tickets))
        context = {
            "default_request_type_id": self.request_type_id.id,
        }
        return {
            'name': _('Convert Child Ticket'),
            'view_mode': 'form',
            'res_model': 'convert.child.ticket',
            'type': 'ir.actions.act_window',
            'target': 'new',
            "context": context,
        }

    # Send By Email
    def action_send_mail(self):
        '''
        This function opens a window to compose an email, with the parent ticket template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup('ppts_parent_ticket.email_template_parent_ticket')[2]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
        except ValueError:
            compose_form_id = False
        if not self.partner_id.email:
            return self._show_notification('Please Enter Customer Email')
        ctx = {
            'default_model': 'parent.ticket',
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

    # Open Wizard Contract
    def action_wizard_contract(self):
        return {
            'name': _('Contract'),
            'view_mode': 'form',
            'res_model': 'contract.contract',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id:
            self.street = self.partner_id.street
            self.street2 = self.partner_id.street2
            # self.city =self.partner_id.city
            self.zip = self.partner_id.zip
            self.phone = self.partner_id.phone
            self.mobile = self.partner_id.mobile
            self.email = self.partner_id.email
            stock_lot_ids = self.env['stock.lot'].search([('customer_id', '=', self.partner_id.id)])
            domain = [('id', 'in', stock_lot_ids.ids)]
        else:
            domain = [('id', 'in', None)]
        return {'domain': {'stock_lot_id': domain}}

    @api.onchange('stock_lot_id')
    def _onchange_stock_lot_id(self):
        for record in self:
            record.product_id = record.stock_lot_id.product_id.id or False
            record.installation_date = record.stock_lot_id.installation_date
            stock_lot_obj = self.env['stock.lot'].search([('id', '=', record.stock_lot_id.id)], limit=1)
            # warranty
            warranty_check_false = stock_lot_obj.filtered(lambda x: x.oem_warranty_check == False)
            warranty_check_true = stock_lot_obj.filtered(lambda x: x.oem_warranty_check == True)
            # repair
            repair_check_false = stock_lot_obj.filtered(lambda x: x.oem_repair_warranty_check == False)
            repair_check_true = stock_lot_obj.filtered(lambda x: x.oem_repair_warranty_check == True)

            if record.stock_lot_id:
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

    @api.onchange('parent_ticket_asset_ids')
    def onchange_parent_ticket_asset_ids(self):
        for order in self.parent_ticket_asset_ids:
            line = self.parent_ticket_asset_ids.filtered(lambda l: l.stock_lot_id == order.stock_lot_id)
            if len(line) > 1:
                raise UserError(_('You cannot have multiple lines with same Serial Number - %s') % (
                        line[1].stock_lot_id.name or ''))

    # Child Count
    def compute_child_count(self):
        for record in self:
            record.child_count = self.env['child.ticket'].search_count([('parent_ticket_id', '=', record.id)])

    # Status Count
    def compute_status_count(self):
        for record in self:
            record.status_count = self.env['tasks.master.line'].search_count([('parent_ticket_id', '=', record.id)])

    # Approvals Count
    def _compute_approvals_count(self):
        for record in self:
            record.approvals_count = self.env['multi.approval'].search_count([('parent_ticket_id', '=', record.id)])

    # Smart Button - Action view Child Tickets
    def action_view_child_tickets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Child Ticket',
            'view_mode': 'tree,form',
            'res_model': 'child.ticket',
            'domain': [('parent_ticket_id', '=', self.id)],
            'context': "{'create': False}"
        }

    # Smart Button - Quotation
    def action_view_quotation(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quotation',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('parent_ticket_id', '=', self.id)],
            'context': "{'create': False}"
        }

    # Smart Button - Invoice
    def action_view_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('parent_ticket_id', '=', self.id)],
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
            'domain': [('parent_ticket_id', '=', self.id)],
            'context': "{'create': False}"
        }

    # Smart Button - Service Request
    def action_view_service_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Request',
            'view_mode': 'tree,form',
            'views': [(self.env.ref('ppts_service_request.service_request_tree_view').id, 'tree'),
                      (self.env.ref('ppts_service_request.service_request_form_view').id, 'form')],
            'res_model': 'service.request',
            'domain': [('parent_ticket_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_sr_count(self):
        for record in self:
            record.sr_count = self.env['service.request'].search_count([('parent_ticket_id', '=', self.id)])

    def compute_request_count(self):
        for record in self:
            record.request_count = self.env['request'].search_count([('parent_ticket_id', '=', self.id)])

    def _compute_installation_count(self):
        for record in self:
            record.installation_count = self.env['project.task'].search_count(
                [('installation_parent_ticket_id', '=', self.id)])

    def _compute_loaner_count(self):
        for record in self:
            record.loaner_count = self.env['sale.order'].search_count(
                [('is_rental_order', '=', True), ('parent_ticket_id', '=', self.id)])

    # Smart Button - Engineer
    def action_view_engineer(self):
        self.ensure_one()
        return {
            'name': 'Engineer',
            'view_mode': 'tree,form',
            'res_model': 'res.users',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': [('id', 'in', self.assign_engineer_ids.ids)],
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

    # Smart Button - Schedule
    def action_view_schedule(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Activities',
            'view_mode': 'tree,form',
            'res_model': 'mail.activity',
            'domain': [('res_id', '=', self.id), ('res_model', '=', 'parent.ticket')],
        }

    # Smart Button - Survey
    def action_view_survey(self):
        return True

    def send_for_approval(self):
        return {
            'name': _('Send for Approval'),
            'view_mode': 'form',
            'res_model': 'parent.ticket.approval',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_view_send_for_approvals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send for Approvals',
            'view_mode': 'tree,form',
            'res_model': 'multi.approval',
            'domain': [('parent_ticket_id', '=', self.id)],
            'context': "{'create': False}"
        }

    # Acknowledgment Button
    def action_send_acknowledgment(self):
        email = ''
        if self.parent_configuration_id:
            if not self.parent_configuration_id.is_create_alert:
                return self._show_notification(
                    'Please Enable On Ticket Create Alert / Notification in Child Configuration')
            if not self.parent_configuration_id.notification_template_id:
                return self._show_notification('Please Select Notification Template')
            if not self.parent_configuration_id.customer_type:
                return self._show_notification('Please Select Customer Type')
            if self.parent_configuration_id.customer_type == 'oem':
                if not self.customer_account_id.email:
                    return self._show_notification('Please Select Customer Account')
                else:
                    email = self.customer_account_id.email
            elif self.parent_configuration_id.customer_type == 'end_customer':
                if not self.partner_id.email:
                    return self._show_notification('Please Select Customer')
                else:
                    email = self.partner_id.email
            elif self.parent_configuration_id.customer_type == 'both':
                if not (self.customer_account_id.email and self.partner_id.email):
                    return self._show_notification('Please Select Both Customer and Customer Account')
                else:
                    email = ",".join([str(self.customer_account_id.email), str(self.partner_id.email)])
            template_id = self.parent_configuration_id.notification_template_id
            if template_id:
                template_id.with_context(email_to=email).sudo().send_mail(self.id, force_send=True)
                return self._show_success_notification('Acknowledgment Sent Successfully')
        else:
            return self._show_notification('Please Enter Parent Configuration')

    @api.onchange('parent_configuration_id')
    def _onchange_parent_configuration_id(self):
        for record in self:
            if self.parent_configuration_id.work_flow_id:
                status = self.parent_configuration_id.work_flow_id.task_list_ids[0]
                status_data = [(0, 0, {
                    'task_id': status.task_id.id,
                    'next_task_ids': [(6, 0, status.next_task_ids.ids)],
                    'status': status.status,
                    'parent_ticket_id': record.id,
                })]
                if status_data:
                    record.sudo().task_list_ids = status_data
                else:
                    record.sudo().task_list_ids = None

    @api.onchange('task_list_ids')
    def _onchange_task_list_ids(self):
        for record in self:
            if self.parent_configuration_id.work_flow_id:
                pro = []
                for task_line in record.task_list_ids:
                    work_flow = self.env["tasks.master.line"].search(
                        [("workflow_id", "=", self.parent_configuration_id.work_flow_id.id),
                         ("task_id", "=", task_line.task_id.id)])
                    if work_flow:
                        for wk in work_flow:
                            if wk.next_task_ids:
                                pro_ids = [(6, 0, wk.next_task_ids.ids)]
                                task_line.next_task_ids = pro_ids
                                self.next_task_ids = [(6, 0, wk.next_task_ids.ids)]
                    #        else:
                    #            pro_ids = False
                    #            self.next_task_ids = False
                    # else:
                    #    self.next_task_ids = False
            ar_hold = record.task_list_ids.task_id.filtered(lambda r: r.python_code == 'ar_hold')
            create_loaner = record.task_list_ids.task_id.filtered(lambda r: r.python_code == 'create_loaner')
            create_installation = record.task_list_ids.task_id.filtered(
                lambda r: r.python_code == 'create_installation')
            # AR Hold
            if ar_hold:
                record.is_ar_hold = True
            else:
                record.is_ar_hold = False
            # Loaner Request
            if create_loaner:
                record.is_create_loaner = True
            else:
                record.is_create_loaner = False
            # Create Installation
            if create_installation:
                record.is_create_installation = True
            else:
                record.is_create_installation = False

    def action_create_installation(self):
        for record in self:
            installation = {
                'is_project_installation': True,
                'installation_service_category_id': record.service_category_id.id or False,
                'installation_service_type_id': record.service_type_id.id or False,
                'installation_parent_ticket_id': record.id or False,
                'installation_customer_id': record.partner_id.id or False,
                'installation_customer_account_id': record.customer_account_id.id or False,
                'team_id': record.team_id.id or False,
                'installation_stock_lot_id': record.stock_lot_id.id or False,
                'installation_categ_id': record.categ_id.id or False,
                'installation_origin': record.name or '',
                'description': record.description or '',
                # 'request_type_id': record.request_type_id.id or False
                'installation_process_alias': record.product_category_id_alias or '',
                # 'installation_child_ticket_type': record.child_ticket_type_id.id or False,
                'installation_title': record.remarks or '',
                'installation_reported_fault': record.faulty_section or '',
                'installation_external_reference': record.remarks or '',

            }
            installation_id = self.env['project.task'].create(installation)
            record.installation_id = installation_id.id
            installation_id.action_start_installation()
            record.write({'is_installation_created': True})

    def action_process_loaner(self):
        if self.request_type_id.ticket_type != 'sr_loaner':
            raise UserError(_('You need to select approval type as Loaner !'))
        sr_order = {
            'is_rental_order': True,
            'lr_from_pt': True,
            'partner_id': self.partner_id.id or False,
            'parent_ticket_id': self.id or False,
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

    def ar_hold(self):
        ar_hold = self.task_list_ids.task_id.filtered(lambda r: r.python_code == 'ar_hold')
        task_ar_hold = self.task_list_ids.filtered(lambda r: r.task_id.name == 'AR Hold')
        for status_update in task_ar_hold:
            status_update.write({'status': 'Hold'})
            self.write({'is_ar_hold_tick': True})

    def ar_release(self):
        self.is_ar_hold_tick = False

    def action_status_update(self):
        return {
            'name': _('Status Update'),
            'view_mode': 'form',
            'res_model': 'parent.ticket',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('ppts_parent_ticket.parent_ticket_status_update_form_view').id,
            'target': 'new',
            'res_id': self.id
        }

    def action_service_request(self):
        self.ensure_one()
        context = {'default_parent_ticket_id': self.id}
        return {
            'name': _('Select Approval Type'),
            'view_mode': 'form',
            'res_model': 'request.type.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            "context": context,
        }

    # While this button is clicked then add the assets on the line and create the view to select the other details
    def action_create_inward(self):
        # search for the Transit and Customer location to map
        '''
        +------------------------+---------------------------------------------------+
        | Source Location       | Customer Location
        +------------------------+---------------------------------------------------+
        | Destination Location  | Transit Location
        +------------------------+---------------------------------------------------+
        '''
        if 'is_outward' in self.env.context and not self.inward_picking_ids:
            raise UserError('Can not create outward without inward order.')
        if 'is_outward' in self.env.context and self.inward_picking_ids.filtered(
                lambda r: r.is_inward_transfer and r.state != 'done'):
            raise UserError('The Inward is not validated. So, validate the inward to create a outward orders.')
        if not self.repair_center_location_id:
            raise UserError(_(' There is no Repair Center Location mapped to create an Inward order'))
        transit_location_id = self.env['stock.location'].search(
            [('wh_id', '=', self.repair_center_location_id.id), ('name', '=', 'Transit'),
             ('usage', '=', 'transit')], limit=1)
        if not transit_location_id:
            raise UserError(
                _('There is no Transit location in this warehouse- %s . Create new location called "Transit" and map location type as "Transit Location" to create an Inward order') % (
                    self.repair_center_location_id.name))
        customer_location_id = self.env['stock.location'].search(
            [('wh_id', '=', self.repair_center_location_id.id), ('name', '=', 'Customers'),
             ('usage', '=', 'customer')], limit=1)
        if not customer_location_id:
            raise UserError(
                _('There is no Customer location in this warehouse- %s . Create new location called "Customers" and map location type as "Customer Location" to create an Inward order') % (
                    self.repair_center_location_id.name))
        if 'is_outward' in self.env.context:
            vals = {
                "location_id": transit_location_id.id,
                "location_dest_id": customer_location_id.id,
                "partner_id": self.partner_id.id,
                'parent_id': self.id,
                'is_outward_transfer': True
            }
        else:
            vals = {
                "location_id": customer_location_id.id,
                "location_dest_id": transit_location_id.id,
                "partner_id": self.partner_id.id,
                'parent_id': self.id,
                'is_inward_transfer': True
            }
        # Check for the TRANSFER is activated in parent.ticket.configuration, if yes take the operation type from there
        # if not show user error to activate and map the operation type to create the inward.
        if self.parent_configuration_id.is_material_movement and self.parent_configuration_id.transfer_operation_type_ids:
            vals['picking_type_id'] = self.parent_configuration_id.transfer_operation_type_ids.ids[0]
        else:
            raise UserError(
                _('There is no Transfer Material movement enabled in this configuration - %s . Enable and map the operation type to create an Inward order') % (
                    self.parent_configuration_id.parent_config_name))
        if self.product_id:
            if vals:
                picking_id = self.env['stock.picking'].create(vals)
                line_vals = {'product_id': self.product_id.id,
                             'product_uom': self.product_id.uom_id.id,
                             'name': self.product_id.name,
                             'quantity_done': 1, 'picking_id': picking_id.id, 'location_id': customer_location_id.id,
                             'location_dest_id': transit_location_id.id}
                self.env['stock.move'].create(line_vals)
        if 'is_outward' in self.env.context:
            return {
                'name': _('Outward Transfers'),
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'type': 'ir.actions.act_window',
                'target': 'current',
                "res_id": picking_id.id,
            }
        else:
            return {
                'name': _('Inward Transfers'),
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'type': 'ir.actions.act_window',
                'target': 'current',
                "res_id": picking_id.id,
            }

    # Smart Button - Inwward
    def action_view_inward_transfer(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inward Transfer',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('id', 'in', self.inward_picking_ids.filtered(lambda r: r.is_inward_transfer).ids)],
            'context': "{'create': False}"
        }

    # Smart Button - Outward
    def action_view_outward_transfer(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Outward Transfer',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('id', 'in', self.inward_picking_ids.filtered(lambda r: r.is_outward_transfer).ids)],
            'context': "{'create': False}"
        }

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
            'domain': [('installation_parent_ticket_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def action_create_quality(self):
        if self.product_id:
            if self.inward_picking_ids.filtered(lambda r: r.is_inward_transfer and r.state != 'done'):
                raise UserError('The Inward is not validated so validate the inward to create quality.')
            quality_alert_id = self.env['quality.alert'].create(
                {'product_id': self.product_id.id, 'name': self.name, 'origin': self.name, 'parent_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'name': 'Quality',
                'view_mode': 'form',
                'res_model': 'quality.alert',
                'res_id': quality_alert_id.id,
                'context': "{'create': False}"
            }
        else:
            raise UserError('Map the product to create inward inspection.')

    # Smart Button - Quality
    def action_view_quality(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quality',
            'view_mode': 'tree,form',
            'res_model': 'quality.alert',
            'domain': [('id', 'in', self.quality_line_ids.ids)],
            'context': "{'create': False}"
        }

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

    def action_parent_ticket_close(self):
        child_count = self.env['child.ticket'].search_count(
            [('parent_ticket_id', '=', self.id), ('state', '!=', 'closed')])
        if not self.stock_lot_id.warranty_end_date and not self.stock_lot_id.warranty_start_date and self.request_type == 'sr_installation':
            raise UserError(_('To close the parent ticket, Update warranty start and end date in Assets'))
        if child_count > 0:
            raise UserError(_('To close the parent ticket, the child ticket must be closed.'))
        return {
            'name': "Reason",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'reason.reason',
            'target': 'new',
            'context': {'default_reason_type': 'close'}
        }

    def action_delete_status(self):
        if self.task_list_ids:
            if len(self.task_list_ids.ids) <= 1:
                raise UserError(_('It is not possible to delete the lines since it has single line.'))
            else:
                task_list_id = self.env['tasks.master.line'].search([('parent_ticket_id', '=', self.id)], limit=1,
                                                                    order='id desc')
                if task_list_id and not task_list_id.is_end_task:
                    task_list_id.meeting_ids.unlink()
                    task_list_id.unlink()
                elif task_list_id and task_list_id.is_end_task:
                    context = {
                        'parent_task_line_id': task_list_id.id
                    }
                    return {
                        'name': _('Send for Approval'),
                        'view_mode': 'form',
                        'res_model': 'parent.ticket.approval',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context': context
                    }
                self._onchange_task_list_ids()
        return True


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    parent_ticket_id = fields.Many2one('parent.ticket', string='Parent Ticket')


class ParentTicketAssetLine(models.Model):
    _name = 'parent.ticket.asset.line'

    parent_ticket_id = fields.Many2one('parent.ticket', string='Parent Ticket')
    product_id = fields.Many2one('product.product', string="Product")
    name = fields.Text(string="Description")
    serial_number_id = fields.Many2one('asset.model', string="Serial Number")
    stock_lot_id = fields.Many2one('stock.lot', string="Asset Lot/Serial Number")


class ParentTicketInventoryLine(models.Model):
    _name = 'parent.ticket.inventory.line'

    parent_ticket_id = fields.Many2one('parent.ticket', string='Parent Ticket')
    product_id = fields.Many2one('product.product', string="Product")
    avaliable_qty = fields.Float(string="Available Qty")
    done_qty = fields.Float(string="Done Qty")


class TasksMasterLine(models.Model):
    _inherit = 'tasks.master.line'

    parent_ticket_id = fields.Many2one('parent.ticket', string='Parent Ticket')
    child_ticket_id = fields.Many2one('child.ticket', string='Child Ticket')
    is_create_service_request = fields.Boolean(string="Create New Request", related='task_id.is_create_service_request')
    is_file_attachment = fields.Boolean(string="File Attachment", related='task_id.is_file_attachment')
    is_sign_required = fields.Boolean(string="Sign Required", related='task_id.is_sign_required')
    is_geo_location = fields.Boolean(string="Geo Location", related='task_id.is_geo_location')
    add_latitude = fields.Float(string='Geo Latitude', digits=(10, 7))
    add_longitude = fields.Float(string='Geo Longitude', digits=(10, 7))
    signature = fields.Html(string="Email Signature", readonly=False, store=True)
    attachment_ids = fields.Many2many('ir.attachment', 'tasks_master_line_attachment_rel', 'tasks_master_line_id',
                                      'attachment_id', 'Attachments',
                                      help="You may attach files to this Task Master, to be added to all ")
    is_enable_child_ticket = fields.Boolean(string="Create Child Ticket Creation",
                                            related='task_id.is_enable_child_ticket')
    is_request_spares = fields.Boolean(string="Request Spares", related='task_id.is_request_spares')
    is_request_raise_invoice = fields.Boolean(string="Request to Raise Invoice",
                                              related='task_id.is_request_raise_invoice')
    is_perform_diagnosis = fields.Boolean(string="Perform Diagnosis", related='task_id.is_perform_diagnosis')
    is_perform_repair = fields.Boolean(string="Perform Repair", related='task_id.is_perform_repair')
    is_perform_testing = fields.Boolean(string="Perform Testing", related='task_id.is_perform_testing')
    is_perform_quality = fields.Boolean(string="Perform Quality", related='task_id.is_perform_quality')
    is_schedule = fields.Boolean(string="Schedule", related='task_id.is_schedule')
    is_check_oem_warranty = fields.Boolean(string="Check OEM Warranty", related='task_id.is_check_oem_warranty')
    is_check_oem_repair_status = fields.Boolean(string="Check OEM Repair Status",
                                                related='task_id.is_check_oem_repair_status')
    meeting_subject = fields.Char(string="Meeting Subject")
    meeting_start_date = fields.Datetime(string="Starting At")
    meeting_end_date = fields.Datetime(string="Ending At")
    is_send_email = fields.Boolean(string="Send Email", related='task_id.is_send_email')
    is_maintenance_completed = fields.Boolean(string="Maintenance Completed",
                                              related='task_id.is_maintenance_completed')
    meeting_ids = fields.Many2many('calendar.event', readonly=True)
    meeting_done = fields.Boolean('calendar.event', readonly=True)
    is_notify = fields.Boolean(string="Notify", related='task_id.is_notify')
    is_allow_edit_after_submit = fields.Boolean(string="Allow Edit after Submit",
                                                related='task_id.is_allow_edit_after_submit')
    is_edit_after_submit = fields.Boolean(string="Allow Edit after Submit", compute='get_edit_after_access')
    is_inventory = fields.Boolean(string="Inventory", related='task_id.is_inventory')

    maintenance_problem_description = fields.Char(string='Problem description')
    recommendation_customer = fields.Char(string='Recommendation to Customers')
    customer_remarks = fields.Char(string='Customer Remarks')
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
    action_taken = fields.Char(string='Action taken')
    final_report_comments = fields.Char(string='Final report(Comments)')

    # PI Required
    complaint_type = fields.Selection([('service', 'Service'), ('user_facility', 'User Facility')],
                                      string='Complaint Type', default='service')
    phone = fields.Char(string='Phone')
    name_of_reporter = fields.Char(string='Name of reporter')
    email = fields.Char(string="Email")
    title = fields.Char(string='Title')
    date_of_reporting = fields.Date(string="Date of reporting")
    awareness_date = fields.Date(string="Awareness Date")
    reason_for_delay = fields.Char(string="Reason for delay")
    date_of_event = fields.Date(string="Date of Event")
    event_description = fields.Char(string="Event Description (be specific)")
    issue_noticed_comment = fields.Char(string="How was the issue noticed")
    select_case_completed = fields.Selection(
        [('complainant_not_aware', 'Complainant Not Aware'), ('no', 'No'), ('yes', 'Yes'),
         ('no_associated', 'No Associated Procedure'), ('not_reported', 'Not Reported')],
        string="Was the case completed successfully")
    select_medical_intervention_needed = fields.Selection(
        [('complainant_not_aware', 'Complainant Not Aware'), ('no', 'No'), ('yes', 'Yes'),
         ('no_associated', 'No Associated Procedure'), ('not_reported', 'Not Reported')],
        string="Was medical intervention needed")
    select_patient_involved = fields.Selection(
        [('complainant_not_aware', 'Complainant Not Aware'), ('no', 'No - No Impact'),
         ('yes', 'Yes - Impact - See Adverse Consequences'),
         ('yes-no_impact', 'Yes - No Impact'), ('not_reported', 'Not Reported')],
        string="Was a patient involved")
    select_surgical_delay = fields.Selection(
        [('complainant_not_aware', 'Complainant Not Aware'), ('no', 'No '), ('yes', 'Yes'),
         ('not_reported', 'Not Reported')],
        string="Was there a surgical delay")
    select_adverse_consequences = fields.Selection(
        [('complainant_not_aware', 'Complainant Not Aware'), ('no', 'No '), ('yes', 'Yes'),
         ('not_reported', 'Not Reported')],
        string="Were there adverse consequences")
    # PI Required Fields
    case_completed_successfully_id = fields.Many2one('case.completed.successfully',
                                                     string="Was the case completed successfully", copy=False)
    medical_intervention_id = fields.Many2one('medical.intervention', string="Was medical intervention needed",
                                              copy=False)
    patient_involved_id = fields.Many2one('patient.involved', string="Was a patient involved", copy=False)
    surgical_delay_id = fields.Many2one('surgical.delay', string="Was there a surgical delay", copy=False)
    length_of_delay = fields.Char(string="Adverse Consequence Details / Length of Delay")
    initial_reporter_facility = fields.Char(string="Initial Reporter Facility")
    ac_addr_number_street = fields.Char(string="(Account Address) Number and Street")
    ac_addr_city = fields.Char(string="(Account Address) City")
    contact_ac_marketing_name = fields.Char(string="(Contact at account making the complaint) Name")
    contact_ac_marketing_title = fields.Char(string="(Contact at account making the complaint) Title")
    contact_ac_marketing_phone = fields.Char(string="(Contact at account making the complaint) Phone")
    contact_ac_marketing_email = fields.Char(string="(Contact at account making the complaint) Email")
    sales_service_rep_name = fields.Char(string="Sales/Service Rep Name")
    product_no = fields.Char(string="Product No")
    product_description = fields.Char(string="Product Description")
    asset_serial_no = fields.Char(string="Serial/Lot Number")
    select_product_avail_stryker = fields.Selection([('not_available', 'Not available to Stryker'),
                                                     (
                                                         'repair',
                                                         'Repaired at India service facility (will provide TSR)'),
                                                     ('return', ' Will Return to Kalamazoo for repair')],
                                                    string="Is the product available to Stryker")
    no_avail_reason = fields.Char(string="If no available why")
    product_ref_no = fields.Char(string="Product Enquiry Reference Number")
    is_pi_mail_sent = fields.Boolean(string="PI Mail Sent")
    check_extended_warranty_status = fields.Boolean("Check Extended Warranty",
                                                    related='task_id.check_extended_warranty_status')

    # Work Order Fields
    # Equipment Details
    is_wk = fields.Boolean(string="Is Work Order", related='task_id.is_work_order')
    wk_cat_no = fields.Char(string="Cat No")
    wk_stock_lot_id = fields.Many2one('stock.lot', string="S.No/Lot No")
    wk_quantity = fields.Float(string="Equipment Quantity")
    wk_description = fields.Char(string="Equipment Description")
    # Customer Expectations
    wk_repair_charge = fields.Char(string="Repair Against Charge")
    # Under Warranty /Contract
    wk_inv_no = fields.Char(string="Invoice No")
    wk_date = fields.Date(string="In House Receive Date")
    # wk_period = fields.Char(string="Warranty/Contract Period")
    wk_install_date = fields.Date(string="Installation Date")
    wk_se_call_no = fields.Char(string="SE Call No", related='child_ticket_id.name')
    wk_exp_pi_no = fields.Char(string="EXP/PI No")
    wk_exp_pi_description = fields.Char(string="EXP/PI No,Description")
    accessories_line_ids = fields.One2many('wk.additional.accessories', 'tasks_master_id',
                                           string="Additional Accessories")
    ref_value = fields.Char(string="Reference Value")
    end_to = fields.Date(string='Warranty/Contract Period')
    start_from = fields.Date(string='Warranty/Contract Period')

    pick_up_arranged = fields.Char(string='Pick-Up Arranged')
    pickaging_checked = fields.Char(string='Packaging Checked')
    courrier_to_sc_name = fields.Char(string='Courrier to SC (Name)')
    tracking_ref_number = fields.Char(string='Tracking Ref Number')
    received_date = fields.Date(string='Received Date')
    is_request_approval = fields.Boolean(string="Request Approval", related='task_id.is_request_approval')
    approval_type_id = fields.Many2one(string="Type", comodel_name="multi.approval.type", required=True)

    def action_request_approval(self):
        for rec in self:
            if rec.task_id.is_request_approval and rec.parent_ticket_id:
                request = {
                    'name': rec.parent_ticket_id.name + ' Status update approval',
                    'type_id': rec.approval_type_id.id or False,
                    'parent_task_line_id': rec.id,
                    'parent_ticket_id': rec.parent_ticket_id.id
                }
                requests = self.env['multi.approval'].create(request)
                requests.action_submit()
                rec.parent_ticket_id.write({'state': 'waiting_for_approval', 'is_send_for_approvals': True})
            elif rec.task_id.is_request_approval and rec.child_ticket_id:
                request = {
                    'name': rec.child_ticket_id.name + ' Status update approval',
                    'type_id': rec.approval_type_id.id or False,
                    'child_task_line_id': rec.id,
                    'child_ticket_id': rec.child_ticket_id.id
                }
                requests = self.env['multi.approval'].create(request)
                requests.action_submit()
                rec.child_ticket_id.write({'state': 'waiting_for_approval', 'is_send_for_approvals': True})
        return True

    @api.onchange('task_id')
    def onchange_task_list(self):
        if self.is_wk and not self.env.user.has_group('ppts_service_request.service_request_group_ct_user'):
            raise ValidationError(_('This Task cannot updated by User Level 2'))
        if self.task_id.is_pi_required and not self.env.user.has_group(
                'ppts_service_request.service_request_group_ct_user'):
            raise ValidationError(_('This Task cannot updated by User Level 2'))
        if self.parent_ticket_id and self.task_id.is_end_task:
            self.action_taken = self.parent_ticket_id.action_taken_at_site
        if self.parent_ticket_id and self.task_id.is_pi_required:
            self.date_of_event = self.parent_ticket_id.service_request_id.event_date
            self.issue_noticed_comment = self.parent_ticket_id.service_request_id.issue_noticed
            self.case_completed_successfully_id = self.parent_ticket_id.service_request_id.case_completed_successfully_id
            self.medical_intervention_id = self.parent_ticket_id.service_request_id.medical_intervention_id
            self.patient_involved_id = self.parent_ticket_id.service_request_id.patient_involved_id
            self.surgical_delay_id = self.parent_ticket_id.service_request_id.surgical_delay_id
            self.select_adverse_consequences = self.parent_ticket_id.service_request_id.select_adverse_consequences
            self.contact_ac_marketing_name = self.parent_ticket_id.requested_by_name
            self.contact_ac_marketing_phone = self.parent_ticket_id.requested_by_contact_number
            self.contact_ac_marketing_email = self.parent_ticket_id.requested_by_email
            self.contact_ac_marketing_title = self.parent_ticket_id.requested_by_title
            self.initial_reporter_facility = self.parent_ticket_id.partner_id.name
        if self.child_ticket_id and self.task_id.is_end_task:
            self.action_taken = self.child_ticket_id.action_taken_at_site
        if self.child_ticket_id and self.task_id.is_pi_required:
            self.date_of_event = self.child_ticket_id.service_request_id.event_date
            self.issue_noticed_comment = self.child_ticket_id.service_request_id.issue_noticed
            self.case_completed_successfully_id = self.child_ticket_id.service_request_id.case_completed_successfully_id
            self.medical_intervention_id = self.child_ticket_id.service_request_id.medical_intervention_id
            self.patient_involved_id = self.child_ticket_id.service_request_id.patient_involved_id
            self.surgical_delay_id = self.child_ticket_id.service_request_id.surgical_delay_id
            self.select_adverse_consequences = self.child_ticket_id.service_request_id.select_adverse_consequences
            self.contact_ac_marketing_name = self.child_ticket_id.parent_ticket_id.requested_by_name
            self.contact_ac_marketing_phone = self.child_ticket_id.parent_ticket_id.requested_by_contact_number
            self.contact_ac_marketing_email = self.child_ticket_id.parent_ticket_id.requested_by_email
            self.contact_ac_marketing_title = self.child_ticket_id.parent_ticket_id.requested_by_title
            self.initial_reporter_facility = self.child_ticket_id.partner_id.name
            address = self.child_ticket_id.partner_id.street
            if address and self.child_ticket_id.partner_id.street2:
                address += ', ' + self.child_ticket_id.partner_id.street2
            if address and self.child_ticket_id.partner_id.zip:
                address += ', ' + self.child_ticket_id.partner_id.zip
            self.ac_addr_number_street = address
            self.ac_addr_city = self.child_ticket_id.partner_id.city_id.name
            if self.child_ticket_id.child_assign_engineer_ids:
                self.name_of_reporter = self.child_ticket_id.child_assign_engineer_ids[-1].name
                self.email = self.child_ticket_id.child_assign_engineer_ids[-1].partner_id.email
                self.phone = self.child_ticket_id.child_assign_engineer_ids[-1].partner_id.phone
                self.sales_service_rep_name = self.child_ticket_id.child_assign_engineer_ids[-1].name
                self.title = self.child_ticket_id.child_assign_engineer_ids[-1].partner_id.title.name
        if self.task_id.is_pi_required:
            self.product_no = self.parent_ticket_id.product_id.product_part or self.child_ticket_id.product_id.product_part
            self.product_description = self.parent_ticket_id.product_id.name or self.child_ticket_id.product_id.name
            self.asset_serial_no = self.parent_ticket_id.stock_lot_id.name or self.child_ticket_id.stock_lot_id.name
        if self.is_wk and self.child_ticket_id:
            self.wk_cat_no = self.child_ticket_id.product_id.product_part
            self.wk_stock_lot_id = self.child_ticket_id.stock_lot_id.id
            self.wk_quantity = 1
            self.wk_description = self.child_ticket_id.product_id.name
            self.wk_inv_no = self.child_ticket_id.stock_lot_id.invoice_number
            self.wk_install_date = self.child_ticket_id.stock_lot_id.installation_date
            self.start_from = self.child_ticket_id.stock_lot_id.warranty_start_date
            self.end_to = self.child_ticket_id.stock_lot_id.warranty_end_date

            # warranty_date_check = self.env['contract.contract'].search(
            #     [('partner_id', '=', self.child_ticket_id.partner_id.name)])
            # warranty_check = self.env['contract.line'].search(
            #     [('stock_lot_id', '=', self.child_ticket_id.stock_lot_id.name)])
            # if warranty_date_check and warranty_check:
            #         warranty_date_check.date_start= self.start_from

    @api.onchange('task_id', 'is_end_task')
    def action_populate_feedback(self):
        # CHILD TICKET
        if self.child_ticket_id.request_type == 'sr_installation' and self.is_end_task:
            installation_id = self.env['project.task'].sudo().search(
                [('installation_child_ticket_id', '=', self.child_ticket_id._origin.id),
                 ('installation_state', '=', 'completed')], limit=1)
            if installation_id:
                self.feed_back_end_task_1 = installation_id.feed_back_end_task_1
                self.feed_back_end_task_2 = installation_id.feed_back_end_task_2
                self.feed_back_end_task_3 = installation_id.feed_back_end_task_3
                self.feed_back_end_task_4 = installation_id.feed_back_end_task_4
                self.feed_back_end_task_5 = installation_id.feed_back_end_task_5
        # PARENT TICKET
        if self.parent_ticket_id.request_type == 'sr_installation' and self.is_end_task:
            installation_id = self.env['project.task'].sudo().search(
                [('installation_child_ticket_id', '=', self.parent_ticket_id._origin.id),
                 ('installation_state', '=', 'completed')], limit=1)
            if installation_id:
                self.feed_back_end_task_1 = installation_id.feed_back_end_task_1
                self.feed_back_end_task_2 = installation_id.feed_back_end_task_2
                self.feed_back_end_task_3 = installation_id.feed_back_end_task_3
                self.feed_back_end_task_4 = installation_id.feed_back_end_task_4
                self.feed_back_end_task_5 = installation_id.feed_back_end_task_5

    def create_inventory(self):

        for rec in self.parent_ticket_id:
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

    # Both For Parent and Child Ticket
    def get_edit_after_access(self):
        for rec in self:
            string = rec.status

            if not string or rec.is_allow_edit_after_submit:
                rec.is_edit_after_submit = False
            elif string:
                rec.is_edit_after_submit = True

    def create(self, vals):
        res = super().create(vals)
        res.button_tasks_update()
        return res

    # This method is used to print the work order report
    def _print_create_workorder_report(self, child_ticket_id, task_id):
        report = self.env.ref('ppts_parent_ticket.action_service_report_config')
        data_record = base64.b64encode(
            self.env['ir.actions.report'].sudo()._render_qweb_pdf(report, [child_ticket_id.id],
                                                                  data=None)[0])
        template_id = self.env.ref('ppts_parent_ticket.mail_template_create_wor_order_child_ticket')
        ir_values = {
            'name': "Create Work Order / " + child_ticket_id.name,
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_model': 'child.ticket',
        }
        report_attachment_id = self.env['ir.attachment'].sudo().create(ir_values)
        template_id.attachment_ids.unlink()
        template_id.attachment_ids = [(4, report_attachment_id.id)]
        employee = self.env['hr.employee'].sudo().search(
            [('job_id', 'in', task_id.sudo().job_ids.ids)]).mapped('work_email')
        employee_cc = self.env['hr.employee'].sudo().search(
            [('job_id', 'in', task_id.sudo().job_cc_ids.ids)]).mapped('work_email')
        mails = ', '.join(employee)
        mails_cc = ', '.join(employee_cc)
        template_id.with_context(email_to=mails, email_cc=mails_cc, task=task_id.id).sudo().send_mail(
            child_ticket_id.id, force_send=True)

    def button_tasks_update(self):
        for record in self:
            employee = self.env['hr.employee'].sudo().search(
                [('job_id', 'in', record.task_id.sudo().job_ids.ids)]).mapped('work_email')
            employee_cc = self.env['hr.employee'].sudo().search(
                [('job_id', 'in', record.task_id.sudo().job_cc_ids.ids)]).mapped('work_email')
            mails = ', '.join(employee)
            mails_cc = ', '.join(employee_cc)
            pro = []
            work_flow = self.env["tasks.master.line"].search(
                [("workflow_id", "=", record.parent_ticket_id.parent_configuration_id.work_flow_id.id),
                 ("task_id", "=", record.task_id.id)])
            child_work_flow = self.env["tasks.master.line"].search(
                [("workflow_id", "=", record.child_ticket_id.child_configuration_id.work_flow_id.id),
                 ("task_id", "=", record.task_id.id)])
            if work_flow and record.parent_ticket_id:
                for wk in work_flow:
                    if wk.next_task_ids:
                        pro_ids = [(6, 0, wk.next_task_ids.ids)]
                        record.parent_ticket_id.next_task_ids = pro_ids
                        record.next_task_ids = [(6, 0, wk.next_task_ids.ids)]
            if child_work_flow and record.child_ticket_id:
                for wk in child_work_flow:
                    if wk.next_task_ids:
                        pro_ids = [(6, 0, wk.next_task_ids.ids)]
                        record.child_ticket_id.next_task_ids = pro_ids
                        record.next_task_ids = [(6, 0, wk.next_task_ids.ids)]
            # Both For Parent and Child Ticket
            if record.is_schedule and record.meeting_subject and record.meeting_start_date and record.meeting_end_date and not record.meeting_done:
                calendar_event = self.env['calendar.event'].create({
                    'name': record.meeting_subject,
                    'start': record.meeting_start_date,
                    'stop': record.meeting_end_date,
                })
                record.meeting_ids = [(4, calendar_event.id)]
                record.status = "%s Scheduled" % calendar_event.name
                record.meeting_done = True
            # If the work order is created without and In taken, then show the warning message
            if record.is_wk and record.child_ticket_id:
                for picking in self.env['stock.picking'].sudo().search(
                        [('child_ticket_id', '=', record.child_ticket_id.id), ('child_ticket_id', '!=', False)]):
                    if picking.picking_type_id.code == 'incoming' and picking.state not in ('done', 'cancel'):
                        raise ValidationError(_('Confirm this order (%s) to start the work order.', picking.name))
                # Print the create work order report while select and save the create work order status on the line.
                self._print_create_workorder_report(record.child_ticket_id, task_id=self.task_id)
            # If this ticket has repair order, without validating the delivery order this status should not be selected.
            if record.task_id.name == 'Start Travel for Equipment Handover':
                child_ticket_id = self.env['child.ticket'].search([('origin', '=', record.child_ticket_id.name)],
                                                                  limit=1)
                # [('id', 'in', self.inward_picking_ids.filtered(lambda r: r.is_inward_transfer).ids)]
                for picking in self.env['stock.picking'].sudo().search(
                        [('child_ticket_id', '=', child_ticket_id.id), ('child_ticket_id', '!=', False)]):
                    if picking.picking_type_id.code == 'outgoing' and picking.state not in ('done', 'cancel'):
                        raise ValidationError(
                            _("Confirm this delivery order (%s) to proceed with this status (%s).", picking.name,
                              record.task_id.name))
            if record.is_notify:
                template_id = self.env.ref('ppts_parent_ticket.notify_email_template')
                if template_id:
                    template_id.with_context(email_to=mails, email_cc=mails_cc).sudo().send_mail(record.id,
                                                                                                 force_send=True)
            if record.is_end_task and record.parent_ticket_id and not record.parent_ticket_id.request_type == 'sr_wr':

                template_id = self.env.ref('ppts_parent_ticket.mail_template_closed_parent_ticket')
                if template_id:
                    template_id.with_context(email_to=mails, email_cc=mails_cc).sudo().send_mail(
                        self.parent_ticket_id.id, force_send=True)

            if record.is_pi_required and not record.is_pi_mail_sent:
                template_id_pi_pt = self.env.ref('ppts_parent_ticket.mail_template_pi_required_parent_ticket')
                template_id_pi_ct = self.env.ref('ppts_parent_ticket.mail_template_pi_required_child_ticket')
                if template_id_pi_pt and record.parent_ticket_id:
                    template_id_pi_pt.with_context(email_to=mails, email_cc=mails_cc, task=record.id).sudo().send_mail(
                        self.parent_ticket_id.id, force_send=True)
                    record.is_pi_mail_sent = True
                elif template_id_pi_ct and record.child_ticket_id:
                    report = self.env.ref('ppts_parent_ticket.pi_sf_field_report')
                    data_record = base64.b64encode(
                        self.env['ir.actions.report'].sudo()._render_qweb_pdf(report, [record.child_ticket_id.id],
                                                                              data=None)[0])
                    # self.env['ir.actions.report'].sudo()._render_qweb_pdf(report, [record.child_ticket_id.service_request_id.id], data=None)[0])
                    ir_values = {
                        'name': "PI-SF-Field Call / " + record.child_ticket_id.name,
                        'type': 'binary',
                        'datas': data_record,
                        'store_fname': data_record,
                        'mimetype': 'application/pdf',
                        'res_model': 'child.ticket',
                    }
                    report_attachment_id = self.env['ir.attachment'].sudo().create(ir_values)
                    template_id_pi_ct.attachment_ids.unlink()
                    template_id_pi_ct.attachment_ids = [(4, report_attachment_id.id)]
                    template_id_pi_ct.with_context(email_to=mails, email_cc=mails_cc, task=record.id).sudo().send_mail(
                        record.child_ticket_id.id, force_send=True)
                    record.is_pi_mail_sent = True
            if record.is_check_oem_warranty and record.parent_ticket_id:
                parent_ticket = self.env['parent.ticket'].search([('id', '=', record.parent_ticket_id.id)])
                stock_lot_obj = self.env['stock.lot'].search([('name', '=', parent_ticket.stock_lot_id.name)])
                # warranty
                warranty_check_false = stock_lot_obj.filtered(lambda x: x.oem_warranty_check == False)
                warranty_check_true = stock_lot_obj.filtered(lambda x: x.oem_warranty_check == True)

                if parent_ticket.stock_lot_id:
                    if warranty_check_false:
                        parent_ticket.oem_warranty_status = 'not_available'
                    if warranty_check_true:
                        oem_warranty = warranty_check_true.search(
                            [('name', '=', parent_ticket.stock_lot_id.name),
                             ('warranty_start_date', '<=', date.today()),
                             ('warranty_end_date', '>=', date.today())])
                        if oem_warranty:
                            parent_ticket.oem_warranty_status = 'in_oem_warranty'
                        else:
                            parent_ticket.oem_warranty_status = 'out_oem_warranty'
                else:
                    parent_ticket.oem_warranty_status = ''
                oem_warranty_status = dict(parent_ticket._fields['oem_warranty_status'].selection).get(
                    parent_ticket.oem_warranty_status)
                template_id_check_oem_warranty = self.env.ref(
                    'ppts_parent_ticket.mail_template_check_oem_warranty_parent_ticket')
                if template_id_check_oem_warranty:
                    template_id_check_oem_warranty.with_context(email_to=mails, email_cc=mails_cc, task=record.id,
                                                                oem_warranty_status=oem_warranty_status).sudo().send_mail(
                        record.parent_ticket_id.id, force_send=True)

            elif record.is_check_oem_repair_status and record.parent_ticket_id:
                parent_ticket = self.env['parent.ticket'].search([('id', '=', record.parent_ticket_id.id)])
                stock_lot_obj = self.env['stock.lot'].search([('name', '=', parent_ticket.stock_lot_id.name)])
                # repair
                repair_check_false = stock_lot_obj.filtered(lambda x: x.oem_repair_warranty_check == False)
                repair_check_true = stock_lot_obj.filtered(lambda x: x.oem_repair_warranty_check == True)

                if parent_ticket.stock_lot_id:
                    if repair_check_false:
                        parent_ticket.oem_repair_status = 'not_available'
                    if repair_check_true:
                        oem_repair = repair_check_true.search(
                            [('name', '=', parent_ticket.stock_lot_id.name),
                             ('repair_warranty_start_date', '<=', date.today()),
                             ('repair_warranty_end_date', '>=', date.today())])
                        if oem_repair:
                            parent_ticket.oem_repair_status = 'in_repair_warranty'
                        else:
                            parent_ticket.oem_repair_status = 'out_repair_warranty'
                else:
                    parent_ticket.oem_repair_status = ''

                oem_repair_status = dict(parent_ticket._fields['oem_repair_status'].selection).get(
                    parent_ticket.oem_repair_status)
                template_id_check_oem_repair_warranty = self.env.ref(
                    'ppts_parent_ticket.mail_template_check_oem_repair_status_parent_ticket')
                if template_id_check_oem_repair_warranty:
                    template_id_check_oem_repair_warranty.with_context(email_to=mails, email_cc=mails_cc,
                                                                       task=record.id,
                                                                       oem_repair_status=oem_repair_status).sudo().send_mail(
                        record.parent_ticket_id.id, force_send=True)
            elif record.check_extended_warranty_status and record.parent_ticket_id or record.child_ticket_id:
                ticket = None
                if record.parent_ticket_id:
                    ticket = self.env['parent.ticket'].search([('id', '=', record.parent_ticket_id.id)])
                elif record.child_ticket_id:
                    ticket = self.env['child.ticket'].search([('id', '=', record.child_ticket_id.id)])
                stock_lot_obj = self.env['stock.lot'].search([('id', '=', ticket.stock_lot_id.id)])
                if stock_lot_obj and stock_lot_obj.extended_warranty_start_date and stock_lot_obj.extended_warranty_end_date:
                    if stock_lot_obj.extended_warranty_end_date >= date.today():
                        ticket.extended_warranty_status = 'in_repair_warranty'
                    else:
                        ticket.extended_warranty_status = 'out_repair_warranty'
                else:
                    ticket.extended_warranty_status = 'not_available'
                extended_warranty_status = dict(ticket._fields['extended_warranty_status'].selection).get(
                    ticket.extended_warranty_status)
                template_extended_warranty_status = self.env.ref(
                    'ppts_parent_ticket.mail_template_check_extended_status_parent_ticket') if record.parent_ticket_id else self.env.ref(
                    'ppts_parent_ticket.mail_template_check_extended_status_child_ticket')
                if template_extended_warranty_status and not ticket.is_ew_status_mailsent:
                    template_extended_warranty_status.with_context(email_to=mails, email_cc=mails_cc, task=record.id,
                                                                   extended_warranty_status=extended_warranty_status).sudo().send_mail(
                        ticket.id, force_send=True)
                    ticket.is_ew_status_mailsent = True  # If the mail sent once then shoudl not send mail again. so marking this field as true not to send mail more than once.
            # Automated Service Request Creation
            if record.task_id.is_create_service_request:
                record.create_sr()
            # Automated Child Ticket Creation
            if record.task_id.is_enable_child_ticket:
                record.child_ticket_id.task_value_notify = record.task_id.id
                record.create_child_ticket()
            # Automated Parent Ticket Creation
            if record.task_id.is_create_ticket:
                record.action_parent_ticket_create()
            # Request Approval
            if record.task_id.is_request_approval:
                record.action_request_approval()
            record.parent_ticket_id.is_request_reassign = record.task_id.is_ressign_engineer
            record.child_ticket_id.is_request_reassign = record.task_id.is_ressign_engineer
            record.parent_ticket_id.is_disable_status_update = record.task_id.is_disable_status_update
            record.child_ticket_id.is_disable_status_update = record.task_id.is_disable_status_update

    def action_parent_ticket_create(self):
        self.ensure_one()
        if self.parent_ticket_id:
            data = {
                'product_id': self.parent_ticket_id.product_id.id or False,
                'partner_id': self.parent_ticket_id.partner_id.id or False,
                'call_source_id': self.parent_ticket_id.call_source_id.id or False,
                'product_category_id_alias': self.parent_ticket_id.product_category_id_alias or '',
                'requested_by_name': self.parent_ticket_id.requested_by_name or '',
                'requested_by_contact_number': self.parent_ticket_id.requested_by_contact_number or '',
                'requested_by_email': self.parent_ticket_id.requested_by_email or '',
                'requested_by_title': self.parent_ticket_id.requested_by_title or '',
                'call_received_id': self.parent_ticket_id.call_received_id.id or False,
                'oem_warranty_status_id': self.parent_ticket_id.oem_warranty_status_id.id or False,
                'repair_warranty_status_id': self.parent_ticket_id.repair_warranty_status_id.id or False,
                'team_id': self.parent_ticket_id.team_id.id or False,
                'state': 'new',
                'remarks': self.parent_ticket_id.remarks or '',
                'problem_description': self.parent_ticket_id.problem_description or '',
                'description': self.parent_ticket_id.description or '',
                'dealer_distributor_id': self.parent_ticket_id.dealer_distributor_id.id or False,
                'stock_lot_id': self.parent_ticket_id.stock_lot_id.id or False,
                'categ_id': self.parent_ticket_id.categ_id.id or False,
                'parent_ticket_id_alias': self.parent_ticket_id.parent_ticket_id_alias or '',
                'service_category_id': self.task_id.service_category_id.id or False,
                'service_type_id': self.task_id.service_type_id.id or False,
                'request_type_id': self.task_id.request_type_id.id or False,
                'parent_configuration_id': self.task_id.parent_configuration_id.id or False,
            }
            parent_ticket = self.env['parent.ticket'].sudo().create(data)
            # If the request type is not need for an approval then this field must be true
            if not self.task_id.request_type_id.is_required_approval:
                parent_ticket.is_send_for_approvals = True
            if not self.task_id.parent_configuration_id.work_flow_id.task_list_ids:
                raise UserError('Tasks are not mapped on this workflow to create parent ticket.')
            if self.task_id.parent_configuration_id.work_flow_id:
                status = self.task_id.parent_configuration_id.work_flow_id.task_list_ids[0]
                status_data = [(0, 0, {
                    'task_id': status.task_id.id,
                    'next_task_ids': [(6, 0, status.next_task_ids.ids)],
                    'status': status.status,
                    'parent_ticket_id': parent_ticket.id,
                })]
                parent_ticket.write({'task_list_ids': status_data})
            parent_ticket._onchange_stock_lot_id()
            parent_ticket._onchange_task_list_ids()
            parent_ticket.onchange_service()
            parent_ticket._onchange_request_type_id()
            parent_ticket._onchange_request_type()
            parent_ticket.get_repair_warranty_approval_required()
            parent_ticket.partner_amc_cmc_status_check()
        elif self.child_ticket_id:
            data = {
                'product_id': self.child_ticket_id.product_id.id or False,
                'partner_id': self.child_ticket_id.partner_id.id or False,
                'call_source_id': self.child_ticket_id.call_source_id.id or False,
                'product_category_id_alias': self.child_ticket_id.product_category_id_alias or '',
                'requested_by_name': self.child_ticket_id.requested_by_name_child or '',
                'requested_by_contact_number': self.child_ticket_id.requested_by_contact_number or '',
                'call_received_id': self.child_ticket_id.call_received_id.id or False,
                'oem_warranty_status_id': self.child_ticket_id.oem_warranty_status_id.id or False,
                'repair_warranty_status_id': self.child_ticket_id.repair_warranty_status_id.id or False,
                'team_id': self.child_ticket_id.team_id.id or False,
                'state': 'new',
                'remarks': self.child_ticket_id.remarks or '',
                'problem_description': self.child_ticket_id.problem_description or '',
                'description': self.child_ticket_id.description or '',
                'dealer_distributor_id': self.child_ticket_id.dealer_distributor_id.id or False,
                'stock_lot_id': self.child_ticket_id.stock_lot_id.id or False,
                'categ_id': self.child_ticket_id.categ_id.id or False,
                'parent_ticket_id_alias': self.child_ticket_id.child_ticket_id_alias or '',
                'service_category_id': self.task_id.service_category_id.id or False,
                'service_type_id': self.task_id.service_type_id.id or False,
                'request_type_id': self.task_id.request_type_id.id or False,
                'parent_configuration_id': self.task_id.parent_configuration_id.id or False,
                'origin': self.child_ticket_id.name
            }
            parent_ticket = self.env['parent.ticket'].sudo().create(data)
            # If the request type is not need for an approval then this field must be true
            if not self.task_id.request_type_id.is_required_approval:
                parent_ticket.is_send_for_approvals = True
            if not self.task_id.parent_configuration_id.work_flow_id.task_list_ids:
                raise UserError(
                    'There is no workflow configured for this type. Map the workflow configuration on the parent ticket configuration.')
            if self.task_id.parent_configuration_id.work_flow_id:
                status = self.task_id.parent_configuration_id.work_flow_id.task_list_ids[0]
                status_data = [(0, 0, {
                    'task_id': status.task_id.id,
                    'next_task_ids': [(6, 0, status.next_task_ids.ids)],
                    'status': status.status,
                    'parent_ticket_id': parent_ticket.id,
                })]
                parent_ticket.write({'task_list_ids': status_data})
            parent_ticket._onchange_stock_lot_id()
            parent_ticket._onchange_task_list_ids()
            parent_ticket.onchange_service()
            parent_ticket._onchange_request_type_id()
            parent_ticket._onchange_request_type()
            parent_ticket.get_repair_warranty_approval_required()
            parent_ticket.partner_amc_cmc_status_check()

    def create_sr(self):
        self.ensure_one()
        # While create service request show all the asset and customer data as per the child or parent ticket.
        if self.parent_ticket_id:
            existing_service_request_id = self.env['service.request'].sudo().search(
                [('parent_ticket_id', '=', self.parent_ticket_id.id)])
            if existing_service_request_id:
                new_service_request_id = existing_service_request_id.copy()
                new_service_request_id.is_from_ct = True
                new_service_request_id.service_request_id_alias = self.parent_ticket_id.parent_ticket_id_alias
                new_service_request_id.service_request_date = datetime.today()
                new_service_request_id.customer_name = self.parent_ticket_id.partner_id.name
                new_service_request_id.request_type_id = self.task_id.request_type_id.id or False
                new_service_request_id.team_id = self.task_id.request_type_id.team_id.id or False
                new_service_request_id.service_category_id = self.task_id.service_category_id.id or False
                new_service_request_id.service_type_id = self.task_id.service_type_id.id or False
                new_service_request_id.parent_ticket_id = self.parent_ticket_id.id or False

        elif self.child_ticket_id:
            existing_service_request_id = self.env['service.request'].sudo().search(
                [('parent_ticket_id', '=', self.child_ticket_id.parent_ticket_id.id)], limit=1)
            if existing_service_request_id:
                new_service_request_id = existing_service_request_id.copy()
                new_service_request_id.is_from_ct = True
                new_service_request_id.service_request_id_alias = self.child_ticket_id.child_ticket_id_alias
                new_service_request_id.service_request_date = datetime.today()
                new_service_request_id.customer_name = self.child_ticket_id.partner_id.name
                new_service_request_id.request_type_id = self.task_id.request_type_id.id or False
                new_service_request_id.team_id = self.task_id.request_type_id.team_id.id or False
                new_service_request_id.service_category_id = self.task_id.service_category_id.id or False
                new_service_request_id.service_type_id = self.task_id.service_type_id.id or False
                new_service_request_id.child_ticket_id = self.child_ticket_id.id or False
                new_service_request_id.partner_id = existing_service_request_id.partner_id.id if existing_service_request_id.partner_id else False
                new_service_request_id._onchange_partner()
                stock_lines = []
                for record in existing_service_request_id.customer_asset_ids:
                    vals = (0, 0, {
                        'stock_lot_id': record.stock_lot_id.id,
                        'product_id': record.product_id.id,
                        'notes': record.notes
                    })
                    stock_lines.append(vals)
                new_service_request_id.customer_asset_ids = stock_lines
                task_id = self.env.ref('ppts_custom_workflow.sr_created')
                self.child_ticket_id.update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })

    def create_child_ticket(self):
        self.ensure_one()
        if self.parent_ticket_id:
            data = {
                'partner_id': self.parent_ticket_id.partner_id.id or False,
                'child_ticket_id_alias': self.parent_ticket_id.parent_ticket_id_alias or '',
                'parent_ticket_id_alias_date': self.parent_ticket_id.parent_ticket_id_alias_date or None,
                'call_source_id': self.parent_ticket_id.call_source_id.id or False,
                'call_date': self.parent_ticket_id.call_date or False,
                'product_id': self.parent_ticket_id.product_id.id or False,
                'stock_lot_id': self.parent_ticket_id.stock_lot_id.id or False,
                'categ_id': self.parent_ticket_id.categ_id.id or False,
                'product_category_id_alias': self.parent_ticket_id.product_category_id_alias or '',
                'problem_description': self.parent_ticket_id.problem_description or '',
                'requested_by_name_child': self.parent_ticket_id.requested_by_name or '',
                'requested_by_contact_number': self.parent_ticket_id.requested_by_contact_number or '',
                'remarks': self.parent_ticket_id.remarks or '',
                'dealer_distributor_id': self.parent_ticket_id.dealer_distributor_id.id or False,
                'call_received_id': self.parent_ticket_id.call_received_id.id or False,
                'alternate_contact_name': self.parent_ticket_id.alternate_contact_name or '',
                'alternate_contact_number': self.parent_ticket_id.alternate_contact_number or '',
                'alternate_contact_email': self.parent_ticket_id.alternate_contact_email or '',
                'oem_warranty_status_id': self.parent_ticket_id.oem_warranty_status_id.id or False,
                'repair_warranty_status_id': self.parent_ticket_id.repair_warranty_status_id.id or False,
                'customer_account_id': self.parent_ticket_id.customer_account_id.id or False,
                'team_id': self.parent_ticket_id.team_id.id or False,
                'faulty_section': self.parent_ticket_id.faulty_section or '',
                'sow': self.parent_ticket_id.sow or '',
                'webdelata_id': self.parent_ticket_id.webdelata_id or '',
                'webdelata': self.parent_ticket_id.webdelata or '',
                'mc_stk': self.parent_ticket_id.mc_stk or False,
                'child_configuration_id': self.task_id.child_configuration_id.id or False,
                'service_category_id': self.task_id.service_category_id.id or False,
                'service_type_id': self.task_id.service_type_id.id or False,
                'request_type_id': self.task_id.request_type_id.id or False,
                'origin': self.parent_ticket_id.name,
                'parent_ticket_id': self.parent_ticket_id.id,
                'repair_location_id': self.parent_ticket_id.repair_center_location_id.id,
            }
            child_ticket = self.env['child.ticket'].sudo().create(data)
            if self.task_id.child_configuration_id.work_flow_id:
                status = self.task_id.child_configuration_id.work_flow_id.task_list_ids[0]
                status_data = [(0, 0, {
                    'task_id': status.task_id.id,
                    'next_task_ids': [(6, 0, status.next_task_ids.ids)],
                    'status': status.status,
                    'child_ticket_id': child_ticket.id,
                })]
                child_ticket.sudo().write({'task_list_ids': status_data})
            # if request type is an approval then this field must be true to send for an approval
            if not self.task_id.request_type_id.is_required_approval:
                child_ticket.is_send_for_approvals = True
            # Create notification for the CT user.
            user_id = self.child_ticket_id.parent_ticket_id.assign_engineer_ids[-1] if self.child_ticket_id else self.sudo().parent_ticket_id.assign_engineer_ids[-1]
            model_id = self.env['ir.model'].sudo().search([('model', '=', 'parent.ticket')])
            self.env['mail.activity'].sudo().create(
                {'activity_type_id': 4, 'user_id': user_id.id,
                 'summary': 'Repair ticket is created and the reference number is' + ' ' + str(child_ticket.name) + ' and the parent reference number is ' + str(self.child_ticket_id.sudo().parent_ticket_id.name or self.sudo().parent_ticket_id.name),
                 'res_model': 'parent.ticket', 'res_model_id': model_id.id,
                 'res_id': self.child_ticket_id.sudo().parent_ticket_id.id or self.sudo().parent_ticket_id.id})
            child_ticket._onchange_stock_lot_id()
            child_ticket._onchange_task_list_ids()
            # Reference For Task
            self.ref_value = child_ticket.name
        elif self.child_ticket_id:
            data = {
                'partner_id': self.child_ticket_id.partner_id.id or False,
                'child_ticket_id_alias': self.child_ticket_id.child_ticket_id_alias or '',
                'parent_ticket_id_alias_date': self.child_ticket_id.parent_ticket_id_alias_date or None,
                'call_source_id': self.child_ticket_id.call_source_id.id or False,
                'call_date': self.child_ticket_id.call_date or False,
                'product_id': self.child_ticket_id.product_id.id or False,
                'stock_lot_id': self.child_ticket_id.stock_lot_id.id or False,
                'categ_id': self.child_ticket_id.categ_id.id or False,
                'product_category_id_alias': self.child_ticket_id.product_category_id_alias or '',
                'problem_description': self.child_ticket_id.problem_description or '',
                'requested_by_name_child': self.child_ticket_id.requested_by_name_child or '',
                'requested_by_contact_number': self.child_ticket_id.requested_by_contact_number or '',
                'remarks': self.child_ticket_id.remarks or '',
                'dealer_distributor_id': self.child_ticket_id.dealer_distributor_id.id or False,
                'call_received_id': self.child_ticket_id.call_received_id.id or False,
                'alternate_contact_name': self.child_ticket_id.alternate_contact_name or '',
                'alternate_contact_number': self.child_ticket_id.alternate_contact_number or '',
                'alternate_contact_email': self.child_ticket_id.alternate_contact_email or '',
                'oem_warranty_status_id': self.child_ticket_id.oem_warranty_status_id.id or False,
                'repair_warranty_status_id': self.child_ticket_id.repair_warranty_status_id.id or False,
                'customer_account_id': self.child_ticket_id.customer_account_id.id or False,
                'team_id': self.child_ticket_id.team_id.id or False,
                'faulty_section': self.child_ticket_id.faulty_section or '',
                'sow': self.child_ticket_id.sow or '',
                'webdelata_id': self.child_ticket_id.webdelata_id or '',
                'webdelata': self.child_ticket_id.webdelata or '',
                'mc_stk': self.child_ticket_id.mc_stk or False,
                'child_configuration_id': self.task_id.child_configuration_id.id or False,
                'service_category_id': self.task_id.service_category_id.id or False,
                'service_type_id': self.task_id.service_type_id.id or False,
                'request_type_id': self.task_id.request_type_id.id or False,
                'origin': self.child_ticket_id.name,
                'parent_ticket_id': self.child_ticket_id.sudo().parent_ticket_id.id,
                'parent_child_ticket_id': self.child_ticket_id.id,
                'repair_location_id': self.child_ticket_id.repair_location_id.id,
                'action_taken_at_site': self.child_ticket_id.action_taken_at_site,
                'product_part_number': self.child_ticket_id.product_part_number,
                'requested_by_email_ct': self.child_ticket_id.requested_by_email_ct,
                'requested_by_title_ct': self.child_ticket_id.requested_by_title_ct,
                'alternate_contact_id': self.child_ticket_id.alternate_contact_id.id,
            }
            child_ticket = self.env['child.ticket'].sudo().create(data)
            # if request type is an approval then this field must be true to send for an approval
            if not self.task_id.request_type_id.is_required_approval:
                child_ticket.is_send_for_approvals = True
            if self.task_id.child_configuration_id.work_flow_id:
                status = self.task_id.child_configuration_id.work_flow_id.task_list_ids[0]
                status_data = [(0, 0, {
                    'task_id': status.task_id.id,
                    'next_task_ids': [(6, 0, status.next_task_ids.ids)],
                    'status': status.status,
                    'child_ticket_id': child_ticket.id,
                })]
                child_ticket.sudo().write({'task_list_ids': status_data})
                # Create notification for the CT user.
                user_id = self.child_ticket_id.parent_ticket_id.assign_engineer_ids[-1]
                model_id = self.env['ir.model'].sudo().search([('model', '=', 'parent.ticket')])
                self.env['mail.activity'].sudo().create(
                    {'activity_type_id': 4, 'user_id': user_id.id,
                     'summary': 'Repair ticket is created and the reference number is' + ' ' + child_ticket.name + ' and the parent reference number is ' + self.child_ticket_id.sudo().parent_ticket_id.name,
                     'res_model': 'parent.ticket', 'res_model_id': model_id.id,
                     'res_id': self.child_ticket_id.sudo().parent_ticket_id.id})
            child_ticket._onchange_stock_lot_id()
            child_ticket._onchange_task_list_ids()
            # Reference For Task
            self.ref_value = child_ticket.name

    def request_spares(self):
        self.ensure_one()
        if self.child_ticket_id:
            context = {
                "default_name": "Spare Request",
                "default_is_spare_request": True,
                "default_child_ticket_id": self.child_ticket_id.id or False,
                "default_team_id": self.child_ticket_id.team_id.id,
                "default_user_id": self.env.user.id,
                "default_partner_id": self.child_ticket_id.partner_id.id,

            }
            context.update(self.env.context)
            return {
                'name': "Request",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'request',
                "target": "new",
                "context": context,
            }
        elif self.parent_ticket_id:
            context = {
                "default_name": "Spare Request",
                "default_is_spare_request": True,
                "default_parent_ticket_id": self.parent_ticket_id.id or False,
                "default_team_id": self.parent_ticket_id.team_id.id,
                "default_user_id": self.env.user.id,
                "default_partner_id": self.parent_ticket_id.partner_id.id,

            }
            context.update(self.env.context)
            return {
                'name': "Request",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'request',
                "target": "new",
                "context": context,
            }

    def request_spares_dummy(self):
        self.ensure_one()
        context = {
            "default_indent_date": datetime.now(),
            "default_requirement": '1',
            "default_type": 'stock',
            "default_parent_ticket_id": self.parent_ticket_id.id or False,
            "default_child_ticket_id": self.child_ticket_id.id or False,
            "default_state": 'draft',
            "default_partner_id": self.parent_ticket_id.partner_id.id or self.child_ticket_id.partner_id.id,
            "default_team_id": self.parent_ticket_id.team_id.id or self.child_ticket_id.team_id.id,
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

    def request_raise_invoice(self):
        request_data = {
            'name': self.task_id.name,
            'parent_ticket_id': self.parent_ticket_id.id,
            'child_ticket_id': self.child_ticket_id.id,
            'team_id': self.parent_ticket_id.team_id.id or self.child_ticket_id.team_id.id,
            'user_id': self.env.user.id,
            'is_create_invoice': True,
        }
        self.env['request'].create(request_data)

    def perform_diagnosis(self):
        pass

    def perform_repair(self):
        self.ensure_one()
        context = {
            "default_name": self.parent_ticket_id.name or self.child_ticket_id.name + " Ticket",
            "default_user_id": self.env.user.id,
            # "default_parent_ticket_id": self.parent_ticket_id.id or False,
            # "default_child_ticket_id": self.child_ticket_id.id or False,
            "default_partner_id": self.parent_ticket_id.partner_id.id or self.child_ticket_id.partner_id.id,
            "default_team_id": self.parent_ticket_id.team_id.id or self.child_ticket_id.team_id.id,
        }
        context.update(self.env.context)
        view_id = self.env.ref("rma_ppts.crm_claims_ppts_form_view").id
        return {
            "type": "ir.actions.act_window",
            "name": "Repair Request",
            "res_model": "crm.claim.ppts",
            "view_mode": "form",
            "views": [(view_id, "form")],
            "target": "new",
            "context": context,
        }
        # request_data = {
        #     'name': self.task_id.name,
        #     'parent_ticket_id': self.parent_ticket_id.id,
        #     'child_ticket_id': self.child_ticket_id.id,
        #     'team_id': self.parent_ticket_id.team_id.id or self.child_ticket_id.team_id.id,
        #     'user_id': self.env.user.id,
        #     'is_create_repair': True,
        # }
        # self.env['request'].create(request_data)

    def perform_testing(self):
        pass

    def perform_quality(self):
        pass

    def send_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup('ppts_parent_ticket.email_template_parent_ticket')[2]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
        except ValueError:
            compose_form_id = False
        # if not self.parent_ticket_id.partner_id.email:
        #     return self._show_notification('Please Enter Customer Email')
        ticket_ids = self.env["parent.ticket"].search([("id", "=", self.parent_ticket_id.id)], limit=1).id
        print(ticket_ids)
        ctx = {
            'default_model': 'parent.ticket',
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

    @api.onchange('next_task_ids')
    def _onchange_next_task_ids(self):
        task_ids = []
        for each in self.next_task_ids:
            task_ids.append(each._origin.id)
        self.parent_ticket_id._origin.next_task_ids = task_ids

    sequence = fields.Integer(string="Sequence", compute='_sequence_generation', readonly=False)

    @api.depends('workflow_id', 'parent_ticket_id', 'child_ticket_id')
    def _sequence_generation(self):
        no = 0
        self.sequence = no
        if self.parent_ticket_id or self.child_ticket_id:
            for line in self.parent_ticket_id.task_list_ids or self.child_ticket_id.task_list_ids:
                no += 1
                line.sequence = no

    # geo locaion
    def geo_location_redirect(self):
        if self.add_longitude and self.add_latitude:
            url = 'http://maps.google.com?q=%s,%s' % (self.add_latitude, self.add_longitude)
            if url:
                return {
                    'type': 'ir.actions.act_url',
                    'name': "Google map",
                    'target': 'new',
                    'url': url,
                }
        else:
            raise UserError(_("There is no longitude and latitude values"))


class MultiApproval(models.Model):
    _inherit = 'multi.approval'

    parent_ticket_id = fields.Many2one('parent.ticket', string='Parent Ticket')
    parent_task_line_id = fields.Many2one('tasks.master.line', string="Parent's Task Line",
                                          help="while delete thet task and if has end task, it needs an approval so this will be the refernece field, once approved then the line will be deleted automatically.")

    def create(self, vals):
        res = super().create(vals)
        template_id = self.env.ref('ppts_parent_ticket.approve_template_parent_ticket')
        rec = res.type_id.line_ids[0].user_id
        if template_id and rec:
            template_id.with_context(email_to=rec.partner_id.email, name=rec.partner_id.name).sudo().send_mail(res.id,
                                                                                                               force_send=True)
        return res

    def action_approve(self):
        values = super().action_approve()
        parent_ticket = self.env['parent.ticket'].sudo().browse(self.parent_ticket_id.id)
        if self.parent_ticket_id.id and self.parent_task_line_id:
            if self.state == 'Approved':
                self.parent_task_line_id.sudo().unlink()
                values = {
                    'res_id': self.parent_ticket_id.id,
                    'model': 'parent.ticket',
                    'body': 'As per the request the status has been deleted.',
                    'author_id': self.env.user.partner_id.id
                }
                self.env['mail.message'].create(values)
                self.parent_ticket_id.sudo().message_post(body='As per the request the status has been deleted.')
        elif self.parent_ticket_id.id:
            if self.state != 'Approved':
                pass
            elif self.parent_ticket_id.is_repair_warranty_approval_required and self.parent_ticket_id.is_warranty_approval_required and not self.parent_ticket_id.is_warranty_approval_done:
                approvals = self.env['multi.approval'].search([('parent_ticket_id', '=', parent_ticket.id)])
                if all(x.state == 'Approved' for x in approvals):
                    parent_ticket.sudo().write({'state': 'confirm', 'is_warranty_approval_done': True})
            elif self.parent_ticket_id.is_warranty_approval_required and not self.parent_ticket_id.is_warranty_approval_done and self.state == 'Approved':
                parent_ticket.sudo().write({'state': 'confirm', 'is_warranty_approval_done': True})
            elif self.parent_ticket_id.is_repair_warranty_approval_required and not self.parent_ticket_id.is_warranty_approval_done and self.state == 'Approved':
                parent_ticket.sudo().write({'state': 'confirm', 'is_warranty_approval_done': True})
            else:
                parent_ticket.sudo().write({'state': 'approved'})
        return values


class ReasonReason(models.TransientModel):
    _inherit = 'reason.reason'
    _description = 'Reason'

    def action_confirm(self):

        res = super(ReasonReason, self).action_confirm()
        if self.env.context.get('active_model') == 'parent.ticket':
            parent_ticket_id = self.env['parent.ticket'].browse(self.env.context.get('active_id'))
            if self.reason_type == 'close':
                parent_ticket_id.state = 'closed'
                parent_ticket_id.close_reason = self.name
                parent_ticket_id.close_date = fields.Datetime.today()
        return True
