from odoo import fields, models, api


class MaintenanceReason(models.TransientModel):
    _name = 'maintenance.reason'
    _description = 'Maintenance Reason'

    name = fields.Text("Reason")
    reason_type = fields.Selection([('hold', 'Hold'),('reject','Reject'),('close', 'Close')], string="Reason Type")

    def action_confirm(self):
        active = self.env['maintenance.request'].browse(self.env.context.get('active_id'))
        for approve_id in self.env['maintenance.approval'].search(
                [('user_id', '=', self.env.user.id), ('maintenance_id', '=', active.id)]):
            if self.reason_type == 'hold':
                approve_id.state = 'hold'
                approve_id.hold_reason = self.name
                approve_id.hold_on = fields.Date.today()
            elif self.reason_type == 'reject':
                approve_id.state = 'rejected'
                approve_id.reject_reason = self.name
                approve_id.rejected_on = fields.Date.today()
        return True
