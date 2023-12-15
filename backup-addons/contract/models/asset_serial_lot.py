from odoo import models, fields, api, _

class AssetlotSerial(models.Model):
    _inherit = 'asset.lot.serial'

    contract_details = fields.Many2many(comodel_name="contract.contract", string='Contract Details')