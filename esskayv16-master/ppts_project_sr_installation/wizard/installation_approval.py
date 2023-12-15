from odoo import fields, models, api, _
from odoo.exceptions import Warning, UserError


class InstallationApproval(models.TransientModel):
	_name = 'installation.approval'
	_description = 'Installation Approval'
	
	installation_id = fields.Many2one('project.task', string="Installation ID", ondelete="cascade")
	sequence = fields.Integer(string='Sequence')
	user_id = fields.Many2one(string='User', comodel_name="res.users")
	type_id = fields.Many2one(string="Type", comodel_name="multi.approval.type", required=True)

	def action_send_for_approval(self):
		active_id = self._context.get('active_id')
		install_id = self.env['project.task'].search([('id', '=', active_id)])
		for record in self:
			request = {
				'name': install_id.name,
				'type_id': record.type_id.id or False,
			}
			requests = self.env['multi.approval'].create(request)
			requests.installation_id = install_id.id
			requests.action_submit()
			install_id.write({'installation_state': 'waiting_for_approval', 'is_send_for_approvals': True})
