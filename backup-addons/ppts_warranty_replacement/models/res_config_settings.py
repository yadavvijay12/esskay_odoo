from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    replacement_order_journal_id = fields.Many2one('account.journal', string='Default Journal', related='company_id.replacement_order_journal_id', readonly=False)