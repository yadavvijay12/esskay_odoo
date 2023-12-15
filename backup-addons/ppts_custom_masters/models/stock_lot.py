from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from random import randint

class AssetProperty(models.Model):
    _inherit = 'product.product'

    asset_properties_definition = fields.PropertiesDefinition('Product Properties')


class AssetModel(models.Model):
    _name = "asset.model"
    _rec_name = "product_serial_number"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Asset Table"

    asset_model = fields.Char(string="Asset Model", required=True)
    name = fields.Char(string="Code")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('asset.model'), help='Inherit / Manual selection/Remove')

    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    rsp_name = fields.Many2one("res.partner", string="RSP Name")
    custom_sale_order = fields.Many2one("sale.order", string="Sale Order")
    contract_flow_id = fields.Many2one("contract.flow", string="Contract Flow")
    asset_type_id = fields.Many2one("asset.type", string="Asset Type", required=True)
    asset_location_id = fields.Many2one("stock.location", string="Asset Location")

    industry_id = fields.Many2one("industry.stock", string="Industry")
    unit_type_id = fields.Many2one("unit.type", string="Unit Type")
    product_id = fields.Many2one("product.product", string="Product", required=True)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    asset_category_id = fields.Many2one("asset.category", string="Asset Category", required=True, help='Category')
    product_types_id = fields.Many2one("product.types", string="Product Type")
    asset_tag_ids = fields.Many2many('asset.tag', string="Asset Tag")
    asset_attachment_ids = fields.Many2many(comodel_name="ir.attachment", relation='asset_ir_attachments_rel',string="Attachments")

    asset_loaner_ids = fields.Many2many('sale.order', string="Loaner")
    ticket_ids = fields.Many2many('service.request', string="Tickets")
    state = fields.Selection(
        [('state_active', 'Active'), ('state_inactive', 'Inactive'), ('state_not_traceable', 'Not Traceable'),
         ('state_not_repairable', 'Not Repairable')],
        string='Status', default='state_active')
    product_serial_number = fields.Char(string="Asset Serial Number", required=True)
    replacement_for = fields.Char(string="Replacement for")
    lattitude = fields.Char(string="Lattitude")
    longitutde = fields.Char(string="Longtitude")
    hardware_version = fields.Char(string="Software Version")
    software_version = fields.Char(string="Hardware Version")
    faulty_sticker = fields.Char(string="Faulty Sticker")
    mc_skt = fields.Char(string="MC-SKT")
    product_code_no = fields.Char(string="Product Code No.")
    product_part_no = fields.Char(string="Product part No.", help="CAT No.")
    asset_id_allias = fields.Char(string="Asset ID Allias")
    service_support_commitment = fields.Char(string="Service Support Commitment")
    invoice_number = fields.Char(string="Invoice Number")
    customer_account = fields.Many2one('res.partner', string="Customer Account")
    region_customer = fields.Char("Region")
    note = fields.Html("Remarks", copy=False)
    sale_count = fields.Integer(string="Sale Order Count", compute="compute_sale_orders")
    sale_quotation_count = fields.Integer(string="Sale Quotations Count")
    purchase_count = fields.Integer(string="Purchase Order Count", compute="compute_purchase_order_count")
    purchase_quotation_count = fields.Integer(string="Purchase Quotations Count")
    invoice_count = fields.Integer(string="Invoices Count", compute="compute_invoice_count")
    product_count = fields.Integer(string="Products", compute="compute_product_template")
    service_ticket_count = fields.Integer(string="Service Count", compute="compute_service_ticket_count")
    service_request_count = fields.Integer(string="Service request Count", compute="compute_service_request_count")
    asset_id_label = fields.Integer(string="Asset ID Label")
    warranty_start_date = fields.Date(string="Warranty Start Date")
    warranty_end_date = fields.Date(string="Warranty End Date")
    extended_warranty_start_date = fields.Date(string="Extended Warranty Start Date")
    extended_warranty_end_date = fields.Date(string="Extended Warranty End Date")
    repair_warranty_start_date = fields.Date(string="Repair Warranty Start Date", help='Manual / Updated by system end of Ticket & Warranty certificate Generation')
    repair_warranty_end_date = fields.Date(string="Repair Warranty End Date", help='Manual / Updated by system end of Ticket & Warranty certificate Generation')
    custom_sale_order_date = fields.Date(string="SaleOrder/PO Date")
    asset_arrival_date = fields.Date(string="Asset Arrival Date")
    installation_date = fields.Date(string="Installation Date")
    product_price = fields.Monetary("Product Price", currency_field='currency_id')
    product_eol = fields.Date("Product End of Life")
    product_eosl = fields.Date("Product End of Service Life")
    asset_eol = fields.Date("Asset End of Life")
    asset_properties = fields.Properties('Properties', definition='product_id.asset_properties_definition', copy=True)
    oem_warranty_check = fields.Boolean("Warranty Check", compute='compute_warranty_check', default=False, copy=True)
    oem_repair_warranty_check = fields.Boolean("Repair Warranty Check", compute='compute_repair_warranty_check', default=False, copy=True)
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ('product_id_product_serial_unique', 'unique (product_id,product_serial_number)', "Product and same serial number already exists!"),
    ]

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('asset_model_seq.sequence') or _('New')
        return super(AssetModel, self).create(vals)

    def create_ticket(self):
        return True

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_price = self.product_id.lst_price
            self.product_eol = self.product_id.product_tmpl_id.product_eol
            self.product_eosl = self.product_id.product_tmpl_id.product_eosl



            # sale_line = self.env['sale.order.line'].search([('product_id', '=', self.product_id.id)])
            # if sale_line:
            #     self.asset_loaner_ids.unlink()
            #     for sale in sale_line.mapped('order_id'):
            #         self.env['asset.loaner.line'].create({
            #             'sale_order_id': sale.id,
            #             'partner_id' : sale.partner_id.id,
            #             'assets_model_id' : self.id,
            #         })
    # Sale order count Smart button

    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        if self.customer_id:
            self.customer_account = self.customer_id.customer_account
            self.region_customer = self.customer_id.customer_region.name

    def compute_sale_orders(self):
        # loaner-tab
        for record in self:
            sale_count = 0
            sale_quotation_count = 0
            if record.product_id:
                sale_order_ids = None; loaner_ids = None; ticket_ids = None
                # Search for the loaner and display here
                loaner_ids = self.env['sale.order'].search([('partner_id', '=', record.customer_id.id),('is_rental_order', '=',True)])
                sale_order_ids = self.env['sale.order'].search(
                    [('partner_id', '=', record.customer_id.id),('state', '=', 'sale'), ('is_rental_order', '=', False)])
                sale_quotation_ids = self.env['sale.order'].search(
                    [('partner_id', '=', record.customer_id.id),('state', '=', 'draft'), ('is_rental_order', '=', False)])
                if loaner_ids:
                    record.asset_loaner_ids = [(6, 0, [record.id for record in loaner_ids])]
                ticket_ids = self.env['service.request'].search(
                    [('partner_id', '=', record.customer_id.id)])
                if ticket_ids:
                    record.ticket_ids = [(6, 0, [ticket.id for ticket in ticket_ids])]
                if sale_order_ids:
                    record.sale_count = len(sale_order_ids.ids)
                    record.asset_id_label = record.id
                else:
                    record.sale_count
                    record.asset_id_label = record.id
                if sale_quotation_ids:
                    record.sale_quotation_count = len(sale_quotation_ids.ids)
                    record.asset_id_label = record.id
                else:
                    record.sale_quotation_count
                    record.asset_id_label = record.id
            else:
                record.sale_count
                record.sale_quotation_count
                record.asset_id_label = record.id

    def action_view_sale_orders(self):
        sale_orders = []
        if self.product_id:
            sale_order_line_ids= self.env['sale.order.line'].search(['|',('order_id.partner_id', '=',self.customer_id.id),('product_id', '=', self.product_id.id),('order_id.state', '=', 'sale')])
            if sale_order_line_ids:
                sale_orders = sale_order_line_ids.mapped('order_id')
        return {
            'name': "Sale Order",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', sale_orders.ids)],
            'views': [[False, 'list'], [False, 'form']]
        }
    def action_view_sale_quotations(self):
        sale_quotations = []
        if self.product_id:
            sale_quotation_line_ids= self.env['sale.order.line'].search(['|',('order_id.partner_id', '=',self.customer_id.id),('product_id', '=', self.product_id.id),('order_id.state', '=', 'draft')])
            if sale_quotation_line_ids:
                sale_quotations = sale_quotation_line_ids.mapped('order_id')
        return {
            'name': "Sale Order",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', sale_quotations.ids)],
            'views': [[False, 'list'], [False, 'form']]
        }



    # Purchase order Count smart button

    def compute_purchase_order_count(self):
        for record in self:
            purchase_quotation_count = 0
            if record.product_id:
                purchase__order_line_ids = self.env['purchase.order.line'].search(
                    ['|', ('order_id.partner_id', '=', self.customer_id.id), ('product_id', '=', self.product_id.id),('order_id.state', '=', 'draft')])
                if purchase__order_line_ids:
                    purchase_quotation_count = len(purchase__order_line_ids.mapped('order_id'))
            record.purchase_quotation_count = purchase_quotation_count

    def action_view_purchase_quotations(self):
        purchase_quotations = []
        purchase_quotations_line_ids = self.env['purchase.order.line'].search(
            ['|', ('order_id.partner_id', '=', self.customer_id.id), ('product_id', '=', self.product_id.id),('order_id.state', '=', 'draft')])
        if purchase_quotations_line_ids:
            purchase_quotations = purchase_quotations_line_ids.mapped('order_id')
        return {
            'name': "Purchase Order",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('id', 'in', purchase_quotations.ids)],
            'views': [[False, 'list'], [False, 'form']]
        }

    def compute_purchase_order_count(self):
        for record in self:
            purchase_count = 0
            if record.product_id:
                purchase__order_line_ids = self.env['purchase.order.line'].search(
                    ['|', ('order_id.partner_id', '=', self.customer_id.id), ('product_id', '=', self.product_id.id),('order_id.state', '=', 'purchase')])
                if purchase__order_line_ids:
                    purchase_count = len(purchase__order_line_ids.mapped('order_id'))
            record.purchase_count = purchase_count

    def action_view_purchase_orders(self):
        purchase_orders = []
        purchase_order_line_ids = self.env['purchase.order.line'].search(
            ['|', ('order_id.partner_id', '=', self.customer_id.id), ('product_id', '=', self.product_id.id),('order_id.state', '=', 'purchase')])
        if purchase_order_line_ids:
            purchase_orders = purchase_order_line_ids.mapped('order_id')
        return {
            'name': "Purchase Order",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('id', 'in', purchase_orders.ids)],
            'views': [[False, 'list'], [False, 'form']]
        }

    # Invoice  Count smart button
    def compute_invoice_count(self):
        for record in self:
            invoice_count = 0
            if record.product_id:
                invoice_line = self.env['account.move.line'].search(['|',('partner_id', '=',record.customer_id.id),('product_id.name', '=', record.product_id.name)])
                if invoice_line:
                    invoice_count = len(invoice_line.mapped('move_id'))
            record.invoice_count = invoice_count

    def action_view_invoices(self):
        invoice_orders = []
        for record in self:
            if record.product_id:
                invoice_line = self.env['account.move.line'].search(['|',('partner_id', '=',record.customer_id.id),('product_id.name', '=', record.product_id.name)])
                if invoice_line:
                    invoice_orders = invoice_line.mapped('move_id')
        return {
            'name': "Invoice Order",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', invoice_orders.ids)],
            'views': [[False, 'list'], [False, 'form']]
        }

    # Service Ticket Count smart button
    def compute_service_request_count(self):
        for record in self:
            service_request_count = 0
            if record.product_serial_number:
                service_request_data = self.env['service.request'].search(
                    ['|', ('partner_id', '=', record.customer_id.id), ('custom_product_serial', '=', record.product_serial_number),('state', '=', 'new')])
                if service_request_data:
                    service_request_count = len(service_request_data)
            record.service_request_count = service_request_count

    def action_view_service_requests(self):
        service_request_data = self.env['service.request'].search(
            ['|', ('partner_id', '=', self.customer_id.id), ('custom_product_serial', '=', self.product_serial_number),('state', '=', 'new')])
        return {
            'name': "Service ticket",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'service.request',
            'domain': [('id', 'in', service_request_data.ids)],
            'views': [[False, 'list'], [False, 'form']]
        }

    def compute_service_ticket_count(self):
        for record in self:
            service_ticket_count = 0
            if record.name:
                service_request_data = self.env['service.request'].search(['|',('partner_id', '=',record.customer_id.id), ('custom_product_serial', '=', self.name),('state', '=', 'converted_to_ticket')])
                if service_request_data:
                    service_ticket_count = len(service_request_data)
            record.service_ticket_count = service_ticket_count

    def compute_product_template(self):
        for record in self:
            product_count = 0
            if record.name:
                product_data = self.env['product.product'].search(['|',('product_tmpl_id', '=',record.product_id.id),('custom_product_serial', '=', self.name),('state', '=', 'converted_to_ticket')])
                if product_data:
                    product_count = len(product_data)
            record.product_count = product_count

    def action_view_service_tickets(self):
        service_request_data = self.env['service.request'].search(['|',('partner_id', '=',self.customer_id.id), ('custom_product_serial', '=', self.name),('state', '=', 'converted_to_ticket')])
        return {
            'name': "Service ticket",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'service.request',
            'domain': [('id', 'in', service_request_data.ids)],
            'views': [[False, 'list'], [False, 'form']]
        }
    def action_view_product_template(self):
        product_template_data = self.env['product.product'].search(['|',('product_tmpl_id', '=',self.product_id.id), ('custom_product_serial', '=', self.name),('state', '=', 'converted_to_ticket')])
        return {
            'name': "Products",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'product.template',
            'domain': [('id', 'in', product_template_data.ids)],
            'views': [[False, 'list'], [False, 'form']]
        }


    def create_sr_ticket(self):
        self.ensure_one()
        return {
            'name': 'Serice Tickets',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'service.request',
            'res_id': self.id,
        }

    # Main Buttons
    def state_active_button(self):
        self.state= 'state_active'
        self.active = True

    def state_inactive_button(self):
        self.state = 'state_inactive'
        self.active = False

    def state_not_traceable_button(self):
        self.state = 'state_not_traceable'

    def state_not_repairable_button(self):
        self.state = 'state_not_repairable'
    
    @api.depends('warranty_start_date','warranty_end_date')
    def compute_warranty_check(self):
        for record in self:
            if record.warranty_start_date and record.warranty_end_date:
                record.oem_warranty_check = True
            else:
                record.oem_warranty_check = False
    
    @api.depends('repair_warranty_start_date','repair_warranty_end_date')
    def compute_repair_warranty_check(self):
        for record in self:
            if record.repair_warranty_start_date and record.repair_warranty_end_date:
                record.oem_repair_warranty_check = True
            else:
                record.oem_repair_warranty_check = False

class ContractFlow(models.Model):
    _name = "contract.flow"
    _rec_name = "contract_flow"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    contract_flow = fields.Char(string="Contract Flow", required=True)
    name = fields.Char(string="Code")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('contract.flow'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('contract.sequence') or _('New')
        return super(ContractFlow, self).create(vals)


class AssetType(models.Model):
    _name = "asset.type"
    _rec_name = "asset_type"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    asset_type = fields.Char(string="Asset Type", required=True)
    name = fields.Char(string="Code")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('asset.type'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('asset.sequence.type') or _('New')
        return super(AssetType, self).create(vals)


# class RegionStock(models.Model):
#     _name = "region.stock"
#     _rec_name = "name"
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _description = "This table is created for Region"
#
#     region_stock = fields.Char(string="Region", required=True)
#     name = fields.Char(string="Code")
#     company_id = fields.Many2one('res.company', 'Company',
#                                  default=lambda self: self.env['res.company']._company_default_get('region.stock'))
#
#     @api.model
#     def create(self, vals):
#         vals['name'] = self.env['ir.sequence'].next_by_code('region.sequence') or _('New')
#         return super(RegionStock, self).create(vals)


class IndustryStock(models.Model):
    _name = "industry.stock"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "This table is created for Industry"

    industry_stock = fields.Char(string="Industry", required=True)
    name = fields.Char(string="Code")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('industry.stock'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('industry.sequence') or _('New')
        return super(IndustryStock, self).create(vals)


class UnitType(models.Model):
    _name = "unit.type"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "This table is created for Unit Type"

    unit_type = fields.Char(string="Unit Type", required=True)
    name = fields.Char(string="Code")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('unit.type'))

class AssetCategory(models.Model):
    _name = "asset.category"
    _rec_name = "asset_category"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "This table is created for Asset Category"

    asset_category = fields.Char(string="Asset Category", required=True)
    name = fields.Char(string="Code")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('asset.category'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('asset_category.sequence') or _('New')
        return super(AssetCategory, self).create(vals)

class AssetLoaner(models.Model):
    _name = 'asset.loaner.line'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True)
    partner_id = fields.Many2one("res.partner", string="Customer", required=True)
    assets_model_id = fields.Many2one("asset.model", string="Asset Model Ref")

class AssetTags(models.Model):
    _name = 'asset.tag'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Tag Name', translate=True)
    color = fields.Integer('Color', default=_get_default_color)






