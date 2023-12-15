from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    survey_notification = fields.Boolean(string="Survey Notification", help="Survey link will be sent to customer after this time.")
    