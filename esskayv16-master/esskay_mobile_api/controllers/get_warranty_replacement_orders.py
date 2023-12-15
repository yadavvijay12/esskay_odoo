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
    @http.route("/api/get_warranty_replacement_value", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_warranty_replacement_value(self, **post,):
        post = json.loads(request.httprequest.data)
        _logger.info('@ /api/get_warranty_replacement_value:%s', post)
        limit = post.get('limit')
        next_count = post.get('next_count')
        search_value = post.get('search_value')
        warranty_replacement_id=post.get('ids')
        state_filter = post.get('state_filter')
        user = request.env.user.browse(post.get('uid'))
        warranty_replacement = request.env['sale.order']
        company_id = request.env.user.company_id.id
        uid = request.env.uid
        user = request.env.user
        user_tz = user.tz or 'UTC'
        local_tz = pytz.timezone(user_tz)
        domain = [('is_replacement_order', '=', True),('company_id','=',company_id),('user_id','=',user.id),]
        if warranty_replacement_id:
            domain += [('id', 'in', list(warranty_replacement_id))]
        if search_value:
            domain += [('name','ilike',search_value)]
        if state_filter and state_filter !='all':
            domain +=[('wr_state','=',state_filter)]
        count = warranty_replacement.sudo().search_count(domain)
        warranty_replacement_ids = warranty_replacement.sudo().search(domain, offset=next_count, limit=limit,order='name desc')

        state_value_all = dict(warranty_replacement._fields['wr_state'].selection)
        filter_state = [{'id': field,
                         'value': state_value_all.get(field), }
                        for field in state_value_all]
        filter_state.insert(0, {'id': 'all', 'value': "ALL"})

        warranty_replacement_list = []
        for rec in warranty_replacement_ids:
            id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                  'value': rec.id if rec.id else '',
                  'editable':False}
            name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                    'value': rec.name if rec.name else '',
                    'editable':False}
            wr_state = { 'key':'wr_state','type': rec._fields['wr_state'].type,'title': rec._fields['wr_state'].string,
                         'value': dict(rec._fields['wr_state'].selection).get(rec.wr_state),
                         'editable': False
                        }
            # WARRANTY REPLACEMENT DETAILS
            wr_process_alias_id = {'key': 'wr_process_alias_id', 'type': rec._fields['wr_process_alias_id'].type, 'title': rec._fields['wr_process_alias_id'].string,
                    'value': rec.wr_process_alias_id if rec.wr_process_alias_id else '',
                    'editable':False}
            wr_install_start_date = {'key': 'wr_install_start_date', 'type': rec._fields['wr_install_start_date'].type, 'title': rec._fields['wr_install_start_date'].string,
                    'value': str(rec.wr_install_start_date) if rec.wr_install_start_date else '',
                     'editable':False}
            wr_install_end_date = {'key': 'wr_install_end_date', 'type': rec._fields['wr_install_end_date'].type, 'title': rec._fields['wr_install_end_date'].string,
                    'value': str(rec.wr_install_end_date) if rec.wr_install_end_date else '',
                    'editable':False}
            reported_fault = {'key': 'reported_fault', 'type': rec._fields['reported_fault'].type, 'title': rec._fields['reported_fault'].string,
                    'value': str(rec.reported_fault) if rec.reported_fault else '',
                    'editable': False}
            parent_ticket_id = {'key': 'parent_ticket_id', 'type': rec._fields['parent_ticket_id'].type, 'title': rec._fields['parent_ticket_id'].string,
                    'value': str(rec.parent_ticket_id.name) if rec.parent_ticket_id else '',
                    'editable':False}
            child_ticket_id = {'key': 'child_ticket_id', 'type': rec._fields['child_ticket_id'].type, 'title': rec._fields['child_ticket_id'].string,
                    'value': str(rec.child_ticket_id.name) if rec.child_ticket_id else '',
                               'editable':False}
            external_reference = {'key': 'external_reference', 'type': rec._fields['external_reference'].type, 'title': rec._fields['external_reference'].string,
                    'value': str(rec.external_reference) if rec.external_reference else '',
                                  'editable':False}
            service_category_id = {'key': 'service_category_id', 'type': rec._fields['service_category_id'].type, 'title': rec._fields['service_category_id'].string,
                    'value': str(rec.service_category_id.name) if rec.service_category_id else '',
                                   'editable':False}
            service_type_id = {'key': 'service_type_id', 'type': rec._fields['service_type_id'].type, 'title': rec._fields['service_type_id'].string,
                    'value': str(rec.service_type_id.name) if rec.service_type_id else '',
                               'editable':False}
            child_ticket_type_id = {'key': 'child_ticket_type_id', 'type': rec._fields['child_ticket_type_id'].type, 'title': rec._fields['child_ticket_type_id'].string,
                    'value': str(rec.child_ticket_type_id.name) if rec.child_ticket_type_id else '',
                                    'editable':False}
            # OTHER INFORMATION
            date_order = {'key': 'date_order', 'type': rec._fields['date_order'].type, 'title': rec._fields['date_order'].string,
                    'value': str(rec.date_order.astimezone(local_tz).replace(tzinfo=None).strftime('%Y-%m-%d %I:%M %p')) if rec.date_order else '',
                          'editable':False}
            pricelist_id = {'key': 'pricelist_id', 'type': rec._fields['pricelist_id'].type, 'title': rec._fields['pricelist_id'].string,
                    'value': str(rec.pricelist_id.name) if rec.pricelist_id else '',
                            'editable':False}
            invoice_number = {'key': 'invoice_number', 'type': rec._fields['invoice_number'].type, 'title': rec._fields['invoice_number'].string,
                    'value': str(rec.invoice_number) if rec.invoice_number else '',
                              'editable':False}
            invoice_date = {'key': 'invoice_date', 'type': rec._fields['invoice_date'].type, 'title': rec._fields['invoice_date'].string,
                    'value': str(rec.invoice_date) if rec.invoice_date else '',
                            'editable':False}
            delivery_number = {'key': 'delivery_number', 'type': rec._fields['delivery_number'].type, 'title': rec._fields['delivery_number'].string,
                    'value': str(rec.delivery_number.name) if rec.delivery_number else '',
                               'editable':False}
            delivery_order_date = {'key': 'delivery_order_date', 'type': rec._fields['delivery_order_date'].type, 'title': rec._fields['delivery_order_date'].string,
                    'value': str(rec.delivery_order_date) if rec.delivery_order_date else '',
                                   'editable':False}
            billing_type = {'key': 'billing_type', 'type': rec._fields['billing_type'].type, 'title': rec._fields['billing_type'].string,
                    'value': str(rec.billing_type) if rec.billing_type else '',
                            'editable':False}
            payment_term_id = {'key': 'payment_term_id', 'type': rec._fields['payment_term_id'].type, 'title': rec._fields['payment_term_id'].string,
                    'value': str(rec.payment_term_id.name) if rec.payment_term_id else '',
                               'editable':False}
            # CUSTOMER INFORMATION
            partner_id = {'key': 'partner_id', 'type': rec._fields['partner_id'].type, 'title': rec._fields['partner_id'].string,
                    'value': str(rec.partner_id.name) if rec.partner_id else '',
                          'editable':False}
            partner_invoice_id = {'key': 'partner_invoice_id', 'type': rec._fields['partner_invoice_id'].type, 'title': rec._fields['partner_invoice_id'].string,
                    'value': str(rec.partner_invoice_id.name) if rec.partner_invoice_id else '',
                                  'editable':False}
            partner_shipping_id = {'key': 'partner_shipping_id', 'type': rec._fields['partner_shipping_id'].type, 'title': rec._fields['partner_shipping_id'].string,
                    'value': str(rec.partner_shipping_id.name) if rec.partner_shipping_id else '',
                                   'editable':False}
            company_id = {'key': 'company_id', 'type': rec._fields['company_id'].type, 'title': rec._fields['company_id'].string,
                    'value': str(rec.company_id.name) if rec.company_id else '',
                          'editable':False}
            team_id = {'key': 'team_id', 'type': rec._fields['team_id'].type, 'title': rec._fields['team_id'].string,
                    'value': str(rec.team_id.name) if rec.team_id else '',
                       'editable':False}
            user_id = {'key': 'user_id', 'type': rec._fields['user_id'].type, 'title': rec._fields['user_id'].string,
                    'value': str(rec.user_id.name) if rec.user_id else '',
                       'editable':False}
            customer_account_id = {'key': 'customer_account_id', 'type': rec._fields['customer_account_id'].type, 'title': rec._fields['customer_account_id'].string,
                    'value': str(rec.customer_account_id.name) if rec.customer_account_id else '',
                                   'editable':False}
            tag_ids = {'key': 'tag_ids', 'type': rec._fields['tag_ids'].type, 'title': rec._fields['tag_ids'].string,
                    'value': [{'id':x.id,'value':x.name} for x in rec.tag_ids] if rec.tag_ids else '',
                       'editable':False}
            install_status = {'key': 'install_status', 'type': rec._fields['install_status'].type, 'title': rec._fields['install_status'].string,
                    'value': dict(rec._fields['install_status'].selection).get(rec.install_status) if rec.install_status else '',
                              'editable':False}
            worksheet_id = {'key': 'worksheet_id', 'type': rec._fields['worksheet_id'].type, 'title': rec._fields['worksheet_id'].string,
                    'value': str(rec.worksheet_id.title) if rec.worksheet_id else '',
                            'editable':False}
            origin = {'key': 'origin', 'type': rec._fields['origin'].type, 'title': rec._fields['origin'].string,
                    'value': str(rec.origin) if rec.origin else '',
                      'editable':False}
            # PRODUCT DETAILS
            product_serial_no = {'key': 'product_serial_no', 'type': rec._fields['product_serial_no'].type, 'title': rec._fields['product_serial_no'].string,
                    'value': str(rec.product_serial_no) if rec.product_serial_no else '',
                                 'editable':False}
            product_code_no = {'key': 'product_code_no', 'type': rec._fields['product_code_no'].type, 'title': rec._fields['product_code_no'].string,
                    'value': str(rec.product_code_no) if rec.product_code_no else '',
                               'editable':False}
            product_part_no = {'key': 'product_part_no', 'type': rec._fields['product_part_no'].type, 'title': rec._fields['product_part_no'].string,
                    'value': str(rec.product_part_no) if rec.product_part_no else '',
                               'editable':False}
            categ_id = {'key': 'categ_id', 'type': rec._fields['categ_id'].type, 'title': rec._fields['categ_id'].string,
                    'value': str(rec.categ_id.name) if rec.categ_id else '',
                        'editable':False}
            po_number = {'key': 'po_number', 'type': rec._fields['po_number'].type, 'title': rec._fields['po_number'].string,
                    'value': str(rec.po_number) if rec.po_number else '',
                         'editable':False}
            po_date = {'key': 'po_date', 'type': rec._fields['po_date'].type, 'title': rec._fields['po_date'].string,
                    'value': str(rec.po_date) if rec.po_date else '',
                       'editable':False}
            product_serial_number = {'key': 'product_serial_number', 'type': rec._fields['product_serial_number'].type, 'title': rec._fields['product_serial_number'].string,
                    'value': str(rec.product_serial_number) if rec.product_serial_number else '',
                    'editable': False if rec.wr_state != 'new' else True,}
            product_part_number = {'key': 'product_part_number', 'type': rec._fields['product_part_number'].type, 'title': rec._fields['product_part_number'].string,
                    'value': str(rec.product_part_number) if rec.product_part_number else '',
                    'editable': False if rec.wr_state != 'new' else True,}
            product_part_code = {'key': 'product_part_code', 'type': rec._fields['product_part_code'].type, 'title': rec._fields['product_part_code'].string,
                    'value': str(rec.product_part_code) if rec.product_part_code else '',
                     'editable': False if rec.wr_state != 'new' else True,}

            warranty_replacement_list.append([id,name,wr_state,wr_process_alias_id,wr_install_start_date,wr_install_end_date,reported_fault,
                    parent_ticket_id,child_ticket_id,external_reference,service_category_id,service_type_id,child_ticket_type_id,
                    date_order,pricelist_id,invoice_number,invoice_date,delivery_number,delivery_order_date,billing_type,
                    payment_term_id,partner_id,partner_invoice_id,partner_shipping_id,company_id,team_id,user_id,
                    customer_account_id,tag_ids,install_status,worksheet_id,origin,product_serial_no,product_code_no,
                    product_part_no,categ_id,po_number,po_date,product_serial_number,product_part_number,product_part_code])
            warranty_replacement_list_len = len(warranty_replacement_list) - 1
            if rec.wr_state in ['new']:
                action_start_wr_process = {'key': 'action_start_wr_process', 'type': "button",
                                                                   'title': 'Started',
                                                                   'value': 'Started',}
                warranty_replacement_list[warranty_replacement_list_len].append(action_start_wr_process)
            if rec.wr_state in ['start'] :
                action_wr_in_progress = {'key': 'action_wr_in_progress', 'type': "button",
                                                                   'title': 'In Progress',
                                                                   'value': 'In Progress',}
                warranty_replacement_list[warranty_replacement_list_len].append(action_wr_in_progress)
            if rec.wr_state in ['approved'] and rec.is_send_for_approvals or rec.wr_state in ['in_progress'] and rec.is_send_for_approvals == False:
                action_wr_complete = {'key': 'action_wr_complete', 'type': "button",
                                         'title': 'Complete',
                                         'value': 'Complete' }
                warranty_replacement_list[warranty_replacement_list_len].append(action_wr_complete)

        if warranty_replacement_list:
            return valid_response2(warranty_replacement_list,filter_state, count, 'Warranty Replacement Orders load successfully', 200)
        else:
            return valid_response2(warranty_replacement_list,filter_state, count, 'There is no record in Warranty Replacement Orders', 200)


    @validate_token
    @http.route("/api/get_warranty_replacement_value/update", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_warranty_replacement_value_update(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('@ /api/get_warranty_replacement_value/update:%s', post)
        wr_id = post.get('wr_id')
        action_start_wr_process = post.get('action_start_wr_process')
        action_wr_in_progress = post.get('action_wr_in_progress')
        action_wr_complete = post.get('action_wr_complete')

        sale_order_obj = request.env['sale.order']
        sale_order_id = sale_order_obj.sudo().browse(int(wr_id))
        message = ''
        try:
            if action_start_wr_process and sale_order_id:
                vals={
                    'product_serial_number': str(post.get('product_serial_number')) if post.get(
                        'product_serial_number') else '',
                    'product_part_number': str(post.get('product_part_number')) if post.get(
                        'product_part_number') else '',
                    'product_part_code': str(post.get('product_part_code')) if post.get(
                        'product_part_code') else '',
                }
                _logger.error('@ get_warranty_replacement_value:%s', vals)
                sale_order_id.sudo().update(vals)
                message = "start process completed"
                sale_order_id.sudo().action_start_wr_process()
            if action_wr_in_progress and sale_order_id:
                sale_order_id.sudo().action_wr_in_progress()
                message = "start process completed"
            if action_wr_complete and sale_order_id:
                sale_order_id.sudo().action_wr_complete()
                message = "completed successfully"
            if action_start_wr_process or action_wr_in_progress or action_wr_complete:
                return valid_response([[{'warranty_replacement_name': sale_order_id.name}]], message, 200)
        except Exception as e:
            info = "There was a problem {}".format((e))
            error = "Something went wrong\n {}".format(info)
            _logger.error(info)
            return invalid_response(info, error, 403)