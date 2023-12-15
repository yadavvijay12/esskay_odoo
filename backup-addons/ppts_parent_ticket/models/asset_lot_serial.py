from odoo import models, fields, api, _

class AssetlotSerial(models.Model):
    _inherit = 'asset.lot.serial'

    parent_ticket_id = fields.Many2one('parent.ticket', string='PT Ref Name')
    child_ticket_id = fields.Many2one('child.ticket', string='CT Ref Name')
