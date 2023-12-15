from odoo import models, fields, api
from datetime import datetime, timedelta, date


class StockMove(models.Model):
    _inherit = "stock.move"

    spare_request_line_id = fields.Many2one('spare.request.lines', string="Spare Request")
    is_hide_mr = fields.Boolean(string="Material")

    def write(self, vals):
        res = super(StockMove, self).write(vals)
        if vals.get('state') == 'done':
            for move in self:
                if move.product_uom_qty > 0.0 and not move.picking_id.is_return:
                    if move.spare_request_line_id:
                        if move.spare_request_line_id.product_uom_qty_issued >= 0.0:
                            move.spare_request_line_id.product_uom_qty_issued += move.product_uom_qty
        return res
