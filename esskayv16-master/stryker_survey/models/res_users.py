
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError 

class ResPartner(models.Model):
    _inherit = 'res.users'

    survey_properties_definition = fields.PropertiesDefinition(string="Survey Properties", copy=True)

