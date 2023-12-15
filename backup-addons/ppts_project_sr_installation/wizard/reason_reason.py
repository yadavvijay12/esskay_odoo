from odoo import fields, models, api


class InstallationReason(models.TransientModel):
    _name = 'installation.reason'
    _description = 'Installation Reason'

    name = fields.Text("Reason")
    reason_type = fields.Selection([('hold', 'Hold'),('reject','Reject'),('close', 'Close')], string="Reason Type")

    def action_confirm(self):
        active = self.env['project.task'].browse(self.env.context.get('active_id'))
        for approve_id in self.env['installation.approval'].search(
                [('user_id', '=', self.env.user.id), ('installation_id', '=', active.id)]):
            if self.reason_type == 'hold':
                approve_id.state = 'hold'
                approve_id.hold_reason = self.name
                approve_id.hold_on = fields.Date.today()
            elif self.reason_type == 'reject':
                approve_id.state = 'rejected'
                approve_id.reject_reason = self.name
                approve_id.rejected_on = fields.Date.today()
        return True
