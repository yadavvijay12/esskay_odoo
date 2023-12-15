from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError


class ServiceRequest(models.Model):
    _inherit = 'service.request'

    wr_count = fields.Integer(compute='compute_wr_count')
    wr_id = fields.Many2one('sale.order', string="WR ID")

    def action_create_warranty_replacement(self):
        for order in self:
            if not order.customer_asset_ids:
                raise UserError(_("Please Select Asset Selection"))
            else:
                wr_order = {
                    'is_replacement_order': True,
                    'partner_id': order.partner_id.id or False,
                    'service_category_id': order.service_category_id.id or False,
                    'team_id': order.team_id.id or False,
                    'service_request_id': order.id or False,
                    'reported_fault': order.problem_reported or '',
                    # 'request_type_id': order.request_type_id.id or False,
                    'parent_ticket_id': order.parent_ticket_id.id or False,
                    'child_ticket_id': order.child_ticket_id.id or False,
                    'external_reference': order.external_reference,
                    'worksheet_id': order.survey_id.id or False,
                    'origin': order.name or '',
                    'order_line': [(0, 0, {
                        'product_id': line.product_id.id,
                        'product_uom_qty': 1,
                        'product_uom': line.product_id.uom_id.id,
                    }) for line in order.customer_asset_ids],
                }
                order = self.env['sale.order'].create(wr_order)
        view = self.env.ref('ppts_warranty_replacement.warranty_replacement_form_view')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Warranty Replacement',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view.id,
            'res_model': 'sale.order',
            'res_id': order.id,
            'target': 'current',
            'domain': [('is_replacement_order', '=', True)],
        }

    def action_view_wr_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Warranty Replacement Order',
            'view_mode': 'tree,form',
            'views': [(self.env.ref('ppts_warranty_replacement.warranty_replacement_tree_view').id, 'tree'),
                      (self.env.ref('ppts_warranty_replacement.warranty_replacement_form_view').id, 'form')],
            'res_model': 'sale.order',
            'domain': [('is_replacement_order', '=', True), ('service_request_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_wr_count(self):
        for record in self:
            record.wr_count = self.env['sale.order'].search_count(
                [('is_replacement_order', '=', True), ('service_request_id', '=', self.id)])
