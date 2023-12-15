from odoo import SUPERUSER_ID, _, api, fields, models

class QualityAlert(models.Model):
    _inherit = "quality.alert"

    parent_id = fields.Many2one('parent.ticket', string='Parent Ticket', help='This is field is the refernce and show the related pickings in parent ticket.')