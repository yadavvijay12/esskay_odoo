# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    rma_count = fields.Integer('RMA Claims', compute='_compute_rma_count')

    def _compute_rma_count(self):
        """
        This method used to RMA count. It will display on the sale order screen.
        """
        for order in self:
            order.rma_count = self.env['crm.claim.ppts'].search_count \
                ([('picking_id.sale_id', '=', order.id)])

    def action_view_rma(self):
        """
        This action used to redirect from sale orders to RMA.
        """
        rma = self.env['crm.claim.ppts'].search([('picking_id.sale_id', '=', self.id)])
        if len(rma) == 1:
            claim_action = {
                'name':"RMA",
                'view_mode':'form',
                'res_model':'crm.claim.ppts',
                'type':'ir.actions.act_window',
                'res_id':rma.id,
            }
        else:
            claim_action = {
                'name':"RMA",
                'view_mode':'tree,form',
                'res_model':'crm.claim.ppts',
                'type':'ir.actions.act_window',
                'domain':[('id', 'in', rma.ids)]
            }
        return claim_action
