from odoo import fields, models, api


class ReasonReason(models.TransientModel):
    _name = 'reason.reason'
    _description = 'Reason'

    name = fields.Text("Reason")
    reason_type = fields.Selection([('hold', 'Hold'),('reject','Reject'),('close', 'Close'),('request_hold', 'Request Hold')], string="Reason Type")

    def action_confirm(self):
        if self.env.context.get('active_model') == 'service.request':
            service_request_id = self.env['service.request'].browse(self.env.context.get('active_id'))
            for approve_id in self.env['service.ticket.approval'].search([('user_id', '=', self.env.user.id),('service_request_id', '=',service_request_id.id)]):
                if self.reason_type == 'hold':
                    approve_id.state = 'hold'
                    approve_id.hold_reason = self.name
                    approve_id.hold_on = fields.Date.today()
                elif self.reason_type == 'reject':
                    approve_id.state = 'rejected'
                    approve_id.reject_reason = self.name
                    approve_id.rejected_on = fields.Date.today()
            if self.reason_type == 'request_hold':
                service_request_id.state = 'hold'
                service_request_id.request_hold_reason = self.name
                service_request_id.request_hold_date = fields.Date.today()
            elif self.reason_type == 'close':
                service_request_id.state = 'closed'
                service_request_id.close_reason = self.name
                service_request_id.action_send_acknowledgment_from_pt()
        return True