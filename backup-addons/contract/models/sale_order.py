from odoo import models, fields, api, _
import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError

class SaleQuotationCustom(models.Model):
    _inherit = "sale.order"

    is_has_contract = fields.Boolean(string='Has Contract product', compute='_search_contract_product')
    contract_count = fields.Integer(string='Contract Count', compute='_get_contract_count')
    quotation_with = fields.Selection([('order_line_price', 'Order Line Price'), ('global_price', 'Global Price')],
                                       string='Quotation With')
    customer_account_id = fields.Many2one('res.partner', string="Customer Account", related='partner_id.customer_account_id')
    assigned_ids = fields.Many2many('res.users', string="Assigned Users", copy=False)

    # This is the method to count the number of contract and to show for the smart button usage.
    def _get_contract_count(self):
        for record in self:
            record.contract_count = self.env['contract.contract'].search_count([('sale_id', '=', record.id)])

    # This is the method to check the contract products and to enable the boolean field to show the button to create contracts.
    @api.depends('order_line.product_id')
    def _search_contract_product(self):
        has_contract_line = False
        for order in self:
            for order_line in order.order_line:
                if order_line.service_product_id.order_type in ('amc_contract', 'cmc_contract'):
                    order.is_has_contract = True
                    has_contract_line = True
                    break
            if not has_contract_line:
                order.is_has_contract = False

    # If any line has contract product then need to show this button then client will create contract manually.
    def action_create_contract(self):
        contract = {
            'name': self.name,
            'partner_id': self.partner_id.id,
            'invoice_partner_id': self.partner_id.id,
            'sale_id': self.id,
            'contract_type': 'sale',
            'custom_contract_type': 'amc',
            'so_ref': self.name,
            'delivery_partner_id': self.partner_id.id,
            'contract_line_fixed_ids': [(0, 0, {
                "display_type": line.display_type,
                'sale_id': line.order_id.id,
                'name': line.name,
                "product_id": line.product_id.id,
                "quantity": line.product_uom_qty,
                "uom_id": line.product_uom.id,
                "price_unit": line.price_unit,
                "price_subtotal": line.price_subtotal,
                "service_product_id": line.service_product_id.id,
                "service_product_categ_id": line.service_product_categ_id.id,
                "stock_lot_id": line.asset_id.id,
            }) for line in self.order_line if line.warranty_select not in ('extended_warranty', 'repair_warranty')],
        }
        contract_id = self.env['contract.contract'].create(contract)

        return {
            'name': _('Contract'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'contract.contract',
            'views': [(self.env.ref('contract.contract_contract_customer_form_view').id, 'form')],
            'res_id': contract_id and contract_id.id,
            'target': 'current',
            'domain': [('sale_id', '=', self.id)],
            'context': "{'create': False}"
        }

    # Button to view contracts against to the sale order.
    def action_view_contract(self):
        contract_id = self.env['contract.contract'].search([('sale_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': _('Contract'),
            'view_mode': 'tree,form',
            'res_model': 'contract.contract',
            'domain': [('id', 'in', tuple(contract_id.ids))],
            'context': "{'create': False}"
        }

    def action_confirm(self):
        res = super().action_confirm()
        self.action_confirm_warranty()
        return res

    def action_confirm_warranty(self):
        for rec in self.order_line.filtered(
                lambda p: p.product_id.product_tmpl_id.order_type in ('repair_warranty', 'extended_warranty')):
            asset_id = rec.asset_id
            # Warranty End Date based on product template warranty terms
            interval = int(rec.product_id.product_tmpl_id.term_type_id.number_days)
            if rec.product_id.product_tmpl_id.term_type_id.interval_type == "daily":
                interval_unit = relativedelta(days=interval)
            elif rec.product_id.product_tmpl_id.term_type_id.interval_type == "monthly":
                interval_unit = relativedelta(months=interval)
            else:
                interval_unit = relativedelta(years=interval)

            warranty_term_days = interval_unit
            new_extended_date = None
            # warranty_term_date =date(rec.return_date)
            if rec.product_id.product_tmpl_id.term_type_id.warranty_date_based == 'installation_date':
                if not asset_id.warranty_end_date:
                    raise ValidationError(_('This Asset (%s) does not have warranty end date to calcualte for new warranty date. Please map the warranty end date or change the configuration.',rec.asset_id.name))
                else:
                    new_extended_date = asset_id.warranty_end_date + warranty_term_days
                    values = {
                            'sale_order_id': rec.order_id.id,
                            'name': rec.order_id.name,
                            'warranty_start_date': datetime.datetime.now(),
                            'warranty_end_date': new_extended_date,
                            'warranty_type': rec.product_id.product_tmpl_id.order_type,
                            'stock_lot_ref_id':asset_id.id,
                        }
                    self.env['asset.warranty'].create(values)
        return True

    def action_cancel(self):
        res =super().action_cancel()
        # While this sale order is cancelled then delete the warranty line from the assets
        for record in self.env['asset.warranty'].search([('sale_order_id', '=', self.id)]):
            record.unlink()
        # While cancel this so delete the contract and try to cancel this order
        for contract in self.env['contract.contract'].search([('sale_id', '=', self.id)]):
            if contract.state == 'started':
                raise ValidationError(_('Cancel this contract (%s) and try to cancel this sale order',contract.name))
            else:
                contract.unlink()
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    service_product_id = fields.Many2one("product.template", string="Service Product", domain="[('detailed_type','=','service')]")
    service_product_categ_id = fields.Many2one('product.category', string='Category')

    @api.onchange('service_product_id')
    def onchange_service_product_id_domain(self):
        if self.service_product_id:
            product_ids = self.service_product_id.contract_product_temp_ids.mapped('id')
            domain = [('id', 'in', product_ids), ('sale_ok', '=', True)]
            return {'domain': {'product_template_id': domain}}

    @api.onchange('service_product_id')
    def onchange_service_categ_id_domain(self):
        if self.service_product_id:
            category_ids = self.service_product_id.contract_product_categ_ids.mapped('id')
            domain = [('id', 'in', category_ids)]
            return {'domain': {'service_product_categ_id': domain}}

    @api.onchange('service_product_categ_id')
    def onchange_service_categ_product_domain(self):
        if self.service_product_categ_id:
            product_ids = self.env['product.template'].search([('categ_id', '=', self.service_product_categ_id.id)])
            domain = [('id', 'in', product_ids.ids), ('sale_ok', '=', True)]
            return {'domain': {'product_template_id': domain}}


class StockLot(models.Model):
    _inherit = "stock.lot"

    contract_id = fields.Many2one("contract.contract", string="Contract Flow")
