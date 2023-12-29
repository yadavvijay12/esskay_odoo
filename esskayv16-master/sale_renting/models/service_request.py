from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, date


class ServiceRequest(models.Model):
    _inherit = 'service.request'

    sr_loaner_count = fields.Integer(compute='compute_sr_count')

    def action_create_loaner(self):
        for order in self:
            if not order.customer_asset_ids:
                raise UserError(_("Please Select Asset Selection"))
            # if not order.customer_account_id:
            #     raise UserError(_("Please Select Customer Account"))
            else:
                sr_order = {
                    'is_rental_order': True,
                    'lr_from_pt': order.is_lr_from_pt,

                    'partner_id': order.partner_id.id or False,
                    'parent_ticket_id': order.parent_ticket_id.id or False,
                    'team_id': order.team_id.id or False,
                    'service_request_id': order.id or False,
                    'order_line': [(0, 0, {
                        'product_id': line.product_id.id,
                        'is_rental': True,
                        'product_uom_qty': 1,
                        'product_uom': line.product_id.uom_id.id,
                        # 'start_date': fields.Datetime.now(),
                        # 'return_date': fields.Datetime.now() + timedelta(days=1),
                    }) for line in order.customer_asset_ids],
                }
                sale_order = self.env['sale.order'].create(sr_order)
                # for rec in sale_order.order_line:
                #     rec._onchange_product_id()
                # sale_order.action_confirm()
        template_id_pi = self.env.ref('sale_renting.mail_template_loaner_created')
        if template_id_pi:
            template_id_pi.sudo().send_mail(self.id, force_send=True)
        return {
            'type': 'ir.actions.act_window',
            'name': 'SR Loaner Order',
            'view_mode': 'form',
            'view_type': 'form',
            # 'view_id': 'form',
            'res_model': 'sale.order',
            'res_id': sale_order and sale_order.id,
            'target': 'current',
            'domain': [('is_rental_order', '=', True)],
            'context': {'default_is_rental_order': 1, 'search_default_filter_today': 1,
                        'search_default_filter_to_return': 1}
        }

    # def compute_sr_count(self):
    #     for record in self:
    #         record.sr_loaner_count = self.env['sale.order'].search_count(
    #             [('is_rental_order', '=', True), ('service_request_id', '=', self.id)])

    def compute_sr_count(self):
        for record in self:
            record.sr_loaner_count = self.env['sale.order'].search_count(
                [('service_request_id', '=', record.id)])

    def action_view_loaner_order(self):
        sale_order = self.env['sale.order'].search([('service_request_id', '=', self.id)])
        field_ids = sale_order.ids
        domain = [('id', 'in', field_ids), ('is_rental_order', '=', True)]
        view_form_id = self.env.ref('sale_renting.rental_order_primary_form_view').id
        view_kanban_id = self.env.ref('sale_renting.rental_order_view_kanban').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'kanban,form',
            'target': 'current',
            'domain': domain,
            'context': "{'create': False}"
        }
        if len(sale_order) == 1:
            action.update({'views': [(view_form_id, 'form')], 'res_id': sale_order.id})
        else:
            action['views'] = [(view_kanban_id, 'kanban'), (view_form_id, 'form')]
        return action
