# -*- coding: utf-8 -*-
#############################################################################
#
#    Point Perfect Technology Solutions.
#
#############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
from odoo.exceptions import UserError, ValidationError
# from pip._internal import req


# Child Ticket Approval
class ChildTicketApproval(models.Model):
	_name = 'child.ticket.approval'
	
	type_id = fields.Many2one(string="Type", comodel_name="multi.approval.type", required=True)
	
	def action_send_for_approval(self):
		active_id = self._context.get('active_id')
		child_ticket_id = self.env['child.ticket'].search([('id', '=', active_id)])
		if child_ticket_id and 'child_task_line_id' in self.env.context:
			task_line_id = self.env['tasks.master.line'].browse(self.env.context.get('child_task_line_id'))
			for record in self:
				request = {
					'name': child_ticket_id.name + ' Status delete approval',
					'type_id': record.type_id.id or False,
					'child_task_line_id': task_line_id.id,
					'child_ticket_id': child_ticket_id.id
				}
				requests = self.env['multi.approval'].create(request)
				requests.action_submit()
				if task_line_id:
					task_line_id.description = "Sent for approval to delete this line."
		elif child_ticket_id:
			for record in self:
				request = {
					'name': child_ticket_id.name,
					'type_id': record.type_id.id or False,
					'child_ticket_id': child_ticket_id.id,
				}
				requests = self.env['multi.approval'].create(request)
				requests.action_submit()
				action_id = self.env.ref('multi_level_approval.multi_approval_approval_action', raise_if_not_found=False)
				template_id = self.env.ref('ppts_parent_ticket.ct_mail_template_notify_approvers')
				base_url = '/web#id=%d&action=%r&model=multi.approval&view_type=form' % (requests.id, action_id.id)
				amc = dict(child_ticket_id._fields['amc_status'].selection).get(child_ticket_id.amc_status)
				cmc = dict(child_ticket_id._fields['cmc_status'].selection).get(child_ticket_id.cmc_status)
				warranty = dict(child_ticket_id._fields['oem_warranty_status'].selection).get(child_ticket_id.oem_warranty_status)
				repair = dict(child_ticket_id._fields['oem_repair_status'].selection).get(child_ticket_id.oem_repair_status)
				extended = dict(child_ticket_id._fields['extended_warranty_status'].selection).get(child_ticket_id.extended_warranty_status)
				mail = ''
				for lines in requests.line_ids:
					mail = lines.user_id.mapped('login')
					break
				if template_id:
					template_id.with_context(rec_url=base_url, email_to=mail, amc=amc, cmc=cmc, warranty=warranty, repair=repair, extended=extended).sudo().send_mail(requests.id, force_send=True)
				# requests.child_ticket_id = child_ticket_id.id
				if child_ticket_id.request_type_id.is_required_approval and child_ticket_id.request_type_id.is_auto_approval:
					child_ticket_id.write({'state': 'approved', 'is_send_for_approvals': True})
					requests.state = 'Approved'
				else:
					child_ticket_id.write({'state': 'waiting_for_approval', 'is_send_for_approvals': True})

