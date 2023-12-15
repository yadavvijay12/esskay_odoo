# Copyright 2016 Tecnativa - Carlos Dauden
# Copyright 2018 ACSONE SA/NV.
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    # We keep this field for migration purpose
    old_contract_id = fields.Many2one("contract.contract")

    def action_post(self):
        res = super().action_post()
        # Check for the warranty term type in product template, if the warranty is based on the invoice date then need to create new contract for this customer
        self.ensure_one()
        source_sale_order_id = self.line_ids.sale_line_ids.order_id
        for rec in source_sale_order_id.order_line.filtered(lambda p: p.product_id.product_tmpl_id.order_type in ('repair_warranty', 'extended_warranty')):
            asset_id = rec.asset_id
            warranty_term_days = int(rec.product_id.product_tmpl_id.term_type_id.number_days)
            new_extended_date = None
            # warranty_term_date =date(rec.return_date)
            if rec.product_id.product_tmpl_id.term_type_id.warranty_date_based == 'invoice_date':
                    new_extended_date = self.invoice_date + timedelta(days=warranty_term_days)
            if not new_extended_date:
                import datetime
                values = {
                    'custom_asset_warranty_line': [(0, 0, {
                        'sale_reference': rec.order_id.id,
                        'name': rec.order_id.name,
                        'warranty_start_date': datetime.datetime.now(),
                        'warranty_end_date': new_extended_date,
                        'warranty_type': rec.product_id.product_tmpl_id.order_type,
                    })]
                }
                asset_id.write(values)
            for sale_id in source_sale_order_id.order_line.filtered(lambda p: p.product_id.product_tmpl_id.order_type in ('amc_contract', 'cmc_contract')):
                contract = self.env['contract.contract'].search([('sale_id', '=', sale_id.id)], limit=1)
                interval = int(sale_id.product_id.product_tmpl_id.term_type_id.number_days)
                if rec.product_id.product_tmpl_id.term_type_id.interval_type == "daily":
                    interval_unit = relativedelta(days=interval)
                elif rec.product_id.product_tmpl_id.term_type_id.interval_type == "monthly":
                    interval_unit = relativedelta(months=interval)
                else:
                    interval_unit = relativedelta(years=interval)

                warranty_term_days = interval_unit
                new_extended_date = None
                if sale_id.product_id.product_tmpl_id.term_type_id.warranty_date_based == 'invoice_date':
                    new_extended_date = self.invoice_date + warranty_term_days
                    contract.date_end = new_extended_date

        return res

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    contract_line_id = fields.Many2one(
        "contract.line", string="Contract Line", index=True
    )
