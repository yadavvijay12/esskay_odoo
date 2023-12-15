from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token,magic_fields
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response,valid_response1,valid_response2
from odoo import http
from odoo.http import request
import json
import pytz
from datetime import datetime , timezone,timedelta
import logging
_logger = logging.getLogger(__name__)

fields = ['activity_type_id', 'activity_ids', 'message_follower_ids', 'message_ids',
                  'message_main_attachment_id', 'website_message_ids', 'name', 'service_request_id_alias',
                  'customer_name', 'dealer_distributor_name', 'state', 'call_source_id', 'service_category_id',
                  'service_type_id', 'request_type_id', 'problem_reported', 'product_name', 'custom_product_serial',
                  'model', 'product_category_id', 'product_category_alias', 'requested_by_name',
                  'requested_by_contact_number', 'call_received_id', 'external_reference', 'remarks', 'issue_noticed',
                  'case_completed_successfully_id', 'medical_intervention_id', 'patient_involved_id',
                  'surgical_delay_id', 'bio_medical_engineer_id', 'service_request_status_id', 'team_id',
                  'dispatch_location_id', 'oem_warranty_status_id', 'repair_warranty_status_id', 'survey_id',
                  'company_id', 'partner_id', 'street', 'street2', 'zip', 'state_id', 'country_id', 'phone', 'mobile',
                  'email', 'description', 'customer_email', 'customer_street', 'customer_street2', 'customer_zip',
                  'customer_state_id', 'customer_country_id', 'user_id', 'service_properties', 'dealer_distributor_id',
                  'child_ticket_id', 'parent_ticket_id', 'approver_id', 'is_parent_ticket_created',
                  'is_child_ticket_created', 'approver_ids', 'close_reason', 'is_check_available',
                  'product_part_number', 'product_part_code', 'location_contact_person', 'customer_po_number',
                  'invoice_number', 'tender_refer_number', 'extended_invoice_number', 'install_addr_street',
                  'install_addr_street2', 'install_addr_zip', 'install_addr_state_id', 'install_addr_country_id',
                  'reason', 'customer_asset_ids', 'customer_city_id', 'city_id', 'customer_type_id',
                  'customer_region_id', 'gst_no', 'tier_tier_id', 'hospital_name', 'surgeon_name', 'customer_group_id',
                  'customer_id_alias', 'd_number', 'c_number', 'customer_id', 'stock_production_lot_id',
                  'maintenance_id', 'wr_id','requested_by_name','install_addr_street']
class APIController(http.Controller):

    @validate_token
    @http.route("/api/get_service_values", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_service_request_details(self, **post, ):
        post = json.loads(request.httprequest.data)
        user = request.env.user.browse(post.get('uid'))
        limit = post.get('limit')
        next_count = post.get('next_count')
        Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
        CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
        Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
            'ppts_service_request.service_request_group_manager')
        National_Head = user.has_group('ppts_service_request.service_request_national_head')

        domain = []
        if CT_Users:
            domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
        elif Show_Service_Request_Service_Engineer:
            domain += [('user_id', '=', user.id)]
        elif Manager_CT_Repair_Manager_Service_Manager_RSM:
            domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
        elif National_Head:
            domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
        else:
            domain += [('id', '=', False)]
        service_request_obj = request.env['service.request']
        count = service_request_obj.sudo().search_count(domain)
        service_request_ids = service_request_obj.sudo().search(domain,offset=next_count , limit=limit , order='name desc')
        service_request_list=[]
        for rec in service_request_ids:
            id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                  'value': rec.id if rec.id else ''}
            name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                  'value': rec.name if rec.name else ''}
            service_request_id_alias = {'key': 'service_request_id_alias', 'type': rec._fields['service_request_id_alias'].type, 'title': rec._fields['service_request_id_alias'].string,
                  'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
            service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type, 'title': rec._fields['service_request_date'].string,
                  'value': str(rec.service_request_date) if rec.service_request_date else ''}
            call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type, 'title': rec._fields['call_source_id'].string,
                  'value': rec.call_source_id.name if rec.call_source_id else ''}
            service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type, 'title': rec._fields['service_type_id'].string,
                  'value': rec.service_type_id.name if rec.service_type_id else ''}
            service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type, 'title': rec._fields['service_category_id'].string,
                  'value': rec.service_category_id.name if rec.service_category_id else ''}
            request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type, 'title': rec._fields['request_type_id'].string,
                  'value': rec.request_type_id.name if rec.request_type_id else ''}
            reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
                  'value': rec.reason if rec.reason else ''}
            requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type, 'title': rec._fields['requested_by_name'].string,
                  'value': rec.requested_by_name if rec.requested_by_name else ''}
            call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type, 'title': rec._fields['call_received_id'].string,
                  'value': rec.call_received_id.name if rec.call_received_id else ''}
            team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type,'title': rec._fields['team_id'].string,
                                'value': rec.team_id.name if rec.team_id else ''}
            oem_warranty_status_id = {'key': 'oem_warranty_status_id', 'type': rec._fields['oem_warranty_status_id'].type,'title': rec._fields['oem_warranty_status_id'].string,
                                'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
            repair_warranty_status_id = {'key': 'repair_warranty_status_id', 'type': rec._fields['repair_warranty_status_id'].type,'title': rec._fields['repair_warranty_status_id'].string,
                                'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
            remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type,'title': rec._fields['remarks'].string,
                                'value': rec.remarks if rec.remarks else ''}
            user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type,'title': rec._fields['user_id'].string,
                                'value': rec.user_id.name if rec.user_id else ''}
            service_request_list.append([id,name,service_request_id_alias,service_request_date,call_source_id,service_type_id,
                    service_category_id,request_type_id,reason,requested_by_name,call_received_id,team_id,oem_warranty_status_id,
                                         repair_warranty_status_id,remarks,user_id
                                         ])
        if service_request_list:
            return valid_response1(service_request_list, count, 'service request loaded successfully', 200)
        else:
            return valid_response1(service_request_list,count, 'there is no service request record', 200)

    @validate_token
    @http.route("/api/get_service_request_values/ticket_type", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_service_request_types(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('/api/get_service_request_values/ticket_type: %s' % post)
        limit = post.get('limit')
        next_count = post.get('next_count')
        ticket_type = post.get('ticket_type')
        request_type_code = post.get('code')
        search_value = post.get('search_value')
        service_request_id = post.get('id')
        service_request_ids= post.get('ids')
        state_filter = post.get('state_filter')
        user = request.env.user.browse(post.get('uid'))
        user_tz = user.tz or 'UTC'
        local_tz = pytz.timezone(user_tz)
        _logger.info('@user time zoneeeeeeeee :%s', user_tz)
        Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
        CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
        Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
            'ppts_service_request.service_request_group_manager')
        National_Head = user.has_group('ppts_service_request.service_request_national_head')
        company_id = request.env.company.id
        domain = [('company_id','=',company_id)]
        if state_filter and state_filter != 'all':
            domain += [('state', '=', state_filter)]
        if ticket_type and ticket_type!='sr_all':
            domain += [('request_type_id.ticket_type','=',ticket_type)]
        if search_value:
            domain += [('name','ilike',search_value)]
        if service_request_id:
            domain += [('id', '=', int(service_request_id))]
        if service_request_ids:
            domain += [('id', 'in', list(service_request_ids))]
        if request_type_code:
            domain += [('request_type_id.code','=',request_type_code)]
        if CT_Users:
            domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
        elif Show_Service_Request_Service_Engineer:
            domain += ['|',('user_id', '=', user.id),('assign_engineer_ids','=',user.id)]
        elif Manager_CT_Repair_Manager_Service_Manager_RSM:
            domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
        elif National_Head:
            domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
        else:
            domain += [('id', '=', False)]
        service_request_obj = request.env['service.request']
        count = service_request_obj.sudo().search_count(domain)
        service_request_ids = service_request_obj.sudo().search(domain,offset=next_count , limit=limit , order='name desc')
        state_value_all = dict(service_request_obj._fields['state'].selection)
        filter_state = [{'id': field,
                         'value': state_value_all.get(field), }
                        for field in state_value_all]
        filter_state.insert(0, {'id': 'all', 'value': "ALL"})
        service_request_list=[]
        message =""
        if ticket_type == 'sr_loaner':
            message = "SR-Loaner load successfully"
            for rec in service_request_ids:
                id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                      'value': rec.id if rec.id else ''}
                name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                      'value': rec.name if rec.name else ''}
                state = {'key': 'state', 'type': rec._fields['state'].type,'title': rec._fields['state'].string,
                    'value':dict(rec._fields['state'].selection).get(rec.state)}
                # SERVICE REQUEST INFORMATION
                service_request_id_alias = {'key': 'service_request_id_alias', 'type': rec._fields['service_request_id_alias'].type, 'title': rec._fields['service_request_id_alias'].string,
                      'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
                service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type, 'title': rec._fields['service_request_date'].string,
                      'value': str(rec.service_request_date.astimezone(local_tz).replace(tzinfo=None).strftime('%Y-%m-%d %I:%M %p')) if rec.service_request_date else ''}
                approver_id = {'key': 'approver_id', 'type': rec._fields['approver_id'].type,
                                  'title': rec._fields['approver_id'].string,
                                  'value': rec.approver_id.name if rec.approver_id else ''}
                parent_ticket_id = {'key': 'parent_ticket_id', 'type': rec._fields['parent_ticket_id'].type, 'title': rec._fields['parent_ticket_id'].string,
                      'value': rec.parent_ticket_id.name if rec.parent_ticket_id else ''}
                child_ticket_id = {'key': 'child_ticket_id', 'type': rec._fields['child_ticket_id'].type, 'title': rec._fields['child_ticket_id'].string,
                      'value': rec.child_ticket_id.name if rec.child_ticket_id else ''}
                child_ticket_type_id = {'key': 'child_ticket_type_id', 'type': rec._fields['child_ticket_type_id'].type, 'title': rec._fields['child_ticket_type_id'].string,
                      'value': rec.child_ticket_type_id.name if rec.child_ticket_type_id else ''}

                # CALL DETAILS
                call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type, 'title': rec._fields['call_source_id'].string,
                      'value': rec.call_source_id.name if rec.call_source_id else ''}
                service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type, 'title': rec._fields['service_type_id'].string,
                      'value': rec.service_type_id.name if rec.service_type_id else ''}
                service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type, 'title': rec._fields['service_category_id'].string,
                      'value': rec.service_category_id.name if rec.service_category_id else ''}
                request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type, 'title': rec._fields['request_type_id'].string,
                      'value': rec.request_type_id.name if rec.request_type_id else ''}

                reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
                      'value': rec.reason if rec.reason else ''}
                requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type, 'title': rec._fields['requested_by_name'].string,
                      'value': rec.requested_by_name if rec.requested_by_name else ''}
                call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type, 'title': rec._fields['call_received_id'].string,
                      'value': rec.call_received_id.name if rec.call_received_id else ''}
                team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type,'title': rec._fields['team_id'].string,
                                    'value': rec.team_id.name if rec.team_id else ''}
                # ASSET DETAILS
                oem_warranty_status_id = {'key': 'oem_warranty_status_id', 'type': rec._fields['oem_warranty_status_id'].type,'title': rec._fields['oem_warranty_status_id'].string,
                                    'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
                repair_warranty_status_id = {'key': 'repair_warranty_status_id', 'type': rec._fields['repair_warranty_status_id'].type,'title': rec._fields['repair_warranty_status_id'].string,
                                    'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
                # OTHER INFORMATION
                remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type,'title': rec._fields['remarks'].string,
                                    'value': rec.remarks if rec.remarks else ''}
                survey_id = {'key': 'survey_id', 'type': rec._fields['survey_id'].type,'title': rec._fields['survey_id'].string,
                                    'value': rec.survey_id.title if rec.survey_id else ''}
                user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type,'title': rec._fields['user_id'].string,
                                    'value': rec.user_id.name if rec.user_id else ''}
                service_request_list.append([id,name,state,service_request_id_alias,service_request_date,approver_id,parent_ticket_id,child_ticket_id,
                        child_ticket_type_id,call_source_id,service_type_id,
                        service_category_id,request_type_id,reason,requested_by_name,call_received_id,team_id,oem_warranty_status_id,
                                             repair_warranty_status_id,remarks,survey_id,user_id
                                             ])
                service_request_list_len = len(service_request_list) - 1
                if rec.state in ['draft']:
                    service_request_list[service_request_list_len].append(
                        {'key': 'submit', 'type': "button",
                         'title': 'Submit',
                         'value': 'Submit',
                         })
        elif ticket_type == 'sr_wr':
            message = "SR-Warranty Replacement load successfully"
            for rec in service_request_ids:
                id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                      'value': rec.id if rec.id else ''}
                name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                      'value': rec.name if rec.name else ''}
                state = {'key': 'state', 'type': rec._fields['state'].type, 'title': rec._fields['state'].string,
                         'value': dict(rec._fields['state'].selection).get(rec.state)}
                # SERVICE REQUEST INFORMATION
                service_request_id_alias = {'key': 'service_request_id_alias', 'type': rec._fields['service_request_id_alias'].type, 'title': rec._fields['service_request_id_alias'].string,
                      'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
                service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type, 'title': rec._fields['service_request_date'].string,
                      'value': str(rec.service_request_date.astimezone(local_tz).replace(tzinfo=None).strftime('%Y-%m-%d %I:%M %p')) if rec.service_request_date else ''}
                approver_id = {'key': 'approver_id', 'type': rec._fields['approver_id'].type,
                               'title': rec._fields['approver_id'].string,
                               'value': rec.approver_id.name if rec.approver_id else ''}
                parent_ticket_id = {'key': 'parent_ticket_id', 'type': rec._fields['parent_ticket_id'].type,
                                    'title': rec._fields['parent_ticket_id'].string,
                                    'value': rec.parent_ticket_id.name if rec.parent_ticket_id else ''}
                child_ticket_id = {'key': 'child_ticket_id', 'type': rec._fields['child_ticket_id'].type,
                                   'title': rec._fields['child_ticket_id'].string,
                                   'value': rec.child_ticket_id.name if rec.child_ticket_id else ''}
                child_ticket_type_id = {'key': 'child_ticket_type_id', 'type': rec._fields['child_ticket_type_id'].type,
                                        'title': rec._fields['child_ticket_type_id'].string,
                                        'value': rec.child_ticket_type_id.name if rec.child_ticket_type_id else ''}
                # CALL DETAILS
                call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type, 'title': rec._fields['call_source_id'].string,
                      'value': rec.call_source_id.name if rec.call_source_id else ''}
                service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type, 'title': rec._fields['service_type_id'].string,
                      'value': rec.service_type_id.name if rec.service_type_id else ''}
                service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type, 'title': rec._fields['service_category_id'].string,
                      'value': rec.service_category_id.name if rec.service_category_id else ''}
                request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type, 'title': rec._fields['request_type_id'].string,
                      'value': rec.request_type_id.name if rec.request_type_id else ''}
                reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
                      'value': rec.reason if rec.reason else ''}
                requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type, 'title': rec._fields['requested_by_name'].string,
                      'value': rec.requested_by_name if rec.requested_by_name else ''}
                call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type, 'title': rec._fields['call_received_id'].string,
                      'value': rec.call_received_id.name if rec.call_received_id else ''}
                team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type,'title': rec._fields['team_id'].string,
                                    'value': rec.team_id.name if rec.team_id else ''}
                # ASSET DETAILS
                oem_warranty_status_id = {'key': 'oem_warranty_status_id', 'type': rec._fields['oem_warranty_status_id'].type,'title': rec._fields['oem_warranty_status_id'].string,
                                    'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
                repair_warranty_status_id = {'key': 'repair_warranty_status_id', 'type': rec._fields['repair_warranty_status_id'].type,'title': rec._fields['repair_warranty_status_id'].string,
                                    'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
                # OTHER INFORMATION
                remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type,'title': rec._fields['remarks'].string,
                                    'value': rec.remarks if rec.remarks else ''}
                user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type,'title': rec._fields['user_id'].string,
                                    'value': rec.user_id.name if rec.user_id else ''}
                survey_id = {'key': 'survey_id', 'type': rec._fields['survey_id'].type,'title': rec._fields['survey_id'].string,
                                    'value': rec.survey_id.title if rec.survey_id else ''}
                service_request_list.append([id,name,state,service_request_id_alias,service_request_date,approver_id,call_source_id,parent_ticket_id,
                                             child_ticket_id,child_ticket_type_id,service_type_id,
                        service_category_id,request_type_id,reason,requested_by_name,call_received_id,team_id,oem_warranty_status_id,
                                             repair_warranty_status_id,remarks,user_id,survey_id
                                             ])
                service_request_list_len = len(service_request_list) - 1
                if rec.state in ['draft']:
                    service_request_list[service_request_list_len].append(
                        {'key': 'submit', 'type': "button",
                         'title': 'Submit',
                         'value': 'Submit',
                         })
        elif ticket_type == 'sr_factory_repair':
            message = "SR-Factory Repair load successfully"
            for rec in service_request_ids:
                id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                      'value': rec.id if rec.id else ''}
                name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                      'value': rec.name if rec.name else ''}
                state = {'key': 'state', 'type': rec._fields['state'].type, 'title': rec._fields['state'].string,
                         'value': dict(rec._fields['state'].selection).get(rec.state)}
                # SERVICE REQUEST INFORMATION
                service_request_id_alias = {'key': 'service_request_id_alias', 'type': rec._fields['service_request_id_alias'].type, 'title': rec._fields['service_request_id_alias'].string,
                      'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
                service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type, 'title': rec._fields['service_request_date'].string,
                      'value': str(rec.service_request_date.astimezone(local_tz).replace(tzinfo=None).strftime('%Y-%m-%d %I:%M:%S %p')) if rec.service_request_date else ''}
                approver_id = {'key': 'approver_id', 'type': rec._fields['approver_id'].type,
                               'title': rec._fields['approver_id'].string,
                               'value': rec.approver_id.name if rec.approver_id else ''}
                parent_ticket_id = {'key': 'parent_ticket_id', 'type': rec._fields['parent_ticket_id'].type,
                                    'title': rec._fields['parent_ticket_id'].string,
                                    'value': rec.parent_ticket_id.name if rec.parent_ticket_id else ''}
                child_ticket_id = {'key': 'child_ticket_id', 'type': rec._fields['child_ticket_id'].type,
                                   'title': rec._fields['child_ticket_id'].string,
                                   'value': rec.child_ticket_id.name if rec.child_ticket_id else ''}
                child_ticket_type_id = {'key': 'child_ticket_type_id', 'type': rec._fields['child_ticket_type_id'].type,
                                        'title': rec._fields['child_ticket_type_id'].string,
                                        'value': rec.child_ticket_type_id.name if rec.child_ticket_type_id else ''}
                # CALL DETAILS
                call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type, 'title': rec._fields['call_source_id'].string,
                      'value': rec.call_source_id.name if rec.call_source_id else ''}
                service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type, 'title': rec._fields['service_type_id'].string,
                      'value': rec.service_type_id.name if rec.service_type_id else ''}
                service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type, 'title': rec._fields['service_category_id'].string,
                      'value': rec.service_category_id.name if rec.service_category_id else ''}
                request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type, 'title': rec._fields['request_type_id'].string,
                      'value': rec.request_type_id.name if rec.request_type_id else ''}
                reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
                      'value': rec.reason if rec.reason else ''}
                problem_reported = {'key': 'problem_reported', 'type': rec._fields['problem_reported'].type, 'title': rec._fields['problem_reported'].string,
                      'value': rec.problem_reported if rec.problem_reported else ''}
                requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type, 'title': rec._fields['requested_by_name'].string,
                      'value': rec.requested_by_name if rec.requested_by_name else ''}
                requested_by_contact_number = {'key': 'requested_by_contact_number', 'type': rec._fields['requested_by_contact_number'].type, 'title': rec._fields['requested_by_contact_number'].string,
                      'value': rec.requested_by_contact_number if rec.requested_by_contact_number else ''}
                call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type, 'title': rec._fields['call_received_id'].string,
                      'value': rec.call_received_id.name if rec.call_received_id else ''}
                team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type,'title': rec._fields['team_id'].string,
                                    'value': rec.team_id.name if rec.team_id else ''}
                #OTHER INFORMATION
                remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type,
                           'title': rec._fields['remarks'].string,
                           'value': rec.remarks if rec.remarks else ''}
                # CUSTOMER INFORMATION
                customer_name = {'key': 'customer_name', 'type': rec._fields['customer_name'].type,
                           'title': rec._fields['customer_name'].string,'value': rec.customer_name if rec.customer_name else ''}
                customer_email = {'key': 'customer_email', 'type': rec._fields['customer_email'].type,
                           'title': rec._fields['customer_email'].string,'value': rec.customer_email if rec.customer_email else ''}
                customer_street = {'key': 'customer_street', 'type': rec._fields['customer_street'].type,
                           'title': rec._fields['customer_street'].string,'value': rec.customer_street if rec.customer_street else ''}
                customer_street2 = {'key': 'customer_street2', 'type': rec._fields['customer_street2'].type,
                           'title': rec._fields['customer_street2'].string,'value': rec.customer_street2 if rec.customer_street2 else ''}
                customer_city_id = {'key': 'customer_city_id', 'type': rec._fields['customer_city_id'].type,'title': rec._fields['customer_city_id'].string,
                                    'value': rec.customer_city_id.name if rec.customer_city_id else ''}
                customer_state_id = {'key': 'customer_state_id', 'type': rec._fields['customer_state_id'].type,'title': rec._fields['customer_state_id'].string,
                                    'value': rec.customer_state_id.name if rec.customer_state_id else ''}
                customer_zip = {'key': 'customer_zip', 'type': rec._fields['customer_zip'].type,'title': rec._fields['customer_zip'].string,
                                    'value': rec.customer_zip if rec.customer_zip else ''}
                customer_country_id = {'key': 'customer_country_id', 'type': rec._fields['customer_country_id'].type,'title': rec._fields['customer_country_id'].string,
                                    'value': rec.customer_country_id.name if rec.customer_country_id else ''}
                dealer_distributor_name = {'key': 'dealer_distributor_name',
                                           'type': rec._fields['dealer_distributor_name'].type,
                                           'title': rec._fields['dealer_distributor_name'].string,
                                           'value': rec.dealer_distributor_name if rec.dealer_distributor_name else ''}

                # ASSET DETAILS
                product_name = {'key': 'product_name', 'type': rec._fields['product_name'].type,'title': rec._fields['product_name'].string,
                                    'value': rec.product_name if rec.product_name else ''}
                custom_product_serial = {'key': 'custom_product_serial', 'type': rec._fields['custom_product_serial'].type,'title': rec._fields['custom_product_serial'].string,
                                    'value': rec.custom_product_serial if rec.custom_product_serial else ''}
                product_part_number = {'key': 'product_part_number', 'type': rec._fields['product_part_number'].type,'title': rec._fields['product_part_number'].string,
                                    'value': rec.product_part_number if rec.product_part_number else ''}
                product_part_code = {'key': 'product_part_code', 'type': rec._fields['product_part_code'].type,'title': rec._fields['product_part_code'].string,
                                    'value': rec.product_part_code if rec.product_part_code else ''}
                oem_warranty_status_id = {'key': 'oem_warranty_status_id', 'type': rec._fields['oem_warranty_status_id'].type,'title': rec._fields['oem_warranty_status_id'].string,
                                    'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
                repair_warranty_status_id = {'key': 'repair_warranty_status_id', 'type': rec._fields['repair_warranty_status_id'].type,'title': rec._fields['repair_warranty_status_id'].string,
                                    'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
                # OTHER INFORMATION
                survey_id = {'key': 'survey_id', 'type': rec._fields['survey_id'].type,
                             'title': rec._fields['survey_id'].string,
                             'value': rec.survey_id.title if rec.survey_id else ''}
                company_id = {'key': 'company_id', 'type': rec._fields['company_id'].type,'title': rec._fields['company_id'].string,
                                    'value': rec.company_id.name if rec.company_id else ''}
                user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type,'title': rec._fields['user_id'].string,
                                    'value': rec.user_id.name if rec.user_id else ''}
                service_request_list.append([id,name,state,service_request_id_alias,service_request_date,approver_id,
                        parent_ticket_id,child_ticket_id,child_ticket_type_id,call_source_id,service_type_id,
                        service_category_id,request_type_id,reason,problem_reported,requested_by_name,
                        requested_by_contact_number,call_received_id,team_id,remarks,customer_name,customer_email,
                        customer_street,customer_street2,customer_city_id,customer_state_id,customer_zip,
                        customer_country_id,dealer_distributor_name,product_name,custom_product_serial,
                        product_part_number,product_part_code,oem_warranty_status_id,repair_warranty_status_id,
                        survey_id,user_id,company_id
                                             ])
                service_request_list_len = len(service_request_list) - 1
                if rec.state in ['draft']:
                    service_request_list[service_request_list_len].append(
                        {'key': 'submit', 'type': "button",
                         'title': 'Submit',
                         'value': 'Submit',
                         })
        elif ticket_type == 'sr_fsm':
            message = "SR-FSM load successfully"
            for rec in service_request_ids:
                id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                      'value': rec.id if rec.id else ''}
                name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                        'value': rec.name if rec.name else ''}
                state = {'key': 'state', 'type': rec._fields['state'].type, 'title': rec._fields['state'].string,
                         'value': dict(rec._fields['state'].selection).get(rec.state)}
                # SERVICE REQUEST INFORMATION
                service_request_id_alias = {'key': 'service_request_id_alias',
                                            'type': rec._fields['service_request_id_alias'].type,
                                            'title': rec._fields['service_request_id_alias'].string,
                                            'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
                service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type,
                                        'title': rec._fields['service_request_date'].string,
                                        'value': str(rec.service_request_date.astimezone(local_tz).replace(tzinfo=None).strftime('%Y-%m-%d %I:%M %p')) if rec.service_request_date else ''}
                approver_id = {'key': 'approver_id', 'type': rec._fields['approver_id'].type,
                               'title': rec._fields['approver_id'].string,
                               'value': rec.approver_id.name if rec.approver_id else ''}
                parent_ticket_id = {'key': 'parent_ticket_id', 'type': rec._fields['parent_ticket_id'].type,
                                    'title': rec._fields['parent_ticket_id'].string,
                                    'value': rec.parent_ticket_id.name if rec.parent_ticket_id else ''}
                child_ticket_id = {'key': 'child_ticket_id', 'type': rec._fields['child_ticket_id'].type,
                                   'title': rec._fields['child_ticket_id'].string,
                                   'value': rec.child_ticket_id.name if rec.child_ticket_id else ''}
                child_ticket_type_id = {'key': 'child_ticket_type_id', 'type': rec._fields['child_ticket_type_id'].type,
                                        'title': rec._fields['child_ticket_type_id'].string,
                                        'value': rec.child_ticket_type_id.name if rec.child_ticket_type_id else ''}
                # CALL DETAILS
                call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
                                  'title': rec._fields['call_source_id'].string,
                                  'value': rec.call_source_id.name if rec.call_source_id else ''}
                service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
                                   'title': rec._fields['service_type_id'].string,
                                   'value': rec.service_type_id.name if rec.service_type_id else ''}
                service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
                                       'title': rec._fields['service_category_id'].string,
                                       'value': rec.service_category_id.name if rec.service_category_id else ''}
                request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
                                   'title': rec._fields['request_type_id'].string,
                                   'value': rec.request_type_id.name if rec.request_type_id else ''}
                reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
                          'value': rec.reason if rec.reason else ''}
                problem_reported = {'key': 'problem_reported', 'type': rec._fields['problem_reported'].type,
                                    'title': rec._fields['problem_reported'].string,
                                    'value': rec.problem_reported if rec.problem_reported else ''}
                requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type,
                                     'title': rec._fields['requested_by_name'].string,
                                     'value': rec.requested_by_name if rec.requested_by_name else ''}
                requested_by_contact_number = {'key': 'requested_by_contact_number',
                                               'type': rec._fields['requested_by_contact_number'].type,
                                               'title': rec._fields['requested_by_contact_number'].string,
                                               'value': rec.requested_by_contact_number if rec.requested_by_contact_number else ''}
                call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
                                    'title': rec._fields['call_received_id'].string,
                                    'value': rec.call_received_id.name if rec.call_received_id else ''}
                team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type,
                           'title': rec._fields['team_id'].string,
                           'value': rec.team_id.name if rec.team_id else ''}
                # OTHER INFORMATION
                remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type,
                           'title': rec._fields['remarks'].string,
                           'value': rec.remarks if rec.remarks else ''}
                # CUSTOMER INFORMATION
                customer_name = {'key': 'customer_name', 'type': rec._fields['customer_name'].type,
                                 'title': rec._fields['customer_name'].string,
                                 'value': rec.customer_name if rec.customer_name else ''}
                customer_email = {'key': 'customer_email', 'type': rec._fields['customer_email'].type,
                                  'title': rec._fields['customer_email'].string,
                                  'value': rec.customer_email if rec.customer_email else ''}
                customer_street = {'key': 'customer_street', 'type': rec._fields['customer_street'].type,
                                   'title': rec._fields['customer_street'].string,
                                   'value': rec.customer_street if rec.customer_street else ''}
                customer_street2 = {'key': 'customer_street2', 'type': rec._fields['customer_street2'].type,
                                    'title': rec._fields['customer_street2'].string,
                                    'value': rec.customer_street2 if rec.customer_street2 else ''}
                customer_city_id = {'key': 'customer_city_id', 'type': rec._fields['customer_city_id'].type,
                                    'title': rec._fields['customer_city_id'].string,
                                    'value': rec.customer_city_id.name if rec.customer_city_id else ''}
                customer_state_id = {'key': 'customer_state_id', 'type': rec._fields['customer_state_id'].type,
                                     'title': rec._fields['customer_state_id'].string,
                                     'value': rec.customer_state_id.name if rec.customer_state_id else ''}
                customer_zip = {'key': 'customer_zip', 'type': rec._fields['customer_zip'].type,
                                'title': rec._fields['customer_zip'].string,
                                'value': rec.customer_zip if rec.customer_zip else ''}
                customer_country_id = {'key': 'customer_country_id', 'type': rec._fields['customer_country_id'].type,
                                       'title': rec._fields['customer_country_id'].string,
                                       'value': rec.customer_country_id.name if rec.customer_country_id else ''}
                dealer_distributor_name = {'key': 'dealer_distributor_name',
                                           'type': rec._fields['dealer_distributor_name'].type,
                                           'title': rec._fields['dealer_distributor_name'].string,
                                           'value': rec.dealer_distributor_name if rec.dealer_distributor_name else ''}

                # ASSET DETAILS
                product_name = {'key': 'product_name', 'type': rec._fields['product_name'].type,
                                'title': rec._fields['product_name'].string,
                                'value': rec.product_name if rec.product_name else ''}
                custom_product_serial = {'key': 'custom_product_serial',
                                         'type': rec._fields['custom_product_serial'].type,
                                         'title': rec._fields['custom_product_serial'].string,
                                         'value': rec.custom_product_serial if rec.custom_product_serial else ''}
                product_part_number = {'key': 'product_part_number', 'type': rec._fields['product_part_number'].type,
                                       'title': rec._fields['product_part_number'].string,
                                       'value': rec.product_part_number if rec.product_part_number else ''}
                product_part_code = {'key': 'product_part_code', 'type': rec._fields['product_part_code'].type,
                                     'title': rec._fields['product_part_code'].string,
                                     'value': rec.product_part_code if rec.product_part_code else ''}
                oem_warranty_status_id = {'key': 'oem_warranty_status_id',
                                          'type': rec._fields['oem_warranty_status_id'].type,
                                          'title': rec._fields['oem_warranty_status_id'].string,
                                          'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
                repair_warranty_status_id = {'key': 'repair_warranty_status_id',
                                             'type': rec._fields['repair_warranty_status_id'].type,
                                             'title': rec._fields['repair_warranty_status_id'].string,
                                             'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
                # OTHER INFORMATION
                survey_id = {'key': 'survey_id', 'type': rec._fields['survey_id'].type,
                             'title': rec._fields['survey_id'].string,
                             'value': rec.survey_id.title if rec.survey_id else ''}
                company_id = {'key': 'company_id', 'type': rec._fields['company_id'].type,
                              'title': rec._fields['company_id'].string,
                              'value': rec.company_id.name if rec.company_id else ''}
                user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type,
                           'title': rec._fields['user_id'].string,
                           'value': rec.user_id.name if rec.user_id else ''}
                service_request_list.append([id, name,state, service_request_id_alias, service_request_date, approver_id,
                                             parent_ticket_id, child_ticket_id, child_ticket_type_id, call_source_id,
                                             service_type_id,
                                             service_category_id, request_type_id, reason, problem_reported,
                                             requested_by_name,
                                             requested_by_contact_number, call_received_id, team_id, remarks,
                                             customer_name, customer_email,
                                             customer_street, customer_street2, customer_city_id, customer_state_id,
                                             customer_zip,
                                             customer_country_id, dealer_distributor_name, product_name,
                                             custom_product_serial,
                                             product_part_number, product_part_code, oem_warranty_status_id,
                                             repair_warranty_status_id,
                                             survey_id, user_id, company_id
                                             ])
                service_request_list_len = len(service_request_list) - 1
                if rec.state in ['draft']:
                    service_request_list[service_request_list_len].append(
                        {'key': 'submit', 'type': "button",
                         'title': 'Submit',
                         'value': 'Submit',
                         })
        elif ticket_type == 'sr_installation':
            message = "SR-Installation load successfully"
            for rec in service_request_ids:
                id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                      'value': rec.id if rec.id else ''}
                name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                      'value': rec.name if rec.name else ''}
                state = {'key': 'state', 'type': rec._fields['state'].type, 'title': rec._fields['state'].string,
                         'value': dict(rec._fields['state'].selection).get(rec.state)}

                # SERVICE REQUEST INFORMATION
                service_request_id_alias = {'key': 'service_request_id_alias',
                                            'type': rec._fields['service_request_id_alias'].type,
                                            'title': rec._fields['service_request_id_alias'].string,
                                            'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
                service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type,
                                        'title': rec._fields['service_request_date'].string,
                                        'value': str(rec.service_request_date.astimezone(local_tz).replace(tzinfo=None).strftime('%Y-%m-%d %I:%M %p')) if rec.service_request_date else ''}
                approver_id = {'key': 'approver_id', 'type': rec._fields['approver_id'].type,
                               'title': rec._fields['approver_id'].string,
                               'value': rec.approver_id.name if rec.approver_id else ''}
                parent_ticket_id = {'key': 'parent_ticket_id', 'type': rec._fields['parent_ticket_id'].type,
                                    'title': rec._fields['parent_ticket_id'].string,
                                    'value': rec.parent_ticket_id.name if rec.parent_ticket_id else ''}
                child_ticket_id = {'key': 'child_ticket_id', 'type': rec._fields['child_ticket_id'].type,
                                   'title': rec._fields['child_ticket_id'].string,
                                   'value': rec.child_ticket_id.name if rec.child_ticket_id else ''}
                child_ticket_type_id = {'key': 'child_ticket_type_id', 'type': rec._fields['child_ticket_type_id'].type,
                                        'title': rec._fields['child_ticket_type_id'].string,
                                        'value': rec.child_ticket_type_id.name if rec.child_ticket_type_id else ''}

                # CALL DETAILS
                call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
                                  'title': rec._fields['call_source_id'].string,
                                  'value': rec.call_source_id.name if rec.call_source_id else ''}
                service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
                                   'title': rec._fields['service_type_id'].string,
                                   'value': rec.service_type_id.name if rec.service_type_id else ''}
                service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
                                       'title': rec._fields['service_category_id'].string,
                                       'value': rec.service_category_id.name if rec.service_category_id else ''}
                request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
                                   'title': rec._fields['request_type_id'].string,
                                   'value': rec.request_type_id.name if rec.request_type_id else ''}
                reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
                          'value': rec.reason if rec.reason else ''}
                problem_reported = {'key': 'problem_reported', 'type': rec._fields['problem_reported'].type,
                                    'title': rec._fields['problem_reported'].string,
                                    'value': rec.problem_reported if rec.problem_reported else ''}
                requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type,
                                     'title': rec._fields['requested_by_name'].string,
                                     'value': rec.requested_by_name if rec.requested_by_name else ''}
                requested_by_contact_number = {'key': 'requested_by_contact_number',
                                               'type': rec._fields['requested_by_contact_number'].type,
                                               'title': rec._fields['requested_by_contact_number'].string,
                                               'value': rec.requested_by_contact_number if rec.requested_by_contact_number else ''}
                call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
                                    'title': rec._fields['call_received_id'].string,
                                    'value': rec.call_received_id.name if rec.call_received_id else ''}
                team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type,
                           'title': rec._fields['team_id'].string,
                           'value': rec.team_id.name if rec.team_id else ''}
                # INSTALLATION INFORMATION
                location_contact_person = {'key': 'location_contact_person', 'type': rec._fields['location_contact_person'].type,'title': rec._fields['location_contact_person'].string,
                                    'value': rec.location_contact_person if rec.location_contact_person else ''}
                customer_po_number = {'key': 'customer_po_number', 'type': rec._fields['customer_po_number'].type,'title': rec._fields['customer_po_number'].string,
                                    'value': rec.customer_po_number if rec.customer_po_number else ''}
                customer_po_date = {'key': 'customer_po_date', 'type': rec._fields['customer_po_date'].type,'title': rec._fields['customer_po_date'].string,
                                    'value': str(rec.customer_po_date) if rec.customer_po_date else ''}
                tender_refer_number = {'key': 'tender_refer_number', 'type': rec._fields['tender_refer_number'].type,'title': rec._fields['tender_refer_number'].string,
                                    'value': rec.tender_refer_number if rec.tender_refer_number else ''}
                installation_date = {'key': 'installation_date', 'type': rec._fields['installation_date'].type,'title': rec._fields['installation_date'].string,
                                    'value': str(rec.installation_date) if rec.installation_date else ''}
                invoice_number = {'key': 'invoice_number', 'type': rec._fields['invoice_number'].type,'title': rec._fields['invoice_number'].string,
                                    'value': rec.invoice_number if rec.invoice_number else ''}
                invoice_date = {'key': 'invoice_date', 'type': rec._fields['invoice_date'].type,'title': rec._fields['invoice_date'].string,
                                    'value': str(rec.invoice_date) if rec.invoice_date else ''}
                extended_invoice_number = {'key': 'extended_invoice_number', 'type': rec._fields['extended_invoice_number'].type,'title': rec._fields['extended_invoice_number'].string,
                                    'value': rec.extended_invoice_number if rec.extended_invoice_number else ''}
                extended_invoice_date = {'key': 'extended_invoice_date', 'type': rec._fields['extended_invoice_date'].type,'title': rec._fields['extended_invoice_date'].string,
                                    'value': str(rec.extended_invoice_date) if rec.extended_invoice_date else ''}
                # CUSTOMER INFORMATION
                customer_name = {'key': 'customer_name', 'type': rec._fields['customer_name'].type,
                                 'title': rec._fields['customer_name'].string,
                                 'value': rec.customer_name if rec.customer_name else ''}
                customer_email = {'key': 'customer_email', 'type': rec._fields['customer_email'].type,
                                  'title': rec._fields['customer_email'].string,
                                  'value': rec.customer_email if rec.customer_email else ''}
                # ASSET DETAILS
                product_name = {'key': 'product_name', 'type': rec._fields['product_name'].type,
                                'title': rec._fields['product_name'].string,
                                'value': rec.product_name if rec.product_name else ''}
                custom_product_serial = {'key': 'custom_product_serial',
                                         'type': rec._fields['custom_product_serial'].type,
                                         'title': rec._fields['custom_product_serial'].string,
                                         'value': rec.custom_product_serial if rec.custom_product_serial else ''}
                product_part_number = {'key': 'product_part_number', 'type': rec._fields['product_part_number'].type,
                                       'title': rec._fields['product_part_number'].string,
                                       'value': rec.product_part_number if rec.product_part_number else ''}
                product_part_code = {'key': 'product_part_code', 'type': rec._fields['product_part_code'].type,
                                     'title': rec._fields['product_part_code'].string,
                                     'value': rec.product_part_code if rec.product_part_code else ''}
                oem_warranty_status_id = {'key': 'oem_warranty_status_id',
                                          'type': rec._fields['oem_warranty_status_id'].type,
                                          'title': rec._fields['oem_warranty_status_id'].string,
                                          'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
                repair_warranty_status_id = {'key': 'repair_warranty_status_id',
                                             'type': rec._fields['repair_warranty_status_id'].type,
                                             'title': rec._fields['repair_warranty_status_id'].string,
                                             'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}

                service_request_list.append([id,name,state,service_request_id_alias,service_request_date,approver_id,parent_ticket_id,
                        child_ticket_id,child_ticket_type_id,call_source_id,service_type_id,service_category_id,request_type_id,
                        reason,problem_reported,requested_by_name,requested_by_contact_number,call_received_id,team_id,
                        location_contact_person,customer_po_number,customer_po_date,tender_refer_number,installation_date,
                        invoice_number,invoice_date,extended_invoice_number,extended_invoice_date,customer_name,customer_email,
                        product_name,custom_product_serial,product_part_number,product_part_number,product_part_code,
                        oem_warranty_status_id,repair_warranty_status_id,
                                             ])
                service_request_list_len = len(service_request_list) - 1
                if rec.state in ['draft']:
                    service_request_list[service_request_list_len].append(
                        {'key': 'submit', 'type': "button",
                         'title': 'Submit',
                         'value': 'Submit',
                         })
        elif ticket_type == 'sr_maintenance':
            message= "SR-Maintenance load successfully"
            for rec in service_request_ids:
                id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                      'value': rec.id if rec.id else ''}
                name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                        'value': rec.name if rec.name else ''}
                state = {'key': 'state', 'type': rec._fields['state'].type, 'title': rec._fields['state'].string,
                         'value': dict(rec._fields['state'].selection).get(rec.state)}
                # SERVICE REQUEST INFORMATION
                service_request_id_alias = {'key': 'service_request_id_alias',
                                            'type': rec._fields['service_request_id_alias'].type,
                                            'title': rec._fields['service_request_id_alias'].string,
                                            'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
                service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type,
                                        'title': rec._fields['service_request_date'].string,
                                        'value': str(rec.service_request_date.astimezone(local_tz).replace(tzinfo=None).strftime('%Y-%m-%d %I:%M %p')) if rec.service_request_date else ''}
                approver_id = {'key': 'approver_id', 'type': rec._fields['approver_id'].type,
                               'title': rec._fields['approver_id'].string,
                               'value': rec.approver_id.name if rec.approver_id else ''}
                parent_ticket_id = {'key': 'parent_ticket_id', 'type': rec._fields['parent_ticket_id'].type,
                                    'title': rec._fields['parent_ticket_id'].string,
                                    'value': rec.parent_ticket_id.name if rec.parent_ticket_id else ''}
                child_ticket_id = {'key': 'child_ticket_id', 'type': rec._fields['child_ticket_id'].type,
                                   'title': rec._fields['child_ticket_id'].string,
                                   'value': rec.child_ticket_id.name if rec.child_ticket_id else ''}
                child_ticket_type_id = {'key': 'child_ticket_type_id', 'type': rec._fields['child_ticket_type_id'].type,
                                        'title': rec._fields['child_ticket_type_id'].string,
                                        'value': rec.child_ticket_type_id.name if rec.child_ticket_type_id else ''}
                # CALL DETAILS
                call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
                                  'title': rec._fields['call_source_id'].string,
                                  'value': rec.call_source_id.name if rec.call_source_id else ''}
                service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
                                   'title': rec._fields['service_type_id'].string,
                                   'value': rec.service_type_id.name if rec.service_type_id else ''}
                service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
                                       'title': rec._fields['service_category_id'].string,
                                       'value': rec.service_category_id.name if rec.service_category_id else ''}
                request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
                                   'title': rec._fields['request_type_id'].string,
                                   'value': rec.request_type_id.name if rec.request_type_id else ''}
                reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
                          'value': rec.reason if rec.reason else ''}
                problem_reported = {'key': 'problem_reported', 'type': rec._fields['problem_reported'].type,
                                    'title': rec._fields['problem_reported'].string,
                                    'value': rec.problem_reported if rec.problem_reported else ''}
                requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type,
                                     'title': rec._fields['requested_by_name'].string,
                                     'value': rec.requested_by_name if rec.requested_by_name else ''}
                requested_by_contact_number = {'key': 'requested_by_contact_number',
                                               'type': rec._fields['requested_by_contact_number'].type,
                                               'title': rec._fields['requested_by_contact_number'].string,
                                               'value': rec.requested_by_contact_number if rec.requested_by_contact_number else ''}
                call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
                                    'title': rec._fields['call_received_id'].string,
                                    'value': rec.call_received_id.name if rec.call_received_id else ''}
                team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type,
                           'title': rec._fields['team_id'].string,
                           'value': rec.team_id.name if rec.team_id else ''}
                # OTHER INFORMATION
                remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type,
                           'title': rec._fields['remarks'].string,
                           'value': rec.remarks if rec.remarks else ''}
                # CUSTOMER INFORMATION
                customer_name = {'key': 'customer_name', 'type': rec._fields['customer_name'].type,
                                 'title': rec._fields['customer_name'].string,
                                 'value': rec.customer_name if rec.customer_name else ''}
                customer_email = {'key': 'customer_email', 'type': rec._fields['customer_email'].type,
                                  'title': rec._fields['customer_email'].string,
                                  'value': rec.customer_email if rec.customer_email else ''}
                customer_street = {'key': 'customer_street', 'type': rec._fields['customer_street'].type,
                                   'title': rec._fields['customer_street'].string,
                                   'value': rec.customer_street if rec.customer_street else ''}
                customer_street2 = {'key': 'customer_street2', 'type': rec._fields['customer_street2'].type,
                                    'title': rec._fields['customer_street2'].string,
                                    'value': rec.customer_street2 if rec.customer_street2 else ''}
                customer_city_id = {'key': 'customer_city_id', 'type': rec._fields['customer_city_id'].type,
                                    'title': rec._fields['customer_city_id'].string,
                                    'value': rec.customer_city_id.name if rec.customer_city_id else ''}
                customer_state_id = {'key': 'customer_state_id', 'type': rec._fields['customer_state_id'].type,
                                     'title': rec._fields['customer_state_id'].string,
                                     'value': rec.customer_state_id.name if rec.customer_state_id else ''}
                customer_zip = {'key': 'customer_zip', 'type': rec._fields['customer_zip'].type,
                                'title': rec._fields['customer_zip'].string,
                                'value': rec.customer_zip if rec.customer_zip else ''}
                customer_country_id = {'key': 'customer_country_id', 'type': rec._fields['customer_country_id'].type,
                                       'title': rec._fields['customer_country_id'].string,
                                       'value': rec.customer_country_id.name if rec.customer_country_id else ''}
                dealer_distributor_name = {'key': 'dealer_distributor_name',
                                           'type': rec._fields['dealer_distributor_name'].type,
                                           'title': rec._fields['dealer_distributor_name'].string,
                                           'value': rec.dealer_distributor_name if rec.dealer_distributor_name else ''}

                # ASSET DETAILS
                product_name = {'key': 'product_name', 'type': rec._fields['product_name'].type,
                                'title': rec._fields['product_name'].string,
                                'value': rec.product_name if rec.product_name else ''}
                custom_product_serial = {'key': 'custom_product_serial',
                                         'type': rec._fields['custom_product_serial'].type,
                                         'title': rec._fields['custom_product_serial'].string,
                                         'value': rec.custom_product_serial if rec.custom_product_serial else ''}
                product_part_number = {'key': 'product_part_number', 'type': rec._fields['product_part_number'].type,
                                       'title': rec._fields['product_part_number'].string,
                                       'value': rec.product_part_number if rec.product_part_number else ''}
                product_part_code = {'key': 'product_part_code', 'type': rec._fields['product_part_code'].type,
                                     'title': rec._fields['product_part_code'].string,
                                     'value': rec.product_part_code if rec.product_part_code else ''}
                oem_warranty_status_id = {'key': 'oem_warranty_status_id',
                                          'type': rec._fields['oem_warranty_status_id'].type,
                                          'title': rec._fields['oem_warranty_status_id'].string,
                                          'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
                repair_warranty_status_id = {'key': 'repair_warranty_status_id',
                                             'type': rec._fields['repair_warranty_status_id'].type,
                                             'title': rec._fields['repair_warranty_status_id'].string,
                                             'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
                # OTHER INFORMATION
                survey_id = {'key': 'survey_id', 'type': rec._fields['survey_id'].type,
                             'title': rec._fields['survey_id'].string,
                             'value': rec.survey_id.title if rec.survey_id else ''}
                company_id = {'key': 'company_id', 'type': rec._fields['company_id'].type,
                              'title': rec._fields['company_id'].string,
                              'value': rec.company_id.name if rec.company_id else ''}
                user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type,
                           'title': rec._fields['user_id'].string,
                           'value': rec.user_id.name if rec.user_id else ''}
                service_request_list.append([id, name,state, service_request_id_alias, service_request_date, approver_id,
                                             parent_ticket_id, child_ticket_id, child_ticket_type_id, call_source_id,
                                             service_type_id,
                                             service_category_id, request_type_id, reason, problem_reported,
                                             requested_by_name,
                                             requested_by_contact_number, call_received_id, team_id, remarks,
                                             customer_name, customer_email,
                                             customer_street, customer_street2, customer_city_id, customer_state_id,
                                             customer_zip,
                                             customer_country_id, dealer_distributor_name, product_name,
                                             custom_product_serial,
                                             product_part_number, product_part_code, oem_warranty_status_id,
                                             repair_warranty_status_id,
                                             survey_id, user_id, company_id
                                             ])
                service_request_list_len = len(service_request_list) - 1
                if rec.state in ['draft']:
                    service_request_list[service_request_list_len].append(
                        {'key': 'submit', 'type': "button",
                         'title': 'Submit',
                         'value': 'Submit',
                         })
        elif ticket_type == 'sr_remote_support':
            message = "SR-Remote Support load successfully"
            for rec in service_request_ids:
                id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                      'value': rec.id if rec.id else ''}
                name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                        'value': rec.name if rec.name else ''}
                state = {'key': 'state', 'type': rec._fields['state'].type, 'title': rec._fields['state'].string,
                         'value': dict(rec._fields['state'].selection).get(rec.state)}
                # SERVICE REQUEST INFORMATION
                service_request_id_alias = {'key': 'service_request_id_alias',
                                            'type': rec._fields['service_request_id_alias'].type,
                                            'title': rec._fields['service_request_id_alias'].string,
                                            'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
                service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type,
                                        'title': rec._fields['service_request_date'].string,
                                        'value': str(rec.service_request_date.astimezone(local_tz).replace(tzinfo=None).strftime('%Y-%m-%d %I:%M %p')) if rec.service_request_date else ''}
                approver_id = {'key': 'approver_id', 'type': rec._fields['approver_id'].type,
                               'title': rec._fields['approver_id'].string,
                               'value': rec.approver_id.name if rec.approver_id else ''}
                parent_ticket_id = {'key': 'parent_ticket_id', 'type': rec._fields['parent_ticket_id'].type,
                                    'title': rec._fields['parent_ticket_id'].string,
                                    'value': rec.parent_ticket_id.name if rec.parent_ticket_id else ''}
                child_ticket_id = {'key': 'child_ticket_id', 'type': rec._fields['child_ticket_id'].type,
                                   'title': rec._fields['child_ticket_id'].string,
                                   'value': rec.child_ticket_id.name if rec.child_ticket_id else ''}
                child_ticket_type_id = {'key': 'child_ticket_type_id', 'type': rec._fields['child_ticket_type_id'].type,
                                        'title': rec._fields['child_ticket_type_id'].string,
                                        'value': rec.child_ticket_type_id.name if rec.child_ticket_type_id else ''}
                # CALL DETAILS
                call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
                                  'title': rec._fields['call_source_id'].string,
                                  'value': rec.call_source_id.name if rec.call_source_id else ''}
                service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
                                   'title': rec._fields['service_type_id'].string,
                                   'value': rec.service_type_id.name if rec.service_type_id else ''}
                service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
                                       'title': rec._fields['service_category_id'].string,
                                       'value': rec.service_category_id.name if rec.service_category_id else ''}
                request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
                                   'title': rec._fields['request_type_id'].string,
                                   'value': rec.request_type_id.name if rec.request_type_id else ''}
                reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
                          'value': rec.reason if rec.reason else ''}
                problem_reported = {'key': 'problem_reported', 'type': rec._fields['problem_reported'].type,
                                    'title': rec._fields['problem_reported'].string,
                                    'value': rec.problem_reported if rec.problem_reported else ''}
                requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type,
                                     'title': rec._fields['requested_by_name'].string,
                                     'value': rec.requested_by_name if rec.requested_by_name else ''}
                requested_by_contact_number = {'key': 'requested_by_contact_number',
                                               'type': rec._fields['requested_by_contact_number'].type,
                                               'title': rec._fields['requested_by_contact_number'].string,
                                               'value': rec.requested_by_contact_number if rec.requested_by_contact_number else ''}
                call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
                                    'title': rec._fields['call_received_id'].string,
                                    'value': rec.call_received_id.name if rec.call_received_id else ''}
                team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type,
                           'title': rec._fields['team_id'].string,
                           'value': rec.team_id.name if rec.team_id else ''}
                # OTHER INFORMATION
                remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type,
                           'title': rec._fields['remarks'].string,
                           'value': rec.remarks if rec.remarks else ''}
                # CUSTOMER INFORMATION
                customer_name = {'key': 'customer_name', 'type': rec._fields['customer_name'].type,
                                 'title': rec._fields['customer_name'].string,
                                 'value': rec.customer_name if rec.customer_name else ''}
                customer_email = {'key': 'customer_email', 'type': rec._fields['customer_email'].type,
                                  'title': rec._fields['customer_email'].string,
                                  'value': rec.customer_email if rec.customer_email else ''}
                customer_street = {'key': 'customer_street', 'type': rec._fields['customer_street'].type,
                                   'title': rec._fields['customer_street'].string,
                                   'value': rec.customer_street if rec.customer_street else ''}
                customer_street2 = {'key': 'customer_street2', 'type': rec._fields['customer_street2'].type,
                                    'title': rec._fields['customer_street2'].string,
                                    'value': rec.customer_street2 if rec.customer_street2 else ''}
                customer_city_id = {'key': 'customer_city_id', 'type': rec._fields['customer_city_id'].type,
                                    'title': rec._fields['customer_city_id'].string,
                                    'value': rec.customer_city_id.name if rec.customer_city_id else ''}
                customer_state_id = {'key': 'customer_state_id', 'type': rec._fields['customer_state_id'].type,
                                     'title': rec._fields['customer_state_id'].string,
                                     'value': rec.customer_state_id.name if rec.customer_state_id else ''}
                customer_zip = {'key': 'customer_zip', 'type': rec._fields['customer_zip'].type,
                                'title': rec._fields['customer_zip'].string,
                                'value': rec.customer_zip if rec.customer_zip else ''}
                customer_country_id = {'key': 'customer_country_id', 'type': rec._fields['customer_country_id'].type,
                                       'title': rec._fields['customer_country_id'].string,
                                       'value': rec.customer_country_id.name if rec.customer_country_id else ''}
                dealer_distributor_name = {'key': 'dealer_distributor_name',
                                           'type': rec._fields['dealer_distributor_name'].type,
                                           'title': rec._fields['dealer_distributor_name'].string,
                                           'value': rec.dealer_distributor_name if rec.dealer_distributor_name else ''}

                # ASSET DETAILS
                product_name = {'key': 'product_name', 'type': rec._fields['product_name'].type,
                                'title': rec._fields['product_name'].string,
                                'value': rec.product_name if rec.product_name else ''}
                custom_product_serial = {'key': 'custom_product_serial',
                                         'type': rec._fields['custom_product_serial'].type,
                                         'title': rec._fields['custom_product_serial'].string,
                                         'value': rec.custom_product_serial if rec.custom_product_serial else ''}
                product_part_number = {'key': 'product_part_number', 'type': rec._fields['product_part_number'].type,
                                       'title': rec._fields['product_part_number'].string,
                                       'value': rec.product_part_number if rec.product_part_number else ''}
                product_part_code = {'key': 'product_part_code', 'type': rec._fields['product_part_code'].type,
                                     'title': rec._fields['product_part_code'].string,
                                     'value': rec.product_part_code if rec.product_part_code else ''}
                oem_warranty_status_id = {'key': 'oem_warranty_status_id',
                                          'type': rec._fields['oem_warranty_status_id'].type,
                                          'title': rec._fields['oem_warranty_status_id'].string,
                                          'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
                repair_warranty_status_id = {'key': 'repair_warranty_status_id',
                                             'type': rec._fields['repair_warranty_status_id'].type,
                                             'title': rec._fields['repair_warranty_status_id'].string,
                                             'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
                # OTHER INFORMATION
                survey_id = {'key': 'survey_id', 'type': rec._fields['survey_id'].type,
                             'title': rec._fields['survey_id'].string,
                             'value': rec.survey_id.title if rec.survey_id else ''}
                company_id = {'key': 'company_id', 'type': rec._fields['company_id'].type,
                              'title': rec._fields['company_id'].string,
                              'value': rec.company_id.name if rec.company_id else ''}
                user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type,
                           'title': rec._fields['user_id'].string,
                           'value': rec.user_id.name if rec.user_id else ''}
                service_request_list.append([id, name,state, service_request_id_alias, service_request_date, approver_id,
                                             parent_ticket_id, child_ticket_id, child_ticket_type_id, call_source_id,
                                             service_type_id,
                                             service_category_id, request_type_id, reason, problem_reported,
                                             requested_by_name,
                                             requested_by_contact_number, call_received_id, team_id, remarks,
                                             customer_name, customer_email,
                                             customer_street, customer_street2, customer_city_id, customer_state_id,
                                             customer_zip,
                                             customer_country_id, dealer_distributor_name, product_name,
                                             custom_product_serial,
                                             product_part_number, product_part_code, oem_warranty_status_id,
                                             repair_warranty_status_id,
                                             survey_id, user_id, company_id
                                             ])
                service_request_list_len = len(service_request_list) - 1
                if rec.state in ['draft']:
                    service_request_list[service_request_list_len].append(
                        {'key': 'submit', 'type': "button",
                         'title': 'Submit',
                         'value': 'Submit',
                         })
        elif ticket_type == 'sr_survey_escalation':
            message = "SR-Survey Escalation load successfully"
            for rec in service_request_ids:
                id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                      'value': rec.id if rec.id else ''}
                name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                      'value': rec.name if rec.name else ''}
                state = {'key': 'state', 'type': rec._fields['state'].type, 'title': rec._fields['state'].string,
                         'value': dict(rec._fields['state'].selection).get(rec.state)}
                # SERVICE REQUEST INFORMATION
                service_request_id_alias = {'key': 'service_request_id_alias', 'type': rec._fields['service_request_id_alias'].type, 'title': rec._fields['service_request_id_alias'].string,
                      'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
                service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type, 'title': rec._fields['service_request_date'].string,
                      'value': str(rec.service_request_date.astimezone(local_tz).replace(tzinfo=None).strftime('%Y-%m-%d %I:%M %p')) if rec.service_request_date else ''}
                service_request_status_id = {'key': 'service_request_status_id', 'type': rec._fields['service_request_status_id'].type, 'title': rec._fields['service_request_status_id'].string,
                      'value': rec.service_request_status_id.name if rec.service_request_status_id else ''}
                # CALL DETAILS
                call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type, 'title': rec._fields['call_source_id'].string,
                      'value': rec.call_source_id.name if rec.call_source_id else ''}
                service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type, 'title': rec._fields['service_category_id'].string,
                      'value': rec.service_category_id.name if rec.service_category_id else ''}
                service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
                                   'title': rec._fields['service_type_id'].string,
                                   'value': rec.service_type_id.name if rec.service_type_id else ''}
                request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type, 'title': rec._fields['request_type_id'].string,
                      'value': rec.request_type_id.name if rec.request_type_id else ''}
                requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type,
                                     'title': rec._fields['requested_by_name'].string,
                                     'value': rec.requested_by_name if rec.requested_by_name else ''}
                requested_by_contact_number = {'key': 'requested_by_contact_number', 'type': rec._fields['requested_by_contact_number'].type,
                                     'title': rec._fields['requested_by_contact_number'].string,
                                     'value': rec.requested_by_contact_number if rec.requested_by_contact_number else ''}
                call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
                                    'title': rec._fields['call_received_id'].string,
                                    'value': rec.call_received_id.name if rec.call_received_id else ''}
                team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type,'title': rec._fields['team_id'].string,
                                    'value': rec.team_id.name if rec.team_id else ''}
                # OTHER INFORMATION
                remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type,
                           'title': rec._fields['remarks'].string,
                           'value': rec.remarks if rec.remarks else ''}
                # CUSTOMER INFORMATION
                customer_name = {'key': 'customer_name', 'type': rec._fields['customer_name'].type,
                                 'title': rec._fields['customer_name'].string,
                                 'value': rec.customer_name if rec.customer_name else ''}
                customer_email = {'key': 'customer_email', 'type': rec._fields['customer_email'].type,
                                  'title': rec._fields['customer_email'].string,
                                  'value': rec.customer_email if rec.customer_email else ''}
                dealer_distributor_name = {'key': 'dealer_distributor_name',
                                           'type': rec._fields['dealer_distributor_name'].type,
                                           'title': rec._fields['dealer_distributor_name'].string,
                                           'value': rec.dealer_distributor_name if rec.dealer_distributor_name else ''}
                # ASSET DETAILS
                product_name = {'key': 'product_name', 'type': rec._fields['product_name'].type,
                                'title': rec._fields['product_name'].string,
                                'value': rec.product_name if rec.product_name else ''}
                custom_product_serial = {'key': 'custom_product_serial',
                                         'type': rec._fields['custom_product_serial'].type,
                                         'title': rec._fields['custom_product_serial'].string,
                                         'value': rec.custom_product_serial if rec.custom_product_serial else ''}
                product_category_id = {'key': 'product_category_id', 'type': rec._fields['product_category_id'].type,'title': rec._fields['product_category_id'].string,
                                    'value': rec.product_category_id.name if rec.product_category_id else ''}
                product_category_alias = {'key': 'product_category_alias', 'type': rec._fields['product_category_alias'].type,'title': rec._fields['product_category_alias'].string,
                                    'value': rec.product_category_alias if rec.product_category_alias else ''}
                model = {'key': 'model', 'type': rec._fields['model'].type,'title': rec._fields['model'].string,
                                    'value': rec.model if rec.model else ''}
                oem_warranty_status_id = {'key': 'oem_warranty_status_id', 'type': rec._fields['oem_warranty_status_id'].type,'title': rec._fields['oem_warranty_status_id'].string,
                                    'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
                repair_warranty_status_id = {'key': 'repair_warranty_status_id', 'type': rec._fields['repair_warranty_status_id'].type,'title': rec._fields['repair_warranty_status_id'].string,
                                    'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
                # OTHER INFORMATION
                dispatch_location_id = {'key': 'dispatch_location_id', 'type': rec._fields['dispatch_location_id'].type,'title': rec._fields['dispatch_location_id'].string,
                                    'value': rec.dispatch_location_id.name if rec.dispatch_location_id else ''}
                survey_id = {'key': 'survey_id', 'type': rec._fields['survey_id'].type,
                             'title': rec._fields['survey_id'].string,
                             'value': rec.survey_id.title if rec.survey_id else ''}
                external_reference = {'key': 'external_reference', 'type': rec._fields['external_reference'].type,
                             'title': rec._fields['external_reference'].string,
                             'value': rec.external_reference if rec.external_reference else ''}
                child_ticket_id = {'key': 'child_ticket_id', 'type': rec._fields['child_ticket_id'].type,
                             'title': rec._fields['child_ticket_id'].string,
                             'value': rec.child_ticket_id.name if rec.child_ticket_id else ''}
                parent_ticket_id = {'key': 'parent_ticket_id', 'type': rec._fields['parent_ticket_id'].type,
                             'title': rec._fields['parent_ticket_id'].string,
                             'value': rec.parent_ticket_id.name if rec.parent_ticket_id else ''}
                assign_engineer_ids = {'key': 'assign_engineer_ids', 'type': rec._fields['assign_engineer_ids'].type,
                             'title': rec._fields['assign_engineer_ids'].string,
                             'value':[{'id':x.id,'value':x.name} for x in rec.assign_engineer_ids] if rec.assign_engineer_ids else ''}
                rsm_ids = {'key': 'rsm_ids', 'type': rec._fields['rsm_ids'].type,
                             'title': rec._fields['rsm_ids'].string,
                             'value':[{'id':x.id,'value':x.name} for x in rec.rsm_ids] if rec.rsm_ids else ''}
                nsm_ids = {'key': 'nsm_ids', 'type': rec._fields['nsm_ids'].type,
                             'title': rec._fields['nsm_ids'].string,
                             'value':[{'id':x.id,'value':x.name} for x in rec.nsm_ids] if rec.nsm_ids else ''}
                service_request_list.append([id,name,state,service_request_id_alias,service_request_date,service_request_status_id,
                        call_source_id,service_category_id,service_type_id,request_type_id,requested_by_name,
                        requested_by_contact_number,call_received_id,team_id,remarks,customer_name,customer_email,
                        dealer_distributor_name,product_name,custom_product_serial,product_category_id,product_category_alias,
                        product_category_alias,model,oem_warranty_status_id,repair_warranty_status_id,dispatch_location_id,
                        survey_id,external_reference,child_ticket_id,parent_ticket_id,assign_engineer_ids,rsm_ids,nsm_ids,
                                             ])
                service_request_list_len = len(service_request_list) - 1
                if rec.state in ['draft']:
                    service_request_list[service_request_list_len].append(
                        {'key': 'submit', 'type': "button",
                         'title': 'Submit',
                         'value': 'Submit',
                         })
        elif ticket_type == 'so_call':
            message = "SO Call load successfully"
            for rec in service_request_ids:
                id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                      'value': rec.id if rec.id else ''}
                name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                        'value': rec.name if rec.name else ''}
                state = {'key': 'state', 'type': rec._fields['state'].type, 'title': rec._fields['state'].string,
                         'value': dict(rec._fields['state'].selection).get(rec.state)}
                # SERVICE REQUEST INFORMATION
                service_request_id_alias = {'key': 'service_request_id_alias',
                                            'type': rec._fields['service_request_id_alias'].type,
                                            'title': rec._fields['service_request_id_alias'].string,
                                            'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
                service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type,
                                        'title': rec._fields['service_request_date'].string,
                                        'value': str(rec.service_request_date.astimezone(local_tz).replace(tzinfo=None).strftime('%Y-%m-%d %I:%M %p')) if rec.service_request_date else ''}
                approver_id = {'key': 'approver_id', 'type': rec._fields['approver_id'].type,
                               'title': rec._fields['approver_id'].string,
                               'value': rec.approver_id.name if rec.approver_id else ''}
                parent_ticket_id = {'key': 'parent_ticket_id', 'type': rec._fields['parent_ticket_id'].type,
                                    'title': rec._fields['parent_ticket_id'].string,
                                    'value': rec.parent_ticket_id.name if rec.parent_ticket_id else ''}
                child_ticket_id = {'key': 'child_ticket_id', 'type': rec._fields['child_ticket_id'].type,
                                   'title': rec._fields['child_ticket_id'].string,
                                   'value': rec.child_ticket_id.name if rec.child_ticket_id else ''}
                child_ticket_type_id = {'key': 'child_ticket_type_id', 'type': rec._fields['child_ticket_type_id'].type,
                                        'title': rec._fields['child_ticket_type_id'].string,
                                        'value': rec.child_ticket_type_id.name if rec.child_ticket_type_id else ''}
                # CALL DETAILS
                call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
                                  'title': rec._fields['call_source_id'].string,
                                  'value': rec.call_source_id.name if rec.call_source_id else ''}
                service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
                                   'title': rec._fields['service_type_id'].string,
                                   'value': rec.service_type_id.name if rec.service_type_id else ''}
                service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
                                       'title': rec._fields['service_category_id'].string,
                                       'value': rec.service_category_id.name if rec.service_category_id else ''}
                request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
                                   'title': rec._fields['request_type_id'].string,
                                   'value': rec.request_type_id.name if rec.request_type_id else ''}
                reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
                          'value': rec.reason if rec.reason else ''}
                problem_reported = {'key': 'problem_reported', 'type': rec._fields['problem_reported'].type,
                                    'title': rec._fields['problem_reported'].string,
                                    'value': rec.problem_reported if rec.problem_reported else ''}
                requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type,
                                     'title': rec._fields['requested_by_name'].string,
                                     'value': rec.requested_by_name if rec.requested_by_name else ''}
                requested_by_contact_number = {'key': 'requested_by_contact_number',
                                               'type': rec._fields['requested_by_contact_number'].type,
                                               'title': rec._fields['requested_by_contact_number'].string,
                                               'value': rec.requested_by_contact_number if rec.requested_by_contact_number else ''}
                call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
                                    'title': rec._fields['call_received_id'].string,
                                    'value': rec.call_received_id.name if rec.call_received_id else ''}
                team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type,
                           'title': rec._fields['team_id'].string,
                           'value': rec.team_id.name if rec.team_id else ''}
                # OTHER INFORMATION
                remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type,
                           'title': rec._fields['remarks'].string,
                           'value': rec.remarks if rec.remarks else ''}
                # CUSTOMER INFORMATION
                customer_name = {'key': 'customer_name', 'type': rec._fields['customer_name'].type,
                                 'title': rec._fields['customer_name'].string,
                                 'value': rec.customer_name if rec.customer_name else ''}
                customer_email = {'key': 'customer_email', 'type': rec._fields['customer_email'].type,
                                  'title': rec._fields['customer_email'].string,
                                  'value': rec.customer_email if rec.customer_email else ''}
                customer_street = {'key': 'customer_street', 'type': rec._fields['customer_street'].type,
                                   'title': rec._fields['customer_street'].string,
                                   'value': rec.customer_street if rec.customer_street else ''}
                customer_street2 = {'key': 'customer_street2', 'type': rec._fields['customer_street2'].type,
                                    'title': rec._fields['customer_street2'].string,
                                    'value': rec.customer_street2 if rec.customer_street2 else ''}
                customer_city_id = {'key': 'customer_city_id', 'type': rec._fields['customer_city_id'].type,
                                    'title': rec._fields['customer_city_id'].string,
                                    'value': rec.customer_city_id.name if rec.customer_city_id else ''}
                customer_state_id = {'key': 'customer_state_id', 'type': rec._fields['customer_state_id'].type,
                                     'title': rec._fields['customer_state_id'].string,
                                     'value': rec.customer_state_id.name if rec.customer_state_id else ''}
                customer_zip = {'key': 'customer_zip', 'type': rec._fields['customer_zip'].type,
                                'title': rec._fields['customer_zip'].string,
                                'value': rec.customer_zip if rec.customer_zip else ''}
                customer_country_id = {'key': 'customer_country_id', 'type': rec._fields['customer_country_id'].type,
                                       'title': rec._fields['customer_country_id'].string,
                                       'value': rec.customer_country_id.name if rec.customer_country_id else ''}
                dealer_distributor_name = {'key': 'dealer_distributor_name',
                                           'type': rec._fields['dealer_distributor_name'].type,
                                           'title': rec._fields['dealer_distributor_name'].string,
                                           'value': rec.dealer_distributor_name if rec.dealer_distributor_name else ''}

                # ASSET DETAILS
                product_name = {'key': 'product_name', 'type': rec._fields['product_name'].type,
                                'title': rec._fields['product_name'].string,
                                'value': rec.product_name if rec.product_name else ''}
                custom_product_serial = {'key': 'custom_product_serial',
                                         'type': rec._fields['custom_product_serial'].type,
                                         'title': rec._fields['custom_product_serial'].string,
                                         'value': rec.custom_product_serial if rec.custom_product_serial else ''}
                product_part_number = {'key': 'product_part_number', 'type': rec._fields['product_part_number'].type,
                                       'title': rec._fields['product_part_number'].string,
                                       'value': rec.product_part_number if rec.product_part_number else ''}
                product_part_code = {'key': 'product_part_code', 'type': rec._fields['product_part_code'].type,
                                     'title': rec._fields['product_part_code'].string,
                                     'value': rec.product_part_code if rec.product_part_code else ''}
                oem_warranty_status_id = {'key': 'oem_warranty_status_id',
                                          'type': rec._fields['oem_warranty_status_id'].type,
                                          'title': rec._fields['oem_warranty_status_id'].string,
                                          'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
                repair_warranty_status_id = {'key': 'repair_warranty_status_id',
                                             'type': rec._fields['repair_warranty_status_id'].type,
                                             'title': rec._fields['repair_warranty_status_id'].string,
                                             'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
                # OTHER INFORMATION
                survey_id = {'key': 'survey_id', 'type': rec._fields['survey_id'].type,
                             'title': rec._fields['survey_id'].string,
                             'value': rec.survey_id.title if rec.survey_id else ''}
                company_id = {'key': 'company_id', 'type': rec._fields['company_id'].type,
                              'title': rec._fields['company_id'].string,
                              'value': rec.company_id.name if rec.company_id else ''}
                user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type,
                           'title': rec._fields['user_id'].string,
                           'value': rec.user_id.name if rec.user_id else ''}
                service_request_list.append([id, name,state, service_request_id_alias, service_request_date, approver_id,
                                             parent_ticket_id, child_ticket_id, child_ticket_type_id, call_source_id,
                                             service_type_id,
                                             service_category_id, request_type_id, reason, problem_reported,
                                             requested_by_name,
                                             requested_by_contact_number, call_received_id, team_id, remarks,
                                             customer_name, customer_email,
                                             customer_street, customer_street2, customer_city_id, customer_state_id,
                                             customer_zip,
                                             customer_country_id, dealer_distributor_name, product_name,
                                             custom_product_serial,
                                             product_part_number, product_part_code, oem_warranty_status_id,
                                             repair_warranty_status_id,
                                             survey_id, user_id, company_id
                                             ])
                service_request_list_len = len(service_request_list) - 1
                if rec.state in ['draft']:
                    service_request_list[service_request_list_len].append(
                        {'key': 'submit', 'type': "button",
                         'title': 'Submit',
                         'value': 'Submit',
                         })
        elif ticket_type=='sr_all':
            message = "SR-ALL load successfully"
            for rec in service_request_ids:
                id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                      'value': rec.id if rec.id else ''}
                name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                        'value': rec.name if rec.name else ''}
                state = {'key': 'state', 'type': rec._fields['state'].type, 'title': rec._fields['state'].string,
                         'value': dict(rec._fields['state'].selection).get(rec.state)}
                # SERVICE REQUEST INFORMATION
                service_request_id_alias = {'key': 'service_request_id_alias',
                                            'type': rec._fields['service_request_id_alias'].type,
                                            'title': rec._fields['service_request_id_alias'].string,
                                            'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
                service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type,
                                        'title': rec._fields['service_request_date'].string,
                                        'value': str(
                                            rec.service_request_date.astimezone(local_tz).replace(tzinfo=None).strftime(
                                                '%Y-%m-%d %I:%M %p')) if rec.service_request_date else ''}
                approver_id = {'key': 'approver_id', 'type': rec._fields['approver_id'].type,
                               'title': rec._fields['approver_id'].string,
                               'value': rec.approver_id.name if rec.approver_id else ''}
                parent_ticket_id = {'key': 'parent_ticket_id', 'type': rec._fields['parent_ticket_id'].type,
                                    'title': rec._fields['parent_ticket_id'].string,
                                    'value': rec.parent_ticket_id.name if rec.parent_ticket_id else ''}
                child_ticket_id = {'key': 'child_ticket_id', 'type': rec._fields['child_ticket_id'].type,
                                   'title': rec._fields['child_ticket_id'].string,
                                   'value': rec.child_ticket_id.name if rec.child_ticket_id else ''}
                child_ticket_type_id = {'key': 'child_ticket_type_id', 'type': rec._fields['child_ticket_type_id'].type,
                                        'title': rec._fields['child_ticket_type_id'].string,
                                        'value': rec.child_ticket_type_id.name if rec.child_ticket_type_id else ''}

                # CALL DETAILS
                call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
                                  'title': rec._fields['call_source_id'].string,
                                  'value': rec.call_source_id.name if rec.call_source_id else ''}
                service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
                                   'title': rec._fields['service_type_id'].string,
                                   'value': rec.service_type_id.name if rec.service_type_id else ''}
                service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
                                       'title': rec._fields['service_category_id'].string,
                                       'value': rec.service_category_id.name if rec.service_category_id else ''}
                request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
                                   'title': rec._fields['request_type_id'].string,
                                   'value': rec.request_type_id.name if rec.request_type_id else ''}
                reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
                          'value': rec.reason if rec.reason else ''}
                problem_reported = {'key': 'problem_reported', 'type': rec._fields['problem_reported'].type,
                                    'title': rec._fields['problem_reported'].string,
                                    'value': rec.problem_reported if rec.problem_reported else ''}
                requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type,
                                     'title': rec._fields['requested_by_name'].string,
                                     'value': rec.requested_by_name if rec.requested_by_name else ''}
                requested_by_contact_number = {'key': 'requested_by_contact_number',
                                               'type': rec._fields['requested_by_contact_number'].type,
                                               'title': rec._fields['requested_by_contact_number'].string,
                                               'value': rec.requested_by_contact_number if rec.requested_by_contact_number else ''}
                call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
                                    'title': rec._fields['call_received_id'].string,
                                    'value': rec.call_received_id.name if rec.call_received_id else ''}
                team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type,
                           'title': rec._fields['team_id'].string,
                           'value': rec.team_id.name if rec.team_id else ''}
                # INSTALLATION INFORMATION
                location_contact_person = {'key': 'location_contact_person',
                                           'type': rec._fields['location_contact_person'].type,
                                           'title': rec._fields['location_contact_person'].string,
                                           'value': rec.location_contact_person if rec.location_contact_person else ''}
                customer_po_number = {'key': 'customer_po_number', 'type': rec._fields['customer_po_number'].type,
                                      'title': rec._fields['customer_po_number'].string,
                                      'value': rec.customer_po_number if rec.customer_po_number else ''}
                customer_po_date = {'key': 'customer_po_date', 'type': rec._fields['customer_po_date'].type,
                                    'title': rec._fields['customer_po_date'].string,
                                    'value': str(rec.customer_po_date) if rec.customer_po_date else ''}
                tender_refer_number = {'key': 'tender_refer_number', 'type': rec._fields['tender_refer_number'].type,
                                       'title': rec._fields['tender_refer_number'].string,
                                       'value': rec.tender_refer_number if rec.tender_refer_number else ''}
                installation_date = {'key': 'installation_date', 'type': rec._fields['installation_date'].type,
                                     'title': rec._fields['installation_date'].string,
                                     'value': str(rec.installation_date) if rec.installation_date else ''}
                invoice_number = {'key': 'invoice_number', 'type': rec._fields['invoice_number'].type,
                                  'title': rec._fields['invoice_number'].string,
                                  'value': rec.invoice_number if rec.invoice_number else ''}
                invoice_date = {'key': 'invoice_date', 'type': rec._fields['invoice_date'].type,
                                'title': rec._fields['invoice_date'].string,
                                'value': str(rec.invoice_date) if rec.invoice_date else ''}
                extended_invoice_number = {'key': 'extended_invoice_number',
                                           'type': rec._fields['extended_invoice_number'].type,
                                           'title': rec._fields['extended_invoice_number'].string,
                                           'value': rec.extended_invoice_number if rec.extended_invoice_number else ''}
                extended_invoice_date = {'key': 'extended_invoice_date',
                                         'type': rec._fields['extended_invoice_date'].type,
                                         'title': rec._fields['extended_invoice_date'].string,
                                         'value': str(rec.extended_invoice_date) if rec.extended_invoice_date else ''}
                # CUSTOMER INFORMATION
                customer_name = {'key': 'customer_name', 'type': rec._fields['customer_name'].type,
                                 'title': rec._fields['customer_name'].string,
                                 'value': rec.customer_name if rec.customer_name else ''}
                customer_email = {'key': 'customer_email', 'type': rec._fields['customer_email'].type,
                                  'title': rec._fields['customer_email'].string,
                                  'value': rec.customer_email if rec.customer_email else ''}
                # ASSET DETAILS
                product_name = {'key': 'product_name', 'type': rec._fields['product_name'].type,
                                'title': rec._fields['product_name'].string,
                                'value': rec.product_name if rec.product_name else ''}
                custom_product_serial = {'key': 'custom_product_serial',
                                         'type': rec._fields['custom_product_serial'].type,
                                         'title': rec._fields['custom_product_serial'].string,
                                         'value': rec.custom_product_serial if rec.custom_product_serial else ''}
                product_part_number = {'key': 'product_part_number', 'type': rec._fields['product_part_number'].type,
                                       'title': rec._fields['product_part_number'].string,
                                       'value': rec.product_part_number if rec.product_part_number else ''}
                product_part_code = {'key': 'product_part_code', 'type': rec._fields['product_part_code'].type,
                                     'title': rec._fields['product_part_code'].string,
                                     'value': rec.product_part_code if rec.product_part_code else ''}
                oem_warranty_status_id = {'key': 'oem_warranty_status_id',
                                          'type': rec._fields['oem_warranty_status_id'].type,
                                          'title': rec._fields['oem_warranty_status_id'].string,
                                          'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
                repair_warranty_status_id = {'key': 'repair_warranty_status_id',
                                             'type': rec._fields['repair_warranty_status_id'].type,
                                             'title': rec._fields['repair_warranty_status_id'].string,
                                             'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}

                service_request_list.append(
                    [id, name,state, service_request_id_alias, service_request_date, approver_id, parent_ticket_id,
                     child_ticket_id, child_ticket_type_id, call_source_id, service_type_id, service_category_id,
                     request_type_id,
                     reason, problem_reported, requested_by_name, requested_by_contact_number, call_received_id,
                     team_id,
                     location_contact_person, customer_po_number, customer_po_date, tender_refer_number,
                     installation_date,
                     invoice_number, invoice_date, extended_invoice_number, extended_invoice_date, customer_name,
                     customer_email,
                     product_name, custom_product_serial, product_part_number, product_part_number, product_part_code,
                     oem_warranty_status_id, repair_warranty_status_id,
                     ])
                service_request_list_len = len(service_request_list) - 1
                if rec.state in ['draft']:
                    service_request_list[service_request_list_len].append(
                        {'key': 'submit', 'type': "button",
                         'title': 'Submit',
                         'value': 'Submit',
                         })

        if service_request_list:
            return valid_response2(service_request_list,filter_state, count, message, 200)
        else:
            return valid_response2(service_request_list,filter_state,count, 'there is no service request record', 200)

    @validate_token
    @http.route("/api/get_service_request_values/ticket_type/update", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_service_request_types_update(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('@ /api/get_service_request_values/ticket_type/update valuesssssss:%s', post)
        service_request_id = post.get('service_request_id')
        token = request.env['api.access_token'].search([('token', '=', post.get('access_token'))])
        user_tz = token.user_id.tz or 'UTC'
        local_tz = pytz.timezone(user_tz)
        submit_button = post.get('submit')
        service_request_obj = request.env['service.request']
        service_id = service_request_obj.sudo().browse(int(service_request_id))
        message = ''
        try:
            if submit_button and service_id:
                service_id.sudo().action_submit()
                message="submit action completed"
            return valid_response([[{'service_request_name': service_id.name}]], message, 200)
        except Exception as e:
            info = "There was a problem {}".format((e))
            error = "Something went wrong"
            _logger.error(info)
            return invalid_response(info, error, 403)


    # @validate_token
    # @http.route("/api/get_service_values", type="json", auth="none", methods=["POST"], csrf=False)
    # def _api_get_service_request_details(self, **post, ):
    #     post = json.loads(request.httprequest.data)
    #     user = request.env.user.browse(post.get('uid'))
    #     Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
    #     CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
    #     Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group('ppts_service_request.service_request_group_manager')
    #     National_Head = user.has_group('ppts_service_request.service_request_national_head')
    #
    #     domain=[]
    #     if CT_Users:
    #         domain += ['|',('user_id','=',user.id),('team_id', 'in', user.team_ids.ids)]
    #     elif Show_Service_Request_Service_Engineer:
    #         domain += [('user_id', '=', user.id)]
    #     elif Manager_CT_Repair_Manager_Service_Manager_RSM:
    #         domain += ['|',('user_id','=',user.id),('team_id', 'in', user.team_ids.ids)]
    #     elif National_Head:
    #         domain += ['|',('user_id', '=', user.id),('team_id', 'in', user.team_ids.ids)]
    #     else:
    #         domain +=[('id','=',False)]
    #     service_request_obj = request.env['service.request']
    #     service_request_all_keys = service_request_obj.sudo().fields_get()
    #     remove_magic_fields_key = list(set(service_request_all_keys.keys()).difference(magic_fields))
    #     custom=[]
    #     for test in service_request_all_keys.items():
    #         if test[1].get('store') and test[1].get('type') not in ['datetime','date','binary']:
    #             custom.append(test)
    #     custom_key=dict(custom).keys()
    #     parent_ticket_keys = list(set(custom_key).difference(magic_fields))
    #     for r in remove_magic_fields_key:
    #         if r in parent_ticket_keys:
    #             remove_magic_fields_key.remove(r)
    #
    #     service_request = service_request_obj.sudo().search_read(domain,fields)
    #     for t in service_request:
    #         sr_obj=service_request_obj.sudo().browse(t.get('id'))
    #         t['customer_po_date']=str(sr_obj.customer_po_date)
    #         t['extended_invoice_date']=str(sr_obj.extended_invoice_date)
    #         t['installation_date']=str(sr_obj.installation_date)
    #         t['invoice_date']= str(sr_obj.invoice_date)
    #         t['my_activity_date_deadline']=str(sr_obj.my_activity_date_deadline)
    #         t['service_request_date'] = str(sr_obj.service_request_date)
    #
    #     if service_request:
    #         return valid_response(service_request, 'Service Request load successfully', 200)
    #     else:
    #         return valid_response(service_request, 'there is no record', 200)


    # @validate_token
    # @http.route("/api/get_service_waiting_approval_request", type="json", auth="none", methods=["POST"], csrf=False)
    # def _api_get_service_request_waiting_for_approval(self, **post, ):
    #     uid = request.session.uid
    #     user = request.env.user.browse(uid)
    #     Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
    #     CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
    #     Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
    #         'ppts_service_request.service_request_group_manager')
    #     National_Head = user.has_group('ppts_service_request.service_request_national_head')
    #
    #     domain = [('state','=','waiting_for_approval'),('approver_ids.state', 'in', ('rejected','hold','new'))]
    #     if CT_Users:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif Show_Service_Request_Service_Engineer:
    #         domain += [('user_id', '=', user.id)]
    #     elif Manager_CT_Repair_Manager_Service_Manager_RSM:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif National_Head:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     else:
    #         domain += [('id', '=', False)]
    #     service_request_obj = request.env['service.request']
    #     waiting_for_approval_request = service_request_obj.sudo().search_read(domain, fields)
    #     for t in waiting_for_approval_request:
    #         sr_obj=service_request_obj.sudo().browse(t.get('id'))
    #         t['customer_po_date']=str(sr_obj.customer_po_date)
    #         t['extended_invoice_date']=str(sr_obj.extended_invoice_date)
    #         t['installation_date']=str(sr_obj.installation_date)
    #         t['invoice_date']= str(sr_obj.invoice_date)
    #         t['my_activity_date_deadline']=str(sr_obj.my_activity_date_deadline)
    #         t['service_request_date'] = str(sr_obj.service_request_date)
    #
    #     if waiting_for_approval_request:
    #         return valid_response(waiting_for_approval_request, 'Service Request waiting approval load successfully', 200)
    #     else:
    #         return valid_response(waiting_for_approval_request, 'there is no record', 200)



    # @validate_token
    # @http.route("/api/get_service_sr_loaner_request", type="json", auth="none", methods=["POST"], csrf=False)
    # def _api_get_service_sr_loaner_request(self, **post, ):
    #     post = json.loads(request.httprequest.data)
    #     user = request.env.user.browse(post.get('uid'))
    #     limit = post.get('limit')
    #     next_count = post.get('next_count')
    #     Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
    #     CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
    #     Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
    #         'ppts_service_request.service_request_group_manager')
    #     National_Head = user.has_group('ppts_service_request.service_request_national_head')
    #
    #     domain = [('request_type_id.ticket_type','=','sr_loaner')]
    #     if CT_Users:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif Show_Service_Request_Service_Engineer:
    #         domain += [('user_id', '=', user.id)]
    #     elif Manager_CT_Repair_Manager_Service_Manager_RSM:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif National_Head:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     else:
    #         domain += [('id', '=', False)]
    #     service_request_obj = request.env['service.request']
    #     count = service_request_obj.sudo().search_count(domain)
    #     service_request_ids = service_request_obj.sudo().search(domain, offset=next_count, limit=limit,
    #                                                             order='name ASC')
    #     service_request_list = []
    #     for rec in service_request_ids:
    #         id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
    #               'value': rec.id if rec.id else ''}
    #         name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
    #                 'value': rec.name if rec.name else ''}
    #         service_request_id_alias = {'key': 'service_request_id_alias',
    #                                     'type': rec._fields['service_request_id_alias'].type,
    #                                     'title': rec._fields['service_request_id_alias'].string,
    #                                     'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
    #         service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type,
    #                                 'title': rec._fields['service_request_date'].string,
    #                                 'value': str(rec.service_request_date) if rec.service_request_date else ''}
    #         call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
    #                           'title': rec._fields['call_source_id'].string,
    #                           'value': rec.call_source_id.name if rec.call_source_id else ''}
    #         service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
    #                            'title': rec._fields['service_type_id'].string,
    #                            'value': rec.service_type_id.name if rec.service_type_id else ''}
    #         service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
    #                                'title': rec._fields['service_category_id'].string,
    #                                'value': rec.service_category_id.name if rec.service_category_id else ''}
    #         request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
    #                            'title': rec._fields['request_type_id'].string,
    #                            'value': rec.request_type_id.name if rec.request_type_id else ''}
    #         reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
    #                   'value': rec.reason if rec.reason else ''}
    #         requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type,
    #                              'title': rec._fields['requested_by_name'].string,
    #                              'value': rec.requested_by_name if rec.requested_by_name else ''}
    #         call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
    #                             'title': rec._fields['call_received_id'].string,
    #                             'value': rec.call_received_id.name if rec.call_received_id else ''}
    #         team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type, 'title': rec._fields['team_id'].string,
    #                    'value': rec.team_id.name if rec.team_id else ''}
    #         oem_warranty_status_id = {'key': 'oem_warranty_status_id',
    #                                   'type': rec._fields['oem_warranty_status_id'].type,
    #                                   'title': rec._fields['oem_warranty_status_id'].string,
    #                                   'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
    #         repair_warranty_status_id = {'key': 'repair_warranty_status_id',
    #                                      'type': rec._fields['repair_warranty_status_id'].type,
    #                                      'title': rec._fields['repair_warranty_status_id'].string,
    #                                      'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
    #         remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type, 'title': rec._fields['remarks'].string,
    #                    'value': rec.remarks if rec.remarks else ''}
    #         user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type, 'title': rec._fields['user_id'].string,
    #                    'value': rec.user_id.name if rec.user_id else ''}
    #         service_request_list.append(
    #             [id, name, service_request_id_alias, service_request_date, call_source_id, service_type_id,
    #              service_category_id, request_type_id, reason, requested_by_name, call_received_id, team_id,
    #              oem_warranty_status_id,
    #              repair_warranty_status_id, remarks, user_id
    #              ])
    #     if service_request_list:
    #         return valid_response1(service_request_list, count, 'SR-Loaner load successfully', 200)
    #     else:
    #         return valid_response1(service_request_list,count, 'there is no SR-Loaner record', 200)
    #
    # @validate_token
    # @http.route("/api/get_service_sr_wr_request", type="json", auth="none", methods=["POST"], csrf=False)
    # def _api_get_service_sr_wr_request(self, **post, ):
    #     post = json.loads(request.httprequest.data)
    #     user = request.env.user.browse(post.get('uid'))
    #     limit = post.get('limit')
    #     next_count = post.get('next_count')
    #     Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
    #     CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
    #     Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
    #         'ppts_service_request.service_request_group_manager')
    #     National_Head = user.has_group('ppts_service_request.service_request_national_head')
    #
    #     domain = [('request_type_id.ticket_type','=','sr_wr')]
    #     if CT_Users:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif Show_Service_Request_Service_Engineer:
    #         domain += [('user_id', '=', user.id)]
    #     elif Manager_CT_Repair_Manager_Service_Manager_RSM:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif National_Head:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     else:
    #         domain += [('id', '=', False)]
    #     service_request_obj = request.env['service.request']
    #     count = service_request_obj.sudo().search_count(domain)
    #     service_request_ids = service_request_obj.sudo().search(domain, offset=next_count, limit=limit,
    #                                                             order='name ASC')
    #     service_request_list = []
    #     for rec in service_request_ids:
    #         id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
    #               'value': rec.id if rec.id else ''}
    #         name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
    #                 'value': rec.name if rec.name else ''}
    #         service_request_id_alias = {'key': 'service_request_id_alias',
    #                                     'type': rec._fields['service_request_id_alias'].type,
    #                                     'title': rec._fields['service_request_id_alias'].string,
    #                                     'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
    #         service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type,
    #                                 'title': rec._fields['service_request_date'].string,
    #                                 'value': str(rec.service_request_date) if rec.service_request_date else ''}
    #         call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
    #                           'title': rec._fields['call_source_id'].string,
    #                           'value': rec.call_source_id.name if rec.call_source_id else ''}
    #         service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
    #                            'title': rec._fields['service_type_id'].string,
    #                            'value': rec.service_type_id.name if rec.service_type_id else ''}
    #         service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
    #                                'title': rec._fields['service_category_id'].string,
    #                                'value': rec.service_category_id.name if rec.service_category_id else ''}
    #         request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
    #                            'title': rec._fields['request_type_id'].string,
    #                            'value': rec.request_type_id.name if rec.request_type_id else ''}
    #         reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
    #                   'value': rec.reason if rec.reason else ''}
    #         requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type,
    #                              'title': rec._fields['requested_by_name'].string,
    #                              'value': rec.requested_by_name if rec.requested_by_name else ''}
    #         call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
    #                             'title': rec._fields['call_received_id'].string,
    #                             'value': rec.call_received_id.name if rec.call_received_id else ''}
    #         team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type, 'title': rec._fields['team_id'].string,
    #                    'value': rec.team_id.name if rec.team_id else ''}
    #         oem_warranty_status_id = {'key': 'oem_warranty_status_id',
    #                                   'type': rec._fields['oem_warranty_status_id'].type,
    #                                   'title': rec._fields['oem_warranty_status_id'].string,
    #                                   'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
    #         repair_warranty_status_id = {'key': 'repair_warranty_status_id',
    #                                      'type': rec._fields['repair_warranty_status_id'].type,
    #                                      'title': rec._fields['repair_warranty_status_id'].string,
    #                                      'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
    #         remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type, 'title': rec._fields['remarks'].string,
    #                    'value': rec.remarks if rec.remarks else ''}
    #         user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type, 'title': rec._fields['user_id'].string,
    #                    'value': rec.user_id.name if rec.user_id else ''}
    #         service_request_list.append(
    #             [id, name, service_request_id_alias, service_request_date, call_source_id, service_type_id,
    #              service_category_id, request_type_id, reason, requested_by_name, call_received_id, team_id,
    #              oem_warranty_status_id,
    #              repair_warranty_status_id, remarks, user_id
    #              ])
    #     if service_request_list:
    #         return valid_response1(service_request_list, count, 'SR-Warranty Replacement load successfully', 200)
    #     else:
    #         return valid_response1(service_request_list,count, 'there is no SR-Warranty Replacement record', 200)
    #
    # @validate_token
    # @http.route("/api/get_service_sr_factory_repair_request", type="json", auth="none", methods=["POST"], csrf=False)
    # def _api_get_service_sr_factory_repair_request(self, **post, ):
    #     post = json.loads(request.httprequest.data)
    #     user = request.env.user.browse(post.get('uid'))
    #     limit = post.get('limit')
    #     next_count = post.get('next_count')
    #     Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
    #     CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
    #     Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
    #         'ppts_service_request.service_request_group_manager')
    #     National_Head = user.has_group('ppts_service_request.service_request_national_head')
    #
    #     domain = [('request_type_id.ticket_type','=','sr_factory_repair')]
    #     if CT_Users:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif Show_Service_Request_Service_Engineer:
    #         domain += [('user_id', '=', user.id)]
    #     elif Manager_CT_Repair_Manager_Service_Manager_RSM:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif National_Head:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     else:
    #         domain += [('id', '=', False)]
    #     service_request_obj = request.env['service.request']
    #     count = service_request_obj.sudo().search_count(domain)
    #     service_request_ids = service_request_obj.sudo().search(domain, offset=next_count, limit=limit,
    #                                                             order='name ASC')
    #     service_request_list = []
    #     for rec in service_request_ids:
    #         id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
    #               'value': rec.id if rec.id else ''}
    #         name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
    #                 'value': rec.name if rec.name else ''}
    #         service_request_id_alias = {'key': 'service_request_id_alias',
    #                                     'type': rec._fields['service_request_id_alias'].type,
    #                                     'title': rec._fields['service_request_id_alias'].string,
    #                                     'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
    #         service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type,
    #                                 'title': rec._fields['service_request_date'].string,
    #                                 'value': str(rec.service_request_date) if rec.service_request_date else ''}
    #         call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
    #                           'title': rec._fields['call_source_id'].string,
    #                           'value': rec.call_source_id.name if rec.call_source_id else ''}
    #         service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
    #                            'title': rec._fields['service_type_id'].string,
    #                            'value': rec.service_type_id.name if rec.service_type_id else ''}
    #         service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
    #                                'title': rec._fields['service_category_id'].string,
    #                                'value': rec.service_category_id.name if rec.service_category_id else ''}
    #         request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
    #                            'title': rec._fields['request_type_id'].string,
    #                            'value': rec.request_type_id.name if rec.request_type_id else ''}
    #         reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
    #                   'value': rec.reason if rec.reason else ''}
    #         requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type,
    #                              'title': rec._fields['requested_by_name'].string,
    #                              'value': rec.requested_by_name if rec.requested_by_name else ''}
    #         call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
    #                             'title': rec._fields['call_received_id'].string,
    #                             'value': rec.call_received_id.name if rec.call_received_id else ''}
    #         team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type, 'title': rec._fields['team_id'].string,
    #                    'value': rec.team_id.name if rec.team_id else ''}
    #         oem_warranty_status_id = {'key': 'oem_warranty_status_id',
    #                                   'type': rec._fields['oem_warranty_status_id'].type,
    #                                   'title': rec._fields['oem_warranty_status_id'].string,
    #                                   'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
    #         repair_warranty_status_id = {'key': 'repair_warranty_status_id',
    #                                      'type': rec._fields['repair_warranty_status_id'].type,
    #                                      'title': rec._fields['repair_warranty_status_id'].string,
    #                                      'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
    #         remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type, 'title': rec._fields['remarks'].string,
    #                    'value': rec.remarks if rec.remarks else ''}
    #         user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type, 'title': rec._fields['user_id'].string,
    #                    'value': rec.user_id.name if rec.user_id else ''}
    #         service_request_list.append(
    #             [id, name, service_request_id_alias, service_request_date, call_source_id, service_type_id,
    #              service_category_id, request_type_id, reason, requested_by_name, call_received_id, team_id,
    #              oem_warranty_status_id,
    #              repair_warranty_status_id, remarks, user_id
    #              ])
    #     if service_request_list:
    #         return valid_response1(service_request_list, count, 'SR-Factory Repair load successfully', 200)
    #     else:
    #         return valid_response1(service_request_list,count, 'there is no SR-Factory Repair record', 200)
    #
    #
    # @validate_token
    # @http.route("/api/get_service_sr_maintenance_request", type="json", auth="none", methods=["POST"], csrf=False)
    # def _api_get_service_sr_maintenance_request(self, **post, ):
    #     post = json.loads(request.httprequest.data)
    #     user = request.env.user.browse(post.get('uid'))
    #     limit = post.get('limit')
    #     next_count = post.get('next_count')
    #     Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
    #     CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
    #     Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
    #         'ppts_service_request.service_request_group_manager')
    #     National_Head = user.has_group('ppts_service_request.service_request_national_head')
    #
    #     domain = [('request_type_id.ticket_type','=','sr_maintenance')]
    #     if CT_Users:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif Show_Service_Request_Service_Engineer:
    #         domain += [('user_id', '=', user.id)]
    #     elif Manager_CT_Repair_Manager_Service_Manager_RSM:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif National_Head:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     else:
    #         domain += [('id', '=', False)]
    #     service_request_obj = request.env['service.request']
    #     count = service_request_obj.sudo().search_count(domain)
    #     service_request_ids = service_request_obj.sudo().search(domain, offset=next_count, limit=limit,
    #                                                             order='name ASC')
    #     service_request_list = []
    #     for rec in service_request_ids:
    #         id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
    #               'value': rec.id if rec.id else ''}
    #         name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
    #                 'value': rec.name if rec.name else ''}
    #         service_request_id_alias = {'key': 'service_request_id_alias',
    #                                     'type': rec._fields['service_request_id_alias'].type,
    #                                     'title': rec._fields['service_request_id_alias'].string,
    #                                     'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
    #         service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type,
    #                                 'title': rec._fields['service_request_date'].string,
    #                                 'value': str(rec.service_request_date) if rec.service_request_date else ''}
    #         call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
    #                           'title': rec._fields['call_source_id'].string,
    #                           'value': rec.call_source_id.name if rec.call_source_id else ''}
    #         service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
    #                            'title': rec._fields['service_type_id'].string,
    #                            'value': rec.service_type_id.name if rec.service_type_id else ''}
    #         service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
    #                                'title': rec._fields['service_category_id'].string,
    #                                'value': rec.service_category_id.name if rec.service_category_id else ''}
    #         request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
    #                            'title': rec._fields['request_type_id'].string,
    #                            'value': rec.request_type_id.name if rec.request_type_id else ''}
    #         reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
    #                   'value': rec.reason if rec.reason else ''}
    #         requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type,
    #                              'title': rec._fields['requested_by_name'].string,
    #                              'value': rec.requested_by_name if rec.requested_by_name else ''}
    #         call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
    #                             'title': rec._fields['call_received_id'].string,
    #                             'value': rec.call_received_id.name if rec.call_received_id else ''}
    #         team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type, 'title': rec._fields['team_id'].string,
    #                    'value': rec.team_id.name if rec.team_id else ''}
    #         oem_warranty_status_id = {'key': 'oem_warranty_status_id',
    #                                   'type': rec._fields['oem_warranty_status_id'].type,
    #                                   'title': rec._fields['oem_warranty_status_id'].string,
    #                                   'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
    #         repair_warranty_status_id = {'key': 'repair_warranty_status_id',
    #                                      'type': rec._fields['repair_warranty_status_id'].type,
    #                                      'title': rec._fields['repair_warranty_status_id'].string,
    #                                      'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
    #         remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type, 'title': rec._fields['remarks'].string,
    #                    'value': rec.remarks if rec.remarks else ''}
    #         user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type, 'title': rec._fields['user_id'].string,
    #                    'value': rec.user_id.name if rec.user_id else ''}
    #         service_request_list.append(
    #             [id, name, service_request_id_alias, service_request_date, call_source_id, service_type_id,
    #              service_category_id, request_type_id, reason, requested_by_name, call_received_id, team_id,
    #              oem_warranty_status_id,
    #              repair_warranty_status_id, remarks, user_id
    #              ])
    #     if service_request_list:
    #         return valid_response1(service_request_list, count, 'SR-Maintenance load successfully', 200)
    #     else:
    #         return valid_response1(service_request_list,count, 'there is no SR-Maintenance record', 200)
    #
    #
    # @validate_token
    # @http.route("/api/get_service_sr_fsm_request", type="json", auth="none", methods=["POST"], csrf=False)
    # def _api_get_service_sr_fsm_request(self, **post, ):
    #     post = json.loads(request.httprequest.data)
    #     user = request.env.user.browse(post.get('uid'))
    #     limit = post.get('limit')
    #     next_count = post.get('next_count')
    #     Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
    #     CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
    #     Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
    #         'ppts_service_request.service_request_group_manager')
    #     National_Head = user.has_group('ppts_service_request.service_request_national_head')
    #
    #     domain = [('request_type_id.ticket_type','=','sr_fsm')]
    #     if CT_Users:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif Show_Service_Request_Service_Engineer:
    #         domain += [('user_id', '=', user.id)]
    #     elif Manager_CT_Repair_Manager_Service_Manager_RSM:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif National_Head:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     else:
    #         domain += [('id', '=', False)]
    #     service_request_obj = request.env['service.request']
    #     count = service_request_obj.sudo().search_count(domain)
    #     service_request_ids = service_request_obj.sudo().search(domain, offset=next_count, limit=limit,
    #                                                             order='name ASC')
    #     service_request_list = []
    #     for rec in service_request_ids:
    #         id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
    #               'value': rec.id if rec.id else ''}
    #         name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
    #                 'value': rec.name if rec.name else ''}
    #         service_request_id_alias = {'key': 'service_request_id_alias',
    #                                     'type': rec._fields['service_request_id_alias'].type,
    #                                     'title': rec._fields['service_request_id_alias'].string,
    #                                     'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
    #         service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type,
    #                                 'title': rec._fields['service_request_date'].string,
    #                                 'value': str(rec.service_request_date) if rec.service_request_date else ''}
    #         call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
    #                           'title': rec._fields['call_source_id'].string,
    #                           'value': rec.call_source_id.name if rec.call_source_id else ''}
    #         service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
    #                            'title': rec._fields['service_type_id'].string,
    #                            'value': rec.service_type_id.name if rec.service_type_id else ''}
    #         service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
    #                                'title': rec._fields['service_category_id'].string,
    #                                'value': rec.service_category_id.name if rec.service_category_id else ''}
    #         request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
    #                            'title': rec._fields['request_type_id'].string,
    #                            'value': rec.request_type_id.name if rec.request_type_id else ''}
    #         reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
    #                   'value': rec.reason if rec.reason else ''}
    #         requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type,
    #                              'title': rec._fields['requested_by_name'].string,
    #                              'value': rec.requested_by_name if rec.requested_by_name else ''}
    #         call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
    #                             'title': rec._fields['call_received_id'].string,
    #                             'value': rec.call_received_id.name if rec.call_received_id else ''}
    #         team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type, 'title': rec._fields['team_id'].string,
    #                    'value': rec.team_id.name if rec.team_id else ''}
    #         oem_warranty_status_id = {'key': 'oem_warranty_status_id',
    #                                   'type': rec._fields['oem_warranty_status_id'].type,
    #                                   'title': rec._fields['oem_warranty_status_id'].string,
    #                                   'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
    #         repair_warranty_status_id = {'key': 'repair_warranty_status_id',
    #                                      'type': rec._fields['repair_warranty_status_id'].type,
    #                                      'title': rec._fields['repair_warranty_status_id'].string,
    #                                      'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
    #         remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type, 'title': rec._fields['remarks'].string,
    #                    'value': rec.remarks if rec.remarks else ''}
    #         user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type, 'title': rec._fields['user_id'].string,
    #                    'value': rec.user_id.name if rec.user_id else ''}
    #         service_request_list.append(
    #             [id, name, service_request_id_alias, service_request_date, call_source_id, service_type_id,
    #              service_category_id, request_type_id, reason, requested_by_name, call_received_id, team_id,
    #              oem_warranty_status_id,
    #              repair_warranty_status_id, remarks, user_id
    #              ])
    #     if service_request_list:
    #         return valid_response1(service_request_list, count, 'SR-FSM load successfully', 200)
    #     else:
    #         return valid_response1(service_request_list,count, 'there is no SR-FSM record', 200)
    #
    # @validate_token
    # @http.route("/api/get_service_sr_survey_escalation", type="json", auth="none", methods=["POST"], csrf=False)
    # def _api_get_service_sr_survey_escalation(self, **post, ):
    #     post = json.loads(request.httprequest.data)
    #     user = request.env.user.browse(post.get('uid'))
    #     limit = post.get('limit')
    #     next_count = post.get('next_count')
    #     Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
    #     CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
    #     Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
    #         'ppts_service_request.service_request_group_manager')
    #     National_Head = user.has_group('ppts_service_request.service_request_national_head')
    #
    #     domain = [('request_type_id.ticket_type','=','sr_survey_escalation')]
    #     if CT_Users:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif Show_Service_Request_Service_Engineer:
    #         domain += [('user_id', '=', user.id)]
    #     elif Manager_CT_Repair_Manager_Service_Manager_RSM:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif National_Head:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     else:
    #         domain += [('id', '=', False)]
    #     service_request_obj = request.env['service.request']
    #     count = service_request_obj.sudo().search_count(domain)
    #     service_request_ids = service_request_obj.sudo().search(domain, offset=next_count, limit=limit,
    #                                                             order='name ASC')
    #     service_request_list = []
    #     for rec in service_request_ids:
    #         id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
    #               'value': rec.id if rec.id else ''}
    #         name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
    #                 'value': rec.name if rec.name else ''}
    #         service_request_id_alias = {'key': 'service_request_id_alias',
    #                                     'type': rec._fields['service_request_id_alias'].type,
    #                                     'title': rec._fields['service_request_id_alias'].string,
    #                                     'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
    #         service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type,
    #                                 'title': rec._fields['service_request_date'].string,
    #                                 'value': str(rec.service_request_date) if rec.service_request_date else ''}
    #         call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
    #                           'title': rec._fields['call_source_id'].string,
    #                           'value': rec.call_source_id.name if rec.call_source_id else ''}
    #         service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
    #                            'title': rec._fields['service_type_id'].string,
    #                            'value': rec.service_type_id.name if rec.service_type_id else ''}
    #         service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
    #                                'title': rec._fields['service_category_id'].string,
    #                                'value': rec.service_category_id.name if rec.service_category_id else ''}
    #         request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
    #                            'title': rec._fields['request_type_id'].string,
    #                            'value': rec.request_type_id.name if rec.request_type_id else ''}
    #         reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
    #                   'value': rec.reason if rec.reason else ''}
    #         requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type,
    #                              'title': rec._fields['requested_by_name'].string,
    #                              'value': rec.requested_by_name if rec.requested_by_name else ''}
    #         call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
    #                             'title': rec._fields['call_received_id'].string,
    #                             'value': rec.call_received_id.name if rec.call_received_id else ''}
    #         team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type, 'title': rec._fields['team_id'].string,
    #                    'value': rec.team_id.name if rec.team_id else ''}
    #         oem_warranty_status_id = {'key': 'oem_warranty_status_id',
    #                                   'type': rec._fields['oem_warranty_status_id'].type,
    #                                   'title': rec._fields['oem_warranty_status_id'].string,
    #                                   'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
    #         repair_warranty_status_id = {'key': 'repair_warranty_status_id',
    #                                      'type': rec._fields['repair_warranty_status_id'].type,
    #                                      'title': rec._fields['repair_warranty_status_id'].string,
    #                                      'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
    #         remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type, 'title': rec._fields['remarks'].string,
    #                    'value': rec.remarks if rec.remarks else ''}
    #         user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type, 'title': rec._fields['user_id'].string,
    #                    'value': rec.user_id.name if rec.user_id else ''}
    #         service_request_list.append(
    #             [id, name, service_request_id_alias, service_request_date, call_source_id, service_type_id,
    #              service_category_id, request_type_id, reason, requested_by_name, call_received_id, team_id,
    #              oem_warranty_status_id,
    #              repair_warranty_status_id, remarks, user_id
    #              ])
    #     if service_request_list:
    #         return valid_response1(service_request_list, count, 'SR-Survey Escalation load successfully', 200)
    #     else:
    #         return valid_response1(service_request_list,count, 'there is no SR-Survey Escalation record', 200)
    #
    #
    #
    # @validate_token
    # @http.route("/api/get_service_sr_installation_request", type="json", auth="none", methods=["POST"], csrf=False)
    # def _api_get_service_sr_installation_request(self, **post, ):
    #     post = json.loads(request.httprequest.data)
    #     user = request.env.user.browse(post.get('uid'))
    #     limit = post.get('limit')
    #     next_count = post.get('next_count')
    #     Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
    #     CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
    #     Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
    #         'ppts_service_request.service_request_group_manager')
    #     National_Head = user.has_group('ppts_service_request.service_request_national_head')
    #
    #     domain = [('request_type_id.ticket_type','=','sr_installation')]
    #     if CT_Users:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif Show_Service_Request_Service_Engineer:
    #         domain += [('user_id', '=', user.id)]
    #     elif Manager_CT_Repair_Manager_Service_Manager_RSM:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif National_Head:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     else:
    #         domain += [('id', '=', False)]
    #     service_request_obj = request.env['service.request']
    #     count = service_request_obj.sudo().search_count(domain)
    #     service_request_ids = service_request_obj.sudo().search(domain, offset=next_count, limit=limit,
    #                                                             order='name ASC')
    #     service_request_list = []
    #     for rec in service_request_ids:
    #         id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
    #               'value': rec.id if rec.id else ''}
    #         name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
    #                 'value': rec.name if rec.name else ''}
    #         service_request_id_alias = {'key': 'service_request_id_alias',
    #                                     'type': rec._fields['service_request_id_alias'].type,
    #                                     'title': rec._fields['service_request_id_alias'].string,
    #                                     'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
    #         service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type,
    #                                 'title': rec._fields['service_request_date'].string,
    #                                 'value': str(rec.service_request_date) if rec.service_request_date else ''}
    #         call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
    #                           'title': rec._fields['call_source_id'].string,
    #                           'value': rec.call_source_id.name if rec.call_source_id else ''}
    #         service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
    #                            'title': rec._fields['service_type_id'].string,
    #                            'value': rec.service_type_id.name if rec.service_type_id else ''}
    #         service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
    #                                'title': rec._fields['service_category_id'].string,
    #                                'value': rec.service_category_id.name if rec.service_category_id else ''}
    #         request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
    #                            'title': rec._fields['request_type_id'].string,
    #                            'value': rec.request_type_id.name if rec.request_type_id else ''}
    #         reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
    #                   'value': rec.reason if rec.reason else ''}
    #         requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type,
    #                              'title': rec._fields['requested_by_name'].string,
    #                              'value': rec.requested_by_name if rec.requested_by_name else ''}
    #         call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
    #                             'title': rec._fields['call_received_id'].string,
    #                             'value': rec.call_received_id.name if rec.call_received_id else ''}
    #         team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type, 'title': rec._fields['team_id'].string,
    #                    'value': rec.team_id.name if rec.team_id else ''}
    #         oem_warranty_status_id = {'key': 'oem_warranty_status_id',
    #                                   'type': rec._fields['oem_warranty_status_id'].type,
    #                                   'title': rec._fields['oem_warranty_status_id'].string,
    #                                   'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
    #         repair_warranty_status_id = {'key': 'repair_warranty_status_id',
    #                                      'type': rec._fields['repair_warranty_status_id'].type,
    #                                      'title': rec._fields['repair_warranty_status_id'].string,
    #                                      'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
    #         remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type, 'title': rec._fields['remarks'].string,
    #                    'value': rec.remarks if rec.remarks else ''}
    #         user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type, 'title': rec._fields['user_id'].string,
    #                    'value': rec.user_id.name if rec.user_id else ''}
    #         service_request_list.append(
    #             [id, name, service_request_id_alias, service_request_date, call_source_id, service_type_id,
    #              service_category_id, request_type_id, reason, requested_by_name, call_received_id, team_id,
    #              oem_warranty_status_id,
    #              repair_warranty_status_id, remarks, user_id
    #              ])
    #     if service_request_list:
    #         return valid_response1(service_request_list, count, 'SR-Installation load successfully', 200)
    #     else:
    #         return valid_response1(service_request_list,count, 'there is no SR-Installation record', 200)
    #
    #
    #
    #
    # @validate_token
    # @http.route("/api/get_service_sr_remote_support_request", type="json", auth="none", methods=["POST"], csrf=False)
    # def _api_get_service_sr_remote_support_request(self, **post, ):
    #     post = json.loads(request.httprequest.data)
    #     user = request.env.user.browse(post.get('uid'))
    #     limit = post.get('limit')
    #     next_count = post.get('next_count')
    #     Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
    #     CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
    #     Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
    #         'ppts_service_request.service_request_group_manager')
    #     National_Head = user.has_group('ppts_service_request.service_request_national_head')
    #
    #     domain = [('request_type_id.ticket_type','=','sr_remote_support')]
    #     if CT_Users:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif Show_Service_Request_Service_Engineer:
    #         domain += [('user_id', '=', user.id)]
    #     elif Manager_CT_Repair_Manager_Service_Manager_RSM:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif National_Head:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     else:
    #         domain += [('id', '=', False)]
    #     service_request_obj = request.env['service.request']
    #     count = service_request_obj.sudo().search_count(domain)
    #     service_request_ids = service_request_obj.sudo().search(domain, offset=next_count, limit=limit,
    #                                                             order='name ASC')
    #     service_request_list = []
    #     for rec in service_request_ids:
    #         id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
    #               'value': rec.id if rec.id else ''}
    #         name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
    #                 'value': rec.name if rec.name else ''}
    #         service_request_id_alias = {'key': 'service_request_id_alias',
    #                                     'type': rec._fields['service_request_id_alias'].type,
    #                                     'title': rec._fields['service_request_id_alias'].string,
    #                                     'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
    #         service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type,
    #                                 'title': rec._fields['service_request_date'].string,
    #                                 'value': str(rec.service_request_date) if rec.service_request_date else ''}
    #         call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
    #                           'title': rec._fields['call_source_id'].string,
    #                           'value': rec.call_source_id.name if rec.call_source_id else ''}
    #         service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
    #                            'title': rec._fields['service_type_id'].string,
    #                            'value': rec.service_type_id.name if rec.service_type_id else ''}
    #         service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
    #                                'title': rec._fields['service_category_id'].string,
    #                                'value': rec.service_category_id.name if rec.service_category_id else ''}
    #         request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
    #                            'title': rec._fields['request_type_id'].string,
    #                            'value': rec.request_type_id.name if rec.request_type_id else ''}
    #         reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
    #                   'value': rec.reason if rec.reason else ''}
    #         requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type,
    #                              'title': rec._fields['requested_by_name'].string,
    #                              'value': rec.requested_by_name if rec.requested_by_name else ''}
    #         call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
    #                             'title': rec._fields['call_received_id'].string,
    #                             'value': rec.call_received_id.name if rec.call_received_id else ''}
    #         team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type, 'title': rec._fields['team_id'].string,
    #                    'value': rec.team_id.name if rec.team_id else ''}
    #         oem_warranty_status_id = {'key': 'oem_warranty_status_id',
    #                                   'type': rec._fields['oem_warranty_status_id'].type,
    #                                   'title': rec._fields['oem_warranty_status_id'].string,
    #                                   'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
    #         repair_warranty_status_id = {'key': 'repair_warranty_status_id',
    #                                      'type': rec._fields['repair_warranty_status_id'].type,
    #                                      'title': rec._fields['repair_warranty_status_id'].string,
    #                                      'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
    #         remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type, 'title': rec._fields['remarks'].string,
    #                    'value': rec.remarks if rec.remarks else ''}
    #         user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type, 'title': rec._fields['user_id'].string,
    #                    'value': rec.user_id.name if rec.user_id else ''}
    #         service_request_list.append(
    #             [id, name, service_request_id_alias, service_request_date, call_source_id, service_type_id,
    #              service_category_id, request_type_id, reason, requested_by_name, call_received_id, team_id,
    #              oem_warranty_status_id,
    #              repair_warranty_status_id, remarks, user_id
    #              ])
    #     if service_request_list:
    #         return valid_response1(service_request_list, count, 'SR-Remote Support load successfully', 200)
    #     else:
    #         return valid_response1(service_request_list,count, 'there is no SR-Remote Support record', 200)
    #
    # @validate_token
    # @http.route("/api/get_service_so_call_request", type="json", auth="none", methods=["POST"], csrf=False)
    # def _api_get_service_so_call_request_request(self, **post, ):
    #     post = json.loads(request.httprequest.data)
    #     user = request.env.user.browse(post.get('uid'))
    #     limit = post.get('limit')
    #     next_count = post.get('next_count')
    #     Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
    #     CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
    #     Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
    #         'ppts_service_request.service_request_group_manager')
    #     National_Head = user.has_group('ppts_service_request.service_request_national_head')
    #
    #     domain = [('request_type_id.ticket_type','=','so_call')]
    #     if CT_Users:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif Show_Service_Request_Service_Engineer:
    #         domain += [('user_id', '=', user.id)]
    #     elif Manager_CT_Repair_Manager_Service_Manager_RSM:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     elif National_Head:
    #         domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
    #     else:
    #         domain += [('id', '=', False)]
    #     service_request_obj = request.env['service.request']
    #     count = service_request_obj.sudo().search_count(domain)
    #     service_request_ids = service_request_obj.sudo().search(domain, offset=next_count, limit=limit,
    #                                                             order='name ASC')
    #     service_request_list = []
    #     for rec in service_request_ids:
    #         id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
    #               'value': rec.id if rec.id else ''}
    #         name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
    #                 'value': rec.name if rec.name else ''}
    #         service_request_id_alias = {'key': 'service_request_id_alias',
    #                                     'type': rec._fields['service_request_id_alias'].type,
    #                                     'title': rec._fields['service_request_id_alias'].string,
    #                                     'value': rec.service_request_id_alias if rec.service_request_id_alias else ''}
    #         service_request_date = {'key': 'service_request_date', 'type': rec._fields['service_request_date'].type,
    #                                 'title': rec._fields['service_request_date'].string,
    #                                 'value': str(rec.service_request_date) if rec.service_request_date else ''}
    #         call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
    #                           'title': rec._fields['call_source_id'].string,
    #                           'value': rec.call_source_id.name if rec.call_source_id else ''}
    #         service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
    #                            'title': rec._fields['service_type_id'].string,
    #                            'value': rec.service_type_id.name if rec.service_type_id else ''}
    #         service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
    #                                'title': rec._fields['service_category_id'].string,
    #                                'value': rec.service_category_id.name if rec.service_category_id else ''}
    #         request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
    #                            'title': rec._fields['request_type_id'].string,
    #                            'value': rec.request_type_id.name if rec.request_type_id else ''}
    #         reason = {'key': 'reason', 'type': rec._fields['reason'].type, 'title': rec._fields['reason'].string,
    #                   'value': rec.reason if rec.reason else ''}
    #         requested_by_name = {'key': 'requested_by_name', 'type': rec._fields['requested_by_name'].type,
    #                              'title': rec._fields['requested_by_name'].string,
    #                              'value': rec.requested_by_name if rec.requested_by_name else ''}
    #         call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
    #                             'title': rec._fields['call_received_id'].string,
    #                             'value': rec.call_received_id.name if rec.call_received_id else ''}
    #         team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type, 'title': rec._fields['team_id'].string,
    #                    'value': rec.team_id.name if rec.team_id else ''}
    #         oem_warranty_status_id = {'key': 'oem_warranty_status_id',
    #                                   'type': rec._fields['oem_warranty_status_id'].type,
    #                                   'title': rec._fields['oem_warranty_status_id'].string,
    #                                   'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
    #         repair_warranty_status_id = {'key': 'repair_warranty_status_id',
    #                                      'type': rec._fields['repair_warranty_status_id'].type,
    #                                      'title': rec._fields['repair_warranty_status_id'].string,
    #                                      'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
    #         remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type, 'title': rec._fields['remarks'].string,
    #                    'value': rec.remarks if rec.remarks else ''}
    #         user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type, 'title': rec._fields['user_id'].string,
    #                    'value': rec.user_id.name if rec.user_id else ''}
    #         service_request_list.append(
    #             [id, name, service_request_id_alias, service_request_date, call_source_id, service_type_id,
    #              service_category_id, request_type_id, reason, requested_by_name, call_received_id, team_id,
    #              oem_warranty_status_id,
    #              repair_warranty_status_id, remarks, user_id
    #              ])
    #     if service_request_list:
    #         return valid_response1(service_request_list, count, 'SO Call load successfully', 200)
    #     else:
    #         return valid_response1(service_request_list,count, 'there is no SO Call Support record', 200)

