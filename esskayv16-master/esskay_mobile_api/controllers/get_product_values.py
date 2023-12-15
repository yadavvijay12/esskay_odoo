from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response,valid_response1
from odoo import http
from odoo.http import request
from bs4 import BeautifulSoup
import json
class APIController(http.Controller):

    @validate_token
    @http.route("/api/get_product_value", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_product_value(self, **post):
        product_object = request.env['product.template']
        post = json.loads(request.httprequest.data)
        limit = post.get('limit')
        next_count = post.get('next_count')
        search_value = post.get('search_value')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url = base_url.replace(':8071', '')
        domain = [('active', '=', True)]
        if search_value:
            domain += [('name','ilike',search_value)]
        count = product_object.sudo().search_count(domain)
        product_values = product_object.sudo().search(domain,offset=next_count , limit=limit , order='name ASC')
        product_list=[]
        for rec in product_values:
            id = {'key': 'id', 'type': rec._fields['id'].type, 'title': rec._fields['id'].string,
                  'value': rec.id if rec.id else ''}
            name = {'key': 'name', 'type': rec._fields['name'].type, 'title': rec._fields['name'].string,
                  'value': rec.name if rec.name else ''}
            description = {'key': 'description', 'type': rec._fields['description'].type, 'title': rec._fields['description'].string,
                  'value': BeautifulSoup(rec.description, "lxml").text if rec.description else ''}
            sale_ok = {'key': 'sale_ok', 'type': rec._fields['sale_ok'].type, 'title': rec._fields['sale_ok'].string,
                  'value': rec.sale_ok}
            purchase_ok = {'key': 'purchase_ok', 'type': rec._fields['purchase_ok'].type, 'title': rec._fields['purchase_ok'].string,
                  'value': rec.purchase_ok}
            is_accessories = {'key': 'is_accessories', 'type': rec._fields['is_accessories'].type, 'title': rec._fields['is_accessories'].string,
                  'value': rec.is_accessories}
            rent_ok = {'key': 'rent_ok', 'type': rec._fields['rent_ok'].type, 'title': rec._fields['rent_ok'].string,
                  'value': rec.rent_ok}
            detailed_type = {'key': 'detailed_type', 'type': rec._fields['detailed_type'].type, 'title': rec._fields['detailed_type'].string,
                  'value': dict(rec._fields['detailed_type'].selection).get(rec.detailed_type) if rec.detailed_type else ''}
            product_code = {'key': 'product_code', 'type': rec._fields['product_code'].type, 'title': rec._fields['product_code'].string,
                  'value': rec.product_code if rec.product_code else ''}
            custom_product_serial = {'key': 'custom_product_serial', 'type': rec._fields['custom_product_serial'].type, 'title': rec._fields['custom_product_serial'].string,
                  'value': rec.custom_product_serial if rec.custom_product_serial else ''}
            customer_account_id = {'key': 'customer_account_id', 'type': rec._fields['customer_account_id'].type, 'title': rec._fields['customer_account_id'].string,
                  'value': rec.customer_account_id.name if rec.customer_account_id else ''}
            default_code = {'key': 'default_code', 'type': rec._fields['default_code'].type, 'title': rec._fields['default_code'].string,
                  'value': rec.default_code if rec.default_code else ''}
            barcode = {'key': 'barcode', 'type': rec._fields['barcode'].type, 'title': rec._fields['barcode'].string,
                  'value': rec.barcode if rec.barcode else ''}
            manufacturer_id = {'key': 'manufacturer_id', 'type': rec._fields['manufacturer_id'].type, 'title': rec._fields['manufacturer_id'].string,
                  'value': rec.manufacturer_id.name if rec.manufacturer_id else ''}
            product_tag_ids = {'key':'product_tag_ids','type': rec._fields['product_tag_ids'].type,'title':rec._fields['product_tag_ids'].string,'value': str(rec.product_tag_ids.mapped('name')).replace("[","").replace("]","").replace("'","") if rec.product_tag_ids else ''}
            uom_id = {'key': 'uom_id', 'type': rec._fields['uom_id'].type, 'title': rec._fields['uom_id'].string,
                  'value': rec.uom_id.name if rec.uom_id else ''}
            service_support_commitment = {'key': 'service_support_commitment', 'type': rec._fields['service_support_commitment'].type, 'title': rec._fields['service_support_commitment'].string,
                  'value': rec.service_support_commitment if rec.service_support_commitment else ''}
            invoice_number = {'key': 'invoice_number', 'type': rec._fields['invoice_number'].type, 'title': rec._fields['invoice_number'].string,
                  'value': rec.invoice_number if rec.invoice_number else ''}
            external_reference = {'key': 'external_reference', 'type': rec._fields['external_reference'].type, 'title': rec._fields['external_reference'].string,
                  'value': rec.external_reference if rec.external_reference else ''}
            currency_id = {'key': 'currency_id', 'type': rec._fields['currency_id'].type, 'title': rec._fields['currency_id'].string,
                  'value': rec.currency_id.name if rec.currency_id else ''}
            product_types_id = {'key': 'product_types_id', 'type': rec._fields['product_types_id'].type, 'title': rec._fields['product_types_id'].string,
                  'value': rec.product_types_id.name if rec.product_types_id else ''}
            product_part = {'key': 'product_part', 'type': rec._fields['product_part'].type, 'title': rec._fields['product_part'].string,
                  'value': rec.product_part if rec.product_part else ''}
            accessories_ids = {'key':'accessories_ids','type': rec._fields['accessories_ids'].type,'title':rec._fields['accessories_ids'].string,'value':[{'id':x.id,'value':x.name} for x in rec.accessories_ids] if rec.accessories_ids else ''}
            invoice_policy = {'key': 'invoice_policy', 'type': rec._fields['invoice_policy'].type, 'title': rec._fields['invoice_policy'].string,
                  'value': rec.invoice_policy if rec.invoice_policy else ''}
            company_id = {'key': 'company_id', 'type': rec._fields['company_id'].type, 'title': rec._fields['company_id'].string,
                  'value': rec.company_id.name if rec.company_id else ''}
            uom_po_id = {'key': 'uom_po_id', 'type': rec._fields['uom_po_id'].type, 'title': rec._fields['uom_po_id'].string,
                  'value': rec.uom_po_id.name if rec.uom_po_id else ''}
            list_price = {'key': 'list_price', 'type': rec._fields['list_price'].type, 'title': rec._fields['list_price'].string,
                  'value': rec.list_price if rec.list_price else ''}
            service_price = {'key': 'service_price', 'type': rec._fields['service_price'].type, 'title': rec._fields['service_price'].string,
                  'value': rec.service_price if rec.service_price else ''}
            taxes_id = {'key': 'taxes_id', 'type': rec._fields['taxes_id'].type, 'title': rec._fields['taxes_id'].string,
                  'value': rec.taxes_id.name if rec.taxes_id else ''}
            categ_id = {'key': 'categ_id', 'type': rec._fields['categ_id'].type, 'title': rec._fields['categ_id'].string,
                  'value': rec.categ_id.name if rec.categ_id else ''}
            image_1920 = {'key': 'image_1920', 'type': 'image', 'title': rec._fields['image_128'].string,
             'value': base_url + '/web/image?' + 'model=product.template&id=' + str(rec.id) + '&field=image_1920'}
            product_eol = {'key': 'product_eol', 'type': rec._fields['product_eol'].type, 'title': rec._fields['product_eol'].string,
                  'value': str(rec.product_eol) if rec.product_eol else ''}
            product_eosl = {'key': 'product_eosl', 'type': rec._fields['product_eosl'].type, 'title': rec._fields['product_eosl'].string,
                  'value': str(rec.product_eosl) if rec.product_eosl else ''}
            product_list.append([id,name,description,sale_ok,purchase_ok,is_accessories,rent_ok,detailed_type,
                                 product_code,custom_product_serial,customer_account_id,default_code,barcode,
                                 manufacturer_id,product_tag_ids,uom_id,service_support_commitment,invoice_number,
                                 external_reference,currency_id,product_types_id,product_part,accessories_ids,
                                 invoice_policy,company_id,uom_po_id,list_price,service_price,taxes_id,categ_id,
                                 image_1920,product_eol,product_eosl])

        if product_values:
            return valid_response1(product_list, count, 'product loaded successfully', 200)
        else:
            return valid_response1(product_list,count, 'there is no product', 200)

    # @validate_token
    # @http.route("/api/get_product_value", type="json", auth="none", methods=["POST"], csrf=False)
    # def _api_get_product_value(self, **post,):
    #     product_object=request.env['product.template']
    #     product_values=product_object.sudo().search_read([('active','=',True)],['name','description','sale_ok','purchase_ok','is_accessories','rent_ok','detailed_type',
    #     'product_code','custom_product_serial','customer_account_id','default_code','barcode','manufacturer_id','product_tag_ids','uom_id',
    #     'service_support_commitment','invoice_number','external_reference','currency_id','product_types_id','product_part','accessories_ids',
    #     'invoice_policy','company_id','uom_po_id','list_price','service_price','taxes_id','categ_id'])
    #     base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     base_url = base_url.replace(':8071', '')
    #     for rec in product_values:
    #         product=product_object.sudo().browse(rec.get('id'))
    #         # image=product.image_1920
    #         # image_1920=image.decode('UTF-8') if image else False
    #         # rec['image_1920'] = image_1920
    #         rec['image_1920_url'] = base_url + '/web/image?' + 'model=product.template&id=' + str(product.id) + '&field=image_128' if product.image_128 else False
    #         print(rec['image_1920_url'],'imgeeee')
    #         rec['product_eol']=str(product.product_eol)
    #         rec['product_eosl']=str(product.product_eosl)
    #         if rec.get('description'):
    #             rec['description'] = BeautifulSoup(rec.get('description'), "lxml").text
    #         # rec.pop('id')
    #         # rec['standard_price']=product.standard_price
    #     # pro_val=[]
    #     # for rec in request.env['product.template'].sudo().search([]):
    #     #     image=rec.image_1920
    #     #     product_image = image.decode('UTF-8') if image else False
    #     #     val={
    #     #         'name':rec.name,
    #     #         'description':rec.description,
    #     #         'sale_ok':rec.sale_ok,
    #     #         'purchase_ok':rec.purchase_ok,
    #     #         'is_accessories':rec.is_accessories,
    #     #         'rent_ok':rec.rent_ok,
    #     #         'image_1920':product_image,
    #     #     }
    #     #     pro_val.append(val)
    #     if product_values:
    #         return valid_response(product_values, 'product load successfully', 200)
    #     else:
    #         return valid_response(product_values, 'there is no product', 200)