from odoo import fields, models, api, _
from odoo.exceptions import Warning, UserError


class MaintenanceApproval(models.TransientModel):
	_name = 'maintenance.approval'
	_description = 'Maintenance Approval'
	
	maintenance_id = fields.Many2one('maintenance.request', string="Maintenance ID", ondelete="cascade")
	sequence = fields.Integer(string='Sequence')
	user_id = fields.Many2one(string='User', comodel_name="res.users")
	type_id = fields.Many2one(string="Type", comodel_name="multi.approval.type", required=True)
	
	def action_send_for_approval(self):
		active_id = self._context.get('active_id')
		maintenance = self.env['maintenance.request'].search([('id', '=', active_id)])
		for record in self:
			request = {
				'name': maintenance.name,
				'type_id': record.type_id.id or False,
			}
			requests = self.env['multi.approval'].create(request)
			requests.maintenance_id = maintenance.id
			requests.action_submit()
			maintenance.write({'maintenance_state': 'waiting_for_approval', 'is_send_for_approvals': True})

