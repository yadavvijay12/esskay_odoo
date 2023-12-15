from odoo import models, fields, api, _
from datetime import datetime, date, timedelta


class WarrantyTerm(models.Model):
    _name = 'warranty.term'
    _inherit = 'mail.thread'

    name = fields.Char(string='Name', tracking=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean('Active', default=True, track_visibility=True)
    interval_type = fields.Selection([("daily", "Day(s)"), ("monthly", "Month(s)"), ("yearly", "Year(s)")],
                                     efault="daily", string="Interval Type",
                                     help="Specify Interval for warranty terms.", )
    number_days = fields.Integer(string="Interval", default=1, help="Interval every (Days/Week/Month/Year)")
    warranty_date_based = fields.Selection(
        [('installation_date', 'Installation Date'), ('invoice_date', 'Invoice Date')], string='Start date Based on ',
        default="installation_date", required=True)

    _sql_constraints = [
        ('name', 'UNIQUE(name)', 'This name and the number is already exists!')]


class ProductCustomcategory(models.Model):
    _inherit = 'product.category'

    product_properties_definition = fields.PropertiesDefinition('Product Properties')


class ProductCustomField(models.Model):
    _inherit = 'product.template'

    detailed_type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'), ('product', 'Storable Product')], string='Product Type', default='product',
        required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')
    modality_id = fields.Many2one('product.modality', string='Modality')
    customer_account_id = fields.Many2one('res.partner', string='Customer Account')
    manufacturer_id = fields.Many2one('product.manufacturer', string='Manufacturer')
    product_code = fields.Char(string="Product Code No.", help='Code/Part Code/Model No')
    product_part = fields.Char(string="Product Part No.", help='Part No / MLFB No / Item No / Cat No')
    service_price = fields.Float(string="Service price")
    external_reference = fields.Char(string="External Reference")
    # product_serial_number = fields.Char(string="Product Serial Number")
    custom_product_serial = fields.Char(string="Serial Number", copy=False)
    product_attachment_ids = fields.Many2many(comodel_name="ir.attachment", relation='product_ir_attachments_rel',
                                              string="Attachments")
    is_accessories = fields.Boolean(string="Accessories")
    accessories_ids = fields.Many2many("product.product", string="Accessory Products")
    product_types_id = fields.Many2one("product.types", string="Part Type", help='Part Type')
    product_properties = fields.Properties('Properties',
                                           definition='categ_id.product_properties_definition',
                                           copy=True)
    product_extra_description = fields.Html('Description')
    company_id = fields.Many2one(
        'res.company', 'Company', index=True, help='Inherit / Manual selection/Remove',
        default=lambda self: self.env.user.company_id)
    product_eol = fields.Date("Product End of Life")
    product_eosl = fields.Date("Product End of Service Support")
    service_support_commitment = fields.Char(string="Service Support Commitment")
    invoice_number = fields.Char(string="Invoice Number")
    state = fields.Selection(
        [('state_active', 'Active'), ('state_inactive', 'Inactive'), ('state_discontinued', 'Discontinued'),
         ('state_eop', 'End of PL'), ('state_eos', 'End of SS')],
        string='Status', default='state_active')
    invoice_policy = fields.Selection(
        [('order', 'Ordered quantities'),
         ('delivery', 'Delivered quantities')], string='Invoicing Policy',
        compute='_compute_invoice_policy', store=True, readonly=False, precompute=True,
        help='Ordered Quantity: Invoice quantities ordered by the customer.\n'
             'Delivered Quantity: Invoice quantities delivered to the customer.\n'
             'Storable products are physical items for which you manage the inventory level.\n'
             'Invoice after delivery, based on quantities delivered, not ordered.')
    parent_count = fields.Integer(compute='compute_parent_count')
    child_count = fields.Integer(compute='compute_child_count')
    service_count = fields.Integer(compute='compute_service_count')
    order_type = fields.Selection(
        [('amc_contract', 'AMC Contract'), ('cmc_contract', 'CMC Contract'), ('extended_warranty', 'Extended Warranty'),
         ('repair_warranty', 'Repair Warranty')],
        string='Contract Type')
    term_type_id = fields.Many2one('warranty.term', string='Contract/Warranty Term')
    # contract_product_ids = fields.Many2many('product.product', 'product_product_rel', string="Contract Products")
    contract_product_temp_ids = fields.Many2many(
        comodel_name='product.template',
        relation='product_optional_rel',
        column1='src_id',
        column2='dest_id',
        string="Contract Products",
        help="Contract Products are suggested")

    contract_product_categ_ids = fields.Many2many('product.category', string='Product Category')

    _sql_constraints = [
        ('product_code_unique', 'unique (product_code)', "Product Code No. already exists !"),
        ('product_part_unique', 'unique (product_part)', "Product Part No. already exists !"),
    ]

    def action_view_parent_ticket(self):
        self.ensure_one()
        parent_ticket_ids = self.env['parent.ticket'].search(
            [('product_id.product_tmpl_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Parent Ticket',
            'view_mode': 'tree,form',
            'res_model': 'parent.ticket',
            'domain': [('id', 'in', parent_ticket_ids.ids)],
            'context': "{'create': False}"
        }

    def action_view_child_ticket(self):
        self.ensure_one()
        child_ticket_ids = self.env['child.ticket'].search(
            [('product_id.product_tmpl_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Child Ticket',
            'view_mode': 'tree,form',
            'res_model': 'child.ticket',
            'domain': [('id', 'in', child_ticket_ids.ids)],
            'context': "{'create': False}"
        }

    def compute_parent_count(self):
        for record in self:
            record.parent_count = self.env['parent.ticket'].search_count(
                [('product_id.product_tmpl_id', '=', record.id)])

    def compute_child_count(self):
        for record in self:
            record.child_count = self.env['child.ticket'].search_count([('product_id.product_tmpl_id', '=', record.id)])

    def compute_service_count(self):
        self.ensure_one()
        for record in self:
            record.service_count = self.env['customer.asset.line'].search_count(
                [('product_id.product_tmpl_id.id', '=', record.id)])

    def write(self, vals):
        # If user change from past date to present of future date move to active state
        res = super(ProductCustomField, self).write(vals)
        future_date = vals.get('product_eol')
        if future_date:
            if str(date.today()) < str(future_date):
                self.state = 'state_active'
        return res

    def update_product_eol(self):
        # If the product end of life is past change to state_eop and if its future date,
        # written the cron to move to state_eop after changing to past date
        # If user change from past date to present of future date move to active state
        date_filter = self.search([('product_eol', '<', date.today())])
        date_filter.state = 'state_eop'

    # Main BUttons
    def state_active_button(self):
        self.state = 'state_active'
        self.active = True

    def state_inactive_button(self):
        self.state = 'state_inactive'
        self.active = False

    def state_discontinued_button(self):
        self.state = 'state_discontinued'

    def state_eop_button(self):
        self.state = 'state_eop'

    def state_eos_button(self):
        self.state = 'state_eos'

    def action_view_reports(self):
        pass

    def action_view_service_requests(self):
        view_id = self.env.ref("ppts_service_request.service_request_tree_view").id
        self.ensure_one()
        tickets = []
        sale_order_line_ids = self.env['customer.asset.line'].search(
            [('product_id.product_tmpl_id.id', '=', self.id)])
        tickets = sale_order_line_ids.mapped('ticket_id')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Requests',
            'view_mode': "tree",
            'views': [(view_id, "tree")],
            'res_model': 'service.request',
            'domain': [('id', 'in', tickets.ids)],
            'context': "{'create': False}"
        }

    # def action_view_sale_orders(self):
    #     sale_orders = []
    #     if self.product_id:
    #         sale_order_line_ids = self.env['sale.order.line'].search(
    #             ['|', ('order_id.partner_id', '=', self.customer_id.id), ('product_id', '=', self.product_id.id),
    #              ('order_id.state', '=', 'sale')])
    #         if sale_order_line_ids:
    #             sale_orders = sale_order_line_ids.mapped('order_id')
    #     return {
    #         'name': "Sale Order",
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'tree,form',
    #         'res_model': 'sale.order',
    #         'domain': [('id', 'in', sale_orders.ids)],
    #         'views': [[False, 'list'], [False, 'form']]
    #     }


class ProductModality(models.Model):
    _name = "product.modality"
    _rec_name = "modality"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    modality = fields.Char(string="Modality")
    name = fields.Char(string="Code")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('product.modality'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('modality.sequence') or _('New')
        return super(ProductModality, self).create(vals)


class ProductManufacturer(models.Model):
    _name = "product.manufacturer"
    _rec_name = "manufacturer"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    manufacturer = fields.Char(string="Manufacturer", tracking=True)
    name = fields.Char(string="Code")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'product.manufacturer'), tracking=True)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('product.manufacturer') or _('New')
        return super(ProductManufacturer, self).create(vals)


class ProductTypes(models.Model):
    _name = "product.types"
    _rec_name = "product_types"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "This table is created for Product Types"

    product_types = fields.Char(string="Part Type", required=True)
    name = fields.Char(string="Code")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('product.types'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('product_types.sequence') or _('New')
        return super(ProductTypes, self).create(vals)
