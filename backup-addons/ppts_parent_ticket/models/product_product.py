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
