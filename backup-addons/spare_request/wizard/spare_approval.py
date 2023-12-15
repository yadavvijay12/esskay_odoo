from odoo import fields, models, api, _
from odoo.exceptions import Warning, UserError


class SpareApproval(models.TransientModel):
	_name = 'spare.approval'
	_description = 'Spare Approval'
	
	spare_id = fields.Many2one('spare.request', string="Spare ID")
	type_id = fields.Many2one(string="Type", comodel_name="multi.approval.type", required=True)
	
	def action_send_for_approval(self):
		active_id = self._context.get('active_id')
		spare = self.env['spare.request'].search([('id', '=', active_id)])
		for record in self:
			request = {
				'name': spare.name,
				'type_id': record.type_id.id or False,
				'spare_request_id': spare.id,
			}
			requests = self.env['multi.approval'].create(request)
			requests.spare_request_id = spare.id
			requests.action_submit()
			action_id = self.env.ref('multi_level_approval.multi_approval_approval_action', raise_if_not_found=False)
			template_id = self.env.ref('spare_request.spare_mail_template_notify_approvers')
			base_url = '/web#id=%d&action=%r&model=multi.approval&view_type=form' % (requests.id, action_id.id)
			mail = ''
			for lines in requests.line_ids:
				mail = lines.user_id.mapped('login')
				break
			if template_id:
				template_id.with_context(rec_url=base_url, email_to=mail).sudo().send_mail(requests.id, force_send=True)
			spare.write({'state': 'waiting_approval', 'is_send_for_approvals': True})

