from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response,valid_response1,valid_response2
from odoo import http
from odoo.http import request
import json
import pytz
from datetime import datetime , timezone,timedelta
import logging
_logger = logging.getLogger(__name__)

class APIController(http.Controller):

    @validate_token
    @http.route("/api/get_installation_value", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_installation_value(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('@ /api/get_installation_value post :%s', post)
        limit = post.get('limit')
        next_count = post.get('next_count')
        search_value = post.get('search_value')
        installation_ids = post.get('ids')
        state_filter = post.get('state_filter')
        user = request.env.user.browse(int(post.get('uid')))
        user_tz = user.tz or 'UTC'
        local_tz = pytz.timezone(user_tz)
        uid = request.session.uid
        _logger.info('@user time zoneeeeeeeee :%s', user_tz)

        project_task_obj = request.env['project.task']
        Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
        CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
        Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
            'ppts_service_request.service_request_group_manager')
        National_Head = user.has_group('ppts_service_request.service_request_national_head')
        company_id = request.env.user.company_id.id
        domain = [('is_project_installation', '=', True),('active','=',True),('user_ids','=',request.env.user.id),
                  ('company_id','=',company_id)]
        if installation_ids:
            domain += [('id', 'in', list(installation_ids))]
        if search_value:
            domain+=[('name','ilike',search_value)]
        if state_filter and state_filter !='all':
            domain +=[('installation_state','=',state_filter)]

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

        count = project_task_obj.sudo().search_count(domain)
        installation_ids = project_task_obj.sudo().search(domain, offset=next_count, limit=limit,
                                                          order='name desc')

        state_value_all = dict(project_task_obj._fields['installation_state'].selection)
        filter_state = [{'id': field,
                         'value': state_value_all.get(field), }
                        for field in state_value_all]
        filter_state.insert(0, {'id': 'all', 'value': "ALL"})

        installation_list = []
        for rec in installation_ids:
            id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,'editable':False,
                  'required': rec._fields['id'].required,
                  'value': rec.id if rec.id else ''}

            name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,'editable':False,
                    'required': rec._fields['name'].required,
                    'value': rec.name if rec.name else ''}

            installation_state =  {'key': 'installation_state', 'type': rec._fields['installation_state'].type, 'title': rec._fields['installation_state'].string,'editable':False,
                    'required': rec._fields['installation_state'].required,
                    'value':dict(rec._fields['installation_state'].selection).get(rec.installation_state)}
            # INSTALLATION DETAILS
            installation_process_alias = {'key': 'installation_process_alias', 'type': rec._fields['installation_process_alias'].type, 'title': rec._fields['installation_process_alias'].string,'editable':False,
                    'required': rec._fields['installation_process_alias'].required,
                    'value': rec.installation_process_alias if rec.installation_process_alias else ''}
            installation_start_date = {'key': 'installation_start_date', 'type': rec._fields['installation_start_date'].type, 'title': rec._fields['installation_start_date'].string,'editable':False,
                    'required': rec._fields['installation_start_date'].required,
                    'value': str(rec.installation_start_date) if rec.installation_start_date else ''}
            installation_end_date = {'key': 'installation_end_date', 'type': rec._fields['installation_end_date'].type, 'title': rec._fields['installation_end_date'].string,'editable':False,
                     'required': rec._fields['installation_end_date'].required,
                    'value': str(rec.installation_end_date) if rec.installation_end_date else ''}
            installation_title = {'key': 'installation_title', 'type': rec._fields['installation_title'].type, 'title': rec._fields['installation_title'].string,'editable':False,
                    'required': rec._fields['installation_title'].required,
                    'value': rec.installation_title if rec.installation_title else ''}
            installation_service_category_id = {'key': 'installation_service_category_id', 'type': rec._fields['installation_service_category_id'].type, 'title': rec._fields['installation_service_category_id'].string,'editable':False,
                    'required': rec._fields['installation_service_category_id'].required,
                    'value': rec.installation_service_category_id.name if rec.installation_service_category_id else ''}
            installation_service_type_id = {'key': 'installation_service_type_id', 'type': rec._fields['installation_service_type_id'].type, 'title': rec._fields['installation_service_type_id'].string,'editable':False,
                    'required': rec._fields['installation_service_type_id'].required,
                    'value': rec.installation_service_type_id.name if rec.installation_service_type_id else ''}
            installation_parent_ticket_id = {'key': 'installation_parent_ticket_id', 'type': rec._fields['installation_parent_ticket_id'].type, 'title': rec._fields['installation_parent_ticket_id'].string,'editable':False,
                    'required': rec._fields['installation_parent_ticket_id'].required,
                    'value': rec.installation_parent_ticket_id.name if rec.installation_parent_ticket_id else '','id': rec.installation_parent_ticket_id.id if rec.installation_parent_ticket_id else ''}
            installation_child_ticket_id = {'key': 'installation_child_ticket_id', 'type': rec._fields['installation_child_ticket_id'].type, 'title': rec._fields['installation_child_ticket_id'].string,'editable':False,
                    'required': rec._fields['installation_child_ticket_id'].required,
                    'value': rec.installation_child_ticket_id.name if rec.installation_child_ticket_id else '','id': rec.installation_child_ticket_id.id if rec.installation_child_ticket_id else False}
            installation_child_ticket_type = {'key': 'installation_child_ticket_type', 'type': rec._fields['installation_child_ticket_type'].type, 'title': rec._fields['installation_child_ticket_type'].string,'editable':False,
                     'required': rec._fields['installation_child_ticket_type'].required,
                    'value': rec.installation_child_ticket_type.name if rec.installation_child_ticket_type else ''}
            # request_type_id = {'key': 'request_type_id', 'type': rec._fields['request_type_id'].type, 'title': rec._fields['request_type_id'].string,
            #         'value': rec.request_type_id.name if rec.request_type_id else ''}
            # approver_id = {'key': 'approver_id', 'type': rec._fields['approver_id'].type, 'title': rec._fields['approver_id'].string,
            #         'value': rec.approver_id.name if rec.approver_id else ''}
            # PRODUCT DETAILS
            installation_stock_lot_id = {'key': 'installation_stock_lot_id', 'type': rec._fields['installation_stock_lot_id'].type, 'title': rec._fields['installation_stock_lot_id'].string,'editable':False,
                    'required': rec._fields['installation_stock_lot_id'].required,
                    'value': rec.installation_stock_lot_id.name if rec.installation_stock_lot_id else ''}
            installation_categ_id = {'key': 'installation_categ_id', 'type': rec._fields['installation_categ_id'].type, 'title': rec._fields['installation_categ_id'].string,'editable':False,
                    'required': rec._fields['installation_categ_id'].required,
                    'value': rec.installation_categ_id.name if rec.installation_categ_id else ''}
            installation_product_serial = {'key': 'installation_product_serial', 'type': rec._fields['installation_product_serial'].type, 'title': rec._fields['installation_product_serial'].string,'editable':False if rec.installation_state != 'in_progress' else True,
                     'required': rec._fields['installation_product_serial'].required,
                    'value': rec.installation_product_serial if rec.installation_product_serial else ''}
            installation_product_code_no = {'key': 'installation_product_code_no', 'type': rec._fields['installation_product_code_no'].type, 'title': rec._fields['installation_product_code_no'].string,'editable':False if rec.installation_state != 'in_progress' else True,
                    'required': rec._fields['installation_product_code_no'].required,
                    'value': rec.installation_product_code_no if rec.installation_product_code_no else ''}
            installation_product_part = {'key': 'installation_product_part', 'type': rec._fields['installation_product_part'].type, 'title': rec._fields['installation_product_part'].string,'editable':False if rec.installation_state != 'in_progress' else True,
                     'required': rec._fields['installation_product_part'].required,
                    'value': rec.installation_product_part if rec.installation_product_part else ''}
            installation_tags = {'key': 'installation_tags', 'type': rec._fields['installation_tags'].type, 'title': rec._fields['installation_tags'].string,'editable':False,
                    'required': rec._fields['installation_tags'].required,
                    'value': [{'id':x.id,'value':x.name} for x in rec.installation_tags] if rec.installation_tags else ''}
            # CUSTOMER DETAILS
            installation_customer_id = {'key': 'installation_customer_id', 'type': rec._fields['installation_customer_id'].type, 'title': rec._fields['installation_customer_id'].string,'editable':False,
                     'required': rec._fields['installation_customer_id'].required,
                    'value': rec.installation_customer_id.name if rec.installation_customer_id else ''}
            installation_customer_account_id = {'key': 'installation_customer_account_id', 'type': rec._fields['installation_customer_account_id'].type, 'title': rec._fields['installation_customer_account_id'].string,'editable':False,
                    'required': rec._fields['installation_customer_account_id'].required,
                    'value': rec.installation_customer_account_id.name if rec.installation_customer_account_id else ''}
            company_id = {'key': 'company_id', 'type': rec._fields['company_id'].type, 'title': rec._fields['company_id'].string,'editable':False,
                     'required': rec._fields['company_id'].required,
                    'value': rec.company_id.name if rec.company_id else ''}
            user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type, 'title': rec._fields['user_id'].string,'editable':False,
                     'required': rec._fields['user_id'].required,
                    'value': rec.user_id.name if rec.user_id else ''}
            team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type, 'title': rec._fields['team_id'].string,'editable':False,
                     'required': rec._fields['team_id'].required,
                    'value': rec.team_id.name if rec.team_id else ''}
            installation_customer_po_number = {'key': 'installation_customer_po_number', 'type': rec._fields['installation_customer_po_number'].type, 'title': rec._fields['installation_customer_po_number'].string,'editable':False,
                    'required': rec._fields['installation_customer_po_number'].required,
                    'value': rec.installation_customer_po_number if rec.installation_customer_po_number else ''}
            installation_customer_po_date = {'key': 'installation_customer_po_date', 'type': rec._fields['installation_customer_po_date'].type, 'title': rec._fields['installation_customer_po_date'].string,'editable':False,
                    'required': rec._fields['installation_customer_po_date'].required,
                    'value': str(rec.installation_customer_po_date) if rec.installation_customer_po_date else ''}
            # OTHER INFORMATION
            installation_external_reference = {'key': 'installation_external_reference', 'type': rec._fields['installation_external_reference'].type, 'title': rec._fields['installation_external_reference'].string,'editable':False,
                    'required': rec._fields['installation_external_reference'].required,
                    'value': rec.installation_external_reference if rec.installation_external_reference else ''}
            installation_reported_fault = {'key': 'installation_reported_fault', 'type': rec._fields['installation_reported_fault'].type, 'title': rec._fields['installation_reported_fault'].string,'editable':False,
                    'required': rec._fields['installation_reported_fault'].required,
                    'value': rec.installation_reported_fault if rec.installation_reported_fault else ''}
            installation_origin = {'key': 'installation_origin', 'type': rec._fields['installation_origin'].type, 'title': rec._fields['installation_origin'].string,'editable':False,
                     'required': rec._fields['installation_origin'].required,
                    'value': rec.installation_origin if rec.installation_origin else ''}
            install_status = {'key': 'install_status', 'type': rec._fields['install_status'].type, 'title': rec._fields['install_status'].string,'editable':False,
                    'required': rec._fields['install_status'].required,
                    'value': dict(rec._fields['install_status'].selection).get(rec.install_status) if rec.install_status else ''}
            worksheet_id = {'key': 'worksheet_id', 'type': rec._fields['worksheet_id'].type, 'title': rec._fields['worksheet_id'].string,'editable':False,
                    'required': rec._fields['worksheet_id'].required,
                    'value': rec.worksheet_id.title if rec.worksheet_id else ''}
            installation_invoice_number = {'key': 'installation_invoice_number', 'type': rec._fields['installation_invoice_number'].type, 'title': rec._fields['installation_invoice_number'].string,'editable':False if rec.installation_state != 'in_progress' else True,
                    'required': rec._fields['installation_invoice_number'].required,
                    'value': rec.installation_invoice_number if rec.installation_invoice_number else ''}
            installation_invoice_date = {'key': 'installation_invoice_date', 'type': rec._fields['installation_invoice_date'].type, 'title': rec._fields['installation_invoice_date'].string,'editable':False if rec.installation_state != 'in_progress' else True,
                    'required': rec._fields['installation_invoice_date'].required,
                    'value': str(rec.installation_invoice_date) if rec.installation_invoice_date else ''}
            installation_delivery_number_ids = request.env['stock.picking'].sudo().search([('id', 'in', rec.stock_picking_ids)])
            installation_delivery_number = {'key': 'installation_delivery_number',
                                            'type': rec._fields['installation_delivery_number'].type,
                                            'title': rec._fields['installation_delivery_number'].string,'editable':False if rec.installation_state != 'in_progress' else True,
                                            'required': rec._fields['installation_delivery_number'].required,
                                            # 'value': rec.installation_delivery_number.name if rec.installation_delivery_number else '',
                                            'value': [{'id':fields.id,'value':fields.name} for fields in installation_delivery_number_ids] if rec.installation_state == 'in_progress' else rec.installation_delivery_number.name or ''}
            installation_order_date = {'key': 'installation_order_date',
                                         'type': rec._fields['installation_order_date'].type,
                                         'title': rec._fields['installation_order_date'].string,
                                         'editable': False if rec.installation_state != 'in_progress' else True,
                                         'required': rec._fields['installation_order_date'].required,
                                         'value': str(
                                             rec.installation_order_date.astimezone(local_tz).replace(tzinfo=None)) if rec.installation_order_date else ''}

            # installation_order_date = {'key': 'installation_order_date', 'type': rec._fields['installation_order_date'].type, 'title': rec._fields['installation_order_date'].string,'editable':False if rec.installation_state != 'in_progress' else True,
            #         'value': str(rec.installation_order_date.astimezone(local_tz).replace(tzinfo=None)) if rec.installation_order_date else ''}

            # if rec.installation_order_date:
            #     _logger.info('@user time installation_order_date :%s',str(rec.installation_order_date.astimezone(local_tz).replace(tzinfo=None)))

            button_value = ''
            if rec.installation_state == 'new':
                button_value += 'Start'
            elif rec.installation_state == 'started':
                button_value += 'In Progress'
            elif rec.installation_state == 'in_progress':
                button_value += 'Complete'
            installation_button = {'key': 'installation_button', 'type': "button",
                                   'title': 'Installation State key',
                                   'value': button_value}
            #     installation_list.append([id,name,installation_button,installation_state,installation_process_alias,installation_start_date,installation_end_date,
            #         installation_title,installation_service_category_id,installation_service_type_id,installation_parent_ticket_id,
            #         installation_child_ticket_id,installation_child_ticket_type,
            #         # request_type_id,approver_id,
            #         installation_stock_lot_id,installation_categ_id,installation_product_serial,installation_product_code_no,
            #         installation_product_part,installation_tags,installation_customer_id,installation_customer_account_id,
            #         company_id,user_id,team_id,installation_customer_po_number,installation_customer_po_date,installation_external_reference,
            #         installation_reported_fault,installation_origin,install_status,worksheet_id,installation_invoice_number,installation_invoice_date,
            #         installation_delivery_number,installation_order_date,
            #                               ])
            # else:
            installation_list.append([id, name, installation_state, installation_process_alias,
                                      installation_start_date, installation_end_date,
                                      installation_title, installation_service_category_id,
                                      installation_service_type_id, installation_parent_ticket_id,
                                      installation_child_ticket_id, installation_child_ticket_type,
                                      # request_type_id,approver_id,
                                      installation_stock_lot_id, installation_categ_id, installation_product_serial,
                                      installation_product_code_no,
                                      installation_product_part, installation_tags, installation_customer_id,
                                      installation_customer_account_id,
                                      company_id, user_id, team_id, installation_customer_po_number,
                                      installation_customer_po_date, installation_external_reference,
                                      installation_reported_fault, installation_origin, install_status,
                                      worksheet_id, installation_invoice_number, installation_invoice_date,
                                      installation_delivery_number, installation_order_date,
                                      ])
            print(len(installation_list)-1,'len')
            installation_list_len = len(installation_list)-1
            if button_value:
                installation_list[installation_list_len].append(installation_button)
            if rec.installation_state in ['started','in_progress']:
                installation_list[installation_list_len].append({'key': 'installation_cancel_button', 'type': "button",
                                                                   'title': 'Installation Cancel key',
                                                                   'value': 'Cancel',})
            if rec.installation_state in ['in_progress']:
                installation_list[installation_list_len].append({'key': 'installation_on_hold_button', 'type': "button",
                                                                 'title': 'Installation on hold key',
                                                                 'value': 'On Hold',
                                                                 })
            if rec.installation_state == 'on_hold':
                installation_list[installation_list_len].append({'key': 'installation_resume_button', 'type': "button",
                                                                 'title': 'Installation Resume key',
                                                                 'value': 'Resume',
                                                                 })
        _logger.info('@ /api/get_installation_value installation_list:%s', installation_list)
        if installation_list:
            return valid_response2(installation_list,filter_state,count, 'Installation load successfully', 200)
        else:
            return valid_response2(installation_list,filter_state,count, 'there is no installation value', 200)

    @validate_token
    @http.route("/api/get_installation_value/update", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_installation_value_update(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('@ /api/get_installation_value/update valuesssssss:%s', post)
        installation_id = post.get('installation_id')
        token= request.env['api.access_token'].search([('token','=',post.get('access_token'))])
        user_tz = token.user_id.tz or 'UTC'
        local_tz = pytz.timezone(user_tz)
        start_button = post.get('start_button')
        in_progress = post.get('in_progress_button')
        complete_button = post.get('complete_button')
        action_cancel_installation = post.get('action_cancel_installation')
        installation_on_hold_button = post.get('installation_on_hold_button')
        installation_resume_button = post.get('installation_resume_button')

        project_task_obj = request.env['project.task']
        project_task_id = project_task_obj.sudo().browse(int(installation_id))
        message = ''
        try:
            if action_cancel_installation and project_task_id:
                project_task_id.sudo().action_cancel_installation()
            if installation_on_hold_button and project_task_id:
                project_task_id.sudo().update({'on_hold_reason': str(post.get('on_hold_reason')) if post.get('on_hold_reason') else '','installation_state':'on_hold'})
                # project_task_id.sudo().installation_state = 'on_hold'
            if installation_resume_button and project_task_id:
                project_task_id.sudo().action_resume()
            if start_button and project_task_id:
                project_task_id.sudo().action_start_installation()
                message="start action completed"
            if in_progress and project_task_id:
                project_task_id.sudo().action_in_progress_installation()
                message = "in progress completed"
            if complete_button and project_task_id:
                # start = datetime.strptime(str('2023-04-12T20:30:00.000'),'%Y-%m-%dT%H:%M:%S.%f')
                # # end = datetime.strptime(str(start),'%Y-%m-%d')
                # _logger.error('@ /api/get_installation_value/update startttt:%s', start)
                # format = "%Y-%m-%dT%H:%M:%S.%f"
                # dt_str = str(post.get('installation_order_date'))
                # print(dt_str,'dt_strrrr')
                # local_dt = datetime.strptime(dt_str, format)
                # print(local_dt,'local dttttt')
                # print(pytz.UTC,'UTCCC')
                # dt_utc = local_dt.astimezone(pytz.utc).replace(tzinfo=None)
                # print('Datetime in UTC Time zone: ', dt_utc - timedelta(hours=5,minutes=30))
                values = {
                    'installation_product_serial' : str(post.get('installation_product_serial')) if post.get('installation_product_serial') else '',
                    'installation_product_code_no' :str(post.get('installation_product_code_no')) if post.get('installation_product_code_no') else '',
                    'installation_product_part' : str(post.get('installation_product_part')) if post.get('installation_product_part') else '',
                    'installation_invoice_number' : str(post.get('installation_invoice_number')) if post.get('installation_invoice_number') else '',
                    'installation_invoice_date' : datetime.strptime(str(post.get('installation_invoice_date')),'%Y-%m-%dT%H:%M:%S.%f') if post.get('installation_invoice_date') else '',
                    'installation_delivery_number' : int(post.get('installation_delivery_number')) if post.get('installation_delivery_number') else False,
                    'installation_order_date' : datetime.strptime(str(post.get('installation_order_date')),'%Y-%m-%dT%H:%M:%S.%f').astimezone(pytz.utc).replace(tzinfo=None) - timedelta(hours=5,minutes=30) if post.get('installation_order_date') else '',
                }
                _logger.error('@ installlation valuessssssss:%s', values)
                project_task_id.sudo().update(values)
                message = "installation completed"
                if project_task_id.installation_stock_lot_id and project_task_id.installation_end_date and project_task_id.installation_start_date:
                    project_task_id.sudo().action_complete_installation_wiz()
                else:
                    message = "Installation dates is not available !"

            if start_button or in_progress or complete_button or action_cancel_installation or installation_on_hold_button or installation_resume_button:
                return valid_response([[{'installation_name': project_task_id.name}]],message, 200)
        except Exception as e:
            info = "There was a problem {}".format((e))
            error = "Something went wrong"
            _logger.error(info)
            return invalid_response(info, error, 403)


        # installation_value = project_task_obj.sudo().search_read([('is_project_installation', '=', True),('active','=',True)], ['name', 'installation_process_alias','installation_title',
        #                                                         'installation_service_category_id','installation_service_type_id','installation_parent_ticket_id',
        #                                                         'installation_child_ticket_id','installation_child_ticket_type','installation_stock_lot_id',
        #                                                         'installation_categ_id','installation_product_serial','installation_product_code_no','installation_product_part',
        #                                                         'installation_tags','installation_customer_id','installation_customer_account_id','company_id','user_id','team_id',
        #                                                         'installation_customer_po_number','installation_external_reference','installation_reported_fault','installation_origin',
        #                                                         'install_status','worksheet_id','installation_invoice_number','installation_delivery_number',
        #                                                         ])
        # for rec in installation_value:
        #     installation=project_task_obj.sudo().browse(rec.get('id'))
        #     rec['installation_start_date'] = str(installation.installation_start_date)
        #     rec['installation_end_date']=str(installation.installation_end_date)
        #     rec['installation_customer_po_date'] =str(installation.installation_customer_po_date)
        #     rec['installation_invoice_date'] = str(installation.installation_invoice_date)
        #     rec['installation_order_date'] = str(installation.installation_order_date)
        #
        # if installation_value:
        #     return valid_response(installation_value, 'Installation load successfully', 200)
        # else:
        #     return valid_response(installation_value, 'there is no installation value', 200)