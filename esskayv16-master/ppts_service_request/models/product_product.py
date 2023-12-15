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

    product_templ_properties = fields.Properties('Properties',
                                                 definition='product_tmpl_id.product_properties_definition', copy=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_properties_definition = fields.PropertiesDefinition('Service Request Properties')
    product_product_properties = fields.PropertiesDefinition('Service Request Properties')
