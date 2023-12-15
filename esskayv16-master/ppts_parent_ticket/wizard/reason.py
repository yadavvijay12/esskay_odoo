from odoo import fields, models, api


class OpenWizard(models.TransientModel):
    _name = 'open.renew'
    _description = 'Reason'

    cancel_renew = fields.Char(string="Reason")

    def action_cancel_renew(self):
        child_ticket_id = self.env['parent.ticket'].browse(self.env.context.get('active_id'))
        child_ticket_id.state = 'new'

    def Cancel(self):
        return True
