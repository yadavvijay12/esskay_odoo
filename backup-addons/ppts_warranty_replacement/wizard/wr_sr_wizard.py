from odoo import fields, models, api, _
from odoo.exceptions import Warning, UserError


class WRWizard(models.Model):
    _name = 'wr.sr.wizard'
    _description = 'SR Create Wizard'

    request_type_id = fields.Many2one('request.type', string="Approval Type", copy=False, required=True)

    # Create Service Request
    def action_create_service_request(self):
        order_id = self.env['sale.order'].browse(self.env.context['active_id'])
        context = {
            'wr_id': order_id.id,
            'customer_name': order_id.partner_id.name,
            'partner_id': order_id.partner_id.id or False,
            # 'customer_account_id': order_id.partner_id.customer_account_id.id or False,
            'service_category_id': order_id.service_category_id.id or False,
            'service_type_id': order_id.service_type_id.id or False,
            'product_name': (x.product_id.name for x in order_id.order_line),
            'custom_product_serial': (y.product_id.custom_product_serial for y in order_id.order_line),
            # 'product_category_id': order_id.categ_id.name,
            'request_type_id': self.request_type_id.id or False,
            'child_ticket_id': order_id.child_ticket_id.id or False,
            'parent_ticket_id': order_id.parent_ticket_id.id or False,
            'team_id': order_id.team_id.id or False,
            'external_reference': order_id.external_reference,
            'problem_reported': order_id.reported_fault or '',
            'survey_id': order_id.worksheet_id.id or False,
            'customer_asset_ids': [(0, 0, {
                # 'stock_lot_id': line.stock_lot_id.id,
                'product_id': line.product_id.id,
            })for line in order_id.order_line]
        }
        service = self.env['service.request'].create(context)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Request',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'service.request',
            'res_id': service.id,
            'target': 'current',
        }
                
                
                
