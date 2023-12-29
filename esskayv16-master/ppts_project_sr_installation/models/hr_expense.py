from odoo import models, fields

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    installation_id = fields.Many2one('project.task', string='Installation Ref')
    child_ticket_id = fields.Many2one('child.ticket', string="Child Ticket ID", readonly=True)

