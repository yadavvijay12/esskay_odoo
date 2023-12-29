from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response,valid_response1,valid_response2
from odoo import http
from odoo.http import request
import json
from datetime import datetime , timezone
import logging
_logger = logging.getLogger(__name__)
class APIController(http.Controller):
    @validate_token
    @http.route("/api/get_parent_ticket_value", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_parent_ticket_value(self, **post,):
        post = json.loads(request.httprequest.data)
        limit = post.get('limit')
        next_count = post.get('next_count')
        ticket_type = post.get('ticket_type')
        search_value = post.get('search_value')
        ticket_ids = post.get('ids')
        state_filter = post.get('state_filter')
        # request_type_code = post.get('code')
        # user = request.env.user.browse(post.get('uid'))

        uid = request.env.uid
        user = request.env.user.browse(uid)
        company_id = request.env.company.id

        parent_ticket_obj = request.env['parent.ticket']
        Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
        CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
        Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
            'ppts_service_request.service_request_group_manager')
        National_Head = user.has_group('ppts_service_request.service_request_national_head')

        domain = [('company_id', '=', company_id)]
        if ticket_ids:
            domain += [('id', 'in', list(ticket_ids))]
        # if request_type_code:
        #     domain += [('request_type_id.code', '=', request_type_code)]
        if search_value:
            domain += [('name', 'ilike', search_value)]
        if ticket_type and ticket_type != 'tk_all':
            domain += [('request_type_id.ticket_type','=',ticket_type)]
        if state_filter and state_filter !='all':
            domain +=[('state','=',state_filter)]

        if CT_Users:
            domain += [('team_id', 'in', user.team_ids.ids)]
        elif Show_Service_Request_Service_Engineer:
            domain += [('team_id', 'in', user.team_ids.ids)]
        elif Manager_CT_Repair_Manager_Service_Manager_RSM:
            domain += [('team_id', 'in', user.team_ids.ids)]
        elif National_Head:
            domain += [('team_id', 'in', user.team_ids.ids)]
        else:
            domain += [('id', '=', False)]
        count = parent_ticket_obj.sudo().search_count(domain)
        parent_ticket_ids = parent_ticket_obj.sudo().search(domain, offset=next_count, limit=limit,
                                                          order='name desc')

        state_value_all = dict(parent_ticket_obj._fields['state'].selection)
        filter_state = [{'id': field,
                         'value': state_value_all.get(field), }
                        for field in state_value_all]
        filter_state.insert(0, {'id': 'all', 'value': "ALL"})

        parent_ticket_list = []
        for rec in parent_ticket_ids:
            id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                  'value': rec.id if rec.id else ''}
            name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                    'value': rec.name if rec.name else ''}
            state = {'key': 'state', 'type': rec._fields['state'].type, 'title': rec._fields['state'].string,
                     'value': dict(rec._fields['state'].selection).get(rec.state)}
            # TICKET INFORMATION
            parent_ticket_id_alias = {'key': 'parent_ticket_id_alias', 'type': rec._fields['parent_ticket_id_alias'].type,
                                     'title': rec._fields['parent_ticket_id_alias'].string,
                                     'value': rec.parent_ticket_id_alias if rec.parent_ticket_id_alias else ''}
            call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
                              'title': rec._fields['call_source_id'].string,
                              'value': rec.call_source_id.name if rec.call_source_id else ''}
            call_date = {'key': 'call_date', 'type': rec._fields['call_date'].type,
                         'title': rec._fields['call_date'].string,
                         'value': str(rec.call_date) if rec.call_date else ''}
            service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
                                   'title': rec._fields['service_category_id'].string,
                                   'value': rec.service_category_id.name if rec.service_category_id else ''}
            service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
                               'title': rec._fields['service_type_id'].string,
                               'value': rec.service_type_id.name if rec.service_type_id else ''}
            parent_configuration_id = {'key': 'parent_configuration_id',
                                      'type': rec._fields['parent_configuration_id'].type,
                                      'title': rec._fields['parent_configuration_id'].string,
                                      'value': rec.parent_configuration_id.parent_config_name if rec.parent_configuration_id else ''}
            request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
                               'title': rec._fields['request_type_id'].string,
                               'value': rec.request_type_id.name if rec.request_type_id else ''}
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
            team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type, 'title': rec._fields['team_id'].string,
                       'value': rec.team_id.name if rec.team_id else ''}
            problem_description = {'key': 'problem_description', 'type': rec._fields['problem_description'].type,
                                   'title': rec._fields['problem_description'].string,
                                   'value': rec.problem_description if rec.problem_description else ''}
            # ASSET DETAILS
            stock_lot_id = {'key': 'stock_lot_id', 'type': rec._fields['stock_lot_id'].type,
                            'title': rec._fields['stock_lot_id'].string,
                            'value': rec.stock_lot_id.name if rec.stock_lot_id else ''}
            product_id = {'key': 'product_id', 'type': rec._fields['product_id'].type,
                          'title': rec._fields['product_id'].string,
                          'value': rec.product_id.name if rec.product_id else ''}
            product_code_no = {'key': 'product_code_no', 'type': rec._fields['product_code_no'].type,
                          'title': rec._fields['product_code_no'].string,
                          'value': rec.product_code_no if rec.product_code_no else ''}
            categ_id = {'key': 'categ_id', 'type': rec._fields['categ_id'].type,
                        'title': rec._fields['categ_id'].string,
                        'value': rec.categ_id.name if rec.categ_id else ''}
            installation_date = {'key': 'installation_date', 'type': rec._fields['installation_date'].type,
                                 'title': rec._fields['installation_date'].string,
                                 'value': str(rec.installation_date) if rec.installation_date else ''}
            oem_warranty_status_id = {'key': 'oem_warranty_status_id',
                                      'type': rec._fields['oem_warranty_status_id'].type,
                                      'title': rec._fields['oem_warranty_status_id'].string,
                                      'value': rec.oem_warranty_status_id.name if rec.oem_warranty_status_id else ''}
            repair_warranty_status_id = {'key': 'repair_warranty_status_id',
                                         'type': rec._fields['repair_warranty_status_id'].type,
                                         'title': rec._fields['repair_warranty_status_id'].string,
                                         'value': rec.repair_warranty_status_id.name if rec.repair_warranty_status_id else ''}
            cmc_status = {'key': 'cmc_status', 'type': rec._fields['cmc_status'].type,
                          'title': rec._fields['cmc_status'].string,
                          'value': rec.cmc_status if rec.cmc_status else ''}
            amc_status = {'key': 'amc_status', 'type': rec._fields['amc_status'].type,
                          'title': rec._fields['amc_status'].string,
                          'value': rec.amc_status if rec.amc_status else ''}
            # OTHER INFORMATION
            external_work_order_date = {'key': 'external_work_order_date', 'type': rec._fields['external_work_order_date'].type,
                                 'title': rec._fields['external_work_order_date'].string,
                                 'value': str(rec.external_work_order_date) if rec.external_work_order_date else ''}
            repair_center_location_id = {'key': 'repair_center_location_id',
                                         'type': rec._fields['repair_center_location_id'].type,
                                         'title': rec._fields['repair_center_location_id'].string,
                                         'value': rec.repair_center_location_id.name if rec.repair_center_location_id else ''}
            price_available_in_contract = {'key': 'price_available_in_contract', 'type': rec._fields['price_available_in_contract'].type, 'title': rec._fields['price_available_in_contract'].string,
                    'value': dict(rec._fields['price_available_in_contract'].selection).get(rec.price_available_in_contract) if rec.price_available_in_contract else ''}
            oem_warranty_status = {'key': 'oem_warranty_status', 'type': rec._fields['oem_warranty_status'].type,
                                   'title': rec._fields['oem_warranty_status'].string,
                                   'value': dict(rec._fields['oem_warranty_status'].selection).get(
                                       rec.oem_warranty_status) if rec.oem_warranty_status else ''}
            oem_repair_status = {'key': 'oem_repair_status', 'type': rec._fields['oem_repair_status'].type,
                                 'title': rec._fields['oem_repair_status'].string,
                                 'value': dict(rec._fields['oem_repair_status'].selection).get(
                                     rec.oem_repair_status) if rec.oem_repair_status else ''}
            company_id = {'key': 'company_id', 'type': rec._fields['company_id'].type,
                          'title': rec._fields['company_id'].string,
                          'value': rec.company_id.name if rec.company_id else ''}
            survey_id = {'key': 'survey_id', 'type': rec._fields['survey_id'].type,
                         'title': rec._fields['survey_id'].string,
                         'value': rec.survey_id.title if rec.survey_id else ''}
            inventory_reference = {'key': 'inventory_reference',
                                         'type': rec._fields['inventory_reference'].type,
                                         'title': rec._fields['inventory_reference'].string,
                                        'value': rec.inventory_reference if rec.inventory_reference else ''}
            remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type, 'title': rec._fields['remarks'].string,
                       'value': rec.remarks if rec.remarks else ''}
            packaging = {'key': 'packaging', 'type': rec._fields['packaging'].type, 'title': rec._fields['packaging'].string,
                       'value': rec.packaging if rec.packaging else ''}
            packaging_alias = {'key': 'packaging_alias', 'type': rec._fields['packaging_alias'].type, 'title': rec._fields['packaging_alias'].string,
                       'value': rec.packaging_alias if rec.packaging_alias else ''}
            service_request_id = {'key': 'service_request_id', 'type': rec._fields['service_request_id'].type,
                                  'title': rec._fields['service_request_id'].string,
                                  'value': rec.service_request_id.name if rec.service_request_id else ''}
            cat_no = {'key': 'cat_no', 'type': rec._fields['cat_no'].type, 'title': rec._fields['cat_no'].string,
                       'value': rec.cat_no if rec.cat_no else ''}
            franchise_id = {'key': 'franchise_id', 'type': rec._fields['franchise_id'].type, 'title': rec._fields['franchise_id'].string,
                       'value': rec.franchise_id.name if rec.franchise_id else ''}
            re_repair = {'key': 're_repair', 'type': rec._fields['re_repair'].type,
                                 'title': rec._fields['re_repair'].string,
                                 'value': dict(rec._fields['re_repair'].selection).get(
                                     rec.re_repair) if rec.re_repair else ''}
            faulty_section = {'key': 'faulty_section', 'type': rec._fields['faulty_section'].type,
                              'title': rec._fields['faulty_section'].string,
                              'value': rec.faulty_section if rec.faulty_section else ''}
            sow = {'key': 'sow', 'type': rec._fields['sow'].type, 'title': rec._fields['sow'].string,
                   'value': rec.sow if rec.sow else ''}
            webdelata_id = {'key': 'webdelata_id', 'type': rec._fields['webdelata_id'].type,
                            'title': rec._fields['webdelata_id'].string,
                            'value': rec.webdelata_id if rec.webdelata_id else ''}
            webdelata = {'key': 'webdelata', 'type': rec._fields['webdelata'].type,
                         'title': rec._fields['webdelata'].string,
                         'value': rec.webdelata if rec.webdelata else ''}
            mc_stk = {'key': 'mc_stk', 'type': rec._fields['mc_stk'].type, 'title': rec._fields['mc_stk'].string,
                      'value': dict(rec._fields['mc_stk'].selection).get(rec.mc_stk) if rec.mc_stk else ''}
            # CUSTOMER DETAILS
            partner_id = {'key': 'partner_id', 'type': rec._fields['partner_id'].type,
                          'title': rec._fields['partner_id'].string,
                          'value': rec.partner_id.name if rec.partner_id else '', 'id':rec.partner_id.id if rec.partner_id else ''}
            customer_account_id = {'key': 'customer_account_id', 'type': rec._fields['customer_account_id'].type,
                                   'title': rec._fields['customer_account_id'].string,
                                   'value': rec.customer_account_id.name if rec.customer_account_id else ''}
            alternate_contact_name = {'key': 'alternate_contact_name',
                                      'type': rec._fields['alternate_contact_name'].type,
                                      'title': rec._fields['alternate_contact_name'].string,
                                      'value': rec.alternate_contact_name if rec.alternate_contact_name else ''}
            alternate_contact_number = {'key': 'alternate_contact_number',
                                        'type': rec._fields['alternate_contact_number'].type,
                                        'title': rec._fields['alternate_contact_number'].string,
                                        'value': rec.alternate_contact_number if rec.alternate_contact_number else ''}
            dealer_distributor_id = {'key': 'dealer_distributor_id', 'type': rec._fields['dealer_distributor_id'].type,
                                     'title': rec._fields['dealer_distributor_id'].string,
                                     'value': rec.dealer_distributor_id.name if rec.dealer_distributor_id else ''}
            child_ticket_obj = request.env['child.ticket'].sudo().search([('child_assign_engineer_ids','in',user.id),('is_pi_true','=',True),('parent_ticket_id', '=', rec.id)])
            child_ticket_ids = {'key': 'child_ticket_ids', 'type': rec._fields['child_ticket_ids'].type,
                                     'title': rec._fields['child_ticket_ids'].string,
                                     'value': ', '.join(child_ticket_obj.mapped(
                                         'name')) if child_ticket_obj else 'NO CHILD TICKET',
                                     'ids': child_ticket_obj.mapped(
                                         'id') if child_ticket_obj else False
                                     }

            parent_ticket_list.append([id,name,state,parent_ticket_id_alias,call_source_id,call_date,service_category_id,
                service_type_id,parent_configuration_id,request_type_id,requested_by_name,requested_by_contact_number,
                call_received_id,team_id,problem_description,stock_lot_id,product_id,product_code_no,categ_id,
                installation_date,oem_warranty_status_id,repair_warranty_status_id,cmc_status,amc_status,external_work_order_date,
                repair_center_location_id,price_available_in_contract,oem_warranty_status,oem_repair_status,company_id,survey_id,
                inventory_reference,remarks,packaging,packaging_alias,service_request_id,cat_no,franchise_id,re_repair,faulty_section,
                sow,webdelata_id,webdelata,mc_stk,partner_id,customer_account_id,alternate_contact_name,alternate_contact_number,
                dealer_distributor_id,child_ticket_ids
                                       ])

        if parent_ticket_list:
            return valid_response2(parent_ticket_list,filter_state,count, 'parent ticket load successfully', 200)
        else:
            return valid_response2(parent_ticket_list,filter_state,count, 'there is no parent ticket', 200)


        # parent_ticket = parent_ticket_obj.sudo().search_read([],['name', 'parent_ticket_id_alias', 'call_source_id', 'service_category_id',
        #                                                     'service_request_id', 'parent_configuration_id', 'request_type_id',
        #                                                     'requested_by_name', 'requested_by_contact_number',
        #                                                     'call_received_id', 'team_id', 'problem_description',
        #                                                     'stock_lot_id', 'product_id', 'product_code_no',
        #                                                     'categ_id', 'repair_center_location_id',
        #                                                     'oem_warranty_status', 'oem_repair_status', 'company_id',
        #                                                      'inventory_reference', 'remarks',
        #                                                     'partner_id', 'customer_account_id', 'alternate_contact_name', 'alternate_contact_number',
        #                                                     'dealer_distributor_id', 'oem_warranty_status_id','repair_warranty_status_id','cmc_status','amc_status',
        #                                                          'packaging','packaging_alias','service_request_id','cat_no','franchise_id','re_repair','faulty_section',
        #                                                          'sow','webdelata_id','webdelata','mc_stk'])
        #
        # parent_ticket_obj = request.env['parent.ticket']
        # ['installation_date', 'call_date', 'external_work_order_date']
        # production_missing_fields = ['survey_id']
        # for rec in parent_ticket:
        #     parent=parent_ticket_obj.sudo().browse(rec.get('id'))
        #     rec['installation_date']=str(parent.installation_date)
        #     rec['call_date'] = str(parent.call_date)
        #     rec['external_work_order_date'] =str(parent.external_work_order_date)

    @validate_token
    @http.route("/api/ticket/status_update", type="json", auth="none", methods=["POST"], csrf=False)
    def api_parent_ticket_status_update(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('/api/ticket/status_update value post: %s' % post)
        parent_ticket_id = post.get('parent_id')
        child_ticket_id = post.get('child_id')
        task_master_line_obj = request.env['tasks.master.line']
        task_list = []
        if parent_ticket_id:
            parent_ticket = request.env['parent.ticket'].sudo().browse(int(parent_ticket_id))
            task_id = {'key': 'task_id', 'type': task_master_line_obj._fields['task_id'].type,
                               'title': task_master_line_obj._fields['task_id'].string,
                               'required': task_master_line_obj._fields['task_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in parent_ticket.next_task_ids]}
            task_list.append(task_id)
            # description = {'key':'description','type':task_master_line_obj._fields['description'].type,'title':task_master_line_obj._fields['description'].string,'required':task_master_line_obj._fields['description'].required}
            # status = {'key':'status','type':task_master_line_obj._fields['status'].type,'title':task_master_line_obj._fields['status'].string,'required':task_master_line_obj._fields['status'].required}
            if parent_ticket.next_task_ids:
                # Geo Location
                # is_geo_location = parent_ticket.next_task_ids.filtered(lambda x: x.is_geo_location == True).mapped('id')
                # if is_geo_location:
                #     add_latitude = {'key':'add_latitude','type':task_master_line_obj._fields['add_latitude'].type,'title':task_master_line_obj._fields['add_latitude'].string,
                #                     'required':task_master_line_obj._fields['add_latitude'].required,
                #                      'visible_task_ids' : is_geo_location}
                #     add_longitude = {'key':'add_longitude','type':task_master_line_obj._fields['add_longitude'].type,
                #                      'title':task_master_line_obj._fields['add_longitude'].string,
                #                      'required':task_master_line_obj._fields['add_longitude'].required,
                #                     'visible_task_ids' : is_geo_location}
                # PI required
                complaint_type_values = dict(task_master_line_obj._fields['complaint_type'].selection)
                # print(dict(var))
                # for rec in dict(var):
                #     print(rec)
                #     print(dict(var).get(rec))
                # print(list(dict(var).keys()))
                is_pi_required = parent_ticket.next_task_ids.filtered(lambda x: x.is_pi_required == True).mapped('id')
                # pi_required=[]
                # for rec in is_pi_required:
                #     pi_required.append(str(rec))
                # pi_required_num = ','.join(pi_required)
                if is_pi_required:

                    complaint_type = {'key':'complaint_type','type':task_master_line_obj._fields['complaint_type'].type,
                                     'title':task_master_line_obj._fields['complaint_type'].string,
                                     'required':task_master_line_obj._fields['complaint_type'].required,
                                        'value': [{'id': field, 'value': complaint_type_values.get(field), } for field in complaint_type_values],
                    'visible_task_ids' : is_pi_required}
                    task_list.append(complaint_type)
                    phone = {'key':'phone','type':task_master_line_obj._fields['phone'].type,'title':task_master_line_obj._fields['phone'].string,'required':task_master_line_obj._fields['phone'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(phone)
                    name_of_reporter = {'key':'name_of_reporter','type':task_master_line_obj._fields['name_of_reporter'].type,'title':task_master_line_obj._fields['name_of_reporter'].string,'required':task_master_line_obj._fields['name_of_reporter'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(name_of_reporter)
                    email = {'key':'email','type':task_master_line_obj._fields['email'].type,'title':task_master_line_obj._fields['email'].string,'required':task_master_line_obj._fields['email'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(email)
                    title = {'key':'title','type':task_master_line_obj._fields['title'].type,'title':task_master_line_obj._fields['title'].string,'required':task_master_line_obj._fields['title'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(title)
                    date_of_reporting = {'key':'date_of_reporting','type':task_master_line_obj._fields['date_of_reporting'].type,'title':task_master_line_obj._fields['date_of_reporting'].string,'required':task_master_line_obj._fields['date_of_reporting'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(date_of_reporting)
                    awareness_date = {'key':'awareness_date','type':task_master_line_obj._fields['awareness_date'].type,'title':task_master_line_obj._fields['awareness_date'].string,'required':task_master_line_obj._fields['awareness_date'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(awareness_date)
                    reason_for_delay = {'key':'reason_for_delay','type':task_master_line_obj._fields['reason_for_delay'].type,'title':task_master_line_obj._fields['reason_for_delay'].string,'required':task_master_line_obj._fields['reason_for_delay'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(reason_for_delay)
                    date_of_event = {'key':'date_of_event','type':task_master_line_obj._fields['date_of_event'].type,'title':task_master_line_obj._fields['date_of_event'].string,'required':task_master_line_obj._fields['date_of_event'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(date_of_event)
                    event_description = {'key':'event_description','type':task_master_line_obj._fields['event_description'].type,'title':task_master_line_obj._fields['event_description'].string,'required':task_master_line_obj._fields['event_description'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(event_description)
                    issue_noticed_comment = {'key':'issue_noticed_comment','type':task_master_line_obj._fields['issue_noticed_comment'].type,'title':task_master_line_obj._fields['issue_noticed_comment'].string,'required':task_master_line_obj._fields['issue_noticed_comment'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(issue_noticed_comment)
                    select_case_completed_value = dict(task_master_line_obj._fields['select_case_completed'].selection)
                    select_case_completed = {'key':'select_case_completed','type':task_master_line_obj._fields['select_case_completed'].type,
                                     'title':task_master_line_obj._fields['select_case_completed'].string,
                                     'required':task_master_line_obj._fields['select_case_completed'].required,
                                        'value': [{'id': field, 'value': select_case_completed_value.get(field), } for field in select_case_completed_value],
                    'visible_task_ids' : is_pi_required}
                    task_list.append(select_case_completed)
                    select_medical_intervention_needed_value = dict(task_master_line_obj._fields['select_medical_intervention_needed'].selection)
                    select_medical_intervention_needed = {'key': 'select_medical_intervention_needed',
                                             'type': task_master_line_obj._fields['select_medical_intervention_needed'].type,
                                             'title': task_master_line_obj._fields['select_medical_intervention_needed'].string,
                                             'required': task_master_line_obj._fields['select_medical_intervention_needed'].required,
                                             'value': [{'id': field, 'value': select_medical_intervention_needed_value.get(field), } for
                                                       field in select_medical_intervention_needed_value],
                                             'visible_task_ids': is_pi_required}
                    task_list.append(select_medical_intervention_needed)
                    select_patient_involved_value = dict(task_master_line_obj._fields['select_patient_involved'].selection)
                    select_patient_involved = {'key': 'select_patient_involved',
                                               'type': task_master_line_obj._fields['select_patient_involved'].type,
                                               'title': task_master_line_obj._fields[
                                                   'select_patient_involved'].string,
                                               'required': task_master_line_obj._fields[
                                                   'select_patient_involved'].required,
                                               'value': [
                                                   {'id': field, 'value': select_patient_involved_value.get(field), }
                                                   for
                                                   field in select_patient_involved_value],
                                               'visible_task_ids': is_pi_required}
                    task_list.append(select_patient_involved)
                    select_surgical_delay_value = dict(task_master_line_obj._fields['select_surgical_delay'].selection)
                    select_surgical_delay = {'key': 'select_surgical_delay',
                                             'type': task_master_line_obj._fields['select_surgical_delay'].type,
                                             'title': task_master_line_obj._fields['select_surgical_delay'].string,
                                             'required': task_master_line_obj._fields['select_surgical_delay'].required,
                                             'value': [{'id': field, 'value': select_surgical_delay_value.get(field), } for
                                                       field in select_surgical_delay_value],
                                             'visible_task_ids': is_pi_required}
                    task_list.append(select_surgical_delay)
                    select_adverse_consequences_value = dict(task_master_line_obj._fields['select_adverse_consequences'].selection)
                    select_adverse_consequences = {'key': 'select_adverse_consequences',
                                             'type': task_master_line_obj._fields['select_adverse_consequences'].type,
                                             'title': task_master_line_obj._fields['select_adverse_consequences'].string,
                                             'required': task_master_line_obj._fields['select_adverse_consequences'].required,
                                             'value': [{'id': field, 'value': select_adverse_consequences_value.get(field), } for
                                                       field in select_adverse_consequences_value],
                                             'visible_task_ids': is_pi_required}
                    task_list.append(select_adverse_consequences)
                    length_of_delay = {'key':'length_of_delay','type':task_master_line_obj._fields['length_of_delay'].type,'title':task_master_line_obj._fields['length_of_delay'].string,'required':task_master_line_obj._fields['length_of_delay'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(length_of_delay)
                    initial_reporter_facility = {'key':'initial_reporter_facility','type':task_master_line_obj._fields['initial_reporter_facility'].type,'title':task_master_line_obj._fields['initial_reporter_facility'].string,'required':task_master_line_obj._fields['initial_reporter_facility'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(initial_reporter_facility)
                    ac_addr_number_street = {'key':'ac_addr_number_street','type':task_master_line_obj._fields['ac_addr_number_street'].type,'title':task_master_line_obj._fields['ac_addr_number_street'].string,'required':task_master_line_obj._fields['ac_addr_number_street'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(ac_addr_number_street)
                    ac_addr_city = {'key':'ac_addr_city','type':task_master_line_obj._fields['ac_addr_city'].type,'title':task_master_line_obj._fields['ac_addr_city'].string,'required':task_master_line_obj._fields['ac_addr_city'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(ac_addr_city)
                    contact_ac_marketing_name = {'key':'contact_ac_marketing_name','type':task_master_line_obj._fields['contact_ac_marketing_name'].type,'title':task_master_line_obj._fields['contact_ac_marketing_name'].string,'required':task_master_line_obj._fields['contact_ac_marketing_name'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(contact_ac_marketing_name)
                    contact_ac_marketing_title = {'key':'contact_ac_marketing_title','type':task_master_line_obj._fields['contact_ac_marketing_title'].type,'title':task_master_line_obj._fields['contact_ac_marketing_title'].string,'required':task_master_line_obj._fields['contact_ac_marketing_title'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(contact_ac_marketing_title)
                    contact_ac_marketing_phone = {'key':'contact_ac_marketing_phone','type':task_master_line_obj._fields['contact_ac_marketing_phone'].type,'title':task_master_line_obj._fields['contact_ac_marketing_phone'].string,'required':task_master_line_obj._fields['contact_ac_marketing_phone'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(contact_ac_marketing_phone)
                    contact_ac_marketing_email = {'key':'contact_ac_marketing_email','type':task_master_line_obj._fields['contact_ac_marketing_email'].type,'title':task_master_line_obj._fields['contact_ac_marketing_email'].string,'required':task_master_line_obj._fields['contact_ac_marketing_email'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(contact_ac_marketing_email)
                    sales_service_rep_name = {'key':'sales_service_rep_name','type':task_master_line_obj._fields['sales_service_rep_name'].type,'title':task_master_line_obj._fields['sales_service_rep_name'].string,'required':task_master_line_obj._fields['sales_service_rep_name'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(sales_service_rep_name)
                    product_no = {'key':'product_no','type':task_master_line_obj._fields['product_no'].type,'title':task_master_line_obj._fields['product_no'].string,'required':task_master_line_obj._fields['product_no'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(product_no)
                    product_description = {'key':'product_description','type':task_master_line_obj._fields['product_description'].type,'title':task_master_line_obj._fields['product_description'].string,'required':task_master_line_obj._fields['product_description'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(product_description)
                    asset_serial_no = {'key':'asset_serial_no','type':task_master_line_obj._fields['asset_serial_no'].type,'title':task_master_line_obj._fields['asset_serial_no'].string,'required':task_master_line_obj._fields['asset_serial_no'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(asset_serial_no)
                    select_product_avail_stryker_value = dict(task_master_line_obj._fields['select_product_avail_stryker'].selection)
                    select_product_avail_stryker = {'key': 'select_product_avail_stryker',
                                                    'type': task_master_line_obj._fields[
                                                        'select_product_avail_stryker'].type,
                                                    'title': task_master_line_obj._fields[
                                                        'select_product_avail_stryker'].string,
                                                    'required': task_master_line_obj._fields[
                                                        'select_product_avail_stryker'].required,
                                                    'value': [
                                                        {'id': field,
                                                         'value': select_product_avail_stryker_value.get(field), }
                                                        for
                                                        field in select_product_avail_stryker_value],
                                                    'visible_task_ids': is_pi_required}
                    task_list.append(select_product_avail_stryker)
                    no_avail_reason = {'key':'no_avail_reason','type':task_master_line_obj._fields['no_avail_reason'].type,'title':task_master_line_obj._fields['no_avail_reason'].string,'required':task_master_line_obj._fields['no_avail_reason'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(no_avail_reason)
                    product_ref_no = {'key':'product_ref_no','type':task_master_line_obj._fields['product_ref_no'].type,'title':task_master_line_obj._fields['product_ref_no'].string,'required':task_master_line_obj._fields['product_ref_no'].required,'visible_task_ids' : is_pi_required}
                    task_list.append(product_ref_no)
                # Call Customer
                is_schedule = parent_ticket.next_task_ids.filtered(lambda x: x.is_schedule == True).mapped('id')
                # schedule = []
                # for rec in is_schedule:
                #     schedule.append(str(rec))
                # schedule_num = ','.join(pi_required)
                if is_schedule:
                    meeting_subject = {'key':'meeting_subject','type':task_master_line_obj._fields['meeting_subject'].type,'title':task_master_line_obj._fields['meeting_subject'].string,'required':task_master_line_obj._fields['meeting_subject'].required,'visible_task_ids' : is_schedule}
                    task_list.append(meeting_subject)
                    meeting_start_date = {'key':'meeting_start_date','type':task_master_line_obj._fields['meeting_start_date'].type,'title':task_master_line_obj._fields['meeting_start_date'].string,'required':task_master_line_obj._fields['meeting_start_date'].required,'visible_task_ids' : is_schedule}
                    task_list.append(meeting_start_date)
                    meeting_end_date = {'key':'meeting_end_date','type':task_master_line_obj._fields['meeting_end_date'].type,'title':task_master_line_obj._fields['meeting_end_date'].string,'required':task_master_line_obj._fields['meeting_end_date'].required,'visible_task_ids' : is_schedule}
                    task_list.append(meeting_end_date)
                # Attachments
                # File/Camera Attachment
                is_file_attachment = parent_ticket.next_task_ids.filtered(lambda x: x.is_file_attachment == True).mapped('id')
                # file_attachment = []
                # for rec in is_file_attachment:
                #     file_attachment.append(str(rec))
                # file_attachment_num = ','.join(pi_required)
                if is_file_attachment:
                    attachment_ids = {'key':'attachment_ids','type':task_master_line_obj._fields['attachment_ids'].type,'title':task_master_line_obj._fields['attachment_ids'].string,'required':task_master_line_obj._fields['attachment_ids'].required,'visible_task_ids' :is_file_attachment}
                    task_list.append(attachment_ids)
                is_end_task = parent_ticket.next_task_ids.filtered(lambda x: x.is_end_task == True).mapped('id')
                if is_end_task:
                    recommendation_customer = {'key':'recommendation_customer','type':task_master_line_obj._fields['recommendation_customer'].type,
                                    'title':task_master_line_obj._fields['recommendation_customer'].string,
                                    'required':task_master_line_obj._fields['recommendation_customer'].required,
                                    'visible_task_ids' : is_end_task}
                    task_list.append(recommendation_customer)

                    customer_remarks = {'key':'customer_remarks','type':task_master_line_obj._fields['customer_remarks'].type,
                                    'title':task_master_line_obj._fields['customer_remarks'].string,
                                    'required':task_master_line_obj._fields['customer_remarks'].required,
                                    'visible_task_ids' : is_end_task}
                    task_list.append(customer_remarks)
                    feed_back_end_task_1_value = dict(
                        task_master_line_obj._fields['feed_back_end_task_1'].selection)
                    feed_back_end_task_1 = {'key': 'feed_back_end_task_1',
                                                   'type': task_master_line_obj._fields[
                                                       'feed_back_end_task_1'].type,
                                                   'title': task_master_line_obj._fields[
                                                       'feed_back_end_task_1'].string,
                                                   'required': task_master_line_obj._fields[
                                                       'feed_back_end_task_1'].required,
                                                   'value': [{'id': field,
                                                              'value': feed_back_end_task_1_value.get(field), }
                                                             for
                                                             field in feed_back_end_task_1_value],
                                                   'visible_task_ids': is_end_task}
                    task_list.append(feed_back_end_task_1)
                    feed_back_end_task_2_value = dict(
                        task_master_line_obj._fields['feed_back_end_task_2'].selection)
                    feed_back_end_task_2 = {'key': 'feed_back_end_task_2',
                                            'type': task_master_line_obj._fields[
                                                'feed_back_end_task_2'].type,
                                            'title': task_master_line_obj._fields[
                                                'feed_back_end_task_2'].string,
                                            'required': task_master_line_obj._fields[
                                                'feed_back_end_task_2'].required,
                                            'value': [{'id': field,
                                                       'value': feed_back_end_task_2_value.get(field), }
                                                      for
                                                      field in feed_back_end_task_2_value],
                                            'visible_task_ids': is_end_task}
                    task_list.append(feed_back_end_task_2)
                    feed_back_end_task_3_value = dict(
                        task_master_line_obj._fields['feed_back_end_task_3'].selection)
                    feed_back_end_task_3 = {'key': 'feed_back_end_task_3',
                                            'type': task_master_line_obj._fields[
                                                'feed_back_end_task_3'].type,
                                            'title': task_master_line_obj._fields[
                                                'feed_back_end_task_3'].string,
                                            'required': task_master_line_obj._fields[
                                                'feed_back_end_task_3'].required,
                                            'value': [{'id': field,
                                                       'value': feed_back_end_task_3_value.get(field), }
                                                      for
                                                      field in feed_back_end_task_3_value],
                                            'visible_task_ids': is_end_task}
                    task_list.append(feed_back_end_task_3)
                    feed_back_end_task_4_value = dict(
                        task_master_line_obj._fields['feed_back_end_task_4'].selection)
                    feed_back_end_task_4 = {'key': 'feed_back_end_task_4',
                                            'type': task_master_line_obj._fields[
                                                'feed_back_end_task_4'].type,
                                            'title': task_master_line_obj._fields[
                                                'feed_back_end_task_4'].string,
                                            'required': task_master_line_obj._fields[
                                                'feed_back_end_task_4'].required,
                                            'value': [{'id': field,
                                                       'value': feed_back_end_task_4_value.get(field), }
                                                      for
                                                      field in feed_back_end_task_4_value],
                                            'visible_task_ids': is_end_task}
                    task_list.append(feed_back_end_task_4)
                    feed_back_end_task_5_value = dict(
                        task_master_line_obj._fields['feed_back_end_task_5'].selection)
                    feed_back_end_task_5 = {'key': 'feed_back_end_task_5',
                                            'type': task_master_line_obj._fields[
                                                'feed_back_end_task_5'].type,
                                            'title': task_master_line_obj._fields[
                                                'feed_back_end_task_5'].string,
                                            'required': task_master_line_obj._fields[
                                                'feed_back_end_task_5'].required,
                                            'value': [{'id': field,
                                                       'value': feed_back_end_task_5_value.get(field), }
                                                      for
                                                      field in feed_back_end_task_5_value],
                                            'visible_task_ids': is_end_task}
                    task_list.append(feed_back_end_task_5)
                    signature = {'key':'signature','type':task_master_line_obj._fields['signature'].type,
                                    'title':task_master_line_obj._fields['signature'].string,
                                    'required':task_master_line_obj._fields['signature'].required,
                                    'visible_task_ids' : is_end_task}
                    task_list.append(signature)

        if child_ticket_id:
            child_ticket = request.env['child.ticket'].sudo().browse(int(child_ticket_id))
            task_id = {'key': 'task_id', 'type': task_master_line_obj._fields['task_id'].type,
                       'title': task_master_line_obj._fields['task_id'].string,
                       'required': task_master_line_obj._fields['task_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in child_ticket.next_task_ids]}
            task_list.append(task_id)
            # description = {'key':'description','type':task_master_line_obj._fields['description'].type,'title':task_master_line_obj._fields['description'].string,'required':task_master_line_obj._fields['description'].required}
            # status = {'key': 'status', 'type': task_master_line_obj._fields['status'].type,
            #           'title': task_master_line_obj._fields['status'].string,
            #           'required': task_master_line_obj._fields['status'].required}
            # add_latitude = {'key': 'add_latitude', 'type': task_master_line_obj._fields['add_latitude'].type,
            #          'title': task_master_line_obj._fields['add_latitude'].string,
            #          'required': task_master_line_obj._fields['add_latitude'].required,
            #          'visible_task_ids': child_ticket.next_task_ids.filtered(
            #              lambda x: x.is_geo_location == True).mapped('id') if child_ticket.next_task_ids else ''}
            # add_longitude = {'key': 'add_longitude', 'type': task_master_line_obj._fields['add_longitude'].type,
            #          'title': task_master_line_obj._fields['add_longitude'].string,
            #          'required': task_master_line_obj._fields['add_longitude'].required,
            #          'visible_task_ids': child_ticket.next_task_ids.filtered(
            #              lambda x: x.is_geo_location == True).mapped('id') if child_ticket.next_task_ids else ''}
            # PI required
            complaint_type_values = dict(task_master_line_obj._fields['complaint_type'].selection)
            is_pi_required = child_ticket.next_task_ids.filtered(lambda x: x.is_pi_required == True).mapped('id')
            if is_pi_required:
                complaint_type = {'key': 'complaint_type', 'type': task_master_line_obj._fields['complaint_type'].type,
                                  'title': task_master_line_obj._fields['complaint_type'].string,
                                  'required': task_master_line_obj._fields['complaint_type'].required,
                                  'value': [{'id': field, 'value': complaint_type_values.get(field), } for field in
                                            complaint_type_values],
                                  'visible_task_ids': is_pi_required}
                task_list.append(complaint_type)
                phone = {'key': 'phone', 'type': task_master_line_obj._fields['phone'].type,
                         'title': task_master_line_obj._fields['phone'].string,
                         'required': task_master_line_obj._fields['phone'].required,
                         'visible_task_ids': is_pi_required}
                task_list.append(phone)
                name_of_reporter = {'key': 'name_of_reporter',
                                    'type': task_master_line_obj._fields['name_of_reporter'].type,
                                    'title': task_master_line_obj._fields['name_of_reporter'].string,
                                    'required': task_master_line_obj._fields['name_of_reporter'].required,
                                    'visible_task_ids': is_pi_required}
                task_list.append(name_of_reporter)
                email = {'key': 'email', 'type': task_master_line_obj._fields['email'].type,
                         'title': task_master_line_obj._fields['email'].string,
                         'required': task_master_line_obj._fields['email'].required,
                         'visible_task_ids': is_pi_required}
                task_list.append(email)
                title = {'key': 'title', 'type': task_master_line_obj._fields['title'].type,
                         'title': task_master_line_obj._fields['title'].string,
                         'required': task_master_line_obj._fields['title'].required,
                         'visible_task_ids': is_pi_required}
                task_list.append(title)
                date_of_reporting = {'key': 'date_of_reporting',
                                     'type': task_master_line_obj._fields['date_of_reporting'].type,
                                     'title': task_master_line_obj._fields['date_of_reporting'].string,
                                     'required': task_master_line_obj._fields['date_of_reporting'].required,
                                     'visible_task_ids': is_pi_required}
                task_list.append(date_of_reporting)
                awareness_date = {'key': 'awareness_date', 'type': task_master_line_obj._fields['awareness_date'].type,
                                  'title': task_master_line_obj._fields['awareness_date'].string,
                                  'required': task_master_line_obj._fields['awareness_date'].required,
                                  'visible_task_ids': is_pi_required}
                task_list.append(awareness_date)
                reason_for_delay = {'key': 'reason_for_delay',
                                    'type': task_master_line_obj._fields['reason_for_delay'].type,
                                    'title': task_master_line_obj._fields['reason_for_delay'].string,
                                    'required': task_master_line_obj._fields['reason_for_delay'].required,
                                    'visible_task_ids': is_pi_required}
                task_list.append(reason_for_delay)
                date_of_event = {'key': 'date_of_event', 'type': task_master_line_obj._fields['date_of_event'].type,
                                 'title': task_master_line_obj._fields['date_of_event'].string,
                                 'required': task_master_line_obj._fields['date_of_event'].required,
                                 'visible_task_ids': is_pi_required}
                task_list.append(date_of_event)
                event_description = {'key': 'event_description',
                                     'type': task_master_line_obj._fields['event_description'].type,
                                     'title': task_master_line_obj._fields['event_description'].string,
                                     'required': task_master_line_obj._fields['event_description'].required,
                                     'visible_task_ids': is_pi_required}
                task_list.append(event_description)
                issue_noticed_comment = {'key': 'issue_noticed_comment',
                                         'type': task_master_line_obj._fields['issue_noticed_comment'].type,
                                         'title': task_master_line_obj._fields['issue_noticed_comment'].string,
                                         'required': task_master_line_obj._fields['issue_noticed_comment'].required,
                                         'visible_task_ids': is_pi_required}
                task_list.append(issue_noticed_comment)
                select_case_completed_value = dict(task_master_line_obj._fields['select_case_completed'].selection)
                select_case_completed = {'key': 'select_case_completed',
                                         'type': task_master_line_obj._fields['select_case_completed'].type,
                                         'title': task_master_line_obj._fields['select_case_completed'].string,
                                         'required': task_master_line_obj._fields['select_case_completed'].required,
                                         'value': [{'id': field, 'value': select_case_completed_value.get(field), } for
                                                   field in select_case_completed_value],
                                         'visible_task_ids': is_pi_required}
                task_list.append(select_case_completed)
                select_medical_intervention_needed_value = dict(
                        task_master_line_obj._fields['select_medical_intervention_needed'].selection)
                select_medical_intervention_needed = {'key': 'select_medical_intervention_needed',
                                                      'type': task_master_line_obj._fields[
                                                          'select_medical_intervention_needed'].type,
                                                      'title': task_master_line_obj._fields[
                                                          'select_medical_intervention_needed'].string,
                                                      'required': task_master_line_obj._fields[
                                                          'select_medical_intervention_needed'].required,
                                                      'value': [{'id': field,
                                                                 'value': select_medical_intervention_needed_value.get(
                                                                     field), } for
                                                                field in select_medical_intervention_needed_value],
                                                      'visible_task_ids': is_pi_required}
                task_list.append(select_medical_intervention_needed)
                select_patient_involved_value = dict(task_master_line_obj._fields['select_patient_involved'].selection)
                select_patient_involved = {'key': 'select_patient_involved',
                                           'type': task_master_line_obj._fields['select_patient_involved'].type,
                                           'title': task_master_line_obj._fields[
                                               'select_patient_involved'].string,
                                           'required': task_master_line_obj._fields[
                                               'select_patient_involved'].required,
                                           'value': [{'id': field, 'value': select_patient_involved_value.get(field), } for
                                                     field in select_patient_involved_value],
                                           'visible_task_ids': is_pi_required}
                task_list.append(select_patient_involved)
                select_surgical_delay_value = dict(task_master_line_obj._fields['select_surgical_delay'].selection)
                select_surgical_delay = {'key': 'select_surgical_delay',
                                         'type': task_master_line_obj._fields['select_surgical_delay'].type,
                                         'title': task_master_line_obj._fields['select_surgical_delay'].string,
                                         'required': task_master_line_obj._fields['select_surgical_delay'].required,
                                         'value': [{'id': field, 'value': select_surgical_delay_value.get(field), } for
                                                   field in select_surgical_delay_value],
                                         'visible_task_ids': is_pi_required}
                task_list.append(select_surgical_delay)
                select_adverse_consequences_value = dict(
                    task_master_line_obj._fields['select_adverse_consequences'].selection)
                select_adverse_consequences = {'key': 'select_adverse_consequences',
                                               'type': task_master_line_obj._fields['select_adverse_consequences'].type,
                                               'title': task_master_line_obj._fields['select_adverse_consequences'].string,
                                               'required': task_master_line_obj._fields[
                                                   'select_adverse_consequences'].required,
                                               'value': [
                                                   {'id': field, 'value': select_adverse_consequences_value.get(field), }
                                                   for
                                                   field in select_adverse_consequences_value],
                                               'visible_task_ids': is_pi_required}
                task_list.append(select_adverse_consequences)
                length_of_delay = {'key': 'length_of_delay', 'type': task_master_line_obj._fields['length_of_delay'].type,
                                   'title': task_master_line_obj._fields['length_of_delay'].string,
                                   'required': task_master_line_obj._fields['length_of_delay'].required,
                                   'visible_task_ids': is_pi_required}
                task_list.append(length_of_delay)
                initial_reporter_facility = {'key': 'initial_reporter_facility',
                                             'type': task_master_line_obj._fields['initial_reporter_facility'].type,
                                             'title': task_master_line_obj._fields['initial_reporter_facility'].string,
                                             'required': task_master_line_obj._fields['initial_reporter_facility'].required,
                                             'visible_task_ids': is_pi_required}
                task_list.append(initial_reporter_facility)
                ac_addr_number_street = {'key': 'ac_addr_number_street',
                                         'type': task_master_line_obj._fields['ac_addr_number_street'].type,
                                         'title': task_master_line_obj._fields['ac_addr_number_street'].string,
                                         'required': task_master_line_obj._fields['ac_addr_number_street'].required,
                                         'visible_task_ids': is_pi_required}
                task_list.append(ac_addr_number_street)
                ac_addr_city = {'key': 'ac_addr_city', 'type': task_master_line_obj._fields['ac_addr_city'].type,
                                'title': task_master_line_obj._fields['ac_addr_city'].string,
                                'required': task_master_line_obj._fields['ac_addr_city'].required,
                                'visible_task_ids': is_pi_required}
                task_list.append(ac_addr_city)
                contact_ac_marketing_name = {'key': 'contact_ac_marketing_name',
                                             'type': task_master_line_obj._fields['contact_ac_marketing_name'].type,
                                             'title': task_master_line_obj._fields['contact_ac_marketing_name'].string,
                                             'required': task_master_line_obj._fields['contact_ac_marketing_name'].required,
                                             'visible_task_ids': is_pi_required}
                task_list.append(contact_ac_marketing_name)
                contact_ac_marketing_title = {'key': 'contact_ac_marketing_title',
                                              'type': task_master_line_obj._fields['contact_ac_marketing_title'].type,
                                              'title': task_master_line_obj._fields['contact_ac_marketing_title'].string,
                                              'required': task_master_line_obj._fields[
                                                  'contact_ac_marketing_title'].required,
                                              'visible_task_ids': is_pi_required}
                task_list.append(contact_ac_marketing_title)
                contact_ac_marketing_phone = {'key': 'contact_ac_marketing_phone',
                                              'type': task_master_line_obj._fields['contact_ac_marketing_phone'].type,
                                              'title': task_master_line_obj._fields['contact_ac_marketing_phone'].string,
                                              'required': task_master_line_obj._fields[
                                                  'contact_ac_marketing_phone'].required,
                                              'visible_task_ids': is_pi_required}
                task_list.append(contact_ac_marketing_phone)
                contact_ac_marketing_email = {'key': 'contact_ac_marketing_email',
                                              'type': task_master_line_obj._fields['contact_ac_marketing_email'].type,
                                              'title': task_master_line_obj._fields['contact_ac_marketing_email'].string,
                                              'required': task_master_line_obj._fields[
                                                  'contact_ac_marketing_email'].required,
                                              'visible_task_ids': is_pi_required}
                task_list.append(contact_ac_marketing_email)
                sales_service_rep_name = {'key': 'sales_service_rep_name',
                                          'type': task_master_line_obj._fields['sales_service_rep_name'].type,
                                          'title': task_master_line_obj._fields['sales_service_rep_name'].string,
                                          'required': task_master_line_obj._fields['sales_service_rep_name'].required,
                                          'visible_task_ids': is_pi_required}
                task_list.append(sales_service_rep_name)
                product_no = {'key': 'product_no', 'type': task_master_line_obj._fields['product_no'].type,
                              'title': task_master_line_obj._fields['product_no'].string,
                              'required': task_master_line_obj._fields['product_no'].required,
                              'visible_task_ids': is_pi_required}
                task_list.append(product_no)
                product_description = {'key': 'product_description',
                                       'type': task_master_line_obj._fields['product_description'].type,
                                       'title': task_master_line_obj._fields['product_description'].string,
                                       'required': task_master_line_obj._fields['product_description'].required,
                                       'visible_task_ids': is_pi_required}
                task_list.append(product_description)
                asset_serial_no = {'key': 'asset_serial_no', 'type': task_master_line_obj._fields['asset_serial_no'].type,
                                   'title': task_master_line_obj._fields['asset_serial_no'].string,
                                   'required': task_master_line_obj._fields['asset_serial_no'].required,
                                   'visible_task_ids': is_pi_required}
                task_list.append(asset_serial_no)
                select_product_avail_stryker_value = dict(
                    task_master_line_obj._fields['select_product_avail_stryker'].selection)
                select_product_avail_stryker = {'key': 'select_product_avail_stryker',
                                               'type': task_master_line_obj._fields['select_product_avail_stryker'].type,
                                               'title': task_master_line_obj._fields[
                                                   'select_product_avail_stryker'].string,
                                               'required': task_master_line_obj._fields[
                                                   'select_product_avail_stryker'].required,
                                               'value': [
                                                   {'id': field,
                                                    'value': select_product_avail_stryker_value.get(field), }
                                                   for
                                                   field in select_product_avail_stryker_value],
                                               'visible_task_ids': is_pi_required}
                task_list.append(select_product_avail_stryker)
                no_avail_reason = {'key': 'no_avail_reason', 'type': task_master_line_obj._fields['no_avail_reason'].type,
                                   'title': task_master_line_obj._fields['no_avail_reason'].string,
                                   'required': task_master_line_obj._fields['no_avail_reason'].required,
                                   'visible_task_ids': is_pi_required}
                task_list.append(no_avail_reason)
                product_ref_no = {'key': 'product_ref_no', 'type': task_master_line_obj._fields['product_ref_no'].type,
                                  'title': task_master_line_obj._fields['product_ref_no'].string,
                                  'required': task_master_line_obj._fields['product_ref_no'].required,
                                  'visible_task_ids': is_pi_required}
                task_list.append(product_ref_no)
            # Call Customer
            is_schedule = child_ticket.next_task_ids.filtered(lambda x: x.is_schedule == True).mapped('id')
            if is_schedule:
                meeting_subject = {'key': 'meeting_subject', 'type': task_master_line_obj._fields['meeting_subject'].type,
                                   'title': task_master_line_obj._fields['meeting_subject'].string,
                                   'required': task_master_line_obj._fields['meeting_subject'].required,
                                   'visible_task_ids': is_schedule}
                task_list.append(meeting_subject)
                meeting_start_date = {'key': 'meeting_start_date',
                                      'type': task_master_line_obj._fields['meeting_start_date'].type,
                                      'title': task_master_line_obj._fields['meeting_start_date'].string,
                                      'required': task_master_line_obj._fields['meeting_start_date'].required,
                                      'visible_task_ids': is_schedule}
                task_list.append(meeting_start_date)
                meeting_end_date = {'key': 'meeting_end_date',
                                    'type': task_master_line_obj._fields['meeting_end_date'].type,
                                    'title': task_master_line_obj._fields['meeting_end_date'].string,
                                    'required': task_master_line_obj._fields['meeting_end_date'].required,
                                    'visible_task_ids': is_schedule}
                task_list.append(meeting_end_date)
            # Attachments
            is_file_attachment = child_ticket.next_task_ids.filtered(lambda x: x.is_file_attachment == True).mapped('id')
            if is_file_attachment:
                attachment_ids = {'key':'attachment_ids','type':'file','title':task_master_line_obj._fields['attachment_ids'].string,'required':task_master_line_obj._fields['attachment_ids'].required,'visible_task_ids' :is_file_attachment}
                task_list.append(attachment_ids)

            is_end_task = child_ticket.next_task_ids.filtered(lambda x: x.is_end_task == True).mapped('id')
            if is_end_task:
                recommendation_customer = {'key':'recommendation_customer','type':task_master_line_obj._fields['recommendation_customer'].type,
                                'title':task_master_line_obj._fields['recommendation_customer'].string,
                                'required':task_master_line_obj._fields['recommendation_customer'].required,
                                'visible_task_ids' : is_end_task}
                task_list.append(recommendation_customer)

                customer_remarks = {'key':'customer_remarks','type':task_master_line_obj._fields['customer_remarks'].type,
                                'title':task_master_line_obj._fields['customer_remarks'].string,
                                'required':task_master_line_obj._fields['customer_remarks'].required,
                                'visible_task_ids' : is_end_task}
                task_list.append(customer_remarks)
                feed_back_end_task_1_value = dict(
                    task_master_line_obj._fields['feed_back_end_task_1'].selection)
                feed_back_end_task_1 = {'key': 'feed_back_end_task_1',
                                               'type': task_master_line_obj._fields[
                                                   'feed_back_end_task_1'].type,
                                               'title': task_master_line_obj._fields[
                                                   'feed_back_end_task_1'].string,
                                               'required': task_master_line_obj._fields[
                                                   'feed_back_end_task_1'].required,
                                               'value': [{'id': field,
                                                          'value': feed_back_end_task_1_value.get(field), }
                                                         for
                                                         field in feed_back_end_task_1_value],
                                               'visible_task_ids': is_end_task}
                task_list.append(feed_back_end_task_1)
                feed_back_end_task_2_value = dict(
                    task_master_line_obj._fields['feed_back_end_task_2'].selection)
                feed_back_end_task_2 = {'key': 'feed_back_end_task_2',
                                        'type': task_master_line_obj._fields[
                                            'feed_back_end_task_2'].type,
                                        'title': task_master_line_obj._fields[
                                            'feed_back_end_task_2'].string,
                                        'required': task_master_line_obj._fields[
                                            'feed_back_end_task_2'].required,
                                        'value': [{'id': field,
                                                   'value': feed_back_end_task_2_value.get(field), }
                                                  for
                                                  field in feed_back_end_task_2_value],
                                        'visible_task_ids': is_end_task}
                task_list.append(feed_back_end_task_2)
                feed_back_end_task_3_value = dict(
                    task_master_line_obj._fields['feed_back_end_task_3'].selection)
                feed_back_end_task_3 = {'key': 'feed_back_end_task_3',
                                        'type': task_master_line_obj._fields[
                                            'feed_back_end_task_3'].type,
                                        'title': task_master_line_obj._fields[
                                            'feed_back_end_task_3'].string,
                                        'required': task_master_line_obj._fields[
                                            'feed_back_end_task_3'].required,
                                        'value': [{'id': field,
                                                   'value': feed_back_end_task_3_value.get(field), }
                                                  for
                                                  field in feed_back_end_task_3_value],
                                        'visible_task_ids': is_end_task}
                task_list.append(feed_back_end_task_3)
                feed_back_end_task_4_value = dict(
                    task_master_line_obj._fields['feed_back_end_task_4'].selection)
                feed_back_end_task_4 = {'key': 'feed_back_end_task_4',
                                        'type': task_master_line_obj._fields[
                                            'feed_back_end_task_4'].type,
                                        'title': task_master_line_obj._fields[
                                            'feed_back_end_task_4'].string,
                                        'required': task_master_line_obj._fields[
                                            'feed_back_end_task_4'].required,
                                        'value': [{'id': field,
                                                   'value': feed_back_end_task_4_value.get(field), }
                                                  for
                                                  field in feed_back_end_task_4_value],
                                        'visible_task_ids': is_end_task}
                task_list.append(feed_back_end_task_4)
                feed_back_end_task_5_value = dict(
                    task_master_line_obj._fields['feed_back_end_task_5'].selection)
                feed_back_end_task_5 = {'key': 'feed_back_end_task_5',
                                        'type': task_master_line_obj._fields[
                                            'feed_back_end_task_5'].type,
                                        'title': task_master_line_obj._fields[
                                            'feed_back_end_task_5'].string,
                                        'required': task_master_line_obj._fields[
                                            'feed_back_end_task_5'].required,
                                        'value': [{'id': field,
                                                   'value': feed_back_end_task_5_value.get(field), }
                                                  for
                                                  field in feed_back_end_task_5_value],
                                        'visible_task_ids': is_end_task}
                task_list.append(feed_back_end_task_5)
                signature = {'key':'signature','type':'signature',
                                'title':task_master_line_obj._fields['signature'].string,
                                'required':task_master_line_obj._fields['signature'].required,
                                'visible_task_ids' : is_end_task}
                task_list.append(signature)
            is_work_order = child_ticket.next_task_ids.filtered(lambda x: x.is_work_order == True).mapped('id')
            if is_work_order:
                wk_exp_pi_no = {'key': 'wk_exp_pi_no',
                                   'type': task_master_line_obj._fields['wk_exp_pi_no'].type,
                                   'title': task_master_line_obj._fields['wk_exp_pi_no'].string,
                                   'required': task_master_line_obj._fields['wk_exp_pi_no'].required,
                                   'visible_task_ids': is_work_order}
                task_list.append(wk_exp_pi_no)
                wk_exp_pi_description = {'key': 'wk_exp_pi_description',
                                   'type': task_master_line_obj._fields['wk_exp_pi_description'].type,
                                   'title': task_master_line_obj._fields['wk_exp_pi_description'].string,
                                   'required': task_master_line_obj._fields['wk_exp_pi_description'].required,
                                   'visible_task_ids': is_work_order}
                task_list.append(wk_exp_pi_description)
                wk_cat_no = {'key': 'wk_cat_no',
                                   'type': task_master_line_obj._fields['wk_cat_no'].type,
                                   'title': task_master_line_obj._fields['wk_cat_no'].string,
                                   'required': task_master_line_obj._fields['wk_cat_no'].required,
                                   'visible_task_ids': is_work_order}
                task_list.append(wk_cat_no)
                stock_lot_obj = request.env['stock.lot'].sudo().search([])
                wk_stock_lot_id = {'key': 'wk_stock_lot_id',
                                   'type': task_master_line_obj._fields['wk_stock_lot_id'].type,
                                   'title': task_master_line_obj._fields['wk_stock_lot_id'].string,
                                   'required': task_master_line_obj._fields['wk_stock_lot_id'].required,
                                   'value': [{'id': stock_lot_id.id, 'value': stock_lot_id.name, } for stock_lot_id in
                                            stock_lot_obj],
                                   'visible_task_ids': is_work_order}
                task_list.append(wk_stock_lot_id)
                wk_quantity = {'key': 'wk_quantity',
                                   'type': task_master_line_obj._fields['wk_quantity'].type,
                                   'title': task_master_line_obj._fields['wk_quantity'].string,
                                   'required': task_master_line_obj._fields['wk_quantity'].required,
                                   'visible_task_ids': is_work_order}
                task_list.append(wk_quantity)
                wk_description = {'key': 'wk_description',
                                   'type': task_master_line_obj._fields['wk_description'].type,
                                   'title': task_master_line_obj._fields['wk_description'].string,
                                   'required': task_master_line_obj._fields['wk_description'].required,
                                   'visible_task_ids': is_work_order}
                task_list.append(wk_description)
                wk_repair_charge = {'key': 'wk_repair_charge',
                                   'type': task_master_line_obj._fields['wk_repair_charge'].type,
                                   'title': task_master_line_obj._fields['wk_repair_charge'].string,
                                   'required': task_master_line_obj._fields['wk_repair_charge'].required,
                                   'visible_task_ids': is_work_order}
                task_list.append(wk_repair_charge)
                wk_inv_no = {'key': 'wk_inv_no',
                                   'type': task_master_line_obj._fields['wk_inv_no'].type,
                                   'title': task_master_line_obj._fields['wk_inv_no'].string,
                                   'required': task_master_line_obj._fields['wk_inv_no'].required,
                                   'visible_task_ids': is_work_order}
                task_list.append(wk_inv_no)
                wk_date = {'key': 'wk_date',
                                   'type': task_master_line_obj._fields['wk_date'].type,
                                   'title': task_master_line_obj._fields['wk_date'].string,
                                   'required': task_master_line_obj._fields['wk_date'].required,
                                   'visible_task_ids': is_work_order}
                task_list.append(wk_date)
                wk_install_date = {'key': 'wk_install_date',
                                   'type': task_master_line_obj._fields['wk_install_date'].type,
                                   'title': task_master_line_obj._fields['wk_install_date'].string,
                                   'required': task_master_line_obj._fields['wk_install_date'].required,
                                   'visible_task_ids': is_work_order}
                task_list.append(wk_install_date)
                wk_se_call_no = {'key': 'wk_se_call_no',
                                   'type': task_master_line_obj._fields['wk_se_call_no'].type,
                                   'title': task_master_line_obj._fields['wk_se_call_no'].string,
                                   'required': task_master_line_obj._fields['wk_se_call_no'].required,
                                   'visible_task_ids': is_work_order}
                task_list.append(wk_se_call_no)
                meeting_start_date = {'key': 'meeting_start_date',
                                   'type': task_master_line_obj._fields['meeting_start_date'].type,
                                   'title': task_master_line_obj._fields['meeting_start_date'].string,
                                   'required': task_master_line_obj._fields['meeting_start_date'].required,
                                   'visible_task_ids': is_work_order}
                task_list.append(meeting_start_date)
                meeting_end_date = {'key': 'meeting_end_date',
                                   'type': task_master_line_obj._fields['meeting_end_date'].type,
                                   'title': task_master_line_obj._fields['meeting_end_date'].string,
                                   'required': task_master_line_obj._fields['meeting_end_date'].required,
                                   'visible_task_ids': is_work_order}
                task_list.append(meeting_end_date)
            is_request_approval = child_ticket.next_task_ids.filtered(lambda x: x.is_request_approval == True).mapped('id')
            if is_request_approval:
                multi_approval_type_obj = request.env['multi.approval.type'].sudo().search([])
                approval_type_id = {'key': 'approval_type_id',
                                   'type': task_master_line_obj._fields['approval_type_id'].type,
                                   'title': task_master_line_obj._fields['approval_type_id'].string,
                                   'required': task_master_line_obj._fields['approval_type_id'].required,
                                   'value': [{'id': multi_approval_type_id.id, 'value': multi_approval_type_id.name, } for multi_approval_type_id in
                                            multi_approval_type_obj],
                                   'visible_task_ids': is_request_approval}
                task_list.append(approval_type_id)
        _logger.info('/api/ticket/status_update value: %s' % task_list)
        if task_list:
            return valid_response([task_list], 'task load successfully', 200)
        else:
            return valid_response(task_list, 'there is no task ', 200)


    @validate_token
    @http.route("/api/ticket/status_update/submit", type="json", auth="none", methods=["POST"], csrf=False)
    def api_parent_ticket_status_update_submit(self, **post):
        post = json.loads(request.httprequest.data)
        # _logger.info('/api/ticket/status_update/submittttttttttttttttttt :%s', post)
        parent_ticket_id = post.get('parent_id')
        child_ticket_id = post.get('child_id')
        task_field_dic ={}
        if parent_ticket_id:
            task_field_dic['parent_ticket_id'] = int(parent_ticket_id)
        elif child_ticket_id:
            task_field_dic['child_ticket_id'] = int(child_ticket_id)
        if post.get('task_id'):
            task_field_dic['task_id'] = int(post.get('task_id'))
        if post.get('add_latitude'):
            task_field_dic['add_latitude'] = float(post.get('add_latitude'))
        if post.get('add_longitude'):
            task_field_dic['add_longitude'] = float(post.get('add_longitude'))
        # PI required
        if post.get('complaint_type'):
            task_field_dic['complaint_type'] = str(post.get('complaint_type'))
        if post.get('phone'):
            task_field_dic['phone'] = str(post.get('phone'))
        if post.get('name_of_reporter'):
            task_field_dic['name_of_reporter'] = str(post.get('name_of_reporter'))
        if post.get('email'):
            task_field_dic['email'] = str(post.get('email'))
        if post.get('title'):
            task_field_dic['title'] = str(post.get('title'))
        if post.get('date_of_reporting'):
            task_field_dic['date_of_reporting'] = datetime.strptime(str(post.get('date_of_reporting')),'%Y-%m-%dT%H:%M:%S.%f')
        if post.get('awareness_date'):
            task_field_dic['awareness_date'] = datetime.strptime(str(post.get('awareness_date')),'%Y-%m-%dT%H:%M:%S.%f')
        if post.get('reason_for_delay'):
            task_field_dic['reason_for_delay'] = str(post.get('reason_for_delay'))
        if post.get('date_of_event'):
            task_field_dic['date_of_event'] = datetime.strptime(str(post.get('date_of_event')),'%Y-%m-%dT%H:%M:%S.%f')
        if post.get('event_description'):
            task_field_dic['event_description'] = str(post.get('event_description'))
        if post.get('issue_noticed_comment'):
            task_field_dic['issue_noticed_comment'] = str(post.get('issue_noticed_comment'))
        if post.get('select_case_completed'):
            task_field_dic['select_case_completed'] = str(post.get('select_case_completed'))
        if post.get('select_medical_intervention_needed'):
            task_field_dic['select_medical_intervention_needed'] = str(post.get('select_medical_intervention_needed'))
        if post.get('select_patient_involved'):
            task_field_dic['select_patient_involved'] = str(post.get('select_patient_involved'))
        if post.get('select_surgical_delay'):
            task_field_dic['select_surgical_delay'] = str(post.get('select_surgical_delay'))
        if post.get('select_adverse_consequences'):
            task_field_dic['select_adverse_consequences'] = str(post.get('select_adverse_consequences'))
        if post.get('length_of_delay'):
            task_field_dic['length_of_delay'] = str(post.get('length_of_delay'))
        if post.get('initial_reporter_facility'):
            task_field_dic['initial_reporter_facility'] = str(post.get('initial_reporter_facility'))
        if post.get('ac_addr_number_street'):
            task_field_dic['ac_addr_number_street'] = str(post.get('ac_addr_number_street'))
        if post.get('ac_addr_city'):
            task_field_dic['ac_addr_city'] = str(post.get('ac_addr_city'))
        if post.get('contact_ac_marketing_name'):
            task_field_dic['contact_ac_marketing_name'] = str(post.get('contact_ac_marketing_name'))
        if post.get('contact_ac_marketing_title'):
            task_field_dic['contact_ac_marketing_title'] = str(post.get('contact_ac_marketing_title'))
        if post.get('contact_ac_marketing_phone'):
            task_field_dic['contact_ac_marketing_phone'] = str(post.get('contact_ac_marketing_phone'))
        if post.get('contact_ac_marketing_email'):
            task_field_dic['contact_ac_marketing_email'] = str(post.get('contact_ac_marketing_email'))
        if post.get('sales_service_rep_name'):
            task_field_dic['sales_service_rep_name'] = str(post.get('sales_service_rep_name'))
        if post.get('product_no'):
            task_field_dic['product_no'] = str(post.get('product_no'))
        if post.get('product_description'):
            task_field_dic['product_description'] = str(post.get('product_description'))
        if post.get('asset_serial_no'):
            task_field_dic['asset_serial_no'] = str(post.get('asset_serial_no'))
        if post.get('select_product_avail_stryker'):
            task_field_dic['select_product_avail_stryker'] = str(post.get('select_product_avail_stryker'))
        if post.get('no_avail_reason'):
            task_field_dic['no_avail_reason'] = str(post.get('no_avail_reason'))
        if post.get('product_ref_no'):
            task_field_dic['product_ref_no'] = str(post.get('product_ref_no'))
        # is_schedule
        if post.get('meeting_subject'):
            task_field_dic['meeting_subject'] = str(post.get('meeting_subject'))
        if post.get('meeting_start_date'):
            task_field_dic['meeting_start_date'] = datetime.strptime(str(post.get('meeting_start_date')),'%Y-%m-%dT%H:%M:%S.%f')
        if post.get('meeting_end_date'):
            task_field_dic['meeting_end_date'] = datetime.strptime(str(post.get('meeting_end_date')),'%Y-%m-%dT%H:%M:%S.%f')
        # is_end_task
        if post.get('recommendation_customer'):
            task_field_dic['recommendation_customer'] = str(post.get('recommendation_customer'))
        if post.get('customer_remarks'):
            task_field_dic['customer_remarks'] = str(post.get('customer_remarks'))
        if post.get('feed_back_end_task_1'):
            task_field_dic['feed_back_end_task_1'] = str(post.get('feed_back_end_task_1'))
        if post.get('feed_back_end_task_2'):
            task_field_dic['feed_back_end_task_2'] = str(post.get('feed_back_end_task_2'))
        if post.get('feed_back_end_task_3'):
            task_field_dic['feed_back_end_task_3'] = str(post.get('feed_back_end_task_3'))
        if post.get('feed_back_end_task_4'):
            task_field_dic['feed_back_end_task_4'] = str(post.get('feed_back_end_task_4'))
        if post.get('feed_back_end_task_5'):
            task_field_dic['feed_back_end_task_5'] = str(post.get('feed_back_end_task_5'))
        if post.get('signature'):
            task_field_dic['signature'] = str(post.get('signature'))
        if post.get('approval_type_id'):
            task_field_dic['approval_type_id'] = int(post.get('approval_type_id'))
        try:
            # if parent_ticket_id:
            #     task = request.env['tasks.master.line'].sudo().create(task_field_dic)
            #     parent_id = request.env['parent.ticket'].sudo().browse(int(parent_ticket_id))
            #     parent_id._onchange_task_list_ids()
            if child_ticket_id:
                _logger.info('#########################\n            *************************************    \n ')
                task = request.env['tasks.master.line'].sudo().create(task_field_dic)
                _logger.info('\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n',task)
                child_id = request.env['child.ticket'].sudo().browse(int(child_ticket_id))
                _logger.info('            *************************************     ', task)
                child_id._onchange_task_list_ids()
                attachments=[]
                attachment_name= 1
                if post.get('attachment_ids'):
                    for att in post.get('attachment_ids'):
                        attachments_vals = request.env['ir.attachment'].create({
                            'name': 'service_engineer_'+str(attachment_name),
                            'res_id': task.id,
                            'res_model': 'tasks.master.line',
                            'datas': att,
                            'type': 'binary',
                        })
                        attachment_name+=1
                        attachments.append((4,attachments_vals.id))
                    if attachments:
                        task.update({
                            'attachment_ids': attachments,
                        })
                    _logger.info('attachment_ids',attachments)
            return valid_response([[{'ticket_status' : str(task.task_id.name) }]],
                                  ' status updated successfully', 200)

        except Exception as e:
            request.env.cr.rollback()
            info = "There was a problem {}".format((e))
            error = "Something went wrong"
            _logger.error(info)
            return invalid_response(info, error, 403)


    @validate_token
    @http.route("/api/get_task_history", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_installation_value_update(self, **post):
        post = json.loads(request.httprequest.data)
        parent_id = post.get('parent_id')
        child_id = post.get('child_id')
        tasks_master_line = request.env['tasks.master.line']
        if parent_id:
            task_id = tasks_master_line.sudo().search([('parent_ticket_id','=',int(parent_id))])
        elif child_id:
            task_id = tasks_master_line.sudo().search([('child_ticket_id','=',int(child_id))])
        task_list = []
        if task_id:
            for rec in task_id:
                vals = {
                    'task_id':rec.task_id.name,
                    'description': rec.description,
                    'create_date': str(rec.create_date)
                }
                task_list.append(vals)
        if task_list:
            return valid_response(task_list, 'task list load successfully', 200)
        else:
            return valid_response(task_list, 'there is no task list', 200)




