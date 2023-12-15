from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError


class ServiceRequest(models.Model):
	_inherit = 'service.request'
	
	maintenance_count = fields.Integer(compute='compute_count')
	
	def action_create_maintenance(self):
		for order in self:
			if not order.customer_asset_ids:
				raise UserError(_("Please Select Asset Selection"))
			for line in order.customer_asset_ids:
				record = {
					'is_sr_maintenance': True,
					'stock_lot_id': line.stock_lot_id.id,
					'product_id': line.product_id.id,
					'partner_id': order.partner_id.id or False,
					'customer_account_id': order.partner_id.customer_account_id.id or False,
					'service_category_id': order.service_category_id.id or False,
					'service_type_id': order.service_type_id.id or False,
					# 'request_type_id': order.request_type_id.id or False,
					'team_id': order.team_id.id or False,
					'parent_ticket_id': order.parent_ticket_id.id or False,
					'child_ticket_id': order.child_ticket_id.id or False,
					'external_reference': order.external_reference,
					'reported_fault': order.problem_reported or '',
					'categ_id': line.product_id.categ_id.id or False,
					'service_request_id': order.id or False,
					'custom_product_serial': line.product_id.custom_product_serial,
					'product_code_no': line.product_id.product_code,
					'cat_no': line.product_id.product_part,
					'worksheet_id': order.survey_id.id or False,
					'origin': order.name,
					'warranty_end_date': line.stock_lot_id.warranty_end_date,
					'extended_warranty_end_date': line.stock_lot_id.extended_warranty_end_date,
				}
				record = self.env['maintenance.request'].create(record)
				record._onchange_stock_lot_id()
		view = self.env.ref('ppts_maintenanace.sr_maintenance_request_view_form')
		return {
			'type': 'ir.actions.act_window',
			'name': 'Maintenance Request',
			'view_mode': 'form',
			'view_type': 'form',
			'view_id': view.id,
			'res_model': 'maintenance.request',
			'res_id': record.id,
			'target': 'current',
			'domain': [('is_sr_maintenance', '=', True)],
		}

	def action_view_maintenance_requests(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': 'Maintenance Request',
			'view_mode': 'tree,form',
			'views': [(self.env.ref('ppts_maintenanace.sr_maintenance_request_view_tree').id, 'tree'),
			          (self.env.ref('ppts_maintenanace.sr_maintenance_request_view_form').id, 'form')],
			'res_model': 'maintenance.request',
			'domain': [('is_sr_maintenance', '=', True), ('service_request_id', '=', self.id)],
			'context': "{'create': False}"
		}
	
	def compute_count(self):
		for record in self:
			record.maintenance_count = self.env['maintenance.request'].search_count(
				[('is_sr_maintenance', '=', True), ('service_request_id', '=', self.id)])


class StockLot(models.Model):
	_inherit = "stock.lot"
	
	extended_warranty_check = fields.Boolean("Extended Warranty Check", compute='compute_extended_warranty_check', default=False, copy=True)
	
	@api.depends('extended_warranty_start_date', 'extended_warranty_end_date')
	def compute_extended_warranty_check(self):
		for record in self:
			if record.extended_warranty_start_date and record.extended_warranty_end_date:
				record.oem_repair_warranty_check = True
			else:
				record.oem_repair_warranty_check = False
