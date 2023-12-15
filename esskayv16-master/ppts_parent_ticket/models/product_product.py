# -*- coding: utf-8 -*-
#############################################################################
#
#    Point Perfect Technology Solutions.
#
#############################################################################
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    parent_ticket_properties_definition = fields.PropertiesDefinition('Parent Ticket Properties')
    child_ticket_properties_definition = fields.PropertiesDefinition('Child Ticket Properties')


class StockLot(models.Model):
    _inherit = "stock.lot"

    historical_data_line = fields.One2many(comodel_name='assets.historical.data', inverse_name='ref_id',
                                           string="Asset Historical Data", copy=True, auto_join=True)

    # Asset -> Warranty View Tickets
    def view_warranty_tickets(self):
        context = self._context.copy()
        return {
            'name': "View Tickets",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'view.warranty.tickets',
            'target': 'new',
            'context': self._context,
        }

    # Asset -> Extend Warranty View Tickets
    def view_extend_warranty_tickets(self):
        context = self._context.copy()
        return {
            'name': "View Tickets",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'view.warranty.tickets',
            'target': 'new',
            'context': self._context,
        }

    # Asset -> Repair Warranty View Tickets
    def view_repair_warranty_tickets(self):
        context = self._context.copy()
        return {
            'name': "View Tickets",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'view.warranty.tickets',
            'target': 'new',
            'context': self._context,
        }


class AssetWarranty(models.Model):
    _inherit = "asset.warranty"

    child_tickets_ids = fields.Many2many('child.ticket', string="Child Tickets", compute="_compute_date_based_tickets")

    @api.depends("warranty_start_date", "warranty_end_date")
    def _compute_date_based_tickets(self):
        for rec in self:
            child_ids = self.env['child.ticket'].search([('warranty_start_dates', '>=', rec.warranty_start_date),
                                                         ('warranty_end_dates', '<=', rec.warranty_end_date),
                                                         ('stock_lot_id', '=', rec.stock_lot_ref_id.id)])
            if child_ids:
                rec.child_tickets_ids = child_ids.ids
            else:
                rec.child_tickets_ids = False
