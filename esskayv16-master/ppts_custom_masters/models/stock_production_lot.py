from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from random import randint
from lxml import etree

from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import datetime


class AssetProperty(models.Model):
    _inherit = 'product.product'

    stock_lot_properties_definition = fields.PropertiesDefinition('Product Properties')


class StockLot(models.Model):
    _inherit = "stock.lot"

    def _get_asset_location(self):
        location = self.env['stock.location'].search(
            [('usage', '=', 'customer'), ('company_id', '=', self.company_id.id)], limit=1)
        if not location:
            raise UserError(_('Can\'t find any Customer location.'))
        return location

    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    customer_account = fields.Many2one('res.partner', string="Customer Account", required=True)
    external_id = fields.Char(string="External ID")
    # product_serial_number = fields.Char(string="Product Serial Number", required=True)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    product_price = fields.Monetary("Product Price", currency_field='currency_id')
    product_eol = fields.Date("Product End of Life")
    product_eosl = fields.Date("Product End of Service Life")
    active = fields.Boolean("Active", default=True)

    # General Information
    custom_sale_order = fields.Many2one("sale.order", string="Sale Order")
    custom_sale_order_date = fields.Date(string="SaleOrder/PO Date")
    contract_flow_id = fields.Many2one("sale.order", string="Contract Flow")
    contract_id = fields.Many2one("contract.contract", string="Contract Flow")
    asset_tag_ids = fields.Many2many('asset.tag', string="Asset Tag")
    asset_id_label = fields.Integer(string="Asset ID")
    service_support_commitment = fields.Char(string="Service Support Commitment")
    replacement_for = fields.Char(string="Replacement for")
    asset_category_id = fields.Many2one("product.category", string="Asset Category", required=True, help='Category')
    asset_type_id = fields.Many2one("asset.type", string="Asset Type", required=True)
    product_part_no = fields.Char(string="Product part No", related='product_id.product_part')
    product_types_id = fields.Many2one("product.types", string="Product Type")
    asset_id_allias = fields.Char(string="Asset ID Allias")
    invoice_number = fields.Char(string="Invoice Number")
    warranty_start_date = fields.Date(string="Warranty Start Date")
    warranty_end_date = fields.Date(string="Warranty End Date")
    extended_warranty_start_date = fields.Date(string="Extended Warranty Start Date")
    extended_warranty_end_date = fields.Date(string="Extended Warranty End Date")
    repair_warranty_start_date = fields.Date(string="Repair Warranty Start Date",
                                             help='Manual / Updated by system end of Ticket & Warranty certificate Generation')
    repair_warranty_end_date = fields.Date(string="Repair Warranty End Date",
                                           help='Manual / Updated by system end of Ticket & Warranty certificate Generation')
    oem_warranty_check = fields.Boolean("Warranty Check", compute='compute_warranty_check', default=False, copy=True)
    oem_repair_warranty_check = fields.Boolean("Repair Warranty Check", compute='compute_repair_warranty_check',
                                               default=False, copy=True)
    asset_arrival_date = fields.Date(string="Asset Arrival Date")
    installation_date = fields.Datetime(string="Installation Start Date")
    installation_end_date = fields.Datetime(string="Installation End Date")
    asset_location_id = fields.Many2one("stock.location", string="Asset Location", default=_get_asset_location)
    lattitude = fields.Float(string="Lattitude", digits=(10, 7))
    longitutde = fields.Float(string="Longtitude", digits=(10, 7))
    faulty_sticker = fields.Char(string="Fautly Sticker")
    rsp_name = fields.Many2one("res.partner", string="RSP Name")
    region_customer = fields.Many2one("customer.region", string="Region")
    unit_type_id = fields.Many2one("unit.type", string="Unit Type")
    industry_id = fields.Many2one("industry.stock", string="Industry")
    hardware_version = fields.Char(string="Software Version")
    software_version = fields.Char(string="Hardware Version")
    mc_skt = fields.Char(string="MC-SKT")
    # Loaner
    asset_loaner_ids = fields.Many2many('sale.order', string="Loaner")
    # service_ticket_ids = fields.Many2many('service.request', string="Tickets")
    all_ticket_ids = fields.One2many('asset.lot.serial', 'stock_lot_id', string="Tickets")
    # Properties
    stock_lot_properties = fields.Properties('Properties', definition='product_id.stock_lot_properties_definition',
                                             copy=True)
    # Others
    state = fields.Selection(
        [('state_active', 'Active'), ('state_inactive', 'Inactive'), ('state_not_traceable', 'Not Traceable'),
         ('state_not_repairable', 'Not Repairable')], string='Status', default='state_active')
    note = fields.Html("Remarks", copy=False)
    parent_ticket_count = fields.Integer(string="Parent Ticket", compute="compute_parent_ticket_count")
    service_request_count = fields.Integer(string="Service Request Count", compute="compute_service_count")
    is_lot = fields.Boolean('Lot',
                            help='This field is used to hide the name field based on the menu action to hide and show the field label since form is same for both menus.')
    asset_attachment_ids = fields.Many2many(comodel_name="ir.attachment", relation='lot_ir_attachments_rel',
                                            string="Attachments")
    is_transfer_done = fields.Boolean(string="Transfer Done")
    custom_asset_warranty_line = fields.One2many('asset.warranty', 'stock_lot_ref_id', string="Asset Warranty")
    invoice_date = fields.Date(string="Invoice Date")
    order_number = fields.Char(string="Order Number")
    company_id = fields.Many2one('res.company', 'Company', required=True, store=True, index=True,
                                 default=lambda self: self.env.company)

    @api.constrains("warranty_start_date", "warranty_end_date")
    def _check_warranty_start_end_dates(self):
        # If warranty state date value is False, Raise Validation Error.
        if self.warranty_end_date and not self.warranty_start_date:
            raise ValidationError(_("Warranty start date is not available"))
        # If warranty end date value is False, Raise Validation Error.
        if self.warranty_start_date and not self.warranty_end_date:
            raise ValidationError(_("Warranty end date is not available"))
        # Warranty start date later than end date, Raise Validation Error.
        if self.warranty_start_date and self.warranty_end_date:
            if self.warranty_start_date > self.warranty_end_date:
                raise ValidationError(_("Warranty Start Date Can't be Later than End Date"))

    @api.constrains('extended_warranty_start_date')
    def extended_warranty_start_date_check(self):
        # If Not Assign warranty Start Date And End Date, Raise Validation Error.
        if self.extended_warranty_start_date:
            if not self.warranty_start_date:
                raise UserError(
                    "Kindly Enter Warranty Start Date and End Date Before Entering Warranty Start Date and End Date")

    @api.onchange('name')
    def _onchange_serial_number_check(self):
        serial = self.env['service.request'].search(
            [('custom_product_serial', '=', self.name)], limit=1)
        if serial:
            self.invoice_number = serial.invoice_number
            self.order_number = serial.order_number

    @api.model
    def create(self, vals):
        rec = super(StockLot, self).create(vals)
        # rec.update_stock_quant()
        rec.update_transfer()
        return rec

    def update_transfer(self):
        for lines in self:
            if lines.env.context.get('is_pt') == True:
                out_picking = self.env['stock.picking.type'].search(
                    [('code', '=', 'outgoing'), ('company_id', '=', lines.company_id.id)], limit=1)
                move_lines = []
                move_vals = {}
                move_vals.update({
                    'product_id': lines.product_id.id,
                    'product_uom_qty': 1,
                    'product_uom': lines.product_uom_id.id,
                    'name': lines.product_id.default_code or lines.product_id.name,
                    'location_id': out_picking.default_location_src_id.id,
                    'location_dest_id': lines.asset_location_id.id,
                    'lot_ids': [(4, lines.id)],
                })
                move_lines.append((0, 0, move_vals))
                values = {
                    'location_id': out_picking.default_location_src_id.id,
                    'location_dest_id': lines.asset_location_id.id,
                    'picking_type_id': out_picking.id,
                    'move_type': 'one',
                    'move_ids': move_lines,
                    'origin': lines.name,
                    'partner_id': lines.customer_id.id,
                }
                if move_lines:
                    stock_id = self.env['stock.picking'].create(values)
                    stock_id.action_confirm()
                    stock_id.button_validate()
                    lines.is_transfer_done = True

    def update_stock_quant(self):
        self.env['stock.quant'].create({
            'location_id': self.asset_location_id.id,
            'product_id': self.product_id.id,
            'quantity': 1,
            'inventory_quantity': 1,
            'lot_id': self.id
        }).action_apply_inventory()

    # _sql_constraints = [
    #     ('external_id_unique', 'unique (external_id)', "External ID already exists !"),
    #     ('product_id_product_serial_unique', 'unique (product_id,product_serial_number)', "Product and same serial number already exists!"),
    # ]

    # def create_sale_order(self):
    #     vals = {
    #         'default_partner_id': self.customer_id.id,
    #         'default_order_line': [0, 0, {
    #             'product_template_id': self.product_id.product_tmpl_id.id,
    #             'name': self.product_id.name,
    #             'product_uom_qty': 1,
    #             'product_uom': self.product_id.uom_id.id,
    #             'price_unit': self.product_id.lst_price,
    #             'customer_lead': 0.0,
    #         }]
    #     }
    #     return {
    #         'name': _('Sale Order'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'sale.order',
    #         'views': [(self.env.ref('sale.view_order_form').id, 'form')],
    #         'context': vals
    #     }

    def create_sale_order(self):
        context = self.env['sale.order'].create({
            'partner_id': self.customer_id.id,
        })
        return {
            'name': "sale order",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'context': {'default_partner_id': self.customer_id.id,
                        },
        }

    def action_internal_transfer(self):
        transit_location = self.env['stock.location'].search(
            [('usage', '=', 'inventory'), ('company_id', '=', self.company_id.id)], limit=1)
        picking_types = self.env['stock.picking.type'].search(
            [('code', '=', 'internal'), ('company_id', '=', self.company_id.id)], limit=1)
        for lines in self:
            move_lines = []
            move_vals = {}
            move_vals.update({
                'product_id': lines.product_id.id,
                'product_uom_qty': 1,
                'product_uom': lines.product_uom_id.id,
                'name': lines.product_id.default_code or lines.product_id.name,
                'location_id': transit_location.id,
                'location_dest_id': lines.asset_location_id.id,
                'lot_ids': [(4, lines.id)],
            })
            move_lines.append((0, 0, move_vals))
            values = {
                'location_id': transit_location.id,
                'location_dest_id': lines.asset_location_id.id,
                'picking_type_id': picking_types.id,
                'move_type': 'one',
                'move_ids': move_lines,
                # 'move_line_ids': move_lines,
                'origin': lines.name,
            }
            if move_lines:
                stock_id = self.env['stock.picking'].create(values)
                stock_id.action_confirm()
                stock_id.button_validate()
                lines.is_transfer_done = True

    def action_view_internal_transfer(self):
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

    def create_ticket(self):
        return True

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_price = self.product_id.lst_price
            self.product_eol = self.product_id.product_eol
            self.product_eosl = self.product_id.product_eosl
            self.product_types_id = self.product_id.product_types_id.id or False
            self.asset_category_id = self.product_id.categ_id.id or False
            if self.product_id.tracking == 'lot':
                self.is_lot = True

    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        if self.customer_id:
            self.customer_account = self.customer_id.customer_account_id.id
            self.region_customer = self.customer_id.customer_region.id
            self.lattitude = self.customer_id.partner_latitude
            self.longitutde = self.customer_id.partner_longitude

    @api.depends('warranty_start_date', 'warranty_end_date')
    def compute_warranty_check(self):
        for record in self:
            if record.warranty_start_date and record.warranty_end_date:
                record.oem_warranty_check = True
            else:
                record.oem_warranty_check = False

    @api.depends('repair_warranty_start_date', 'repair_warranty_end_date')
    def compute_repair_warranty_check(self):
        for record in self:
            if record.repair_warranty_start_date and record.repair_warranty_end_date:
                record.oem_repair_warranty_check = True
            else:
                record.oem_repair_warranty_check = False

    # Main Buttons
    def state_active_button(self):
        self.state = 'state_active'
        self.active = True

    def state_inactive_button(self):
        self.state = 'state_inactive'
        self.active = False

    def state_not_traceable_button(self):
        self.state = 'state_not_traceable'

    def state_not_repairable_button(self):
        self.state = 'state_not_repairable'

        # Service Request

    def action_service_request(self):
        view_id = self.env.ref(
            'ppts_service_request.service_request_sr_installation_form_view', False)
        context = {
            "default_stock_production_lot_id": self.id,
            "default_partner_id": self.customer_id.id,
            "default_customer_name": self.customer_id.name,
            "default_product_name": self.product_id.name,
            "default_custom_product_serial": self.name,
            "default_product_category_id": self.product_id.categ_id.name,
            "default_customer_asset_ids": [(0, 0, {
                "stock_lot_id": self.id,
            })]
        }
        return {
            'name': _('Service Request'),
            'view_mode': 'form',
            'res_model': 'service.request',
            'view_id': view_id and view_id.id or False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            "context": context,
        }

    def action_view_service_request(self):
        self.ensure_one()
        tickets = []
        ticket_line_ids = self.env['customer.asset.line'].search(
            [('stock_lot_id', '=', self.id)])
        if ticket_line_ids:
            tickets = ticket_line_ids.mapped('ticket_id')
            return {
                'type': 'ir.actions.act_window',
                'name': 'Service Requests',
                'view_mode': 'tree,form',
                'res_model': 'service.request',
                'domain': [('id', 'in', tickets.ids)],
                'context': "{'create': True}"
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Service Requests',
                'view_mode': 'tree,form',
                'res_model': 'service.request',
                'domain': [('id', 'in', tickets)],
                'context': "{'create': True}"
            }

    # Service Request Count
    def compute_service_count(self):
        for record in self:
            tickets = []
            ticket_line_ids = self.env['customer.asset.line'].search(
                [('stock_lot_id', '=', record.id)])
            if ticket_line_ids:
                tickets = ticket_line_ids.mapped('ticket_id')
                record.service_request_count = self.env['service.request'].search_count([('id', 'in', tickets.ids)])
            else:
                record.service_request_count = 0

    # Parent Ticket
    def action_parent_ticket(self):
        context = {
            "default_stock_production_lot_id": self.id,
            "default_partner_id": self.customer_id.id,
            "default_product_id": self.product_id.name,
            "default_categ_id": self.product_id.categ_id.id,
            "default_stock_lot_id": self.name,
            # "default_product_id": self.product_id.id,
        }
        return {
            'name': _('Parent Ticket'),
            'view_mode': 'form',
            'res_model': 'parent.ticket',
            'type': 'ir.actions.act_window',
            'target': 'new',
            "context": context,
        }

    def action_view_parent_ticket(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Parent Ticket',
            'view_mode': 'tree,form',
            'res_model': 'parent.ticket',
            'domain': [('stock_lot_id', '=', self.id)],
            'context': "{'create': True}"
        }

    # Parent Ticket Count
    def compute_parent_ticket_count(self):
        for record in self:
            record.parent_ticket_count = self.env['parent.ticket'].search_count([('stock_lot_id', '=', record.id)])

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

    def action_view_reports(self):
        pass

    def action_view_invoices(self):
        pass

    def action_view_approvals(self):
        pass

    def action_view_purchases(self):
        pass


class AssetWarranty(models.Model):
    _name = 'asset.warranty'

    name = fields.Char(string='Name', tracking=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    is_active = fields.Boolean('Active', default=True)
    sale_order_id = fields.Many2one('sale.order', string="Sale Reference")
    warranty_start_date = fields.Datetime(string="Warranty Start Date")
    warranty_end_date = fields.Datetime(string="Warranty End Date")
    stock_lot_ref_id = fields.Many2one("stock.lot", string="Lot/Serial")
    warranty_type = fields.Selection(
        [("repair_warranty", "Repair Warranty"), ("extended_warranty", "Extended Warranty")], string="Warranty Type")

    def extended_warranty(self):
        today = datetime.now()
        for rec in self.env['asset.warranty'].search([('warranty_end_date', '<', today)]):
            rec.is_active = False

    def warranty_remainder(self):
        company_id = self.env.user.company_id
        today = datetime.today()
        asset_warranty = self.env['asset.warranty'].search([])
        dt = company_id.recurring_interval
        for rec in asset_warranty:
            if company_id.recurring_rule_type == 'daily':
                delta = rec.warranty_end_date - relativedelta(days=dt)
            elif company_id.recurring_rule_type == 'weekly':
                delta = rec.warranty_end_date - relativedelta(weeks=dt)
            elif company_id.recurring_rule_type == 'monthly':
                delta = rec.warranty_end_date - relativedelta(months=dt)
            elif company_id.recurring_rule_type == 'yearly':
                delta = rec.warranty_end_date - relativedelta(years=dt)
            if today == delta:
                template_id = self.env.ref('ppts_custom_masters.email_template_warranty_date')
                template_id.send_mail(rec.id, force_send=True)
        return asset_warranty


class AssetlotSerial(models.Model):
    _name = 'asset.lot.serial'

    service_request_id = fields.Many2one("service.request", string='SR Ref Name')
    ticket_type = fields.Selection([("sr", "Service Request"), ("pt", "Parent Ticket"), ("ct", "Child Ticket")],
                                   string='Ticket Type')
    problem_description = fields.Char(string='Description')
    stock_lot_id = fields.Many2one("stock.lot", string="Tickets")
    parent_ticket_id = fields.Many2one('parent.ticket', string='PT Ref Name')
    child_ticket_id = fields.Many2one('child.ticket', string='CT Ref Name')
    service_type_id = fields.Many2one('service.type', string="Service Type")
    service_category_id = fields.Many2one('service.category', string="Service Category", copy=False)
    ticket_create_date = fields.Datetime(string='Ticket Create Date')
    ct_user_id = fields.Many2one('res.users', string='CT User Name')
    engineer_id = fields.Many2one('res.users', string='Engineer Name')
    contract_details = fields.Many2many(comodel_name="contract.contract", string='Contract Details')
    status = fields.Char(string='Status')
