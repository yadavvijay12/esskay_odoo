from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response,valid_response1,valid_response2
from odoo import http
from odoo.http import request
import json
import pytz
import logging
_logger = logging.getLogger(__name__)

class APIController(http.Controller):
    @validate_token
    @http.route("/api/get_maintenance_value", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_maintenance_value(self, **post):
        post = json.loads(request.httprequest.data)
        limit = post.get('limit')
        next_count = post.get('next_count')
        user = request.env.user.browse(post.get('uid'))
        search_value = post.get('search_value')
        state_filter = post.get('state_filter')
        maintenance_ids = post.get('ids')
        maintenance_obj = request.env['maintenance.request']
        Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
        CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
        Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
            'ppts_service_request.service_request_group_manager')
        National_Head = user.has_group('ppts_service_request.service_request_national_head')
        company_id = request.env.user.company_id.id
        domain = [('is_sr_maintenance', '=', True),('company_id','=',company_id)]
        if search_value:
            domain+=[('name','ilike',search_value)]
        if state_filter and state_filter !='all':
            domain +=[('maintenance_state','=',state_filter)]
        if maintenance_ids:
            domain += [('id', 'in', list(maintenance_ids))]


        # if CT_Users:
        #     domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
        # elif Show_Service_Request_Service_Engineer:
        #     domain += [('user_id', '=', user.id)]
        # elif Manager_CT_Repair_Manager_Service_Manager_RSM:
        #     domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
        # elif National_Head:
        #     domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
        # else:
        #     domain += [('id', '=', False)]

        count = maintenance_obj.sudo().search_count(domain)
        maintenance_ids = maintenance_obj.sudo().search(domain, offset=next_count, limit=limit,
                                                          order='name desc')

        state_value_all = dict(maintenance_obj._fields['maintenance_state'].selection)
        filter_state = [{'id': field,
                         'value': state_value_all.get(field), }
                        for field in state_value_all]
        filter_state.insert(0, {'id': 'all', 'value': "ALL"})

        maintenance_list = []
        for rec in maintenance_ids:
            id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                  'value': rec.id if rec.id else ''}
            name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                    'value': rec.name if rec.name else ''}
            # MAINTENANCE
            maintenance_process_alias_id = {'key': 'maintenance_process_alias_id', 'type': rec._fields['maintenance_process_alias_id'].type, 'title': rec._fields['maintenance_process_alias_id'].string,
                    'value': rec.maintenance_process_alias_id if rec.maintenance_process_alias_id else ''}
            maintenance_install_start_date = {'key': 'maintenance_install_start_date', 'type': rec._fields['maintenance_install_start_date'].type, 'title': rec._fields['maintenance_install_start_date'].string,
                    'value': str(rec.maintenance_install_start_date) if rec.maintenance_install_start_date else ''}
            maintenance_install_end_date = {'key': 'maintenance_install_end_date', 'type': rec._fields['maintenance_install_end_date'].type, 'title': rec._fields['maintenance_install_end_date'].string,
                    'value': str(rec.maintenance_install_end_date) if rec.maintenance_install_end_date else ''}
            title = {'key': 'title', 'type': rec._fields['title'].type, 'title': rec._fields['title'].string,
                    'value': rec.title if rec.title else ''}
            reported_fault = {'key': 'reported_fault', 'type': rec._fields['reported_fault'].type, 'title': rec._fields['reported_fault'].string,
                    'value': rec.reported_fault if rec.reported_fault else ''}
            service_request_id = {'key': 'service_request_id', 'type': rec._fields['service_request_id'].type, 'title': rec._fields['service_request_id'].string,
                    'value': rec.service_request_id.name if rec.service_request_id else ''}
            parent_ticket_id = {'key': 'parent_ticket_id', 'type': rec._fields['parent_ticket_id'].type, 'title': rec._fields['parent_ticket_id'].string,
                    'value': rec.parent_ticket_id.name if rec.parent_ticket_id else ''}
            child_ticket_id = {'key': 'child_ticket_id', 'type': rec._fields['child_ticket_id'].type, 'title': rec._fields['child_ticket_id'].string,
                    'value': rec.child_ticket_id.name if rec.child_ticket_id else ''}
            external_reference = {'key': 'external_reference', 'type': rec._fields['external_reference'].type, 'title': rec._fields['external_reference'].string,
                    'value': rec.external_reference if rec.external_reference else ''}
            service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type, 'title': rec._fields['service_category_id'].string,
                    'value': rec.service_category_id.name if rec.service_category_id else ''}
            service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type, 'title': rec._fields['service_type_id'].string,
                    'value': rec.service_type_id.name if rec.service_type_id else ''}
            child_ticket_type_id = {'key': 'child_ticket_type_id', 'type': rec._fields['child_ticket_type_id'].type, 'title': rec._fields['child_ticket_type_id'].string,
                    'value': rec.child_ticket_type_id.name if rec.child_ticket_type_id else ''}
            # PRODUCT DETAILS
            product_id = {'key': 'product_id', 'type': rec._fields['product_id'].type, 'title': rec._fields['product_id'].string,
                    'value': rec.product_id.name if rec.product_id else ''}
            stock_lot_id = {'key': 'stock_lot_id', 'type': rec._fields['stock_lot_id'].type, 'title': rec._fields['stock_lot_id'].string,
                    'value': rec.stock_lot_id.name if rec.stock_lot_id else ''}

            categ_id = {'key': 'categ_id', 'type': rec._fields['categ_id'].type, 'title': rec._fields['categ_id'].string,
                    'value': rec.categ_id.name if rec.categ_id else ''}
            asset_tag_ids = {'key': 'asset_tag_ids', 'type': rec._fields['asset_tag_ids'].type, 'title': rec._fields['asset_tag_ids'].string,
                    'value': [{'id':x.id,'value':x.name} for x in rec.asset_tag_ids] if rec.asset_tag_ids else ''}
            product_code_no = {'key': 'product_code_no', 'type': rec._fields['product_code_no'].type, 'title': rec._fields['product_code_no'].string,
                    'value': rec.product_code_no if rec.product_code_no else ''}
            cat_no = {'key': 'cat_no', 'type': rec._fields['cat_no'].type, 'title': rec._fields['cat_no'].string,
                    'value': rec.cat_no if rec.cat_no else ''}
            # OTHER INFORMATIONS
            worksheet_id = {'key': 'worksheet_id', 'type': rec._fields['worksheet_id'].type, 'title': rec._fields['worksheet_id'].string,
                    'value': rec.worksheet_id.title if rec.worksheet_id else ''}
            origin = {'key': 'origin', 'type': rec._fields['origin'].type, 'title': rec._fields['origin'].string,
                    'value': rec.origin if rec.origin else ''}
            po_number = {'key': 'po_number', 'type': rec._fields['po_number'].type, 'title': rec._fields['po_number'].string,
                    'value': rec.po_number if rec.po_number else ''}
            po_date = {'key': 'po_date', 'type': rec._fields['po_date'].type, 'title': rec._fields['po_date'].string,
                    'value': str(rec.po_date) if rec.po_date else ''}
            invoice_number = {'key': 'invoice_number', 'type': rec._fields['invoice_number'].type, 'title': rec._fields['invoice_number'].string,
                    'value': str(rec.invoice_number) if rec.invoice_number else ''}
            invoice_date = {'key': 'invoice_number', 'type': rec._fields['invoice_number'].type, 'title': rec._fields['invoice_number'].string,
                    'value': str(rec.invoice_number) if rec.invoice_number else ''}
            warranty_status = {'key': 'warranty_status', 'type': rec._fields['warranty_status'].type,
                               'title': rec._fields['warranty_status'].string,
                               'value': dict(rec._fields['warranty_status'].selection).get(
                                   rec.warranty_status) if rec.warranty_status else ''}
            warranty_end_date = {'key': 'warranty_end_date', 'type': rec._fields['warranty_end_date'].type, 'title': rec._fields['warranty_end_date'].string,
                    'value': str(rec.warranty_end_date) if rec.warranty_end_date else ''}
            extended_warranty_status = {'key': 'extended_warranty_status', 'type': rec._fields['extended_warranty_status'].type,
                               'title': rec._fields['extended_warranty_status'].string,
                               'value': dict(rec._fields['extended_warranty_status'].selection).get(
                                   rec.extended_warranty_status) if rec.extended_warranty_status else ''}
            extended_warranty_end_date = {'key': 'extended_warranty_end_date', 'type': rec._fields['extended_warranty_end_date'].type, 'title': rec._fields['extended_warranty_end_date'].string,
                    'value': str(rec.extended_warranty_end_date) if rec.extended_warranty_end_date else ''}
            amc_status = {'key': 'amc_status', 'type': rec._fields['amc_status'].type, 'title': rec._fields['amc_status'].string,
                    'value': str(rec.amc_status) if rec.amc_status else ''}
            amc_end_date = {'key': 'amc_end_date', 'type': rec._fields['amc_end_date'].type, 'title': rec._fields['amc_end_date'].string,
                    'value': str(rec.amc_end_date) if rec.amc_end_date else ''}
            cmc_status = {'key': 'cmc_status', 'type': rec._fields['cmc_status'].type, 'title': rec._fields['cmc_status'].string,
                    'value': str(rec.cmc_status) if rec.cmc_status else ''}
            cmc_end_date = {'key': 'cmc_end_date', 'type': rec._fields['cmc_end_date'].type, 'title': rec._fields['cmc_end_date'].string,
                    'value': str(rec.cmc_end_date) if rec.cmc_end_date else ''}
            action_taken_site = {'key': 'action_taken_site', 'type': rec._fields['action_taken_site'].type, 'title': rec._fields['action_taken_site'].string,
                    'value': str(rec.action_taken_site) if rec.action_taken_site else ''}

            # CUSTOMER DETAILS
            partner_id = {'key': 'partner_id', 'type': rec._fields['partner_id'].type, 'title': rec._fields['partner_id'].string,
                    'value': str(rec.partner_id.name) if rec.partner_id else ''}
            customer_account_id = {'key': 'customer_account_id', 'type': rec._fields['customer_account_id'].type, 'title': rec._fields['customer_account_id'].string,
                    'value': str(rec.customer_account_id.name) if rec.customer_account_id else ''}
            company_id = {'key': 'company_id', 'type': rec._fields['company_id'].type, 'title': rec._fields['company_id'].string,
                    'value': str(rec.company_id.name) if rec.company_id else ''}
            user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type, 'title': rec._fields['user_id'].string,
                    'value': str(rec.user_id.name) if rec.user_id else ''}
            team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type, 'title': rec._fields['team_id'].string,
                    'value': str(rec.team_id.name) if rec.team_id else ''}
            maintenance_list.append([id,name,maintenance_process_alias_id,maintenance_install_start_date,
                maintenance_install_end_date,title,reported_fault,service_request_id,parent_ticket_id,child_ticket_id,
                external_reference,service_category_id,service_type_id,child_ticket_type_id,product_id,stock_lot_id,
                categ_id,asset_tag_ids,product_code_no,cat_no,worksheet_id,origin,po_number,po_date,invoice_number,
                invoice_date,warranty_status,warranty_end_date,extended_warranty_status,extended_warranty_end_date,
                amc_status,amc_end_date,cmc_status,cmc_end_date,action_taken_site,partner_id,customer_account_id,
                company_id,user_id,team_id])
            maintenance_list_len = len(maintenance_list) - 1
            if rec.maintenance_state in ['new','rescheduled']:
                start_button = {'key': 'start_button', 'type': "button",
                                       'title': 'Start',
                                       'value': 'Start'}
                maintenance_list[maintenance_list_len].append(start_button)
            if rec.maintenance_state in ['started']:
                in_progress_button = {'key': 'in_progress_button', 'type': "button",
                                     'title': 'In progress',
                                     'value': 'In Progress'}
                maintenance_list[maintenance_list_len].append(in_progress_button)
            if rec.maintenance_state in ['approved','in_progress']:
                complete_button = {'key': 'complete_button', 'type': "button",
                                           'title': 'Complete',
                                           'value': 'Complete'}
                maintenance_list[maintenance_list_len].append(complete_button)


        if maintenance_list:
            return valid_response2(maintenance_list,filter_state,count, 'maintenance load successfully', 200)
        else:
            return valid_response2(maintenance_list,filter_state,count, 'there is no maintenance value', 200)

        # maintenance_obj = request.env['maintenance.request']
        # maintenance_value = maintenance_obj.sudo().search_read([('is_sr_maintenance', '=', True)], ['name', 'maintenance_process_alias_id','title','reported_fault','service_request_id',
        #                                                         'parent_ticket_id', 'child_ticket_id','external_reference','service_category_id','service_type_id',
        #                                                         'child_ticket_type_id','product_id','stock_lot_id','categ_id','asset_tag_ids','product_code_no',
        #                                                         'cat_no','worksheet_id','origin','po_number','warranty_status','amc_status','cmc_status',
        #                                                         'action_taken_site','partner_id','customer_account_id','company_id','user_id','team_id'
        #                                                         ])
        # for rec in maintenance_value:
        #     maintenance=maintenance_obj.sudo().browse(rec.get('id'))
        #     rec['maintenance_install_start_date'] = str(maintenance.maintenance_install_start_date)
        #     rec['maintenance_install_end_date']=str(maintenance.maintenance_install_end_date)
        #     rec['po_date'] = str(maintenance.po_date)
        #     rec['invoice_date']= str(maintenance.invoice_date)
        #     rec['extended_warranty_end_date']=str(maintenance.extended_warranty_end_date)
        #     rec['amc_end_date'] = str(maintenance.amc_end_date)
        #     rec['cmc_end_date'] = str(maintenance.cmc_end_date)
        #     rec['invoice_number'] = str(maintenance.invoice_number)
        #
        # if maintenance_value:
        #     return valid_response(maintenance_value, 'maintenance load successfully', 200)
        # else:
        #     return valid_response(maintenance_value, 'there is no maintenance value', 200)

    @validate_token
    @http.route("/api/get_maintenance_value/update", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_maintenance_value_update(self, **post):
        post = json.loads(request.httprequest.data)
        maintenance_id = post.get('maintenance_id')
        token = request.env['api.access_token'].search([('token', '=', post.get('access_token'))])
        user_tz = token.user_id.tz or 'UTC'
        local_tz = pytz.timezone(user_tz)
        start_button = post.get('start_button')
        in_progress = post.get('in_progress_button')
        complete_button = post.get('complete_button')
        maintenance_obj = request.env['maintenance.request']
        maintenance = maintenance_obj.sudo().browse(int(maintenance_id))
        message = ''
        try:
            if start_button and maintenance:
                maintenance.sudo().action_start_process()
                message = "start action completed"
            if in_progress and maintenance:
                maintenance.sudo().action_in_progress()
                message = "in progress completed"
            if complete_button and maintenance:
                message = "maintenance completed"
                maintenance.sudo().action_complete()
            if start_button or in_progress or complete_button:
                return valid_response([[{'maintenance_name': maintenance.name}]], message, 200)
            return invalid_response("there is no button selected","Please select any one button",400)
        except Exception as e:
            info = "There was a problem {}".format((e))
            error = "Something went wrong"
            _logger.error(info)
            return invalid_response(info, error, 403)