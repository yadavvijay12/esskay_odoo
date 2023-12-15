from odoo import fields, models, api


class InstallationReasonType(models.Model):
    _name = 'installation.reason.type'
    _description = 'Description'

    reason = fields.Char('On Hold Reason')

    def on_hold_reason(self):
        on_hold_id = self.env["project.task"].browse(self.env.context.get('active_id'))
        on_hold_id.on_hold_reason = self.reason
        on_hold_id.installation_state = 'on_hold'