from odoo import fields, models, api, _
from odoo.exceptions import Warning, UserError
from datetime import datetime


class RequestTypeWizard(models.TransientModel):
    _name = 'request.type.wizard'
    _description = 'Request Type Wizard'

    pt_sr_id = fields.Many2one('service.request', string="Default Service Ticket ID")
    parent_ticket_id = fields.Many2one('parent.ticket', string="Default Parent Ticket ID")
    child_ticket_id = fields.Many2one('child.ticket', string="Default Child Ticket ID")
    request_type_id = fields.Many2one('request.type', string="Approval Type", copy=False, required=True,
                                      help="Select Request Type to Create Service Request")

    def action_sr_create(self):
        sr_id = None
        if self.request_type_id.ticket_type == 'sr_loaner':
            view = self.env.ref('ppts_service_request.service_request_sr_loaner_form_view')
        elif self.request_type_id.ticket_type == 'sr_wr':
            view = self.env.ref('ppts_service_request.service_request_sr_wr_form_view')
        elif self.request_type_id.ticket_type == 'sr_factory_repair':
            view = self.env.ref('ppts_service_request.service_request_sr_factory_form_view')
        elif self.request_type_id.ticket_type == 'sr_fsm':
            view = self.env.ref('ppts_service_request.service_request_sr_fsm_form_view')
        elif self.request_type_id.ticket_type == 'sr_installation':
            view = self.env.ref('ppts_service_request.service_request_sr_installation_form_view')
        elif self.request_type_id.ticket_type == 'sr_maintenance':
            view = self.env.ref('ppts_service_request.service_request_maintenance_form_view')
        elif self.request_type_id.ticket_type == 'sr_remote_support':
            view = self.env.ref('ppts_service_request.service_request_sr_remote_support_form_view')
        else:
            view = self.env.ref('ppts_service_request.service_request_form_view')

        if self.env.context.get('active_model') == 'parent.ticket':
            ticket_id = self.env['parent.ticket'].browse(self.env.context['active_id'])
            sr_id = self.env['service.request'].sudo().search([('id', '=', ticket_id.service_request_id.id)], limit=1)
        elif self.env.context.get('active_model') == 'child.ticket':
            ticket_id = self.env['child.ticket'].browse(self.env.context['active_id'])
            sr_id = self.env['service.request'].sudo().search(
                [('id', '=', ticket_id.sudo().parent_ticket_id.service_request_id.id)], limit=1)
        elif self.env.context.get('active_model') == 'tasks.master.line':
            ticket_id = self.env['tasks.master.line'].browse(self.env.context['active_id'])
            if ticket_id.sudo().parent_ticket_id:
                sr_id = self.env['service.request'].sudo().search(
                    [('id', '=', ticket_id.sudo().parent_ticket_id.service_request_id.id)], limit=1)
            elif ticket_id.child_ticket_id:
                sr_id = self.env['service.request'].sudo().search(
                    [('id', '=', ticket_id.child_ticket_id.sudo().parent_ticket_id.service_request_id.id)], limit=1)
        if sr_id:
            context = {
                'service_request_date': datetime.today(),
                'is_from_ct': True,
                'customer_name': sr_id.customer_name,
                'partner_id': sr_id.partner_id.id or False,
                'service_category_id': sr_id.service_category_id.id or False,
                'service_type_id': sr_id.service_type_id.id or False,
                'product_name': sr_id.product_name,
                'custom_product_serial': sr_id.custom_product_serial,
                'request_type_id': self.request_type_id.id or False,
                'child_ticket_id': self.child_ticket_id.id or False,
                'product_name': self.child_ticket_id.product_id.name,
                'custom_product_serial': self.child_ticket_id.stock_lot_id.name,
                'parent_ticket_id': self.parent_ticket_id.id or self.child_ticket_id.parent_ticket_id.id or False,
                'team_id': sr_id.team_id.id or False,
                'external_reference': sr_id.external_reference,
                'problem_reported': sr_id.problem_reported or '',
                'survey_id': sr_id.survey_id.id or False,
                'dealer_distributor_name': sr_id.dealer_distributor_name,
                'call_source_id': sr_id.call_source_id.id or False,
                'requested_by_name': sr_id.requested_by_name or '',
                'requested_by_contact_number': sr_id.requested_by_contact_number or '',
                'call_received_id': sr_id.call_received_id.id or False,
                'remarks': sr_id.remarks or '',
                'bio_medical_engineer_id': sr_id.bio_medical_engineer_id or '',
                'oem_warranty_status_id': sr_id.oem_warranty_status_id.id or False,
                'repair_warranty_status_id': sr_id.repair_warranty_status_id.id or False,
                'dealer_distributor_id': sr_id.dealer_distributor_id.id or False,
                'product_part_number': sr_id.product_part_number or '',
                'product_part_code': sr_id.product_part_code or '',
                'reason': sr_id.reason or '',
                'service_request_id_alias': sr_id.service_request_id_alias or '',

                'customer_asset_ids': [(0, 0, {
                    'stock_lot_id': line.stock_lot_id.id,
                    'product_id': line.product_id.id,
                    'notes': line.notes,
                }) for line in sr_id.customer_asset_ids]
            }
            service = self.env['service.request'].sudo().create(context)
            service._onchange_partner()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Service Request',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view.id,
                'res_model': 'service.request',
                'res_id': service.id,
                'target': 'current',
            }
        else:
            context = {
                'service_request_date': datetime.today(),
                'is_from_ct': True,
                'customer_name': ticket_id.partner_id.name,
                'partner_id': ticket_id.partner_id.id or False,
                'service_category_id': ticket_id.service_category_id.id or False,
                'service_type_id': ticket_id.service_type_id.id or False,
                'product_name': ticket_id.product_id.name,
                'custom_product_serial': ticket_id.stock_lot_id.id,
                'request_type_id': self.request_type_id.id or False,
                'child_ticket_id': self.child_ticket_id.id or False,
                'product_name': self.child_ticket_id.product_id.name,
                'custom_product_serial': self.child_ticket_id.stock_lot_id.name,
                'parent_ticket_id': self.parent_ticket_id.id or self.child_ticket_id.parent_ticket_id.id or False,
                'problem_reported': ticket_id.problem_description,
                'survey_id': ticket_id.survey_id.id,
                'dealer_distributor_name': ticket_id.dealer_distributor_id.name,
                'call_source_id': ticket_id.call_source_id.id,
                'requested_by_name': ticket_id.requested_by_name,
                'requested_by_contact_number': ticket_id.requested_by_contact_number,
                'call_received_id': ticket_id.call_received_id.id,
                'remarks': ticket_id.remarks,
                'oem_warranty_status_id': ticket_id.oem_warranty_status_id.id,
                'repair_warranty_status_id': ticket_id.repair_warranty_status_id.id,
                'product_part_number': ticket_id.cat_no,
                'product_part_code': ticket_id.product_code_no,
                'service_request_id_alias': ticket_id.parent_ticket_id_alias,
                'customer_asset_ids': [(0, 0, {
                    'stock_lot_id': ticket_id.stock_lot_id.id,
                    'product_id': ticket_id.product_id.id,
                })]

            }
            service = self.env['service.request'].sudo().create(context)
            service._onchange_partner()

            return {
                'type': 'ir.actions.act_window',
                'name': 'Service Request',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view.id,
                'res_model': 'service.request',
                'target': 'current',
                "context": {'default_request_type_id': self.request_type_id.id},
            }
