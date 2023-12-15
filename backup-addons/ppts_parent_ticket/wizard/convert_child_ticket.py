from odoo import fields, models, api, _
from odoo.exceptions import Warning, UserError


class ConvertChildTicket(models.Model):
    _name = 'convert.child.ticket'

    child_ticket_configuration_id = fields.Many2one('child.ticket.configuration', string="Child Ticket Configuration",
                                                    required=True)
    request_type_id = fields.Many2one('request.type', string="Approval Type", copy=False, required=True)

    @api.onchange('request_type_id')
    def onchange_request_type_domain(self):
        parent_ticket = None
        if self.env.context.get('active_model') == 'parent.ticket':
            parent_ticket = self.env['parent.ticket'].search([('id', '=', self._context.get('active_id'))])
        elif self.env.context.get('active_model') == 'tasks.master.line':
            parent_ticket = self.env['tasks.master.line'].search(
                [('id', '=', self._context.get('active_id'))]).parent_ticket_id
        elif self.env.context.get('active_model') == 'service.request':
            parent_ticket = self.env['service.request'].search(
                [('id', '=', self._context.get('active_id'))]).parent_ticket_id
        if parent_ticket:
            domain = [('ticket_type', '=', parent_ticket.request_type_id.ticket_type),
                      ('team_id', '=', parent_ticket.team_id.id)]
            return {'domain': {'request_type_id': domain}}

    @api.onchange('child_ticket_configuration_id')
    def onchange_child_ticket_configuration_id(self):
        domain = {}
        parent_ticket = None
        if self.env.context.get('active_model') == 'parent.ticket':
            parent_ticket = self.env['parent.ticket'].search([('id', '=', self._context.get('active_id'))])
        elif self.env.context.get('active_model') == 'tasks.master.line':
            parent_ticket = self.env['tasks.master.line'].search(
                [('id', '=', self._context.get('active_id'))]).parent_ticket_id
        elif self.env.context.get('active_model') == 'service.request':
            parent_ticket = self.env['service.request'].search(
                [('id', '=', self._context.get('active_id'))]).parent_ticket_id
        if parent_ticket:
            child_ids = self.env['child.ticket.line'].search(
                [('child_ticket_id', '=', parent_ticket.parent_configuration_id.id)])
            domain = {'child_ticket_configuration_id': [('id', 'in', child_ids.child_ids.ids)]}
            return {'domain': domain}

    # Convert to Child Ticket
    def action_child_ticket_create(self):
        # active_id = self._context.get('active_id')
        # service_request = self.env['service.request'].search([('id', '=', active_id)])
        if self.env.context.get('active_model') == 'service.request':
            service_request = self.env['service.request'].browse(self.env.context['active_id'])
            for order in service_request:
                if not self.child_ticket_configuration_id.work_flow_id:
                    raise UserError(_("Please Configure Work Flow in Child Ticket Configuration"))
                if not order.customer_asset_ids:
                    raise UserError(_("Please Select Asset Selection"))
                for line in order.customer_asset_ids:
                    child_tick = {
                        'stock_lot_id': line.stock_lot_id.id,
                        'product_id': line.product_id.id,
                        'partner_id': order.partner_id.id or False,
                        'call_source_id': order.call_source_id.id or False,
                        'service_category_id': order.service_category_id.id or False,
                        'service_type_id': order.service_type_id.id or False,
                        'product_category_id_alias': order.product_category_alias or '',
                        'requested_by_name_child': order.requested_by_name or '',
                        'requested_by_email_ct': order.requested_by_email or '',
                        'requested_by_title_ct': order.requested_by_title or '',
                        'requested_by_contact_number': order.requested_by_contact_number or '',
                        'call_received_id': order.call_received_id.id or False,
                        'oem_warranty_status_id': order.oem_warranty_status_id.id or False,
                        'repair_warranty_status_id': order.repair_warranty_status_id.id or False,
                        'team_id': order.team_id.id,
                        'state': 'new',
                        'remarks': order.remarks or '',
                        'problem_description': order.problem_reported or '',
                        'categ_id': line.product_id.categ_id.id or False,
                        'description': order.description or '',
                        'dealer_distributor_id': order.dealer_distributor_id.id or False,
                        'request_type_id': order.request_type_id.id,
                        'child_configuration_id': self.child_ticket_configuration_id.id or False,
                        'parent_ticket_id': order.parent_ticket_id.id or order.child_ticket_id.parent_ticket_id.id,
                        'parent_ticket_id_alias_date': order.parent_ticket_id_alias_date,

                        'repair_location_id': order.child_ticket_id.repair_location_id.id or order.parent_ticket_id.repair_center_location_id.id or order.child_ticket_id.parent_ticket_id.repair_center_location_id.id,
                    }
                    child_ticket = self.env['child.ticket'].create(child_tick)
                    if not self.child_ticket_configuration_id.work_flow_id.task_list_ids:
                        raise UserError('Tasks are not mapped on this workflow to create parent ticket.')
                    if self.child_ticket_configuration_id.work_flow_id:
                        status = self.child_ticket_configuration_id.work_flow_id.task_list_ids[0]
                        status_data = [(0, 0, {
                            'task_id': status.task_id.id,
                            'next_task_ids': [(6, 0, status.next_task_ids.ids)],
                            'status': status.status,
                            'child_ticket_id': child_ticket.id,
                        })]
                        child_ticket.write({'task_list_ids': status_data})
                    child_ticket.service_request_id = order.id
                    child_ticket._onchange_stock_lot_id()
                    child_ticket._onchange_task_list_ids()
                    child_ticket.onchange_service()
                    order.write({'state': 'converted_to_ticket'})
                    task_id = self.env.ref('ppts_custom_workflow.sr_converted_to_ticket')
                    order.child_ticket_id.update({
                        'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                    })
        if self.env.context.get('active_model') == 'parent.ticket':
            parent_ticket = self.env['parent.ticket'].browse(self.env.context['active_id'])
            for order in parent_ticket:
                if not self.child_ticket_configuration_id.work_flow_id:
                    raise UserError(_("Please Configure Work Flow in Child Ticket Configuration"))
                if self.child_ticket_configuration_id:
                    child_tick = {
                        'partner_id': order.partner_id.id or False,
                        'call_source_id': order.call_source_id.id or False,
                        'call_date': order.call_date or False,
                        'service_category_id': order.service_category_id.id or False,
                        'service_type_id': order.service_type_id.id or False,
                        'product_id': order.product_id.id or False,
                        'stock_lot_id': order.stock_lot_id.id or False,
                        'categ_id': order.categ_id.id or False,
                        'product_category_id_alias': order.product_category_id_alias or '',
                        'problem_description': order.problem_description or '',
                        'requested_by_name_child': order.requested_by_name or '',
                        'requested_by_email_ct': order.requested_by_email or '',
                        'requested_by_title_ct': order.requested_by_title or '',
                        'requested_by_contact_number': order.requested_by_contact_number or '',
                        'remarks': order.remarks or '',
                        'installation_date': order.installation_date or False,
                        'dealer_distributor_id': order.dealer_distributor_id.id or False,
                        'call_received_id': order.call_received_id.id or False,
                        'alternate_contact_name': order.alternate_contact_name or '',
                        'alternate_contact_number': order.alternate_contact_number or '',
                        'alternate_contact_email': order.alternate_contact_email,
                        're_repair': order.re_repair,
                        'oem_warranty_status_id': order.oem_warranty_status_id.id or False,
                        'repair_warranty_status_id': order.repair_warranty_status_id.id or False,
                        'customer_account_id': order.customer_account_id.id or False,
                        'team_id': order.team_id.id or False,
                        'faulty_section': order.faulty_section or '',
                        'sow': order.sow or '',
                        'webdelata_id': order.webdelata_id or '',
                        'webdelata': order.webdelata or '',
                        'mc_stk': order.mc_stk or False,
                        'child_configuration_id': self.child_ticket_configuration_id.id or False,
                        'child_ticket_id_alias': order.parent_ticket_id_alias or '',
                        'request_type_id': self.request_type_id.id or False,
                        'service_request_id': order.service_request_id.id or False,
                        'is_send_for_approvals': True if not self.request_type_id.is_required_approval else False,
                        'amc_status': order.amc_status,
                        'cmc_status': order.cmc_status,
                        'parent_ticket_id': order.id,
                        'customer_street': order.customer_street,
                        'customer_street2': order.customer_street2,
                        'customer_zip': order.customer_zip,
                        'customer_state_id': order.customer_state_id.id,
                        'customer_country_id': order.customer_country_id.id,
                        'customer_country_code': order.customer_country_code,
                        'repair_location_id': order.repair_center_location_id.id,
                        'parent_ticket_id_alias': order.parent_ticket_id_alias,
                        'price_available_in_contract': order.price_available_in_contract,
                        'product_part_number': order.cat_no,
                        'parent_ticket_id_alias_date': order.parent_ticket_id_alias_date,
                        'team_id': order.team_id.id,

                    }
                    child_ticket = self.env['child.ticket'].create(child_tick)
                    if not self.child_ticket_configuration_id.work_flow_id.task_list_ids:
                        raise UserError('Tasks are not mapped on this workflow to create child ticket.')
                    if self.child_ticket_configuration_id.work_flow_id:
                        status = self.child_ticket_configuration_id.work_flow_id.task_list_ids[0]
                        status_data = [(0, 0, {
                            'task_id': status.task_id.id,
                            'next_task_ids': [(6, 0, status.next_task_ids.ids)],
                            'status': status.status,
                            'child_ticket_id': child_ticket.id,
                        })]
                        child_ticket.write({'task_list_ids': status_data})

                    child_ticket.parent_ticket_id = order.id
                    child_ticket._onchange_stock_lot_id()
                    child_ticket._onchange_task_list_ids()
                    child_ticket._onchange_task_list_ids()
                    child_ticket.onchange_service()
                    order.child_ticket_id = child_ticket.id
                    order.service_request_id.child_ticket_id = child_ticket.id
                    order.write({'is_child_ticket_created': True})
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Child Ticket',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'res_model': 'child.ticket',
                        'res_id': child_ticket.id,
                        'target': 'current',
                    }
        if self.env.context.get('active_model') == 'tasks.master.line':
            ticket_id = self.env['tasks.master.line'].browse(self.env.context['active_id'])
            parent_ticket = self.env['parent.ticket'].sudo().search(
                [('id', '=', ticket_id.parent_ticket_id.id)], limit=1)
            for order in parent_ticket:
                if not self.child_ticket_configuration_id.work_flow_id:
                    raise UserError(_("Please Configure Work Flow in Child Ticket Configuration"))
                if self.child_ticket_configuration_id:
                    child_tick = {
                        'partner_id': order.partner_id.id or False,
                        'call_source_id': order.call_source_id.id or False,
                        'call_date': order.call_date or False,
                        'service_category_id': order.service_category_id.id or False,
                        'service_type_id': order.service_type_id.id or False,
                        'product_id': order.product_id.id or False,
                        'stock_lot_id': order.stock_lot_id.id or False,
                        'categ_id': order.categ_id.id or False,
                        'product_category_id_alias': order.product_category_id_alias or '',
                        'problem_description': order.problem_description or '',
                        'requested_by_name_child': order.requested_by_name or '',
                        'requested_by_contact_number': order.requested_by_contact_number or '',
                        'remarks': order.remarks or '',
                        'installation_date': order.installation_date or False,
                        'dealer_distributor_id': order.dealer_distributor_id.id or False,
                        'call_received_id': order.call_received_id.id or False,
                        'alternate_contact_name': order.alternate_contact_name or '',
                        'alternate_contact_number': order.alternate_contact_number or '',
                        'alternate_contact_email': order.alternate_contact_email,
                        're_repair': order.re_repair,
                        'oem_warranty_status_id': order.oem_warranty_status_id.id or False,
                        'repair_warranty_status_id': order.repair_warranty_status_id.id or False,
                        'customer_account_id': order.customer_account_id.id or False,
                        'team_id': order.team_id.id or False,
                        'faulty_section': order.faulty_section or '',
                        'sow': order.sow or '',
                        'webdelata_id': order.webdelata_id or '',
                        'webdelata': order.webdelata or '',
                        'mc_stk': order.mc_stk or False,
                        'child_configuration_id': self.child_ticket_configuration_id.id or False,
                        'child_ticket_id_alias': order.parent_ticket_id_alias or '',
                        'request_type_id': order.request_type_id.id or False,
                        'amc_status': order.amc_status,
                        'cmc_status': order.cmc_status,
                        'customer_street': order.customer_street,
                        'customer_street2': order.customer_street2,
                        'customer_zip': order.customer_zip,
                        'customer_state_id': order.customer_state_id.id,
                        'customer_country_id': order.customer_country_id.id,
                        'customer_country_code': order.customer_country_code,
                        'repair_location_id': order.repair_center_location_id.id,
                        'parent_ticket_id_alias': order.parent_ticket_id_alias,
                        'price_available_in_contract': order.price_available_in_contract,
                        'product_part_number': order.cat_no,
                        'parent_ticket_id_alias_date': order.parent_ticket_id_alias_date,
                        'team_id': order.team_id.id,
                    }
                    child_ticket = self.env['child.ticket'].create(child_tick)
                    if self.child_ticket_configuration_id.work_flow_id:
                        status = self.child_ticket_configuration_id.work_flow_id.task_list_ids[0]
                        status_data = [(0, 0, {
                            'task_id': status.task_id.id,
                            'next_task_ids': [(6, 0, status.next_task_ids.ids)],
                            'status': status.status,
                            'child_ticket_id': child_ticket.id,
                        })]
                        child_ticket.write({'task_list_ids': status_data})
                    child_ticket.parent_ticket_id = order.id
                    child_ticket._onchange_stock_lot_id()
                    child_ticket._onchange_task_list_ids()
                    child_ticket.onchange_service()

                    order.child_ticket_id = child_ticket.id
                    order.write({'state': 'confirm', 'is_child_ticket_created': True})
