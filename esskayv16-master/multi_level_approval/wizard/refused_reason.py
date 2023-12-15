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
        approval.write({'reason': self.reason})
        # if approval.service_request_id:
        if approval.child_ticket_id:
            rejected_task = approval.child_ticket_id.child_configuration_id.work_flow_id.task_list_ids.task_id.filtered(
                lambda r: r.name == 'Rejected')
            if rejected_task:
                approval.child_ticket_id.sudo().write(
                    {'state': 'rejected', 'task_list_ids': [(0, 0, {'task_id': rejected_task.id})]})
                values = {
                    'res_id': approval.child_ticket_id.id,
                    'model': 'child.ticket',
                    'body': 'As per the request the status has been rejected.',
                    'author_id': self.env.user.partner_id.id
                }
                self.env['mail.message'].create(values)
            else:
                raise UserError('There is no Approval Task available on workflow to update on ticket status')
        return approval.action_refuse()

    # def action_reason_apply(self):
    #     approval = self.env['multi.approval'].browse(
    #         self.env.context.get('active_ids'))
    #     approval.write({'reason': self.reason})
    #     if approval.service_request_id:
    #         if approval.service_request_id.child_ticket_id:
    #             service_request_submitted_task_id = self.env['tasks.master'].search(
    #                 [('python_code', '=', 'service_request_rejected')])
    #             if not service_request_submitted_task_id:
    #                 raise UserError(
    #                     "Create Service Request Rejected with python code as 'service_request_rejected' to proceed further.")
    #             approval.service_request_id.child_ticket_id.task_list_ids = [(0, 0, {
    #                 'task_id': service_request_submitted_task_id.id, 'status': self.reason,
    #                 'description': self.reason})]
    #     return approval.action_refuse()
