from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response
from odoo import http
from odoo.http import request
import json
import logging
_logger = logging.getLogger(__name__)

class APIController(http.Controller):

    @validate_token
    @http.route("/api/create_installation", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_create_installation(self, **post):
        installation_obj = request.env['project.task']
        installation_state = installation_obj.sudo().fields_get(allfields=['installation_state'])['installation_state']['selection']

        service_category_obj = request.env['service.category'].sudo().search([])
        service_category_value = [{'name': field.name, 'id': field.id, 'string': 'Service Category'} for field in
                                  service_category_obj]

        service_type_obj = request.env['service.type'].sudo().search([])
        service_type_value = [{'name': field.name, 'id': field.id, 'string': 'Service Type'} for field in
                              service_type_obj]
        parent_ticket_obj = request.env['parent.ticket'].sudo().search([])
        parent_ticket_value = [{'name': field.name, 'id': field.id, 'string': 'Parent Ticket ID'} for field in
                              parent_ticket_obj]

        child_ticket_obj = request.env['child.ticket'].sudo().search([])
        child_ticket_value = [{'name': field.name, 'id': field.id, 'string': 'Child Ticket ID'} for field in
                              child_ticket_obj]

        child_ticket_type_obj = request.env['child.ticket.type'].sudo().search([])
        child_ticket_type_value = [{'name': field.name, 'id': field.id, 'string': '	Child Ticket Type'} for field in
                              child_ticket_type_obj]

        request_type_obj = request.env['request.type'].sudo().search([])
        request_type_value = [{'name': field.name, 'id': field.id, 'string': 'Request Type'} for field in
                              request_type_obj]

        approver_obj = request.env['multi.approval.type'].sudo().search([])
        approver_value = [{'name': field.name, 'id': field.id, 'string': 'Approval Level'} for field in
                              approver_obj]

        stock_lot_obj = request.env['stock.lot'].sudo().search([])
        stock_lot_value = [{'name': field.name, 'id': field.id, 'string': 'Products/Assets'} for field in
                           stock_lot_obj]

        categ_obj = request.env['product.category'].sudo().search([])
        categ_value = [{'name': field.display_name, 'id': field.id, 'string': 'Product Categories'} for field in
                       categ_obj]

        tags_obj = request.env['sla.tags'].sudo().search([])
        tags_value = [{'name': field.display_name, 'id': field.id, 'string': 'Tags'} for field in
                       tags_obj]

        partner_obj = request.env['res.partner'].sudo().search([])
        partner_value = [{'name': field.name, 'id': field.id, 'string': 'Customer'} for
                                    field in partner_obj]
        company_obj = request.env['res.company'].sudo().search([])
        company_value = [{'name': field.name, 'id': field.id, 'string': 'Company'} for
                                    field in company_obj]
        user_obj = request.env['res.users'].sudo().search([])
        user_value = [{'name': field.name, 'id': field.id, 'string': 'Responsible'} for
                                    field in user_obj]
        team_obj = request.env['crm.team'].sudo().search([('is_service_request', '=', True)])
        team_value = [{'name': field.name, 'id': field.id, 'string': 'Team'} for field in team_obj]

        survery_obj= request.env['survey.survey'].sudo().search([])
        survey_value = [{'name': field.title, 'id': field.id, 'string': 'Worksheet'} for field in survery_obj]

        installation_list = []
        installation_list.append({
            'state': installation_state,
            'installation_service_category_id' : service_category_value,
            'installation_service_type_id' : service_type_value,
            'installation_parent_ticket_id' : parent_ticket_value,
            'installation_child_ticket_id': child_ticket_value,
            'installation_child_ticket_type' : child_ticket_type_value,
            'request_type_id' : request_type_value,
            'approver_id': approver_value,
            'installation_stock_lot_id' : stock_lot_value,
            'installation_categ_id': categ_value,
            'tag_ids': tags_value,
            'partner_id': partner_value, # installation customer account can user
            'company_id': company_value,
            'user_id': user_value,
            'team_id': team_value,
            'worksheet_id': survey_value,
        })

        return valid_response(installation_list, 'create installation load successfully', 200)

    @validate_token
    @http.route("/api/create_installation/submit", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_create_installation_submit(self, **post):
        post = json.loads(request.httprequest.data)
        try:
            values_list = []
            values_list.append({
                'team_id': int(post.get('team_id')),
                'request_type_id':int(post.get('request_type_id')),
                'company_id':int(post.get('company_id')),
                'user_id' : int(post.get('user_id')),
                'is_project_installation': post.get('is_project_installation'),
            })
            installation_ticket = request.env['project.task'].sudo().create(values_list)
            if installation_ticket:
                return valid_response([{'installation_ticket_name ': installation_ticket.name}], ' ticket create successfully',
                                      200)
        except Exception as e:
            info = "There was a problem {}".format((e))
            error = "Something went wrong"
            _logger.error(info)
            return invalid_response(info, error, 403)






