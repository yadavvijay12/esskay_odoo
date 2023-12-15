from odoo import fields, models, api, _
from odoo.exceptions import Warning, UserError


class ConvertParentTicket(models.Model):
    _name = 'convert.parent.ticket'

    call_source_id = fields.Many2one('call.source', string="Call Source/Type")
    service_category_id = fields.Many2one('service.category', string="Service Category")
    service_type_id = fields.Many2one('service.type', string="Service Type", )
    parent_ticket_configuration_id = fields.Many2one('parent.ticket.configuration',
                                                     string="Parent Ticket Configuration", required=True)
    pt_conf_ids = fields.Many2many('parent.ticket.configuration', compute='_compute_pt_conf_ids',
                                   string="Parent Ticket Configuration IDS", store=True, precompute=True, )
    request_type_id = fields.Many2one('request.type', string="Approval Type", copy=False, required=True)

    @api.onchange('request_type_id')
    def onchange_request_type_domain(self):
        active_id = self._context.get('active_id')
        sr = self.env['service.request'].search([('id', '=', active_id)])
        domain = [('ticket_type', '=', sr.request_type_id.ticket_type)]
        # domain = [('ticket_type', '=', sr.request_type_id.ticket_type), ('team_id', 'in', sr.user_id.team_ids.ids)]
        return {'domain': {'request_type_id': domain}}

    @api.depends('service_category_id', 'service_type_id')
    def _compute_pt_conf_ids(self):
        conf_ids = []
        active_id = self._context.get('active_id')
        sr = self.env['service.request'].search([('id', '=', active_id)])
        pt_conf_ids = self.env['parent.ticket.configuration'].search(
            [('service_category_id', '=', sr.service_category_id.id), ('service_type_id', '=', sr.service_type_id.id)])
        for each in pt_conf_ids:
            conf_ids.append(each.id)
        self.pt_conf_ids = conf_ids

    # Convert to Parent Ticket
    def action_parent_ticket_create(self):
        active_id = self._context.get('active_id')
        service_request = self.env['service.request'].search([('id', '=', active_id)])
        for order in service_request:
            if not self.parent_ticket_configuration_id.work_flow_id:
                raise UserError(_("Please Configure Work Flow in Parent Ticket Configuration"))
            if not order.customer_asset_ids:
                raise UserError(_("Please Select Asset Selection"))
            '''
                1. If the request type is installation then needless to consider the assets
            '''
            parent_tick = {
                'partner_id': order.partner_id.id or False,
                'call_source_id': order.call_source_id.id or False,
                'service_category_id': order.service_category_id.id or False,
                'service_type_id': order.service_type_id.id or False,
                'product_category_id_alias': order.product_category_alias or '',
                'requested_by_name': order.requested_by_name or '',
                'requested_by_contact_number': order.requested_by_contact_number or '',
                'requested_by_email': order.requested_by_email or '',
                'requested_by_title': order.requested_by_title or '',
                'alternate_contact_name': order.alternate_contact_name,
                'alternate_contact_number': order.alternate_contact_number,
                'alternate_contact_email': order.alternate_contact_email,
                'call_received_id': order.call_received_id.id or False,
                # 'oem_warranty_status_id': order.oem_warranty_status_id.id or False,
                # 'repair_warranty_status_id': order.repair_warranty_status_id.id or False,
                'team_id': order.team_id.id or False,
                'call_date': order.call_received_on,
                'state': 'new',
                'remarks': order.remarks or '',
                'problem_description': order.problem_reported or '',
                'description': order.description or '',
                'dealer_distributor_id': order.dealer_distributor_id.id or False,
                'parent_configuration_id': self.parent_ticket_configuration_id.id or False,
                'request_type_id': self.request_type_id.id or False,
                'parent_ticket_id_alias': order.service_request_id_alias or '',
                # 'oem_warranty_status_id': order.oem_warranty_status or False,
                'assign_engineer_ids': [(4, self.env.user.id)],

            }
            for line in order.customer_asset_ids:
                parent_tick['stock_lot_id'] = line.stock_lot_id.id,
                parent_tick['categ_id'] = line.product_id.categ_id.id or False,
            parent_ticket = self.env['parent.ticket'].create(parent_tick)
            if not self.parent_ticket_configuration_id.work_flow_id.task_list_ids:
                raise UserError('Tasks are not mapped on this workflow to create parent ticket.')
            if self.parent_ticket_configuration_id.work_flow_id:
                status = self.parent_ticket_configuration_id.work_flow_id.task_list_ids[0]
                status_data = [(0, 0, {
                    'task_id': status.task_id.id,
                    'next_task_ids': [(6, 0, status.next_task_ids.ids)],
                    'status': status.status,
                    'parent_ticket_id': parent_ticket.id,
                })]
                parent_ticket.write({'task_list_ids': status_data})
            parent_ticket.service_request_id = order.id
            parent_ticket._onchange_stock_lot_id()
            parent_ticket._onchange_task_list_ids()
            parent_ticket.onchange_service()
            parent_ticket._onchange_request_type_id()
            parent_ticket._onchange_request_type()
            parent_ticket.get_repair_warranty_approval_required()
            parent_ticket.partner_amc_cmc_status_check()
            parent_ticket._onchange_product_id()

            order.write({'state': 'converted_to_ticket', 'parent_ticket_id': parent_ticket.id})
            task_id = self.env.ref('ppts_custom_workflow.sr_converted_to_ticket')
            order.child_ticket_id.update({
                'task_list_ids': [(0, 0, {'task_id': task_id.id})],
            })
