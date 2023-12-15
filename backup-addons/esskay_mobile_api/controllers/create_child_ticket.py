from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response
from odoo import http
from odoo.http import request
import json
import logging
_logger = logging.getLogger(__name__)

class APIController(http.Controller):
    @validate_token
    @http.route("/api/create_child_ticket", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_create_child_ticket(self, **post):
        child_ticket_obj = request.env['child.ticket']
        child_state = child_ticket_obj.sudo().fields_get(allfields=['state'])['state']['selection']

        mc_stk = child_ticket_obj.sudo().fields_get(allfields=['mc_stk'])['mc_stk']['selection']

        child_ticket_conf_obj = request.env['child.ticket.configuration'].sudo().search([])
        child_ticket_conf_value = [{'name': field.child_config_name, 'id': field.id, 'string': 'Child Configuration'} for field in child_ticket_conf_obj]

        call_source_obj = request.env['call.source'].sudo().search([])
        call_source_value = [{'name': field.name, 'id': field.id, 'string': 'Call Source'} for field in call_source_obj]

        service_category_obj = request.env['service.category'].sudo().search([])
        service_category_value = [{'name': field.name, 'id': field.id, 'string': 'Service Category'} for field in service_category_obj]

        service_type_obj = request.env['service.type'].sudo().search([])
        service_type_value = [{'name': field.name, 'id': field.id, 'string': 'Service Type'} for field in service_type_obj]

        request_type_obj = request.env['request.type'].sudo().search([])
        request_type_value = [{'name': field.name, 'id': field.id, 'string': 'Request Type'} for field in request_type_obj]

        call_received_obj = request.env['call.received'].sudo().search([])
        call_received_value = [{'name': field.name, 'id': field.id, 'string': 'Call Received by'} for field in call_received_obj]

        team_obj = request.env['crm.team'].sudo().search([('is_service_request', '=', True)])
        team_value = [{'name': field.name, 'id': field.id, 'string': 'Team'} for field in team_obj]

        product_obj = request.env['product.product'].sudo().search([])
        product_value = [{'name': field.name, 'id': field.id, 'string': 'Product'} for field in product_obj]

        stock_lot_obj = request.env['stock.lot'].sudo().search([])
        stock_lot_value = [{'name': field.name, 'id': field.id, 'string': 'Asset / Product Serial Number'} for field in stock_lot_obj]

        categ_obj = request.env['product.category'].sudo().search([])
        categ_value = [{'name': field.display_name, 'id': field.id, 'string': 'Product Category ID'} for field in categ_obj]

        partner_obj = request.env['res.partner'].sudo().search([('is_block_partner', '=','not_blocked')])
        partner_value = [{'name': field.name, 'id': field.id, 'string': 'Customer'} for field in partner_obj]

        customer_account_obj = request.env['res.partner'].sudo().search([('customer_rank','>',0)])
        customer_account_value = [{'name': field.name, 'id': field.id, 'string': 'Customer Account'} for field in customer_account_obj]

        dealer_distributor_obj = request.env['res.partner'].sudo().search([])
        dealer_distributor_value = [{'name': field.name, 'id': field.id, 'string': 'Dealer / Distributor Name'} for field in dealer_distributor_obj]

        oem_warranty_status_obj = request.env['oem.warranty.status'].sudo().search([])
        oem_warranty_status_value = [{'name': field.name, 'id': field.id, 'string': 'OEM Warranty Status (As per customer)'} for field in
            oem_warranty_status_obj]



        child_list=[]
        child_list.append({
            'state': child_state,
            'child_configuration_id' : child_ticket_conf_value,
            'child_ticket_type_id' : None,
            'partner_id': partner_value,
            'call_source_id' : call_source_value,
            'request_type_id': request_type_value,
            'service_category_id' : service_category_value,
            'service_type_id' : service_type_value,
            'product_id': product_value,
            'stock_lot_id': stock_lot_value,
            'categ_id': categ_value,
            'dealer_distributor_id': dealer_distributor_value,
            'call_received_id' : call_received_value,
            'oem_warranty_status_id': oem_warranty_status_value,
            'repair_warranty_status_id':None,
            'team_id' : team_value,
            'customer_account_id': customer_account_value,
            'mc_stk': mc_stk

        })

        return valid_response(child_list, 'Child Ticket create load successfully', 200)

    @validate_token
    @http.route("/api/create_child_ticket/submit", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_create_child_ticket_submit(self, **post):
        post = json.loads(request.httprequest.data)
        try:
            values_list = []
            values_list.append({
                'team_id': int(post.get('team_id')),
                'request_type_id': int(post.get('request_type_id')),
            })
            parent_ticket = request.env['child.ticket'].sudo().create(values_list)
            if parent_ticket:
                return valid_response([{'child_ticket_name ': parent_ticket.name}], 'child ticket create successfully',
                                      200)
        except Exception as e:
            info = "There was a problem {}".format((e))
            error = "Something went wrong"
            _logger.error(info)
            return invalid_response(info, error, 403)



