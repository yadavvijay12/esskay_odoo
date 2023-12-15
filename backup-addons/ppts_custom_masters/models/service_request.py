from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError


class ServiceRequest(models.Model):
    _inherit = 'service.request'

    customer_asset_ids = fields.One2many('customer.asset.line', 'ticket_id', string='Assets')
    customer_city_id = fields.Many2one("customer.city", string='City', copy=False)
    city_id = fields.Many2one("customer.city", string='City', copy=False)
    customer_type_id = fields.Many2one('customer.type', string="Customer Type", copy=False)
    customer_region_id = fields.Many2one('customer.region', string="Region", copy=False)
    gst_no = fields.Char(string="GST No.", copy=False)
    tier_tier_id = fields.Many2one('tier.tier', string="Tier", copy=False)
    hospital_name = fields.Char(string="Name of Hospital", copy=False)
    surgeon_name = fields.Char(string="Name of Surgeon", copy=False)
    customer_group_id = fields.Many2one('customer.group', string="Customer Group", copy=False)
    customer_id_alias = fields.Char(string="ID Alias", copy=False)
    d_number = fields.Char(string="D Number", copy=False)
    c_number = fields.Char(string="C Number", copy=False)
    customer_id = fields.Integer(string="Customer ID", copy=False)
    stock_production_lot_id = fields.Many2one("stock.lot", string='Stock Lot', copy=False)
    customer_account_id = fields.Many2one('res.partner', string="Customer Account",
                                          related='partner_id.customer_account_id')

    @api.onchange('customer_asset_ids')
    def onchange_partner_domain(self):
        domain = []
        lists = []

        for assets in self.customer_asset_ids.mapped('stock_lot_id'):
            if assets.customer_id.id not in lists and lists:
                raise UserError('Please Select Assets that selected customer owned or Assets with same customer')
            else:
                lists.append(assets.customer_id.id)
        if lists:
            domain = [('id', 'in', lists), ('is_block_partner', '!=', 'blocked')]
        else:
            domain = [('is_block_partner', '!=', 'blocked')]
        return {'domain': {'partner_id': domain}}

    @api.onchange('customer_asset_ids')
    def _onchange_line_stock_lot_id(self):
        for record in self.customer_asset_ids:
            record.product_id = record.stock_lot_id.product_id.id or False
            # record.installation_date = record.stock_lot_id.installation_date
            stock_lot_obj = self.env['stock.lot'].search([('name', '=', record.stock_lot_id.name)])
            # warranty
            warranty_check_false = stock_lot_obj.filtered(lambda x: x.oem_warranty_check == False)
            warranty_check_true = stock_lot_obj.filtered(lambda x: x.oem_warranty_check == True)
            # repair
            repair_check_false = stock_lot_obj.filtered(lambda x: x.oem_repair_warranty_check == False)
            repair_check_true = stock_lot_obj.filtered(lambda x: x.oem_repair_warranty_check == True)

            if record.stock_lot_id:
                if warranty_check_false:
                    record.ticket_id.oem_warranty_status = 'not_available'
                if repair_check_false:
                    record.ticket_id.oem_repair_status = 'not_available'
                if warranty_check_true:
                    oem_warranty = warranty_check_true.search(
                        [('name', '=', record.stock_lot_id.name), ('warranty_start_date', '<=', date.today()),
                         ('warranty_end_date', '>=', date.today())])
                    if oem_warranty:
                        record.ticket_id.oem_warranty_status = 'in_oem_warranty'
                    else:
                        record.ticket_id.oem_warranty_status = 'out_oem_warranty'
                if repair_check_true:
                    oem_repair = repair_check_true.search(
                        [('name', '=', record.stock_lot_id.name), ('repair_warranty_start_date', '<=', date.today()),
                         ('repair_warranty_end_date', '>=', date.today())])
                    if oem_repair:
                        record.ticket_id.oem_repair_status = 'in_repair_warranty'
                    else:
                        record.ticket_id.oem_repair_status = 'out_repair_warranty'
            else:
                record.ticket_id.oem_warranty_status = ''
                record.ticket_id.oem_repair_status = ''

    @api.onchange('partner_id')
    def _onchange_partner_inherit(self):
        if self.partner_id:
            self.c_number = self.partner_id.c_number or ''


class CustomerAssetLine(models.Model):
    _name = 'customer.asset.line'

    name = fields.Char(string='Customer Asset Line')
    ticket_id = fields.Many2one('service.request', string='Ticket')
    product_id = fields.Many2one('product.product', string="Product")
    serial_number_id = fields.Many2one('asset.model', string="Asset Lot/Serial Number")
    stock_lot_id = fields.Many2one('stock.lot', string="Asset Lot/Serial Number", required=True)
    notes = fields.Char('Notes')
    partner_id = fields.Many2one('res.partner', related='ticket_id.partner_id', string="Partner")
    is_available = fields.Boolean(string="Is Available")

    @api.onchange('stock_lot_id')
    def _onchange_stock_lot_id(self):
        if self.stock_lot_id:
            self.product_id = self.stock_lot_id.product_id.id
            self.stock_lot_id.custom_sale_order_date = self.ticket_id.customer_po_date
            self.stock_lot_id.order_number = self.ticket_id.order_number
            self.stock_lot_id.invoice_date = self.ticket_id.invoice_date
            self.stock_lot_id.invoice_number = self.ticket_id.invoice_number

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
