from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ResCompany(models.Model):
    _inherit = "res.company"

    auto_close_pt = fields.Boolean(string="PT Auto Close",
                                   help="Auto close parent ticket when all child tickets have closed !")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_default_customer_ac(self):
        company_id = self.env.company
        if company_id:
            partners = self.env['res.partner'].search(
                [('id', 'in', self.env.user.customer_account_ids.ids), ('company_id', '=', self.company_id.id)],
                limit=1)
        return partners or company_id.partner_id

    @api.onchange('customer_account_id')
    def _filter_customer_account(self):
        partners = self.env['res.partner'].search(
            [('id', 'in', self.env.user.customer_account_ids.ids), ('company_id', '=', self.company_id.id)])
        domain = [('id', 'in', partners.ids)]
        return {'domain': {'customer_account_id': domain}}

    company_id = fields.Many2one('res.company', string='Company')
    customer_type = fields.Many2one('customer.type', string=" Customer Type", tracking=True)
    is_customer_account_required = fields.Boolean(string="Customer Account Required?",
                                                  related='customer_type.is_customer_account_required')
    parent_customer_id = fields.Many2one('res.partner', string="Parent Customer", help='Business Unit Group')
    customer_account = fields.Char(string="Customer Account")
    customer_account_id = fields.Many2one('res.partner', string="Customer Account", default=_get_default_customer_ac)
    city_id = fields.Many2one('customer.city', string="City")
    branch_id = fields.Many2one('branch.branch', string="Branch", tracking=True)
    # After Esskay team testing, they told us to remove those three fields.File name: Test Results - From Esskay, line number31
    branch_actual_id = fields.Integer(string="Branch ID", related="branch_id.id", tracking=True)
    branch_id_alias = fields.Char(string="Branch ID Alias", related="branch_id.id_alias", tracking=True)
    customer_region = fields.Many2one('customer.region', string="Region", tracking=True, help='Work Location')
    target_group = fields.Many2one('target.group', string="Target Group", tracking=True)
    tier_tier = fields.Many2one('tier.tier', string="Tier", tracking=True)
    customer_group = fields.Many2one('customer.group', string="Customer Group", tracking=True)
    process_id = fields.Many2one('process.process', string="Process")
    role_id = fields.Many2one('role.role', string="Role Channel")
    base_type_id = fields.Many2one('base.base', string="Base Type")
    work_location_id = fields.Many2one('work.location', string="Work Location")
    industry_id = fields.Many2one('industry.industry', string="Process")
    spare_category_id = fields.Many2one('spare.category', string="Spare Category")
    customer_id_alias = fields.Char(string="ID Alias", tracking=True)
    reference = fields.Char(string="Reference", tracking=True)
    secondary_contact_number = fields.Char(string="Secondary Contact Number", tracking=True)
    gst_no = fields.Char(string="GST No.", tracking=True)
    hospital_name = fields.Char(string="Name of the Hospital", tracking=True)
    surgeon_name = fields.Char(string="Name of the Surgeon", tracking=True)
    description = fields.Char(string="Description", tracking=True)
    vendor_code = fields.Char(string="Vendor Code", tracking=True)
    c_number = fields.Char(string="C Number", tracking=True)
    d_number = fields.Char(string="D Number", tracking=True)
    customer_properties = fields.PropertiesDefinition(string="Customer Properties", copy=True)
    service_ticket_properties = fields.PropertiesDefinition(string="Service Ticket Properties", copy=True)
    properties = fields.Properties('Properties', definition='user_id.customer_properties', copy=True)
    fax_no = fields.Char(string="Fax No.")
    asset_line_ids = fields.Many2many('asset.model', string='Assets')
    customer_asset_line_ids = fields.Many2many('customer.asset.line', string='Assets')
    location_id = fields.Many2one('asset.location', string="Location", tracking=True)
    loaner_ids = fields.Many2many('sale.order', string="Loaner")
    ticket_ids = fields.Many2many('service.request', string="Service Requests")
    stock_lot_ids = fields.Many2many('stock.lot', string='Stock Lots')
    service_ticket_count = fields.Integer(string="Service Count", compute="compute_service_ticket_count")
    customer_attachments = fields.Many2many(comodel_name="ir.attachment", relation='customer_ir_attachments_rel',
                                            string="Attachments")
    type = fields.Selection(selection_add=[('branch', 'Branch')])
    dealer_distributer_ids = fields.One2many('customer.dealerinfo', 'partner_id', string='Dealer/Distributor')
    branc_ids = fields.Many2many('branch.branch', 'partner_id', string='Branch')
    is_block_partner = fields.Selection([('not_blocked', 'Un Block'), ('blocked', 'Block')], default="not_blocked",
                                        string='Block Partner')
    parent_count = fields.Integer(compute='compute_parent_count')
    child_count = fields.Integer(compute='compute_child_count')
    service_count = fields.Integer(compute='compute_service_count')
    customer_type_partner = fields.Selection(
        [('stryker', 'Stryker'), ('epson', 'Epson'), ('termo_fisher', 'Thermofisher'), ('rational', 'Rational')],
        string='Web Form')
    custom_company_type = fields.Selection(string='Company Type',
                                           selection=[('person', 'Individual'), ('company', 'Company'),
                                                      ('branch', 'Branch')], default='person')
    contact_branch_ids = fields.Many2many('res.partner', 'contact_branch_rel', string='Branches',
                                          compute='_compute_branch')
    is_customer_acc = fields.Boolean(string="Default Customer Account")
    ex_customer_type = fields.Selection(string='Create', selection=[('create_customer', 'Customer'),
                                                                    ('create_account', 'Customer Account')],
                                        required=True, default='create_customer')
    pan_number = fields.Char(string='Pan Number', size=10)

    @api.onchange('pan_number')
    def _onchange_pan_number(self):
        val = str(self.pan_number)
        self.pan_number = val.upper()

    @api.onchange('is_customer_acc')
    def _onchange_customer_account_line(self):
        partners = self.env['res.partner'].search_count([('is_customer_acc', '=', True)])
        if partners > 1:
            raise UserError('You Are Not Allowed To Add Multiple Default Customer')

    company_type = fields.Selection(string='Company Type',
                                    selection=[('person', 'Individual'), ('company', 'Company'), ('branch', 'Branch')],
                                    compute='_compute_company_type')
    is_branch = fields.Boolean('Branch', default=False)
    is_person = fields.Boolean('Person', default=False)

    stock_checking_process_ids = fields.One2many(
        comodel_name="stock.checking",
        inverse_name="stock_checking_ids",
        string="Stock Checking Process",
    )

    # @api.onchange('custom_company_type')
    # def onchange_company_type_domain(self):
    #     partners = self.env['res.partner'].search([('custom_company_type', '=', 'branch')])
    #     domain = [('id', 'in', partners.ids)]
    #     return {'domain': {'parent_customer_id': domain}}

    @api.onchange('stock_checking_process_ids')
    def onchange_stock_checking_process_ids(self):
        result = self.stock_checking_process_ids.filtered(lambda l: l.request_type == 'loaner')
        if len(result) > 1:
            raise UserError('You Are Not Allowed To Add Same Request Type Again')
        warranty = self.stock_checking_process_ids.filtered(lambda l: l.request_type == 'warranty_replacement')
        if len(warranty) > 1:
            raise UserError('You Are Not Allowed To Add Same Request Type Again')
        spare = self.stock_checking_process_ids.filtered(lambda l: l.request_type == 'spare_parts')
        if len(spare) > 1:
            raise UserError('You Are Not Allowed To Add Same Request Type Again')

    @api.depends('is_company', 'is_branch', 'is_person')
    def _compute_company_type(self):
        for partner in self:
            if partner.is_company:
                partner.company_type = 'company'
            elif partner.is_branch:
                partner.company_type = 'branch'
            else:
                partner.company_type = 'person'

    @api.onchange('company_type')
    def onchange_company_type(self):
        if self.company_type == 'company':
            self.is_company = True
            self.is_branch = False
            self.is_person = False
        elif self.company_type == 'branch':
            self.is_company = False
            self.is_branch = True
            self.is_person = False
        elif self.company_type == 'person':
            self.is_company = False
            self.is_branch = False
            self.is_person = True

    def _compute_branch(self):
        for record in self:
            contact_branch_ids = self.env['res.partner'].search(
                [('company_type', '=', 'branch'), ('parent_customer_id', '=', self.parent_customer_id.id)])
            if contact_branch_ids:
                record.contact_branch_ids = [(6, 0, [branch.id for branch in contact_branch_ids])]
            else:
                record.contact_branch_ids = None

    @api.onchange('city_id')
    def _onchange_city_id(self):
        if self.city_id:
            self.city = self.city_id.name

    def ticket_creation(self):
        if self.is_block_partner == 'not_blocked':
            return {
                'name': _('Parent Ticket'),
                'view_mode': 'form',
                'domain': [],
                'res_model': 'parent.ticket',
                'type': 'ir.actions.act_window',
                'context': {'default_partner_id': self.id, },
            }
        else:
            raise ValidationError(
                _('Can not create parent ticket since this customer is blocked. Un-Block to create parent ticket!'))

    def service_ticket_creation(self):
        if self.is_block_partner == 'not_blocked':
            return {
                'name': _('Service Ticket'),
                'view_mode': 'form',
                'domain': [],
                'res_model': 'service.request',
                'type': 'ir.actions.act_window',
                'context': {'default_customer_name': self.name, 'default_partner_id': self.id,
                            'default_street': self.street, 'default_phone': self.phone, 'default_mobile': self.mobile,
                            'default_email': self.email},
            }
        else:
            raise ValidationError(
                _('Can not create service ticket since this customer is blocked. Un-Block to create service ticket!'))

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            if 'active' in vals and vals.get('active'):
                for contact in self.search([('parent_id', '=', record.id), ('active', '=', False)]):
                    contact.active = True
            elif 'active' in vals and not vals.get('active'):
                for contact in self.search([('parent_id', '=', record.id)]):
                    contact.active = False
            else:
                if 'active' in vals and not vals.get('active'):
                    for contact in self.search([('parent_id', '=', record.id), ('active', '=', False)]):
                        contact.active = True
        return res

    def action_block_customer(self):
        for record in self:
            record.is_block_partner = 'blocked'
            # Block all the contacts of this customer
            for contact in self.search([('parent_id', '=', record.id)]):
                contact.is_block_partner = 'blocked'

    def action_unblock_customer(self):
        for record in self:
            record.is_block_partner = 'not_blocked'
            # Un-Block all the contacts of this customer
            for contact in self.search([('parent_id', '=', record.id)]):
                contact.is_block_partner = 'not_blocked'

    def action_view_service_tickets(self):
        service_tickets = []
        if self.name:
            service_request_data = self.env['service.request'].search([('custom_product_serial', '=', self.name)])
            if service_request_data:
                for ticket in service_request_data:
                    service_tickets.append(ticket.id)

        return {
            'name': "Service ticket",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'service.request',
            'domain': [('id', 'in', service_tickets)],
            'views': [[False, 'list'], [False, 'form']]
        }

    def _compute_sale_order_count(self):
        res = super()._compute_sale_order_count()
        for sale in self:
            # Search for the loaner and display here
            loaner_ids = self.env['sale.order'].search(
                [('partner_id', '=', sale.id), ('is_rental_order', '=', True)])
            if loaner_ids:
                sale.loaner_ids = [(6, 0, [record.id for record in loaner_ids])]
            ticket_ids = self.env['service.request'].search(
                [('partner_id', '=', sale.id)])
            if ticket_ids:
                sale.ticket_ids = [(6, 0, [ticket.id for ticket in ticket_ids])]
            asset_line_ids = self.env['stock.lot'].search([('customer_id', '=', sale.id)])
            if asset_line_ids:
                sale.stock_lot_ids = [(6, 0, [asset.id for asset in asset_line_ids])]
        return res

    def compute_service_ticket_count(self):
        for record in self:
            service_ticket_count = 0
            if record.name:
                service_request_data = self.env['service.request'].search([('custom_product_serial', '=', record.name)])
                if service_request_data:
                    service_ticket_count = len(service_request_data)
            record.service_ticket_count = service_ticket_count

    # Smart Button - Action view Parent Tickets
    def action_view_parent_tickets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Parent Ticket',
            'view_mode': 'tree,form',
            'res_model': 'parent.ticket',
            'domain': [('partner_id', '=', self.id)],
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
            'domain': [('partner_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def action_view_service_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Requests',
            'view_mode': 'tree,form',
            'res_model': 'service.request',
            'domain': [('partner_id', '=', self.id)],
            'context': "{'create': False}"
        }

    # Count
    def compute_parent_count(self):
        for record in self:
            record.parent_count = self.env['parent.ticket'].search_count([('partner_id', '=', record.id)])

    def compute_child_count(self):
        for record in self:
            record.child_count = self.env['child.ticket'].search_count([('partner_id', '=', record.id)])

    def compute_service_count(self):
        for record in self:
            record.service_count = self.env['service.request'].search_count([('partner_id', '=', record.id)])

    def action_view_reports(self):
        pass


class CustomerType(models.Model):
    _name = 'customer.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Char(string='Code', default='New')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean('Active', default=True, track_visibility=True)
    name = fields.Char(string="Name")
    is_customer_account_required = fields.Boolean(string="Customer Account Required?")

    _sql_constraints = [
        ('name', 'UNIQUE(name,company_id)', 'This name is already used!')]

    @api.model
    def create(self, vals):
        customer_type = self.env['customer.type'].search([('sequence', '!=', True)], limit=1,
                                                         order='sequence DESC')
        vals['sequence'] = self.env['ir.sequence'].next_by_code(
            'customer.type') or _("New")
        return super().create(vals)


class CustomerCity(models.Model):
    _name = 'customer.city'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Char(string='Code', default='New')
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean('Active', default=True, track_visibility=True)

    _sql_constraints = [
        ('name', 'UNIQUE(name)', 'This name is already used!')]

    @api.model
    def create(self, vals):
        customer_city = self.env['customer.city'].search([('sequence', '!=', False)], limit=1,
                                                         order='sequence DESC')
        vals['sequence'] = self.env['ir.sequence'].next_by_code(
            'customer.city') or _("New")
        return super().create(vals)


class BranchName(models.Model):
    _name = 'branch.branch'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Char(string='Code', default='New')
    name = fields.Char(string="Name", required=True)
    id_alias = fields.Char(string="ID Alias", required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean('Active', default=True, track_visibility=True)

    _sql_constraints = [
        ('name', 'UNIQUE(name)', 'This name is already used!')]

    @api.model
    def create(self, vals):
        branch = self.env['branch.branch'].search([('sequence', '!=', False)], limit=1,
                                                  order='sequence DESC')
        vals['sequence'] = self.env['ir.sequence'].next_by_code('branch.branch') or _("New")

        return super().create(vals)


class CustomerRegion(models.Model):
    _name = 'customer.region'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name', tracking=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    sequence = fields.Char(string='Code', default='New')
    active = fields.Boolean('Active', default=True, track_visibility=True)

    _sql_constraints = [
        ('name', 'UNIQUE(name)', 'This name is already used!')]

    @api.model
    def create(self, vals):
        region_master_ids = self.env['customer.region'].search([('sequence', '!=', False)], limit=1,
                                                               order='sequence DESC')
        vals['sequence'] = self.env['ir.sequence'].next_by_code(
            'customer.region') or _("New")
        return super().create(vals)


class TargetGroup(models.Model):
    _name = 'target.group'
    _description = 'Target Group'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name', tracking=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    sequence = fields.Char(string='Code', default='New')
    active = fields.Boolean('Active', default=True, track_visibility=True)
    _sql_constraints = [
        ('name', 'UNIQUE(name)', 'This name is already used!')]

    @api.model
    def create(self, vals):
        target_group = self.env['target.group'].search([('sequence', '!=', False)], limit=1,
                                                       order='sequence DESC')
        vals['sequence'] = self.env['ir.sequence'].next_by_code(
            'target.group') or _("New")
        return super().create(vals)


class TierMaster(models.Model):
    _name = 'tier.tier'
    _description = 'Tier'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name', tracking=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    sequence = fields.Char(string='Code', default='New')
    active = fields.Boolean('Active', default=True, track_visibility=True)
    _sql_constraints = [
        ('name', 'UNIQUE(name)', 'This name is already used!')]

    @api.model
    def create(self, vals):
        tier_tier = self.env['tier.tier'].search([('sequence', '!=', False)], limit=1,
                                                 order='sequence DESC')
        vals['sequence'] = self.env['ir.sequence'].next_by_code(
            'tier.tier') or _("New")
        return super().create(vals)


class CustomerGroup(models.Model):
    _name = 'customer.group'
    _description = 'Customer Group'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name', tracking=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    sequence = fields.Char(string='Code', default='New')
    active = fields.Boolean('Active', default=True, track_visibility=True)
    _sql_constraints = [
        ('name', 'UNIQUE(name)', 'This name is already used!')]

    @api.model
    def create(self, vals):
        customer_group = self.env['customer.group'].search([('sequence', '!=', False)], limit=1,
                                                           order='sequence DESC')
        vals['sequence'] = self.env['ir.sequence'].next_by_code(
            'customer.group') or _("New")
        return super().create(vals)


class AssetLocation(models.Model):
    _name = 'asset.location'
    _description = 'Customer Group'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', tracking=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    sequence = fields.Char(string='Code', default='New')
    user_id = fields.Many2one('res.users', string="partner")
    active = fields.Boolean('Active', default=True, track_visibility=True)
    street = fields.Char(required=True)
    street2 = fields.Char()
    zip = fields.Char(required=True)
    city_id = fields.Many2one('customer.city', required=True)
    state_id = fields.Many2one('res.country.state', domain="[('country_id', '=?', country_id)]", required=True)
    country_id = fields.Many2one('res.country', required=True)

    _sql_constraints = [
        ('name', 'UNIQUE(name)', 'This name is already used!')
    ]

    @api.model
    def create(self, vals):
        asset_location = self.env['asset.location'].search([('sequence', '!=', False)], limit=1,
                                                           order='sequence DESC')
        vals['sequence'] = self.env['ir.sequence'].next_by_code(
            'asset.location') or _("New")
        return super().create(vals)


class ProcessMaster(models.Model):
    _name = 'process.process'
    _description = 'Process Form'

    name = fields.Char(string='Name', tracking=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    sequence = fields.Char(string="Code", readonly=True, required=True, copy=False, default='New')
    active = fields.Boolean('Active', default=True, track_visibility=True)

    _sql_constraints = [
        ('name', 'UNIQUE(name)', 'This name is already used!')
    ]

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('process.process') or 'New'
        result = super(ProcessMaster, self).create(vals)
        return result


class RolesChannel(models.Model):
    _name = 'role.role'
    _description = 'Roles Channel Form'

    name = fields.Char(string='Name', tracking=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    sequence = fields.Char(string="Code", readonly=True, required=True, copy=False, default='New')
    active = fields.Boolean('Active', default=True, track_visibility=True)

    _sql_constraints = [
        ('name', 'UNIQUE(name)', 'This name is already used!')
    ]

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('role.role') or 'New'
        result = super(RolesChannel, self).create(vals)
        return result


class BaseType(models.Model):
    _name = 'base.base'
    _description = 'Base Form'

    name = fields.Char(string='Name', tracking=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    sequence = fields.Char(string="Code", readonly=True, required=True, copy=False, default='New')
    active = fields.Boolean('Active', default=True, track_visibility=True)

    _sql_constraints = [
        ('name', 'UNIQUE(name)', 'This name is already used!')
    ]

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('base.base') or 'New'
        result = super(BaseType, self).create(vals)
        return result


class IndustryMaster(models.Model):
    _name = 'industry.industry'
    _description = 'Industry Form'

    name = fields.Char(string='Name', tracking=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    sequence = fields.Char(string="Code", readonly=True, required=True, copy=False, default='New')
    active = fields.Boolean('Active', default=True, track_visibility=True)

    _sql_constraints = [
        ('name', 'UNIQUE(name)', 'This name is already used!')
    ]

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('industry.industry') or 'New'
        result = super(IndustryMaster, self).create(vals)
        return result


class WorkLocation(models.Model):
    _name = 'work.location'
    _description = 'Work Location'

    name = fields.Char(string='Name', tracking=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    sequence = fields.Char(string="Code", readonly=True, required=True, copy=False, default='New')
    active = fields.Boolean('Active', default=True, track_visibility=True)

    _sql_constraints = [
        ('name', 'UNIQUE(name)', 'This name is already used!')
    ]

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('work.location') or 'New'
        result = super(WorkLocation, self).create(vals)
        return result


class SpareCategory(models.Model):
    _name = 'spare.category'
    _description = 'Spare Category'

    name = fields.Char(string='Name', tracking=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    sequence = fields.Char(string="Code", readonly=True, required=True, copy=False, default='New')
    active = fields.Boolean('Active', default=True, track_visibility=True)

    _sql_constraints = [
        ('name', 'UNIQUE(name)', 'This name is already used!')
    ]

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('spare.category') or 'New'
        result = super(SpareCategory, self).create(vals)
        return result


class AssetLoaner(models.Model):
    _name = 'asset.loaner.line'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    partner_id = fields.Many2one("res.partner", string="Customer")
    # assets_model_id = fields.Many2one("asset.model", string="Asset Model Ref")


class AssetTickets(models.Model):
    _name = 'asset.ticket.line'

    product_id = fields.Many2one('product.product', string="Product")
    custom_ticket_id = fields.Many2one("service.request", string="Ticket")
    assets_ticket_id = fields.Many2one("asset.model", string="Asset Id")


class CustomerDealerinfo(models.Model):
    _name = 'customer.dealerinfo'

    partner_id = fields.Many2one('res.partner', string='Customer', ondelete='cascade')
    dealer_id = fields.Many2one('res.partner', string='Dealer Name')

    @api.onchange('dealer_id')
    def _onchange_dealer_id(self):
        dealer_ids = self.env['customer.type'].search([('company_id', '=', self.env.user.company_id.id), (
        'name', 'in', ('Dealer', 'dealer', 'Distributor', 'distributor'))])
        if dealer_ids:
            partner_ids = self.env['res.partner'].search([('customer_type', 'in', dealer_ids.ids)])
            if partner_ids:
                return {'domain': {'id': [('id', 'in', partner_ids.ids)]}}
            else:
                return {'domain': {'id': [('id', 'in', [])]}}


class StockChecking(models.Model):
    _name = 'stock.checking'

    stock_checking_ids = fields.Many2one('res.partner', string="Partner")
    request_type = fields.Selection(
        [('loaner', 'Loaner'), ('warranty_replacement', 'Warranty Replacement'), ('spare_parts', 'Spare Parts')],
        string='Approval Type')
    stock_request_type = fields.Selection(
        [('internal', 'Internal'), ('external', 'External')],
        string='Stock Request Type')
