from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token,magic_fields
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response,valid_response1
from odoo import http
from odoo.http import request
import json
from bs4 import BeautifulSoup

class APIController(http.Controller):

    @validate_token
    @http.route("/api/get_asset_with_lot_num", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_asset_with_lot_num_value(self, **post, ):
        stock_lot_obj = request.env['stock.lot']
        post = json.loads(request.httprequest.data)
        limit = post.get('limit')
        next_count = post.get('next_count')
        search_value = post.get('search_value')
        domain = [('active','=',True),('product_id.tracking', '=', 'lot'),('is_lot','=','True')]
        if search_value:
            domain += [('name', 'ilike', search_value)]
        count = stock_lot_obj.sudo().search_count(domain)
        stock_lot_ids =  stock_lot_obj.sudo().search(domain,offset=next_count , limit=limit , order='name ASC')
        stock_lot_list=[]
        for rec in stock_lot_ids:
            id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                  'value': rec.id if rec.id else ''}
            name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                  'value': rec.name if rec.name else ''}
            customer_id = {'key': 'customer_id', 'type': rec._fields['customer_id'].type, 'title': rec._fields['customer_id'].string,
                  'value': rec.customer_id.name if rec.customer_id else ''}
            customer_account = {'key': 'customer_account', 'type': rec._fields['customer_account'].type, 'title': rec._fields['customer_account'].string,
                  'value': rec.customer_account.name if rec.customer_account else ''}
            external_id = {'key': 'external_id', 'type': rec._fields['external_id'].type, 'title': rec._fields['external_id'].string,
                  'value': rec.external_id if rec.external_id else ''}
            product_id = {'key': 'product_id', 'type': rec._fields['product_id'].type, 'title': rec._fields['product_id'].string,
                  'value': rec.product_id.name if rec.product_id else ''}
            product_price = {'key': 'product_price', 'type': rec._fields['product_price'].type, 'title': rec._fields['product_price'].string,
                  'value': rec.product_price if rec.product_price else ''}
            product_qty = {'key': 'product_qty', 'type': rec._fields['product_qty'].type, 'title': rec._fields['product_qty'].string,
                  'value': rec.product_qty if rec.product_qty else ''}
            product_uom_id = {'key': 'product_uom_id', 'type': rec._fields['product_uom_id'].type, 'title': rec._fields['product_uom_id'].string,
                  'value': rec.product_uom_id.name if rec.product_uom_id else ''}
            ref = {'key': 'ref', 'type': rec._fields['ref'].type, 'title': rec._fields['ref'].string,
                  'value': rec.ref if rec.ref else ''}
            company_id = {'key': 'company_id', 'type': rec._fields['company_id'].type, 'title': rec._fields['company_id'].string,
                  'value': rec.company_id.name if rec.company_id else ''}
            custom_sale_order = {'key': 'custom_sale_order', 'type': rec._fields['custom_sale_order'].type, 'title': rec._fields['custom_sale_order'].string,
                  'value': rec.custom_sale_order.name if rec.custom_sale_order else ''}
            contract_flow_id = {'key': 'contract_flow_id', 'type': rec._fields['contract_flow_id'].type, 'title': rec._fields['contract_flow_id'].string,
                  'value': rec.contract_flow_id.name if rec.contract_flow_id else ''}
            asset_tag_ids = {'key': 'asset_tag_ids', 'type': rec._fields['asset_tag_ids'].type, 'title': rec._fields['asset_tag_ids'].string,
                  'value': [{'id':x.id,'value':x.name} for x in rec.asset_tag_ids] if rec.asset_tag_ids else ''}
            asset_id_label = {'key': 'asset_id_label', 'type': rec._fields['asset_id_label'].type, 'title': rec._fields['asset_id_label'].string,
                  'value': rec.asset_id_label if rec.asset_id_label else ''}
            service_support_commitment = {'key': 'service_support_commitment', 'type': rec._fields['service_support_commitment'].type, 'title': rec._fields['service_support_commitment'].string,
                  'value': rec.service_support_commitment if rec.service_support_commitment else ''}
            asset_location_id = {'key': 'asset_location_id', 'type': rec._fields['asset_location_id'].type, 'title': rec._fields['asset_location_id'].string,
                  'value': rec.asset_location_id.name if rec.asset_location_id else ''}
            lattitude = {'key': 'lattitude', 'type': rec._fields['lattitude'].type, 'title': rec._fields['lattitude'].string,
                  'value': rec.lattitude if rec.lattitude else ''}
            longitutde = {'key': 'longitutde', 'type': rec._fields['longitutde'].type, 'title': rec._fields['longitutde'].string,
                  'value': rec.longitutde if rec.longitutde else ''}
            faulty_sticker = {'key': 'faulty_sticker', 'type': rec._fields['faulty_sticker'].type, 'title': rec._fields['faulty_sticker'].string,
                  'value': rec.faulty_sticker if rec.faulty_sticker else ''}
            rsp_name = {'key': 'rsp_name', 'type': rec._fields['rsp_name'].type, 'title': rec._fields['rsp_name'].string,
                  'value': rec.rsp_name if rec.rsp_name else ''}
            replacement_for = {'key': 'replacement_for', 'type': rec._fields['replacement_for'].type, 'title': rec._fields['replacement_for'].string,
                  'value': rec.replacement_for if rec.replacement_for else ''}
            asset_category_id = {'key': 'asset_category_id', 'type': rec._fields['asset_category_id'].type, 'title': rec._fields['asset_category_id'].string,
                  'value': rec.asset_category_id.name if rec.asset_category_id else ''}
            asset_type_id = {'key': 'asset_type_id', 'type': rec._fields['asset_type_id'].type, 'title': rec._fields['asset_type_id'].string,
                  'value': rec.asset_type_id.name if rec.asset_type_id else ''}
            product_types_id = {'key': 'product_types_id', 'type': rec._fields['product_types_id'].type, 'title': rec._fields['product_types_id'].string,
                  'value': rec.product_types_id.name if rec.product_types_id else ''}
            asset_id_allias = {'key': 'asset_id_allias', 'type': rec._fields['asset_id_allias'].type, 'title': rec._fields['asset_id_allias'].string,
                  'value': rec.asset_id_allias if rec.asset_id_allias else ''}
            invoice_number = {'key': 'invoice_number', 'type': rec._fields['invoice_number'].type, 'title': rec._fields['invoice_number'].string,
                  'value': rec.invoice_number if rec.invoice_number else ''}
            unit_type_id = {'key': 'unit_type_id', 'type': rec._fields['unit_type_id'].type, 'title': rec._fields['unit_type_id'].string,
                  'value': rec.unit_type_id if rec.unit_type_id else ''}
            industry_id = {'key': 'industry_id', 'type': rec._fields['industry_id'].type, 'title': rec._fields['industry_id'].string,
                  'value': rec.industry_id.name if rec.industry_id else ''}
            hardware_version = {'key': 'hardware_version', 'type': rec._fields['hardware_version'].type, 'title': rec._fields['hardware_version'].string,
                  'value': rec.hardware_version if rec.hardware_version else ''}
            software_version = {'key': 'software_version', 'type': rec._fields['software_version'].type, 'title': rec._fields['software_version'].string,
                  'value': rec.software_version if rec.software_version else ''}
            mc_skt = {'key': 'mc_skt', 'type': rec._fields['mc_skt'].type, 'title': rec._fields['mc_skt'].string,
                  'value': rec.mc_skt if rec.mc_skt else ''}
            product_eol = {'key': 'product_eol', 'type': rec._fields['product_eol'].type, 'title': rec._fields['product_eol'].string,
                  'value': str(rec.product_eol) if rec.product_eol else ''}
            product_eosl = {'key': 'product_eosl', 'type': rec._fields['product_eosl'].type, 'title': rec._fields['product_eosl'].string,
                  'value': str(rec.product_eosl) if rec.product_eosl else ''}
            custom_sale_order_date = {'key': 'custom_sale_order_date', 'type': rec._fields['custom_sale_order_date'].type, 'title': rec._fields['custom_sale_order_date'].string,
                  'value': str(rec.custom_sale_order_date) if rec.custom_sale_order_date else ''}
            warranty_start_date = {'key': 'warranty_start_date', 'type': rec._fields['warranty_start_date'].type, 'title': rec._fields['warranty_start_date'].string,
                  'value': str(rec.warranty_start_date) if rec.warranty_start_date else ''}
            warranty_end_date = {'key': 'warranty_end_date', 'type': rec._fields['warranty_end_date'].type, 'title': rec._fields['warranty_end_date'].string,
                  'value': str(rec.warranty_end_date) if rec.warranty_end_date else ''}
            extended_warranty_start_date = {'key': 'extended_warranty_start_date', 'type': rec._fields['extended_warranty_start_date'].type, 'title': rec._fields['extended_warranty_start_date'].string,
                  'value': str(rec.extended_warranty_start_date) if rec.extended_warranty_start_date else ''}
            extended_warranty_end_date = {'key': 'extended_warranty_end_date', 'type': rec._fields['extended_warranty_end_date'].type, 'title': rec._fields['extended_warranty_end_date'].string,
                  'value': str(rec.extended_warranty_end_date) if rec.extended_warranty_end_date else ''}
            repair_warranty_start_date = {'key': 'repair_warranty_start_date', 'type': rec._fields['repair_warranty_start_date'].type, 'title': rec._fields['repair_warranty_start_date'].string,
                  'value': str(rec.repair_warranty_start_date) if rec.repair_warranty_start_date else ''}
            repair_warranty_end_date = {'key': 'repair_warranty_end_date', 'type': rec._fields['repair_warranty_end_date'].type, 'title': rec._fields['repair_warranty_end_date'].string,
                  'value': str(rec.repair_warranty_end_date) if rec.repair_warranty_end_date else ''}
            asset_arrival_date = {'key': 'asset_arrival_date', 'type': rec._fields['asset_arrival_date'].type, 'title': rec._fields['asset_arrival_date'].string,
                  'value': str(rec.asset_arrival_date) if rec.asset_arrival_date else ''}
            installation_date = {'key': 'installation_date', 'type': rec._fields['installation_date'].type, 'title': rec._fields['installation_date'].string,
                  'value': str(rec.installation_date) if rec.installation_date else ''}
            note = {'key': 'note', 'type': rec._fields['note'].type, 'title': rec._fields['note'].string,
                  'value': BeautifulSoup(rec.note, "lxml").text if rec.note else ''}
            region_customer = {'key': 'region_customer', 'type': rec._fields['region_customer'].type, 'title': rec._fields['region_customer'].string,
                  'value': rec.region_customer.name if rec.region_customer else ''}
            stock_lot_list.append([id,name,customer_id,customer_account,external_id,product_id,product_price,product_qty,
                        product_uom_id,ref,company_id,custom_sale_order,contract_flow_id,asset_tag_ids,
                        asset_id_label,service_support_commitment,asset_location_id,lattitude,longitutde,
                        faulty_sticker,rsp_name,replacement_for,asset_category_id,asset_type_id,product_types_id,
                        asset_id_allias,invoice_number,unit_type_id,industry_id,hardware_version,software_version,
                        mc_skt,product_eol,product_eosl,custom_sale_order_date,warranty_start_date,warranty_end_date,
                        extended_warranty_start_date,extended_warranty_end_date,repair_warranty_start_date,repair_warranty_end_date,
                        asset_arrival_date,installation_date,note,region_customer])

        if stock_lot_list:
            return valid_response1(stock_lot_list,count, 'asset lot number load successfully', 200)
        else:
            return valid_response1(stock_lot_list,count, 'there is not record in  asset lot number', 200)

    @validate_token
    @http.route("/api/get_asset_with_serial_num", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_asset_with_serial_num_value(self, **post,):
        stock_lot_obj = request.env['stock.lot']
        post = json.loads(request.httprequest.data)
        limit = post.get('limit')
        next_count = post.get('next_count')
        search_value = post.get('search_value')
        domain = [('active','=',True),('product_id.tracking', '=', 'serial')]
        if search_value:
            domain += [('name','ilike',search_value)]
        count = stock_lot_obj.sudo().search_count(domain)
        stock_lot_ids = stock_lot_obj.sudo().search(domain, offset=next_count,limit=limit, order='name ASC')
        stock_lot_list = []
        for rec in stock_lot_ids:
            id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                  'value': rec.id if rec.id else ''}
            name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                    'value': rec.name if rec.name else ''}
            customer_id = {'key': 'customer_id', 'type': rec._fields['customer_id'].type,
                           'title': rec._fields['customer_id'].string,
                           'value': rec.customer_id.name if rec.customer_id else ''}
            customer_account = {'key': 'customer_account', 'type': rec._fields['customer_account'].type,
                                'title': rec._fields['customer_account'].string,
                                'value': rec.customer_account.name if rec.customer_account else ''}
            external_id = {'key': 'external_id', 'type': rec._fields['external_id'].type,
                           'title': rec._fields['external_id'].string,
                           'value': rec.external_id if rec.external_id else ''}
            product_id = {'key': 'product_id', 'type': rec._fields['product_id'].type,
                          'title': rec._fields['product_id'].string,
                          'value': rec.product_id.name if rec.product_id else ''}
            product_price = {'key': 'product_price', 'type': rec._fields['product_price'].type,
                             'title': rec._fields['product_price'].string,
                             'value': rec.product_price if rec.product_price else ''}
            product_qty = {'key': 'product_qty', 'type': rec._fields['product_qty'].type,
                           'title': rec._fields['product_qty'].string,
                           'value': rec.product_qty if rec.product_qty else ''}
            product_uom_id = {'key': 'product_uom_id', 'type': rec._fields['product_uom_id'].type,
                              'title': rec._fields['product_uom_id'].string,
                              'value': rec.product_uom_id.name if rec.product_uom_id else ''}
            ref = {'key': 'ref', 'type': rec._fields['ref'].type, 'title': rec._fields['ref'].string,
                   'value': rec.ref if rec.ref else ''}
            company_id = {'key': 'company_id', 'type': rec._fields['company_id'].type,
                          'title': rec._fields['company_id'].string,
                          'value': rec.company_id.name if rec.company_id else ''}
            custom_sale_order = {'key': 'custom_sale_order', 'type': rec._fields['custom_sale_order'].type,
                                 'title': rec._fields['custom_sale_order'].string,
                                 'value': rec.custom_sale_order.name if rec.custom_sale_order else ''}
            contract_flow_id = {'key': 'contract_flow_id', 'type': rec._fields['contract_flow_id'].type,
                                'title': rec._fields['contract_flow_id'].string,
                                'value': rec.contract_flow_id.name if rec.contract_flow_id else ''}
            asset_tag_ids = {'key': 'asset_tag_ids', 'type': rec._fields['asset_tag_ids'].type,
                             'title': rec._fields['asset_tag_ids'].string,
                             'value': [{'id': x.id, 'value': x.name} for x in
                                       rec.asset_tag_ids] if rec.asset_tag_ids else ''}
            asset_id_label = {'key': 'asset_id_label', 'type': rec._fields['asset_id_label'].type,
                              'title': rec._fields['asset_id_label'].string,
                              'value': rec.asset_id_label if rec.asset_id_label else ''}
            service_support_commitment = {'key': 'service_support_commitment',
                                          'type': rec._fields['service_support_commitment'].type,
                                          'title': rec._fields['service_support_commitment'].string,
                                          'value': rec.service_support_commitment if rec.service_support_commitment else ''}
            asset_location_id = {'key': 'asset_location_id', 'type': rec._fields['asset_location_id'].type,
                                 'title': rec._fields['asset_location_id'].string,
                                 'value': rec.asset_location_id.name if rec.asset_location_id else ''}
            lattitude = {'key': 'lattitude', 'type': rec._fields['lattitude'].type,
                         'title': rec._fields['lattitude'].string,
                         'value': rec.lattitude if rec.lattitude else ''}
            longitutde = {'key': 'longitutde', 'type': rec._fields['longitutde'].type,
                          'title': rec._fields['longitutde'].string,
                          'value': rec.longitutde if rec.longitutde else ''}
            faulty_sticker = {'key': 'faulty_sticker', 'type': rec._fields['faulty_sticker'].type,
                              'title': rec._fields['faulty_sticker'].string,
                              'value': rec.faulty_sticker if rec.faulty_sticker else ''}
            rsp_name = {'key': 'rsp_name', 'type': rec._fields['rsp_name'].type,
                        'title': rec._fields['rsp_name'].string,
                        'value': rec.rsp_name.name if rec.rsp_name else ''}
            replacement_for = {'key': 'replacement_for', 'type': rec._fields['replacement_for'].type,
                               'title': rec._fields['replacement_for'].string,
                               'value': rec.replacement_for if rec.replacement_for else ''}
            asset_category_id = {'key': 'asset_category_id', 'type': rec._fields['asset_category_id'].type,
                                 'title': rec._fields['asset_category_id'].string,
                                 'value': rec.asset_category_id.name if rec.asset_category_id else ''}
            asset_type_id = {'key': 'asset_type_id', 'type': rec._fields['asset_type_id'].type,
                             'title': rec._fields['asset_type_id'].string,
                             'value': rec.asset_type_id.name if rec.asset_type_id else ''}
            product_types_id = {'key': 'product_types_id', 'type': rec._fields['product_types_id'].type,
                                'title': rec._fields['product_types_id'].string,
                                'value': rec.product_types_id.name if rec.product_types_id else ''}
            asset_id_allias = {'key': 'asset_id_allias', 'type': rec._fields['asset_id_allias'].type,
                               'title': rec._fields['asset_id_allias'].string,
                               'value': rec.asset_id_allias if rec.asset_id_allias else ''}
            invoice_number = {'key': 'invoice_number', 'type': rec._fields['invoice_number'].type,
                              'title': rec._fields['invoice_number'].string,
                              'value': rec.invoice_number if rec.invoice_number else ''}
            unit_type_id = {'key': 'unit_type_id', 'type': rec._fields['unit_type_id'].type,
                            'title': rec._fields['unit_type_id'].string,
                            'value': rec.unit_type_id if rec.unit_type_id else ''}
            industry_id = {'key': 'industry_id', 'type': rec._fields['industry_id'].type,
                           'title': rec._fields['industry_id'].string,
                           'value': rec.industry_id.name if rec.industry_id else ''}
            hardware_version = {'key': 'hardware_version', 'type': rec._fields['hardware_version'].type,
                                'title': rec._fields['hardware_version'].string,
                                'value': rec.hardware_version if rec.hardware_version else ''}
            software_version = {'key': 'software_version', 'type': rec._fields['software_version'].type,
                                'title': rec._fields['software_version'].string,
                                'value': rec.software_version if rec.software_version else ''}
            mc_skt = {'key': 'mc_skt', 'type': rec._fields['mc_skt'].type, 'title': rec._fields['mc_skt'].string,
                      'value': rec.mc_skt if rec.mc_skt else ''}
            product_eol = {'key': 'product_eol', 'type': rec._fields['product_eol'].type,
                           'title': rec._fields['product_eol'].string,
                           'value': str(rec.product_eol) if rec.product_eol else ''}
            product_eosl = {'key': 'product_eosl', 'type': rec._fields['product_eosl'].type,
                            'title': rec._fields['product_eosl'].string,
                            'value': str(rec.product_eosl) if rec.product_eosl else ''}
            custom_sale_order_date = {'key': 'custom_sale_order_date',
                                      'type': rec._fields['custom_sale_order_date'].type,
                                      'title': rec._fields['custom_sale_order_date'].string,
                                      'value': str(rec.custom_sale_order_date) if rec.custom_sale_order_date else ''}
            warranty_start_date = {'key': 'warranty_start_date', 'type': rec._fields['warranty_start_date'].type,
                                   'title': rec._fields['warranty_start_date'].string,
                                   'value': str(rec.warranty_start_date) if rec.warranty_start_date else ''}
            warranty_end_date = {'key': 'warranty_end_date', 'type': rec._fields['warranty_end_date'].type,
                                 'title': rec._fields['warranty_end_date'].string,
                                 'value': str(rec.warranty_end_date) if rec.warranty_end_date else ''}
            extended_warranty_start_date = {'key': 'extended_warranty_start_date',
                                            'type': rec._fields['extended_warranty_start_date'].type,
                                            'title': rec._fields['extended_warranty_start_date'].string,
                                            'value': str(
                                                rec.extended_warranty_start_date) if rec.extended_warranty_start_date else ''}
            extended_warranty_end_date = {'key': 'extended_warranty_end_date',
                                          'type': rec._fields['extended_warranty_end_date'].type,
                                          'title': rec._fields['extended_warranty_end_date'].string,
                                          'value': str(
                                              rec.extended_warranty_end_date) if rec.extended_warranty_end_date else ''}
            repair_warranty_start_date = {'key': 'repair_warranty_start_date',
                                          'type': rec._fields['repair_warranty_start_date'].type,
                                          'title': rec._fields['repair_warranty_start_date'].string,
                                          'value': str(
                                              rec.repair_warranty_start_date) if rec.repair_warranty_start_date else ''}
            repair_warranty_end_date = {'key': 'repair_warranty_end_date',
                                        'type': rec._fields['repair_warranty_end_date'].type,
                                        'title': rec._fields['repair_warranty_end_date'].string,
                                        'value': str(
                                            rec.repair_warranty_end_date) if rec.repair_warranty_end_date else ''}
            asset_arrival_date = {'key': 'asset_arrival_date', 'type': rec._fields['asset_arrival_date'].type,
                                  'title': rec._fields['asset_arrival_date'].string,
                                  'value': str(rec.asset_arrival_date) if rec.asset_arrival_date else ''}
            installation_date = {'key': 'installation_date', 'type': rec._fields['installation_date'].type,
                                 'title': rec._fields['installation_date'].string,
                                 'value': str(rec.installation_date) if rec.installation_date else ''}
            note = {'key': 'note', 'type': rec._fields['note'].type, 'title': rec._fields['note'].string,
                    'value': BeautifulSoup(rec.note, "lxml").text if rec.note else ''}
            region_customer = {'key': 'region_customer', 'type': rec._fields['region_customer'].type,
                               'title': rec._fields['region_customer'].string,
                               'value': rec.region_customer.name if rec.region_customer else ''}
            stock_lot_list.append([id, name, customer_id, customer_account,external_id, product_id, product_price, product_qty,
                                   product_uom_id, ref, company_id, custom_sale_order, contract_flow_id, asset_tag_ids,
                                   asset_id_label, service_support_commitment, asset_location_id, lattitude, longitutde,
                                   faulty_sticker, rsp_name, replacement_for, asset_category_id, asset_type_id,
                                   product_types_id,
                                   asset_id_allias, invoice_number, unit_type_id, industry_id, hardware_version,
                                   software_version,
                                   mc_skt, product_eol, product_eosl, custom_sale_order_date, warranty_start_date,
                                   warranty_end_date,
                                   extended_warranty_start_date, extended_warranty_end_date, repair_warranty_start_date,
                                   repair_warranty_end_date,
                                   asset_arrival_date, installation_date,note,region_customer
                                   ])

        if stock_lot_list:
            return valid_response1(stock_lot_list, count, 'asset serial number load successfully', 200)
        else:
            return valid_response1(stock_lot_list,count, 'there is not record in  asset wth serial number', 200)

    # @validate_token
    # @http.route("/api/get_asset_with_lot_num", type="json", auth="none", methods=["POST"], csrf=False)
    # def _api_get_asset_with_lot_num_value(self, **post,):
    #     stock_lot_conf = request.env['stock.lot'].sudo().search_read([('active','=',True),('product_id.tracking', '=', 'lot'),('is_lot','=','True')],
    #     fields=['name','customer_id','customer_account','product_id','product_price','product_qty','product_uom_id','ref','company_id','custom_sale_order',
    #     'contract_flow_id','asset_tag_ids','asset_id_label','service_support_commitment','asset_location_id','lattitude','longitutde','faulty_sticker',
    #     'rsp_name','replacement_for','asset_category_id','asset_type_id','product_types_id','asset_id_allias','invoice_number','unit_type_id','industry_id',
    #     'hardware_version','software_version','mc_skt'])
    #     for rec in stock_lot_conf:
    #         stock_lot = request.env['stock.lot'].sudo().browse(rec.get('id'))
    #         rec['product_eol']=str(stock_lot.product_eol)
    #         rec['product_eosl']=str(stock_lot.product_eosl)
    #         rec['custom_sale_order_date']=str(stock_lot.custom_sale_order_date)
    #         rec['warranty_start_date']=str(stock_lot.warranty_start_date)
    #         rec['warranty_end_date']=str(stock_lot.warranty_end_date)
    #         rec['extended_warranty_start_date']=str(stock_lot.extended_warranty_start_date)
    #         rec['extended_warranty_end_date']=str(stock_lot.extended_warranty_end_date)
    #         rec['repair_warranty_end_date']=str(stock_lot.repair_warranty_end_date)
    #         rec['repair_warranty_start_date']=str(stock_lot.repair_warranty_start_date)
    #         rec['asset_arrival_date']=str(stock_lot.asset_arrival_date)
    #         rec['installation_date']=str(stock_lot.installation_date)
    #
    #     if stock_lot_conf:
    #         return valid_response(stock_lot_conf, 'asset lot number load successfully', 200)
    #     else:
    #         return valid_response(stock_lot_conf, 'there is not record in  asset lot number', 200)

    # @validate_token
    # @http.route("/api/get_asset_with_serial_num", type="json", auth="none", methods=["POST"], csrf=False)
    # def _api_get_asset_with_serial_num_value(self, **post,):
    #     stock_lot_conf = request.env['stock.lot'].sudo().search_read([('active','=',True),('product_id.tracking', '=', 'serial')],fields=['name','customer_id','customer_account','product_id','product_price','product_qty','product_uom_id','ref','company_id','custom_sale_order','contract_flow_id','asset_tag_ids','asset_id_label','service_support_commitment','asset_location_id','lattitude','longitutde','faulty_sticker','rsp_name','replacement_for','asset_category_id','asset_type_id','product_types_id','asset_id_allias','invoice_number','unit_type_id','industry_id','hardware_version','software_version','mc_skt'])
    #     for rec in stock_lot_conf:
    #         stock_lot = request.env['stock.lot'].sudo().browse(rec.get('id'))
    #         rec['product_eol']=str(stock_lot.product_eol)
    #         rec['product_eosl']=str(stock_lot.product_eosl)
    #         rec['custom_sale_order_date']=str(stock_lot.custom_sale_order_date)
    #         rec['warranty_start_date']=str(stock_lot.warranty_start_date)
    #         rec['warranty_end_date']=str(stock_lot.warranty_end_date)
    #         rec['extended_warranty_start_date']=str(stock_lot.extended_warranty_start_date)
    #         rec['extended_warranty_end_date']=str(stock_lot.extended_warranty_end_date)
    #         rec['repair_warranty_end_date']=str(stock_lot.repair_warranty_end_date)
    #         rec['repair_warranty_start_date']=str(stock_lot.repair_warranty_start_date)
    #         rec['asset_arrival_date']=str(stock_lot.asset_arrival_date)
    #         rec['installation_date']=str(stock_lot.installation_date)
    #
    #     if stock_lot_conf:
    #         return valid_response(stock_lot_conf, 'asset serial number load successfully', 200)
    #     else:
    #         return valid_response(stock_lot_conf, 'there is not record in  asset wth serial number', 200)
    #
