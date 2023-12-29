from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response, valid_response1, valid_response2
from odoo import http
from odoo.http import request
import json
import pytz
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
        request_type_code = post.get('code')
        search_value = post.get('search_value')
        ticket_id = post.get('id')
        ticket_ids = post.get('ids')
        service_request_id = post.get('service_request_id')
        state_filter = post.get('state_filter')
        uid = request.env.uid
        company_id = request.env.company.id
        user = request.env.user.browse(uid)
        child_ticket_obj = request.env['child.ticket']
        service_request_obj = request.env['service.request']
        Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
        CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
        Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
            'ppts_service_request.service_request_group_manager')
        National_Head = user.has_group('ppts_service_request.service_request_national_head')
        user_tz = user.tz or 'UTC'
        local_tz = pytz.timezone(user_tz)

        employee_id = request.env['hr.employee'].sudo().search(
            [('user_id', '=', uid), ('company_id', '=', user.company_id.id)])
        attendance = request.env['hr.attendance'].sudo().search(
            [('employee_id', '=', employee_id.id), ('check_out', '=', False)], limit=1)

        domain = []
        if ticket_type and ticket_type != 'tk_all':
            domain += [('request_type_id.ticket_type', '=', ticket_type)]
        if ticket_id:
            domain += [('id', '=', int(ticket_id))]
        if ticket_ids:
            domain += [('id', 'in', list(ticket_ids))]

        if request_type_code:
            domain += [('request_type_id.code', '=', request_type_code)]
        if service_request_id:
            domain += [('service_request_id', '=', int(service_request_id))]
        if search_value:
            domain += [('name', 'ilike', search_value)]
        if state_filter and state_filter != 'all':
            domain += [('state', '=', state_filter)]
        if CT_Users:
            domain += [('team_id', 'in', user.team_ids.ids)]
        elif Show_Service_Request_Service_Engineer:
            domain += [('child_assign_engineer_ids', 'in', user.id), ('is_pi_true', '=', True)]
        elif [Manager_CT_Repair_Manager_Service_Manager_RSM]:
            domain += [('team_id', 'in', user.team_ids.ids)]
        elif National_Head:
            domain += [('team_id', 'in', user.team_ids.ids)]
        else:
            domain += [('id', '=', False)]
        _logger.info('domain : %s', domain)
        count = child_ticket_obj.sudo().search_count(domain)
        child_ticket_ids = child_ticket_obj.sudo().search(domain, offset=next_count, limit=limit,
                                                          order='name DESC')
        state_value_all = dict(child_ticket_obj._fields['state'].selection)
        filter_state = [{'id': field,
                         'value': state_value_all.get(field), }
                        for field in state_value_all]
        filter_state.insert(0, {'id': 'all', 'value': "ALL"})
        child_ticket_list = []
        if not ticket_ids:
            return valid_response2(child_ticket_list, filter_state, count, 'there is no child ticket', 200)
        # filter={
        #     'key':'state_filter','type':child_ticket_obj._fields['state'].type,
        #     'title':child_ticket_obj._fields['state'].string,
        #     'value':filter_state
        # }
        # child_ticket_list.append(filter)
        for rec in child_ticket_ids:
            id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                  'value': rec.id if rec.id else ''}
            name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                    'value': rec.name if rec.name else ''}
            child_ticket_type_id = {'key': 'child_ticket_type_id', 'type': rec._fields['child_ticket_type_id'].type,
                                    'title': rec._fields['child_ticket_type_id'].string,
                                    'value': rec.child_ticket_type_id.name if rec.child_ticket_type_id else ''}
            customer_type = {'key': 'customer_type', 'type': rec._fields['partner_id'].type, 'title': 'Customer Type',
                             'value': rec.partner_id.customer_type.name if rec.partner_id.customer_type else ''}
            create_date = {'key': 'create_date', 'type': rec._fields['create_date'].type,
                           'title': rec._fields['create_date'].string,
                           'value': str(rec.create_date.astimezone(local_tz).replace(tzinfo=None).strftime(
                               '%B %d,%Y %I:%M %p')) if rec.create_date else ''}
            state = {'key': 'state', 'type': rec._fields['state'].type, 'title': rec._fields['state'].string,
                     'value': dict(rec._fields['state'].selection).get(rec.state)}
            child_ticket_id_alias = {'key': 'child_ticket_id_alias', 'type': rec._fields['child_ticket_id_alias'].type,
                                     'title': rec._fields['child_ticket_id_alias'].string,
                                     'value': rec.child_ticket_id_alias if rec.child_ticket_id_alias else ''}
            child_configuration_id = {'key': 'child_configuration_id',
                                      'type': rec._fields['child_configuration_id'].type,
                                      'title': rec._fields['child_configuration_id'].string,
                                      'value': rec.child_configuration_id.child_config_name if rec.child_configuration_id else ''}
            call_source_id = {'key': 'call_source_id', 'type': rec._fields['call_source_id'].type,
                              'title': rec._fields['call_source_id'].string,
                              'value': rec.call_source_id.name if rec.call_source_id else ''}
            partner_id = {'key': 'partner_id', 'type': rec._fields['partner_id'].type,
                          'title': rec._fields['partner_id'].string,
                          'value': rec.partner_id.name if rec.partner_id else '',
                          'id': rec.partner_id.id if rec.partner_id else ''}

            call_date = {'key': 'call_date', 'type': rec._fields['call_date'].type,
                         'title': rec._fields['call_date'].string,
                         'value': str(rec.call_date) if rec.call_date else ''}
            request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type,
                               'title': rec._fields['request_type_id'].string,
                               'value': rec.request_type_id.name if rec.request_type_id else ''}
            service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type,
                                   'title': rec._fields['service_category_id'].string,
                                   'value': rec.service_category_id.name if rec.service_category_id else ''}
            service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type,
                               'title': rec._fields['service_type_id'].string,
                               'value': rec.service_type_id.name if rec.service_type_id else ''}
            stock_lot_id = {'key': 'stock_lot_id', 'type': rec._fields['stock_lot_id'].type,
                            'title': rec._fields['stock_lot_id'].string,
                            'value': rec.stock_lot_id.name if rec.stock_lot_id else ''}
            product_id = {'key': 'product_id', 'type': rec._fields['product_id'].type,
                          'title': rec._fields['product_id'].string,
                          'value': rec.product_id.name if rec.product_id else ''}
            product_part_number = {'key': 'product_part_number', 'type': rec._fields['product_part_number'].type,
                                   'title': rec._fields['product_part_number'].string,
                                   'value': rec.product_part_number if rec.product_part_number else ''}
            repair_location_id = {'key': 'repair_location_id', 'type': rec._fields['repair_location_id'].type,
                                  'title': rec._fields['repair_location_id'].string,
                                  'value': rec.repair_location_id.name if rec.repair_location_id else ''}
            oem_warranty_status = {'key': 'oem_warranty_status', 'type': rec._fields['oem_warranty_status'].type,
                                   'title': rec._fields['oem_warranty_status'].string,
                                   'value': dict(rec._fields['oem_warranty_status'].selection).get(
                                       rec.oem_warranty_status) if rec.oem_warranty_status else ''}
            oem_repair_status = {'key': 'oem_repair_status', 'type': rec._fields['oem_repair_status'].type,
                                 'title': rec._fields['oem_repair_status'].string,
                                 'value': dict(rec._fields['oem_repair_status'].selection).get(
                                     rec.oem_repair_status) if rec.oem_repair_status else ''}
            extended_warranty_status = {'key': 'extended_warranty_status',
                                        'type': rec._fields['extended_warranty_status'].type,
                                        'title': rec._fields['extended_warranty_status'].string,
                                        'value': dict(rec._fields['extended_warranty_status'].selection).get(
                                            rec.extended_warranty_status) if rec.extended_warranty_status else ''}
            categ_id = {'key': 'categ_id', 'type': rec._fields['categ_id'].type,
                        'title': rec._fields['categ_id'].string,
                        'value': rec.categ_id.name if rec.categ_id else ''}
            product_category_id_alias = {'key': 'product_category_id_alias',
                                         'type': rec._fields['product_category_id_alias'].type,
                                         'title': rec._fields['product_category_id_alias'].string,
                                         'value': rec.product_category_id_alias if rec.product_category_id_alias else ''}
            problem_description = {'key': 'problem_description', 'type': rec._fields['problem_description'].type,
                                   'title': rec._fields['problem_description'].string,
                                   'value': rec.problem_description if rec.problem_description else ''}
            requested_by_name_child = {'key': 'requested_by_name_child',
                                       'type': rec._fields['requested_by_name_child'].type,
                                       'title': rec._fields['requested_by_name_child'].string,
                                       'value': rec.requested_by_name_child if rec.requested_by_name_child else ''}
            requested_by_contact_number = {'key': 'requested_by_contact_number',
                                           'type': rec._fields['requested_by_contact_number'].type,
                                           'title': rec._fields['requested_by_contact_number'].string,
                                           'value': rec.requested_by_contact_number if rec.requested_by_contact_number else ''}
            requested_by_email_ct = {'key': 'requested_by_email_ct', 'type': rec._fields['requested_by_email_ct'].type,
                                     'title': rec._fields['requested_by_email_ct'].string,
                                     'value': rec.requested_by_email_ct if rec.requested_by_email_ct else ''}
            requested_by_title_ct = {'key': 'requested_by_title_ct', 'type': rec._fields['requested_by_title_ct'].type,
                                     'title': rec._fields['requested_by_title_ct'].string,
                                     'value': rec.requested_by_title_ct if rec.requested_by_title_ct else ''}
            remarks = {'key': 'remarks', 'type': rec._fields['remarks'].type, 'title': rec._fields['remarks'].string,
                       'value': rec.remarks if rec.remarks else ''}
            installation_date = {'key': 'installation_date', 'type': rec._fields['installation_date'].type,
                                 'title': rec._fields['installation_date'].string,
                                 'value': str(rec.installation_date) if rec.installation_date else ''}
            dealer_distributor_id = {'key': 'dealer_distributor_id', 'type': rec._fields['dealer_distributor_id'].type,
                                     'title': rec._fields['dealer_distributor_id'].string,
                                     'value': rec.dealer_distributor_id.name if rec.dealer_distributor_id else ''}
            call_received_id = {'key': 'call_received_id', 'type': rec._fields['call_received_id'].type,
                                'title': rec._fields['call_received_id'].string,
                                'value': rec.call_received_id.name if rec.call_received_id else ''}
            alternate_contact_name = {'key': 'alternate_contact_name',
                                      'type': rec._fields['alternate_contact_name'].type,
                                      'title': rec._fields['alternate_contact_name'].string,
                                      'value': rec.alternate_contact_name if rec.alternate_contact_name else ''}
            alternate_contact_email = {'key': 'alternate_contact_email',
                                       'type': rec._fields['alternate_contact_email'].type,
                                       'title': rec._fields['alternate_contact_email'].string,
                                       'value': rec.alternate_contact_email if rec.alternate_contact_email else ''}
            alternate_contact_id = {'key': 'alternate_contact_id', 'type': rec._fields['alternate_contact_id'].type,
                                    'title': rec._fields['alternate_contact_id'].string,
                                    'value': rec.alternate_contact_id.name if rec.alternate_contact_id else ''}
            alternate_contact_number = {'key': 'alternate_contact_number',
                                        'type': rec._fields['alternate_contact_number'].type,
                                        'title': rec._fields['alternate_contact_number'].string,
                                        'value': rec.alternate_contact_number if rec.alternate_contact_number else ''}
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
            current_asset_location = {'key': 'current_asset_location',
                                      'type': rec._fields['current_asset_location'].type,
                                      'title': rec._fields['current_asset_location'].string,
                                      'value': rec.current_asset_location.name if rec.current_asset_location else ''}
            team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type, 'title': rec._fields['team_id'].string,
                       'value': rec.team_id.name if rec.team_id else ''}
            customer_account_id = {'key': 'customer_account_id', 'type': rec._fields['customer_account_id'].type,
                                   'title': rec._fields['customer_account_id'].string,
                                   'value': rec.customer_account_id.name if rec.customer_account_id else ''}
            parent_ticket_id = {'key': 'parent_ticket_id', 'type': rec._fields['parent_ticket_id'].type,
                                'title': rec._fields['parent_ticket_id'].string,
                                'value': rec.parent_ticket_id.name if rec.parent_ticket_id else ''}
            service_request_id = {'key': 'service_request_id', 'type': rec._fields['service_request_id'].type,
                                  'title': rec._fields['service_request_id'].string,
                                  'value': rec.service_request_id.name if rec.service_request_id else ''}
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
            company_id = {'key': 'company_id', 'type': rec._fields['company_id'].type,
                          'title': rec._fields['company_id'].string,
                          'value': rec.company_id.name if rec.company_id else ''}
            survey_id = {'key': 'survey_id', 'type': rec._fields['survey_id'].type,
                         'title': rec._fields['survey_id'].string,
                         'value': rec.survey_id.title if rec.survey_id else ''}
            price_available_in_contract = {'key': 'price_available_in_contract',
                                           'type': rec._fields['price_available_in_contract'].type,
                                           'title': rec._fields['price_available_in_contract'].string,
                                           'value': rec.price_available_in_contract if rec.price_available_in_contract else ''}
            re_repair = {'key': 're_repair', 'type': rec._fields['re_repair'].type,
                         'title': rec._fields['re_repair'].string,
                         'value': dict(rec._fields['re_repair'].selection).get(rec.re_repair) if rec.re_repair else ''}
            parent_ticket_id_alias = {'key': 'parent_ticket_id_alias',
                                      'type': rec._fields['parent_ticket_id_alias'].type,
                                      'title': rec._fields['parent_ticket_id_alias'].string,
                                      'value': rec.parent_ticket_id_alias if rec.parent_ticket_id_alias else ''}
            parent_ticket_id_alias_date = {'key': 'parent_ticket_id_alias_date',
                                           'type': rec._fields['parent_ticket_id_alias_date'].type,
                                           'title': rec._fields['parent_ticket_id_alias_date'].string,
                                           'value': str(rec.parent_ticket_id_alias_date.strftime(
                                               '%B %d,%Y')) if rec.parent_ticket_id_alias_date else ''}
            action_taken_at_site = {'key': 'action_taken_at_site', 'type': rec._fields['action_taken_at_site'].type,
                                    'title': rec._fields['action_taken_at_site'].string,
                                    'value': rec.action_taken_at_site if rec.action_taken_at_site else ''}
            version = {'key': 'version', 'type': rec._fields['version'].type, 'title': rec._fields['version'].string,
                       'value': rec.version if rec.version else ''}
            job_closed_date = {'key': 'job_closed_date', 'type': rec._fields['job_closed_date'].type,
                               'title': rec._fields['job_closed_date'].string,
                               'value': str(rec.job_closed_date.astimezone(local_tz).replace(tzinfo=None).strftime(
                                   '%B %d,%Y %I:%M %p')) if rec.job_closed_date else ''}
            installation_id = {'key': 'installation_id', 'type': rec._fields['installation_id'].type,
                               'title': rec._fields['installation_id'].string,
                               'value': rec.installation_id.name if rec.installation_id else '',
                               'ids': [rec.installation_id.id] if rec.installation_id else ''}
            replacement_order_ids = {'key': 'replacement_order_ids', 'type': rec._fields['replacement_order_ids'].type,
                                     'title': rec._fields['replacement_order_ids'].string,
                                     # 'value':[{'id':fields.id,'value':fields.name} for fields in rec.replacement_order_ids] if rec.replacement_order_ids else '',
                                     'value': ', '.join(
                                         rec.replacement_order_ids.mapped('name')) if rec.replacement_order_ids else '',
                                     'ids': rec.replacement_order_ids.mapped(
                                         'id') if rec.replacement_order_ids else False,
                                     }
            maintenance_ids = {'key': 'maintenance_ids', 'type': rec._fields['maintenance_ids'].type,
                               'title': rec._fields['maintenance_ids'].string,
                               'value': ', '.join(rec.maintenance_ids.mapped('name')) if rec.maintenance_ids else '',
                               'ids': rec.maintenance_ids.mapped('id') if rec.maintenance_ids else False
                               }
            service_request = service_request_obj.sudo().search([('child_ticket_id', '=', rec.id)])
            service_request_ids = {'key': 'service_request_ids', 'type': rec._fields['service_request_id'].type,
                                   'title': rec._fields['service_request_id'].string,
                                   'value': ', '.join(service_request.mapped('name')) if service_request else '',
                                   'ids': service_request.mapped('id') if service_request else False
                                   }
            child_ticket_list.append(
                [id, name, child_ticket_type_id, customer_type, create_date, state, product_id, child_ticket_id_alias,
                 child_configuration_id, call_source_id,
                 call_date, request_type_id, service_type_id, service_category_id, stock_lot_id, product_part_number,
                 repair_location_id,
                 oem_warranty_status, oem_repair_status, extended_warranty_status, categ_id, problem_description,
                 requested_by_name_child,
                 requested_by_contact_number, requested_by_email_ct, requested_by_title_ct, remarks,
                 dealer_distributor_id,
                 call_received_id, partner_id, alternate_contact_name, alternate_contact_email, alternate_contact_id,
                 alternate_contact_number,
                 oem_warranty_status_id, repair_warranty_status_id, cmc_status, amc_status, current_asset_location,
                 team_id, customer_account_id,
                 parent_ticket_id, service_request_id, faulty_section, sow, webdelata_id, mc_stk, company_id, survey_id,
                 price_available_in_contract,
                 re_repair, parent_ticket_id_alias, parent_ticket_id_alias_date, action_taken_at_site, version,
                 job_closed_date, installation_date,
                 webdelata, installation_id, replacement_order_ids, maintenance_ids, service_request_ids,
                 ])
            child_ticket_len = len(child_ticket_list) - 1
            if rec.state not in ['cancel', 'closed'] and attendance:
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
                action_expense = {'key': 'action_expences', 'type': "button",
                                  'title': 'Expense',
                                  'value': True
                                  }
                child_ticket_list[child_ticket_len].append(action_expense)

            if rec.state not in ['cancel',
                                 'closed'] and not rec.is_ar_hold_tick and not rec.is_disable_status_update and attendance:
                action_child_status = {'key': 'action_child_status', 'type': "button",
                                       'title': 'Status',
                                       'value': True}
                child_ticket_list[child_ticket_len].append(action_child_status)
            if rec.is_create_installation and rec.is_installation_created == False and attendance:
                start_installation = {'key': 'start_installation', 'type': "button",
                                      'title': 'Start Installation',
                                      'value': True
                                      }
                child_ticket_list[child_ticket_len].append(start_installation)
            if rec.task_value_notify:
                child_ticket_message = {'key': 'child_ticket_message', 'type': "message",
                                        'title': 'A new child ticket is created to proceed further. To access new child ticket open the parent ticket  ' + rec.parent_ticket_id.name if rec.parent_ticket_id else '',
                                        'value': True,
                                        'error': False,
                                        }
                child_ticket_list[child_ticket_len].append(child_ticket_message)
            if rec.is_auto_approval and rec.state == 'approved':
                child_ticket_message_approval = {'key': 'child_ticket_message_approval', 'type': "message",
                                                 'title': 'Automatic Approval has enabled to this Child Ticket',
                                                 'value': True,
                                                 'error': False,
                                                 }
                child_ticket_list[child_ticket_len].append(child_ticket_message_approval)
            _logger.info('replacement_order_count :%s', rec.replacement_order_count)
            _logger.info('is_create_wr_order :%s', rec.is_create_wr_order)
            _logger.info('request_type :%s', rec.request_type)
            if rec.replacement_order_count <= 0 and rec.is_create_wr_order == True and rec.request_type == 'sr_wr' and attendance:
                action_create_warranty_replacement = {'key': 'action_create_warranty_replacement', 'type': "button",
                                                      'title': 'Request Replacement',
                                                      'value': True
                                                      }
                child_ticket_list[child_ticket_len].append(action_create_warranty_replacement)
            if rec.is_create_maintenance and rec.is_maintenance_created == False:
                action_create_maintenance = {
                    'key': 'action_create_maintenance', 'type': "button",
                    'title': 'Maintenance Request',
                    'value': True
                }
                child_ticket_list[child_ticket_len].append(action_create_maintenance)
            if rec.request_count > 0:
                action_request_data = {'key': 'action_request_data', 'type': "button",
                                       'title': 'Request',
                                       'value': True}
                child_ticket_list[child_ticket_len].append(action_request_data)
        if child_ticket_list:
            return valid_response2(child_ticket_list, filter_state, count, 'child ticket load successfully', 200)
        else:
            return valid_response2(child_ticket_list, filter_state, count, 'there is no child ticket', 200)

    @validate_token
    @http.route("/api/get_child_ticket_value/start_installation", type="json", auth="none", methods=["POST"],
                csrf=False)
    def _api_get_installation_value_update(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('/api/get_child_ticket_value/start_installation :%s', post)
        try:
            start_installation = post.get('start_installation')
            child_id = post.get('child_id')
            child_ticket = request.env['child.ticket'].sudo().browse(int(child_id))
            if child_ticket:
                child_ticket.action_create_installation()
                return valid_response([[{'child_ticket_start_button': True}]], 'child ticket load successfully', 200)
        except Exception as e:
            info = "There was a problem {}".format((e))
            error = "Something went wrong"
            _logger.error(info)
            return invalid_response(info, error, 403)

    @validate_token
    @http.route("/api/get_child_ticket_value/button_update", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_child_ticket_button_update(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('/api/get_child_ticket_value/button_update :%s', post)
        try:
            start_installation = post.get('start_installation')
            action_create_warranty_replacement = post.get('action_create_warranty_replacement')
            request_raise_invoice = post.get('request_raise_invoice')
            action_expense = post.get('action_expense')
            request_quotation = post.get('request_quotation')
            action_spare_request = post.get('action_spare_request')
            action_create_maintenance = post.get('action_create_maintenance')
            child_id = post.get('child_id')
            child_obj = request.env['child.ticket'].sudo()
            request_obj = request.env['request.asset.line'].sudo()
            expense_obj = request.env['hr.expense']
            child_ticket = child_obj.browse(int(child_id))
            message = ''
            # spare_request_list = []
            list = []
            if request_raise_invoice and child_ticket:
                child_ticket.request_raise_invoice()
                message = 'request raise invoice button load successfully'
            elif request_quotation and child_ticket:
                child_ticket.request_quotation()
                message = 'request quotation button load successfully'
            elif start_installation and child_ticket:
                child_ticket.action_create_installation()
                message = 'installation button load successfully'
            elif action_create_warranty_replacement and child_ticket:
                child_ticket.action_create_warranty_replacement()
                message = 'warranty replacement button load successfully'
            elif action_create_maintenance and child_ticket:
                child_ticket.action_create_maintenance()
                message = 'Maintenance Request button load successfully'
            elif action_spare_request and child_ticket:
                # child_ticket.action_spare_request()
                message = 'action_spare_request button load successfully'
                print(request_obj._fields, 'teeeeee')
                print(request_obj._fields['description'].string)
                description = {'key': 'description', 'type': request_obj._fields['description'].type,
                               'title': request_obj._fields['description'].string,
                               'required': request_obj._fields['description'].required}
                list.append(description)
                part_number = {'key': 'part_number', 'type': request_obj._fields['part_number'].type,
                               'title': request_obj._fields['part_number'].string,
                               'required': request_obj._fields['part_number'].required}
                list.append(part_number)
                serial_number = {'key': 'serial_number', 'type': request_obj._fields['serial_number'].type,
                                 'title': request_obj._fields['serial_number'].string,
                                 'required': request_obj._fields['serial_number'].required}
                list.append(serial_number)
                quantity = {'key': 'quantity', 'type': request_obj._fields['quantity'].type,
                            'title': request_obj._fields['quantity'].string,
                            'required': request_obj._fields['quantity'].required}
                list.append(quantity)

            elif action_expense and child_ticket:
                message = 'Expense button load successfully'
                name = {'key': 'name', 'type': expense_obj._fields['name'].type,
                        'title': expense_obj._fields['name'].string,
                        'required': expense_obj._fields['name'].required}
                list.append(name)
                child_ticket_id = {'key': 'child_ticket_id', 'type': expense_obj._fields['child_ticket_id'].type,
                                   'title': expense_obj._fields['child_ticket_id'].string,
                                   'required': expense_obj._fields['child_ticket_id'].required}
                list.append(child_ticket_id)
                product_object = request.env['product.product'].sudo().search(
                    [('can_be_expensed', '=', True)
                     ])
                product_id = {'key': 'product_id', 'type': expense_obj._fields['product_id'].type,
                              'title': expense_obj._fields['product_id'].string,
                              'required': expense_obj._fields['product_id'].required,
                              'value': [{'id': field.id, 'value': field.name, } for field in product_object]
                              }
                list.append(product_id)
                unit_amount = {'key': 'unit_amount', 'type': expense_obj._fields['unit_amount'].type,
                               'title': expense_obj._fields['unit_amount'].string,
                               'required': expense_obj._fields['unit_amount'].required}
                list.append(unit_amount)
                total_amount = {'key': 'total_amount', 'type': expense_obj._fields['total_amount'].type,
                                'title': expense_obj._fields['total_amount'].string,
                                'required': expense_obj._fields['total_amount'].required}
                list.append(total_amount)
                quantity = {'key': 'quantity', 'type': expense_obj._fields['quantity'].type,
                            'title': expense_obj._fields['quantity'].string,
                            'required': expense_obj._fields['quantity'].required}
                list.append(quantity)
                payment_mode_value = dict(expense_obj._fields['payment_mode'].selection)
                payment_mode = {'key': 'payment_mode', 'type': expense_obj._fields['payment_mode'].type,
                                'title': expense_obj._fields['payment_mode'].string,
                                'required': expense_obj._fields['payment_mode'].required,
                                'value': [{'id': field, 'value': payment_mode_value.get(field) } for field in payment_mode_value]
                                }
                list.append(payment_mode)
                date = {'key': 'date', 'type': expense_obj._fields['date'].type,
                        'title': expense_obj._fields['date'].string,
                        'required': expense_obj._fields['date'].required}
                list.append(date)




                # sale_order_id = {'key': 'sale_order_id', 'type': expense_obj._fields['sale_order_id'].type,
                #                  'title': expense_obj._fields['sale_order_id'].string,
                #                  'required': expense_obj._fields['sale_order_id'].required}
                # list.append(sale_order_id)



            return valid_response([list], message, 200)
        except Exception as e:
            info = "There was a problem {}".format((e))
            error = "Something went wrong"
            _logger.error(info)
            return invalid_response(info, error, 403)

    @validate_token
    @http.route("/api/get_child_ticket_value/action_spare_request", type="json", auth="none", methods=["POST"],
                csrf=False)
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
                "name": "Spare Request",
                "is_spare_request": True,
                "child_ticket_id": child_ticket.id,
                "team_id": child_ticket.team_id.id,
                "user_id": request.env.user.id,
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
#priya
    @validate_token
    @http.route("/api/get_child_ticket_value/action_expense", type="json", auth="none", methods=["POST"])
    def _api_get_child_ticket_action_expense_update(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('/api/get_child_ticket_value/action_expense: %s' % post)
        try:
            expense_values_dic = {}
            if post.get('name'):
                expense_values_dic['name'] = post.get('name')
            if post.get('child_ticket_id'):
                expense_values_dic['child_ticket_id'] = int(post.get('child_ticket_id'))
            if post.get('product_id'):
                expense_values_dic['product_id'] = int(post.get('product_id'))
            if post.get('total_amount'):
                expense_values_dic['total_amount'] = float(post.get('total_amount'))
            if post.get('payment_mode'):
                expense_values_dic['payment_mode'] =post.get('payment_mode')
            if post.get('date'):
                expense_values_dic['date'] =post.get('date')
            if post.get('unit_amount'):
                expense_values_dic['unit_amount'] = float(post.get('unit_amount'))
            expense_id = request.env['hr.expense'].sudo().create(expense_values_dic)
            if expense_id:

                attachments = []
                attachment_name = 1
                if post.get('attachment_ids'):
                    for att in post.get('attachment_ids'):
                        attachments_vals = request.env['ir.attachment'].create({
                            'name': 'expense_' + str(attachment_name),
                            'res_id': expense_id.id,
                            'res_model': 'hr.expense',
                            'datas': att,
                            'type': 'binary',
                        })
                        attachment_name += 1
                        attachments.append((4, attachments_vals.id))
                    # if attachments:
                    #     expense_id.update({
                    #         'attachment_ids': attachments,
                    #     })
                return valid_response([[{'create_expense_id': expense_id.name}]],
                                  'Expense create successfully', 200)
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
            count = request_obj.search_count([('child_ticket_id', '=', int(child_id))])
            child_request_ids = request_obj.search([('child_ticket_id', '=', int(child_id))])
            child_request_list = []
            for rec in child_request_ids:
                id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                      'value': rec.id if rec.id else ''}
                name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                        'value': rec.name if rec.name else ''}
                child_ticket_id = {'key': 'child_ticket_id', 'type': rec._fields['child_ticket_id'].type,
                                   'title': rec._fields['child_ticket_id'].string,
                                   'value': rec.child_ticket_id.name if rec.child_ticket_id else ''}
                team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type,
                           'title': rec._fields['team_id'].string,
                           'value': rec.team_id.name if rec.team_id else ''}
                user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type,
                           'title': rec._fields['user_id'].string,
                           'value': rec.user_id.name if rec.user_id else ''}
                company_id = {'key': 'company_id', 'type': rec._fields['company_id'].type,
                              'title': rec._fields['company_id'].string,
                              'value': rec.company_id.name if rec.company_id else ''}
                child_request_list.append([id, name, child_ticket_id, team_id, user_id, company_id])
                requst_list_index = len(child_request_list) - 1
                if rec.is_spare_request:
                    spare_list = []
                    for spare in rec.asset_ids:
                        id = {'key': 'id', 'type': spare._fields['id'].type, 'title': spare._fields['id'].string,
                              'value': spare.id if spare.id else ''}
                        product_id = {'key': 'product_id', 'type': spare._fields['product_id'].type,
                                      'title': spare._fields['product_id'].string,
                                      'value': spare.product_id.name if spare.product_id else ''}
                        description = {'key': 'description', 'type': spare._fields['description'].type,
                                       'title': spare._fields['description'].string,
                                       'value': spare.description if spare.description else ''}
                        part_number = {'key': 'part_number', 'type': spare._fields['part_number'].type,
                                       'title': spare._fields['part_number'].string,
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
                        spare_list.append(
                            [id, product_id, description, part_number, serial_number, quantity, stock_availability])
                    if spare_list:
                        asset_ids = {'key': 'asset_ids', 'type': rec._fields['asset_ids'].type,
                                     'title': rec._fields['asset_ids'].string,
                                     'value': '',
                                     'data': spare_list, }
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
