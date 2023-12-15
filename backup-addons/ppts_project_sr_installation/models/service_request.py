from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class ServiceRequest(models.Model):
	_inherit = 'service.request'
	
	installation_count = fields.Integer(compute='compute_install_count')
	install_addr_city_id = fields.Many2one("customer.city", string='City', copy=False)
	
	def action_create_installation(self):
		for order in self:
			if not order.customer_asset_ids:
				raise UserError(_("Please Select Asset Selection"))
			for line in order.customer_asset_ids:
				record = {
					'is_project_installation': True,
					'installation_stock_lot_id': line.stock_lot_id.id,
					# 'installation_product_id': line.product_id.id,
					'installation_customer_id': order.partner_id.id or False,
					'installation_customer_account_id': order.partner_id.customer_account_id.id or False,
					'installation_service_category_id': order.service_category_id.id or False,
					'installation_service_type_id': order.service_type_id.id or False,
					# 'installation_request_type_id': order.request_type_id.id or False,
					# 'installation_team_id': order.team_id.id or False,
					'installation_parent_ticket_id': order.parent_ticket_id.id or False,
					'installation_child_ticket_id': order.child_ticket_id.id or False,
					'installation_external_reference': order.external_reference,
					'installation_reported_fault': order.problem_reported or '',
					'installation_categ_id': line.product_id.categ_id.id or False,
					# 'installation_custom_product_serial': line.product_id.custom_product_serial,
					'installation_product_code_no': line.product_id.product_code,
					'installation_product_part': line.product_id.product_part,
					# 'installation_worksheet_id': order.survey_id.id or False,
					'installation_origin': order.name,
					'service_request_id': order.id,
				}
				record = self.env['project.task'].create(record)
		view = self.env.ref('ppts_project_sr_installation.view_task_form2_sr_installation')
		return {
			'type': 'ir.actions.act_window',
			'name': 'Installation',
			'view_mode': 'form',
			'view_type': 'form',
			'view_id': view.id,
			'res_model': 'project.task',
			'res_id': record.id,
			'target': 'current',
			'domain': [('is_project_installation', '=', True)],
		}
	
	def action_view_installations(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': 'Installation',
			'view_mode': 'tree,form',
			'views': [(self.env.ref('ppts_project_sr_installation.view_task_tree2_sr_installation').id, 'tree'),
			          (self.env.ref('ppts_project_sr_installation.view_task_form2_sr_installation').id, 'form')],
			'res_model': 'project.task',
			'domain': [('is_project_installation', '=', True), ('service_request_id', '=', self.id)],
			'context': "{'create': False}"
		}
	
	def compute_install_count(self):
		for record in self:
			record.installation_count = self.env['project.task'].search_count(
				[('is_project_installation', '=', True), ('service_request_id', '=', self.id)])