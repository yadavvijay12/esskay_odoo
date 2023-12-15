# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import api, fields, models
from odoo.exceptions import UserError

class RefusedReason(models.TransientModel):
    _name = 'refused.reason'
    _description = 'Refused Reason'

    reason = fields.Text('Reason', required=True)

    def action_reason_apply(self):
        approval = self.env['multi.approval'].browse(
            self.env.context.get('active_ids'))
        approval.write({'reason':self.reason})
        if approval.service_request_id:
            if approval.service_request_id.child_ticket_id:
                service_request_submitted_task_id = self.env['tasks.master'].search(
                    [('python_code', '=', 'service_request_rejected')])
                if not service_request_submitted_task_id:
                    raise UserError(
                        "Create Service Request Rejected with python code as 'service_request_rejected' to proceed further.")
                approval.service_request_id.child_ticket_id.task_list_ids = [(0, 0, {'task_id': service_request_submitted_task_id.id, 'status':self.reason, 'description':self.reason})]
        return approval.action_refuse()
