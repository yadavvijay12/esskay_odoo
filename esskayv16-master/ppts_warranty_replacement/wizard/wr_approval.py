from odoo import fields, models, api, _
from odoo.exceptions import Warning, UserError


class WRApproval(models.TransientModel):
	_name = 'wr.approval'
	_description = 'Warranty Request Approval'
	
	wr_id = fields.Many2one('sale.order', string="WR ID", ondelete="cascade")
	sequence = fields.Integer(string='Sequence')
	user_id = fields.Many2one(string='User', comodel_name="res.users")
	type_id = fields.Many2one(string="Type", comodel_name="multi.approval.type", required=True)
	
	def action_send_for_approval(self):
		active_id = self._context.get('active_id')
		wr_id = self.env['sale.order'].search([('id', '=', active_id)])
		for record in self:
			request = {
				'name': wr_id.name,
				'type_id': record.type_id.id or False,
			}
			requests = self.env['multi.approval'].create(request)
			requests.wr_id = wr_id.id
			requests.action_submit()
			wr_id.write({'wr_state': 'waiting_for_approval', 'is_send_for_approvals': True})

