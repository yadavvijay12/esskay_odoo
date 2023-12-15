from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response,valid_response1
from odoo import http
from odoo.http import request
import json
import logging
_logger = logging.getLogger(__name__)
class APIController(http.Controller):
    @validate_token
    @http.route("/api/get_child_ticket_value", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_child_ticket_value(self, **post):
        post = json.loads(request.httprequest.data)
        limit = post.get('limit')
        next_count = post.get('next_count')
        ticket_type = post.get('ticket_type')
        search_value = post.get('search_value')
        ticket_id = post.get('id')
        user = request.env.user.browse(post.get('uid'))
        child_ticket_obj = request.env['child.ticket']
        Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
        CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
        Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
            'ppts_service_request.service_request_group_manager')
        National_Head = user.has_group('ppts_service_request.service_request_national_head')

        domain = [('request_type_id.ticket_type','=',ticket_type)]
        if ticket_id:
            domain += [('id', '=', int(ticket_id))]
        if search_value:
            domain += [('name', 'ilike', search_value)]
        if CT_Users:
            domain += [('team_id', 'in', user.team_ids.ids)]
        elif Show_Service_Request_Service_Engineer:
            domain += [('assign_engineer_ids','in',user.id),('is_pi_true','=',True)]
        elif Manager_CT_Repair_Manager_Service_Manager_RSM:
            domain += [('team_id', 'in', user.team_ids.ids)]
        elif National_Head:
            domain += [('team_id', 'in', user.team_ids.ids)]
        else:
            domain += [('id', '=', False)]
        _logger.info('domain',domain)
        count = child_ticket_obj.sudo().search_count(domain)
        child_ticket_ids = child_ticket_obj.sudo().search(domain, offset=next_count, limit=limit,
                                                                order='name DESC')
        child_ticket_list = []
        for rec in child_ticket_ids:
            id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                  'value': rec.id if rec.id else ''}
            name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                    'value': rec.name if rec.name else ''}
            child_ticket_id_alias = {'key': 'child_ticket_id_alias', 'type': rec._fields['child_ticket_id_alias'].type, 'title': rec._fields['child_ticket_id_alias'].string,
                    'value': rec.child_ticket_id_alias if rec.child_ticket_id_alias else ''}
            child_configuration_id = {'key': 'child_configuration_id', 'type': rec._fields['child_configuration_id'].type, 'title': rec._fields['child_configuration_id'].string,
                    'value': rec.child_configuration_id.child_config_name if rec.child_configuration_id else ''}
            child_ticket_type_id = {'key': 'child_ticket_type_id', 'type': rec._fields['child_ticket_type_id'].type, 'title': rec._fields['child_ticket_type_id'].string,
                    'value': rec.child_ticket_type_id.name if rec.child_ticket_type_id else ''}
            partner_id = {'key': 'partner_id', 'type': rec._fields['partner_id'].type, 'title': rec._fields['partner_id'].string,
                    'value': rec.partner_id.name if rec.partner_id else '','id': rec.partner_id.id if rec.partner_id else ''}
            call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type, 'title': rec._fields['call_source_id'].string,
                    'value': rec.call_source_id.name if rec.call_source_id else ''}
            call_date = {'key': 'call_date', 'type': rec._fields['call_date'].type, 'title': rec._fields['call_date'].string,
                    'value': str(rec.call_date) if rec.call_date else ''}
            request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type, 'title': rec._fields['request_type_id'].string,
                    'value': rec.request_type_id.name if rec.request_type_id else ''}
            service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type, 'title': rec._fields['service_category_id'].string,
                    'value': rec.service_category_id.name if rec.service_category_id else ''}
            service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type, 'title': rec._fields['service_type_id'].string,
                    'value': rec.service_type_id.name if rec.service_type_id else ''}
            stock_lot_id = {'key': 'stock_lot_id', 'type': rec._fields['stock_lot_id'].type, 'title': rec._fields['stock_lot_id'].string,
                    'value': rec.stock_lot_id.name if rec.stock_lot_id else ''}
            product_id = {'key': 'product_id', 'type': rec._fields['product_id'].type, 'title': rec._fields['product_id'].string,
                    'value': rec.product_id.name if rec.product_id else ''}
            oem_warranty_status = {'key': 'oem_warranty_status', 'type': rec._fields['oem_warranty_status'].type, 'title': rec._fields['oem_warranty_status'].string,
                    'value': dict(rec._fields['oem_warranty_status'].selection).get(rec.oem_warranty_status) if rec.oem_warranty_status else ''}
            oem_repair_status = {'key': 'oem_repair_status', 'type': rec._fields['oem_repair_status'].type, 'title': rec._fields['oem_repair_status'].string,
                    'value': dict(rec._fields['oem_repair_status'].selection).get(rec.oem_repair_status) if rec.oem_repair_status else ''}
            categ_id = {'key': 'categ_id', 'type': rec._fields['categ_id'].type, 'title': rec._fields['categ_id'].string,
                    'value': rec.categ_id.name if rec.categ_id else ''}
            product_category_id_alias = {'key': 'product_category_id_alias', 'type': rec._fields['product_category_id_alias'].type, 'title': rec._fields['product_category_id_alias'].string,
                    'value': rec.product_category_id_alias if rec.product_category_id_alias else ''}
            problem_description = {'key': 'problem_description', 'type': rec._fields['problem_description'].type, 'title': rec._fields['problem_description'].string,
                    'value': rec.problem_description if rec.problem_description else ''}
            requested_by_name_child = {'key': 'requested_by_name_child', 'type': rec._fields['requested_by_name_child'].type, 'title': rec._fields['requested_by_name_child'].string,
                    'value': rec.requested_by_name_child if rec.requested_by_name_child else ''}
            requested_by_contact_number =  {'key': 'requested_by_contact_number', 'type': rec._fields['requested_by_contact_number'].type, 'title': rec._fields['requested_by_contact_number'].string,
                    'value': rec.requested_by_contact_number if rec.requested_by_contact_number else ''}
            remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type, 'title': rec._fields['remarks'].string,
                    'value': rec.remarks if rec.remarks else ''}
            installation_date = {'key': 'installation_date', 'type': rec._fields['installation_date'].type, 'title': rec._fields['installation_date'].string,
                    'value': str(rec.installation_date) if rec.installation_date else ''}
            dealer_distributor_id = {'key': 'dealer_distributor_id', 'type': rec._fields['dealer_distributor_id'].type, 'title': rec._fields['dealer_distributor_id'].string,
                    'value': rec.dealer_distributor_id.name if rec.dealer_distributor_id else ''}
            call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type, 'title': rec._fields['call_received_id'].string,
                    'value': rec.call_received_id.name if rec.call_received_id else ''}
            alternate_contact_name = {'key': 'alternate_contact_name', 'type': rec._fields['alternate_contact_name'].type, 'title': rec._fields['alternate_contact_name'].string,
                    'value': rec.alternate_contact_name if rec.alternate_contact_name else ''}
            alternate_contact_number = {'key': 'alternate_contact_number', 'type': rec._fields['alternate_contact_number'].type, 'title': rec._fields['alternate_contact_number'].string,
                    'value': rec.alternate_contact_number if rec.alternate_contact_number else ''}
            oem_warranty_status_id = {'key': 'oem_warranty_status_id', 'type': rec._fields['oem_warranty_status_id'].type, 'title': rec._fields['oem_warranty_status_id'].string,
                    'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
            repair_warranty_status_id = {'key': 'repair_warranty_status_id', 'type': rec._fields['repair_warranty_status_id'].type, 'title': rec._fields['repair_warranty_status_id'].string,
                    'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
            cmc_status = {'key': 'cmc_status', 'type': rec._fields['cmc_status'].type, 'title': rec._fields['cmc_status'].string,
                    'value': rec.cmc_status if rec.cmc_status else ''}
            amc_status = {'key': 'amc_status', 'type': rec._fields['amc_status'].type, 'title': rec._fields['amc_status'].string,
                    'value': rec.amc_status if rec.amc_status else ''}
            current_asset_location = {'key': 'current_asset_location', 'type': rec._fields['current_asset_location'].type, 'title': rec._fields['current_asset_location'].string,
                    'value': rec.current_asset_location if rec.current_asset_location else ''}
            team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type, 'title': rec._fields['team_id'].string,
                    'value': rec.team_id.name if rec.team_id else ''}
            customer_account_id = {'key': 'customer_account_id', 'type': rec._fields['customer_account_id'].type, 'title': rec._fields['customer_account_id'].string,
                    'value': rec.customer_account_id.name if rec.customer_account_id else ''}
            parent_ticket_id = {'key': 'parent_ticket_id', 'type': rec._fields['parent_ticket_id'].type, 'title': rec._fields['parent_ticket_id'].string,
                    'value': rec.parent_ticket_id.name if rec.parent_ticket_id else ''}
            service_request_id = {'key': 'service_request_id', 'type': rec._fields['service_request_id'].type, 'title': rec._fields['service_request_id'].string,
                    'value': rec.service_request_id.name if rec.service_request_id else ''}
            faulty_section = {'key': 'faulty_section', 'type': rec._fields['faulty_section'].type, 'title': rec._fields['faulty_section'].string,
                    'value': rec.faulty_section if rec.faulty_section else ''}
            sow = {'key': 'sow', 'type': rec._fields['sow'].type, 'title': rec._fields['sow'].string,
                    'value': rec.sow if rec.sow else ''}
            webdelata_id = {'key': 'webdelata_id', 'type': rec._fields['webdelata_id'].type, 'title': rec._fields['webdelata_id'].string,
                    'value': rec.webdelata_id if rec.webdelata_id else ''}
            webdelata = {'key': 'webdelata', 'type': rec._fields['webdelata'].type, 'title': rec._fields['webdelata'].string,
                    'value': rec.webdelata if rec.webdelata else ''}
            mc_stk = {'key': 'mc_stk', 'type': rec._fields['mc_stk'].type, 'title': rec._fields['mc_stk'].string,
                    'value': dict(rec._fields['mc_stk'].selection).get(rec.mc_stk) if rec.mc_stk else ''}
            company_id = {'key': 'company_id', 'type': rec._fields['company_id'].type, 'title': rec._fields['company_id'].string,
                    'value': rec.company_id.name if rec.company_id else ''}
            survey_id = {'key': 'survey_id', 'type': rec._fields['survey_id'].type, 'title': rec._fields['survey_id'].string,
                    'value': rec.survey_id.title if rec.survey_id else ''}

            child_ticket_list.append(
                [id, name, child_ticket_id_alias, child_configuration_id, child_ticket_type_id, partner_id,
                 call_source_id, call_date, request_type_id, service_category_id, service_type_id, stock_lot_id,
                 product_id,
                 oem_warranty_status, oem_repair_status, categ_id, product_category_id_alias, problem_description,
                 requested_by_name_child, requested_by_contact_number, remarks, installation_date,
                 dealer_distributor_id, call_received_id,
                 alternate_contact_name, alternate_contact_number, oem_warranty_status_id,
                 repair_warranty_status_id,
                 cmc_status, amc_status, current_asset_location, team_id, customer_account_id, parent_ticket_id,
                 service_request_id,
                 faulty_section, sow, webdelata_id, webdelata, mc_stk, company_id, survey_id,
                 ])
            child_ticket_len = len(child_ticket_list)-1
            if rec.state not in ['cancel','closed']:
                request_raise_invoice = {'key': 'request_raise_invoice', 'type': "button",
                                         'title': 'Invoice Request',
                                         'value': True
                                         }
                child_ticket_list[child_ticket_len].append(request_raise_invoice)
                request_quotation = {'key': 'request_quotation', 'type': "button",
                                     'title': 'Quote Request',
                                     'value': True
                                     }
                child_ticket_list[child_ticket_len].append(request_quotation)
                action_spare_request = {'key': 'action_spare_request', 'type': "button",
                                        'title': 'Spare Request',
                                        'value': True
                                        }
                child_ticket_list[child_ticket_len].append(action_spare_request)
                action_child_status = {'key':'action_child_status','type': "button",
                                        'title': 'Status',
                                        'value': True}
                child_ticket_list[child_ticket_len].append(action_child_status)
            if rec.is_create_installation and rec.is_installation_created == False:
                start_installation = {'key': 'start_installation', 'type': "button",
                                      'title': 'Start Installation',
                                      'value': True
                                      }
                child_ticket_list[child_ticket_len].append(start_installation)
            if rec.request_count > 0:
                print(rec.request_count,'request_count')
                action_request_data = {'key': 'action_request_data', 'type': "button",
                                       'title': 'Request',
                                       'value': True}
                child_ticket_list[child_ticket_len].append(action_request_data)
        if child_ticket_list:
            return valid_response1(child_ticket_list,count, 'child ticket load successfully', 200)
        else:
            return valid_response1(child_ticket_list,count, 'there is no child ticket', 200)

    @validate_token
    @http.route("/api/get_child_ticket_value/start_installation", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_installation_value_update(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('/api/get_child_ticket_value/start_installation :%s', post)
        try:
            start_installation = post.get('start_installation')
            child_id = post.get('child_id')
            child_ticket = request.env['child.ticket'].sudo().browse(int(child_id))
            if child_ticket:
                child_ticket.action_create_installation()
                return valid_response([[{'child_ticket_start_button':True}]], 'child ticket load successfully', 200)
        except Exception as e:
            info = "There was a problem {}".format((e))
            error = "Something went wrong"
            _logger.error(info)
            return invalid_response(info, error, 403)
    @validate_token
    @http.route("/api/get_child_ticket_value/button_update",type="json",auth="none",methods=["POST"],csrf=False)
    def _api_get_child_ticket_button_update(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('/api/get_child_ticket_value/button_update :%s', post)
        try:
            start_installation = post.get('start_installation')
            request_raise_invoice = post.get('request_raise_invoice')
            request_quotation = post.get('request_quotation')
            action_spare_request = post.get('action_spare_request')
            child_id = post.get('child_id')
            child_obj = request.env['child.ticket'].sudo()
            request_obj = request.env['request.asset.line'].sudo()
            child_ticket = child_obj.browse(int(child_id))
            message =''
            spare_request_list = []
            if request_raise_invoice and child_ticket:
                child_ticket.request_raise_invoice()
                message = 'request raise invoice button load successfully'
            elif request_quotation and child_ticket:
                child_ticket.request_quotation()
                message = 'request quotation button load successfully'
            elif start_installation and child_ticket:
                child_ticket.action_create_installation()
                message = 'installation button load successfully'
            elif action_spare_request and child_ticket:
                # child_ticket.action_spare_request()
                message = 'action_spare_request button load successfully'
                print(request_obj._fields,'teeeeee')
                print(request_obj._fields['description'].string)
                description = {'key': 'description', 'type': request_obj._fields['description'].type,
                           'title': request_obj._fields['description'].string,
                           'required': request_obj._fields['description'].required}
                spare_request_list.append(description)
                part_number = {'key': 'part_number', 'type': request_obj._fields['part_number'].type,
                               'title': request_obj._fields['part_number'].string,
                               'required': request_obj._fields['part_number'].required}
                spare_request_list.append(part_number)
                serial_number = {'key': 'serial_number', 'type': request_obj._fields['serial_number'].type,
                               'title': request_obj._fields['serial_number'].string,
                               'required': request_obj._fields['serial_number'].required}
                spare_request_list.append(serial_number)
                quantity = {'key': 'quantity', 'type': request_obj._fields['quantity'].type,
                               'title': request_obj._fields['quantity'].string,
                               'required': request_obj._fields['quantity'].required}
                spare_request_list.append(quantity)
            return valid_response([spare_request_list], message, 200)
        except Exception as e:
            info = "There was a problem {}".format((e))
            error = "Something went wrong"
            _logger.error(info)
            return invalid_response(info, error, 403)

    @validate_token
    @http.route("/api/get_child_ticket_value/action_spare_request", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_child_ticket_action_spare_request_update(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('/api/get_child_ticket_value/action_spare_request: %s' % post)
        try:
            child_id = post.get('child_id')
            child_obj = request.env['child.ticket'].sudo()
            child_ticket = child_obj.browse(int(child_id))
            asset_values_dic = {}
            if post.get('description'):
                asset_values_dic['description'] = post.get('description')
            if post.get('part_number'):
                asset_values_dic['part_number'] = post.get('part_number')
            if post.get('serial_number'):
                asset_values_dic['serial_number'] = post.get('serial_number')
            if post.get('quantity'):
                asset_values_dic['quantity'] = int(post.get('quantity'))
            request_vals = {
                "name" : "Spare Request",
                "is_spare_request" : True,
                "child_ticket_id" : child_ticket.id,
                "team_id" : child_ticket.team_id.id,
                "user_id" : request.env.user.id,
                "partner_id": child_ticket.partner_id.id,
                "asset_ids": [(0, 0, asset_values_dic)]
            }
            request_id = request.env['request'].sudo().create(request_vals)
            if request_id:
                return valid_response([[{'create_spare_request_id': request_id.name}]],
                                      'Spare request create successfully', 200)
        except Exception as e:
            info = "There was a problem {}".format((e))
            error = "Something went wrong"
            _logger.error(info)
            return invalid_response(info, error, 403)

    @validate_token
    @http.route("/api/get_child_ticket_value/child_request", type="json", auth="none", methods=["POST"],
                csrf=False)
    def _api_get_child_ticket_value_child_request(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('/api/get_child_ticket_value/child_request: %s' % post)
        try:
            child_id = post.get('child_id')
            request_obj = request.env['request'].sudo()
            count = request_obj.search_count([('child_ticket_id','=',int(child_id))])
            child_request_ids = request_obj.search([('child_ticket_id','=',int(child_id))])
            child_request_list = []
            for rec in child_request_ids:
                id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                      'value': rec.id if rec.id else ''}
                name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                      'value': rec.name if rec.name else ''}
                child_ticket_id = {'key': 'child_ticket_id', 'type': rec._fields['child_ticket_id'].type, 'title': rec._fields['child_ticket_id'].string,
                      'value': rec.child_ticket_id.name if rec.child_ticket_id else ''}
                team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type, 'title': rec._fields['team_id'].string,
                      'value': rec.team_id.name if rec.team_id else ''}
                user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type, 'title': rec._fields['user_id'].string,
                      'value': rec.user_id.name if rec.user_id else ''}
                company_id = {'key': 'company_id', 'type': rec._fields['company_id'].type, 'title': rec._fields['company_id'].string,
                      'value': rec.company_id.name if rec.company_id else ''}
                child_request_list.append([id,name,child_ticket_id,team_id,user_id,company_id])
                requst_list_index = len(child_request_list) - 1
                if rec.is_spare_request:
                    spare_list = []
                    for spare in rec.asset_ids:
                        id = {'key': 'id', 'type': spare._fields['id'].type, 'title': spare._fields['id'].string,
                              'value': spare.id if spare.id else ''}
                        product_id = {'key': 'product_id', 'type': spare._fields['product_id'].type, 'title': spare._fields['product_id'].string,
                              'value': spare.product_id.name if spare.product_id else ''}
                        description = {'key': 'description', 'type': spare._fields['description'].type, 'title': spare._fields['description'].string,
                              'value': spare.description if spare.description else ''}
                        part_number = {'key': 'part_number', 'type': spare._fields['part_number'].type, 'title': spare._fields['part_number'].string,
                              'value': spare.part_number if spare.part_number else ''}
                        serial_number = {'key': 'serial_number', 'type': spare._fields['serial_number'].type,
                                       'title': spare._fields['serial_number'].string,
                                       'value': spare.serial_number if spare.serial_number else ''}
                        quantity = {'key': 'quantity', 'type': spare._fields['quantity'].type,
                                       'title': spare._fields['quantity'].string,
                                       'value': spare.quantity if spare.quantity else ''}
                        stock_availability = {'key': 'stock_availability',
                                              'type': spare._fields['stock_availability'].type,
                                              'title': spare._fields['stock_availability'].string,
                                              'value': dict(spare._fields['stock_availability'].selection).get(
                                                  spare.stock_availability)}
                        spare_list.append([id,product_id,description,part_number,serial_number,quantity,stock_availability])
                    if spare_list:
                        asset_ids = {'key': 'asset_ids', 'type': rec._fields['asset_ids'].type,
                                      'title': rec._fields['asset_ids'].string,
                                      'value':'',
                                     'data': spare_list,}
                        child_request_list[requst_list_index].append(asset_ids)
            if child_request_list:
                return valid_response1(child_request_list, count, 'child ticket request load successfully', 200)
            else:
                return valid_response1(child_request_list, count, 'there is no request', 200)
        except Exception as e:
            info = "There was a problem {}".format((e))
            error = "Something went wrong"
            _logger.error(info)
            return invalid_response(info, error, 403)
        # production_missing_fields = ['survey_id']
        # child_ticket = child_ticket_obj.sudo().search_read([], ['name', 'child_ticket_id_alias','child_configuration_id','child_ticket_type_id','partner_id',
        #                                                         'call_source_id', 'request_type_id','service_category_id','service_type_id','stock_lot_id','product_id',
        #                                                         'oem_warranty_status','oem_repair_status', 'categ_id','product_category_id_alias','problem_description',
        #                                                         'requested_by_name_child','requested_by_contact_number','remarks', 'dealer_distributor_id','call_received_id',
        #                                                         'alternate_contact_name','alternate_contact_number','oem_warranty_status_id','repair_warranty_status_id',
        #                                                         'cmc_status','amc_status','current_asset_location','team_id','customer_account_id','parent_ticket_id',
        #                                                         'service_request_id','faulty_section','sow','webdelata_id','webdelata','mc_stk','company_id',
        #                                                         ])
        # for rec in child_ticket:
        #     parent=child_ticket_obj.sudo().browse(rec.get('id'))
        #     rec['call_date'] = str(parent.call_date)
        #     rec['installation_date']=str(parent.installation_date)
        # if child_ticket:
        #     return valid_response(child_ticket, 'child ticket load successfully', 200)
        # else:
        #     return valid_response(child_ticket, 'there is no child ticket', 200)