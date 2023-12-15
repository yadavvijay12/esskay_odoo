from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    parent_ticket_id = fields.Many2one('parent.ticket', string='Parent Ticket', copy=False)
    child_ticket_id = fields.Many2one('child.ticket', string='Child Ticket', copy=False)
