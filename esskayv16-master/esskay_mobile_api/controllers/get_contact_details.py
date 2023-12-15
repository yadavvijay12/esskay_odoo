from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token,magic_fields
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response,valid_response1
from odoo import http
from odoo.http import request
import json
from bs4 import BeautifulSoup
import logging
_logger = logging.getLogger(__name__)
class APIController(http.Controller):

    @validate_token
    @http.route("/api/get_contact", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_contact_details(self, **post,):
        contact_obj = request.env['res.partner']
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url = base_url.replace(':8071', '')
        fields=['active_lang_count','active','name','user_livechat_username',
        'parent_name','lastname','surgeon_name','firstname','mobile','email','customer_account','street','street2','city','zip','state_id','country_id','city_id',
        'customer_properties','website_id','website_published','is_published','can_publish','website_url','message_is_follower','message_follower_ids',
         'message_partner_ids','message_ids','has_message','message_attachment_count','message_main_attachment_id','website_message_ids','email_normalized',
        'is_blacklisted','message_bounce','activity_ids','activity_state','activity_user_id','activity_type_id','activity_type_icon','activity_summary',
        'activity_exception_decoration','activity_exception_icon','title','parent_id','child_ids','ref','lang','tz','tz_offset','user_id','vat','same_vat_partner_id','same_company_registry_partner_id',
        'company_registry','bank_ids','website','comment','category_id','employee','function','type','partner_latitude','partner_longitude','email_formatted','phone','is_company','is_public','industry_id','company_type',
        'company_id','color','user_ids','partner_share','contact_address','commercial_partner_id','commercial_company_name','company_name','im_status','channel_ids','signup_token','signup_type','signup_expiration',
        'signup_valid','signup_url','employee_ids','employees_count','team_id','partner_gid','additional_info','phone_sanitized','phone_sanitized_blacklisted','phone_blacklisted','mobile_blacklisted','phone_mobile_search',
        'certifications_count','certifications_company_count','payment_token_ids','payment_token_count','credit','show_credit_limit','debit','debit_limit','currency_id','journal_item_count','ref_company_ids',
        'has_unreconciled_entries','last_time_entries_checked','invoice_ids','contract_ids','bank_account_count','invoice_warn','invoice_warn_msg','supplier_rank','customer_rank','duplicated_bank_account_partners_count',
       'task_ids','user_livechat_username','task_count','picking_warn','picking_warn_msg','visitor_ids','sale_contract_count','purchase_contract_count','supplier_invoice_count','purchase_warn','purchase_warn_msg',
        'l10n_in_gst_treatment','purchase_line_ids','on_time_rate','sale_order_count','sale_order_ids','sale_warn','sale_warn_msg','customer_type','parent_customer_id','customer_account_id','branch_id','branch_actual_id',
        'branch_id_alias','customer_region','target_group','tier_tier','customer_group','process_id','role_id','base_type_id','work_location_id','spare_category_id','customer_id_alias','reference','secondary_contact_number',
        'gst_no','hospital_name','surgeon_name','description','vendor_code','c_number','d_number','customer_properties','service_ticket_properties','properties','fax_no','asset_line_ids','location_id','loaner_ids',
        'ticket_ids','service_ticket_count','customer_attachments','dealer_distributer_ids','branc_ids','is_block_partner','parent_count','child_count','service_count']

        # contact_all_keys = contact_obj.sudo().fields_get().keys()
        # print(contact_all_keys,'keys')
        # contact_keys = list(set(contact_all_keys).difference(magic_fields))

        contact=request.env['res.partner'].sudo().search_read([('active','=',True)] , fields)
        for rec in contact:
            con=contact_obj.sudo().browse(rec.get('id'))
            rec['image_1920']=base_url + '/web/image?' + 'model=res.partner&id=' + str(con.id) + '&field=image_1920' if con.image_1920 else False
            # rec['date'] = str(con.data) if con.data else False
        if contact:
            return valid_response(contact, 'contact loaded successfully', 200)
        else:
            return valid_response(contact, 'there is no contact', 200)



# not in user fields
# ['date_localization', 'property_purchase_currency_id', 'my_activity_date_deadline', 'message_has_error_counter', 'avatar_128', 'use_partner_credit_limit', 'message_needaction', 'purchase_order_count', 'credit_limit', 'property_supplier_payment_term_id', 'message_has_sms_error', 'property_payment_term_id', 'avatar_256', 'property_account_payable_id', 'property_stock_customer', 'message_needaction_counter', 'property_account_position_id', 'trust', 'property_stock_supplier', 'property_product_pricelist', 'display_name', 'total_invoiced', 'receipt_reminder_email', 'avatar_1920', 'avatar_1024', 'image_128', 'image_512', 'barcode', 'property_account_receivable_id', 'date', 'activity_date_deadline', 'image_1024', 'avatar_512', 'message_has_error', 'image_1920', 'country_code', 'image_256', 'reminder_date_before_receipt', 'self']

    @validate_token
    @http.route("/api/get_contact_page", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_contact_details_page(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('/api/get_contact_page value post: %s' % post)
        limit=post.get('limit')
        next_count=post.get('next_count')
        search_value = post.get('search_value')
        partner_id = post.get('id')
        contact_obj = request.env['res.partner']
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url = base_url.replace(':8071', '')
        domain = [('active', '=', True)]
        if search_value:
            domain += [('name','ilike',str(search_value))]
        if partner_id:
            domain += [('id', '=', int(partner_id))]
        # contact=request.env['res.partner'].sudo().search_read([('active','=',True)] , fields , offset=next_count , limit=limit , order='name ASC')
        count = contact_obj.sudo().search_count(domain)
        # contact=[{'name':[{'value':record.get('name'),'title':"Name"}]} for record in contact]
        # [index[record.id] for record in contact if record.id in index]
        contact_ids= contact_obj.sudo().search(domain, offset=next_count , limit=limit , order='name ASC')
        contact=[]
        for rec in contact_ids:
            id = {'key':'id','type': rec._fields['id'].type,'title':rec._fields['id'].string,'value':rec.id if rec.id else ''}
            company_type = {'key':'company_type','type':rec._fields['company_type'].type,'title': rec._fields['company_type'].string,'value':dict(rec._fields['company_type'].selection).get(rec.company_type) if rec.company_type else False}
            firstname = {'key':'firstname','type': rec._fields['firstname'].type,'title':rec._fields['firstname'].string,'value': rec.firstname if rec.firstname else ''}
            lastname = {'key':'lastname','type': rec._fields['lastname'].type,'title': rec._fields['lastname'].string,'value':rec.lastname if rec.lastname else ''}
            name = {'key':'name','type': rec._fields['name'].type,'title':rec._fields['name'].string,'value':rec.name if rec.name else ''}
            image_1920 = {'key':'image_1920','type': 'image','title':rec._fields['image_1920'].string,'value':base_url + '/web/image?' + 'model=res.partner&id=' + str(rec.id) + '&field=image_1920'}
            parent_customer_id = {'key':'parent_customer_id','type': rec._fields['parent_customer_id'].type,'title':rec._fields['parent_customer_id'].string,'value':rec.parent_customer_id.name if rec.parent_customer_id else "" }
            customer_account_id = {'key':'customer_account_id','type': rec._fields['customer_account_id'].type,'title':rec._fields['customer_account_id'].string,'value':rec.customer_account_id.name if rec.customer_account_id else "" }

            # BASIC INFORMATIONS
            parent_id = {'key':'parent_id','type': rec._fields['parent_id'].type,'title':rec._fields['parent_id'].string,'value':rec.parent_id.name if rec.parent_id else "" }
            type= {'key':'type','type': rec._fields['type'].type,'title':rec._fields['type'].string,'value':dict(rec._fields['type'].selection).get(rec.type) if rec.type else ''}
            street = {'key':'street','type': rec._fields['street'].type,'title':rec._fields['street'].string,'value':rec.street if rec.street else ''}
            street2 = {'key':'street2','type': rec._fields['street2'].type,'title':rec._fields['street2'].string,'value':rec.street2 if rec.street2 else ''}
            city_id = {'key':'city_id','type': rec._fields['city_id'].type,'title':rec._fields['city_id'].string,'value':rec.city_id.name if rec.city_id else ''}
            state_id = {'key':'state_id','type': rec._fields['state_id'].type,'title':rec._fields['state_id'].string,'value':rec.state_id.name if rec.state_id else ''}
            country_id = {'key':'country_id','type': rec._fields['country_id'].type,'title':rec._fields['country_id'].string,'value':rec.country_id.name if rec.country_id else ''}
            l10n_in_gst_treatment = {'key':'l10n_in_gst_treatment','type': rec._fields['l10n_in_gst_treatment'].type,'title':rec._fields['l10n_in_gst_treatment'].string,'value':dict(rec._fields['l10n_in_gst_treatment'].selection).get(rec.l10n_in_gst_treatment) if rec.l10n_in_gst_treatment else ''}
            vat = {'key':'vat','type': rec._fields['vat'].type,'title':rec._fields['vat'].string,'value':rec.vat if rec.vat else ''}
            gst_no = {'key':'gst_no','type': rec._fields['gst_no'].type,'title':rec._fields['gst_no'].string,'value':rec.gst_no if rec.gst_no else ''}
            is_block_partner = {'key':'is_block_partner','type': rec._fields['is_block_partner'].type,'title':rec._fields['is_block_partner'].string,'value':dict(rec._fields['is_block_partner'].selection).get(rec.is_block_partner) if rec.is_block_partner else ''}
            function = {'key':'function','type': rec._fields['function'].type,'title':rec._fields['function'].string,'value':rec.function if rec.function else ''}
            phone = {'key':'phone','type': rec._fields['phone'].type,'title':rec._fields['phone'].string,'value':rec.phone if rec.phone else ''}
            mobile = {'key':'mobile','type': rec._fields['mobile'].type,'title':rec._fields['mobile'].string,'value':rec.mobile if rec.mobile else ''}
            email = {'key':'email','type': rec._fields['email'].type,'title':rec._fields['email'].string,'value':rec.email if rec.email else ''}
            website = {'key':'website','type': rec._fields['website'].type,'title':rec._fields['website'].string,'value':rec.website if rec.website else ''}
            title = {'key':'title','type': rec._fields['title'].type,'title':rec._fields['title'].string,'value':rec.title.name if rec.title else ''}
            category_id = {'key':'category_id','type': rec._fields['category_id'].type,'title':rec._fields['category_id'].string,'value':[{'id':x.id,'value':x.name} for x in rec.category_id] if rec.category_id else ''}
            fax_no = {'key':'fax_no','type': rec._fields['fax_no'].type,'title':rec._fields['fax_no'].string,'value':rec.fax_no if rec.fax_no else ''}

            # OTHER INFORMATIONS
            customer_id_alias = {'key':'customer_id_alias','type': rec._fields['customer_id_alias'].type,'title':rec._fields['customer_id_alias'].string,'value':rec.customer_id_alias if rec.customer_id_alias else ''}
            customer_type = {'key':'customer_type','type': rec._fields['customer_type'].type,'title':rec._fields['customer_type'].string,'value':rec.customer_type.name if rec.customer_type else ''}
            customer_region = {'key':'customer_region','type': rec._fields['customer_region'].type,'title':rec._fields['customer_region'].string,'value':rec.customer_region.name if rec.customer_region else ''}
            target_group = {'key':'target_group','type': rec._fields['target_group'].type,'title':rec._fields['target_group'].string,'value':rec.target_group.name if rec.target_group else ''}
            tier_tier = {'key':'tier_tier','type': rec._fields['tier_tier'].type,'title':rec._fields['tier_tier'].string,'value':rec.tier_tier.name if rec.tier_tier else ''}
            reference = {'key':'reference','type': rec._fields['reference'].type,'title':rec._fields['reference'].string,'value':rec.reference if rec.reference else ''}
            customer_group = {'key':'customer_group','type': rec._fields['customer_group'].type,'title':rec._fields['customer_group'].string,'value':rec.customer_group.name if rec.customer_group else ''}
            location_id = {'key':'location_id','type': rec._fields['location_id'].type,'title':rec._fields['location_id'].string,'value':rec.location_id.name if rec.location_id else ''}
            hospital_name = {'key':'hospital_name','type': rec._fields['hospital_name'].type,'title':rec._fields['hospital_name'].string,'value':rec.hospital_name if rec.hospital_name else ''}
            surgeon_name = {'key':'surgeon_name','type': rec._fields['surgeon_name'].type,'title':rec._fields['surgeon_name'].string,'value':rec.surgeon_name if rec.surgeon_name else ''}
            description = {'key':'description','type': rec._fields['description'].type,'title':rec._fields['description'].string,'value':rec.description if rec.description else ''}
            secondary_contact_number = {'key':'secondary_contact_number','type': rec._fields['secondary_contact_number'].type,'title':rec._fields['secondary_contact_number'].string,'value':rec.secondary_contact_number if rec.secondary_contact_number else ''}
            vendor_code = {'key':'vendor_code','type': rec._fields['vendor_code'].type,'title':rec._fields['vendor_code'].string,'value':rec.vendor_code if rec.vendor_code else ''}
            c_number = {'key':'c_number','type': rec._fields['c_number'].type,'title':rec._fields['c_number'].string,'value':rec.c_number if rec.c_number else ''}
            d_number = {'key':'d_number','type': rec._fields['d_number'].type,'title':rec._fields['d_number'].string,'value':rec.d_number if rec.d_number else ''}

            # INTERNAL NOTES
            comment = {'key':'comment','type': rec._fields['comment'].type,'title':rec._fields['comment'].string,'value':BeautifulSoup(rec.comment, "lxml").text if rec.comment else ''}

            parent_name = {'key': 'parent_name','type': rec._fields['parent_name'].type, 'title': rec._fields['parent_name'].string,'value': rec.parent_name if rec.parent_name else ""}
            # Sales & purchase
            user_id = {'key':'user_id','type': rec._fields['user_id'].type,'title':rec._fields['user_id'].string,'value':rec.user_id.name if rec.user_id else ''}
            #GEO Location
            partner_latitude = {'key':'partner_latitude','type': rec._fields['partner_latitude'].type,'title':rec._fields['partner_latitude'].string,'value':rec.partner_latitude if rec.partner_latitude else ''}
            partner_longitude = {'key':'partner_longitude','type': rec._fields['partner_longitude'].type,'title':rec._fields['partner_longitude'].string,'value':rec.partner_longitude if rec.partner_longitude else ''}

            contact.append([id,company_type,firstname,lastname,name,image_1920,parent_customer_id,customer_account_id,
                            parent_id,type,street,street2,city_id,state_id,country_id,l10n_in_gst_treatment,vat,gst_no,
                            is_block_partner,function,phone,mobile,email,website,title,category_id,fax_no,
                            customer_id_alias,customer_type,customer_region,target_group,tier_tier,reference,customer_group,
                            location_id,hospital_name,surgeon_name,description,secondary_contact_number,vendor_code,c_number,
                               d_number,comment,parent_name,user_id,partner_latitude,partner_longitude])
        _logger.info('/api/get_contact_page get values: %s' % contact)
        if contact:
            return valid_response1(contact,count, 'contact loaded successfully', 200)
        else:
            return valid_response1(contact,count, 'there is no contact', 200)

    @validate_token
    @http.route("/api/get_contact/fields", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_contact_details_fields(self, **post,):
        contact_obj = request.env['res.partner']
        contact_all = contact_obj.sudo().fields_get(['active_lang_count','active','name','user_livechat_username',
        'parent_name','lastname','surgeon_name','firstname','mobile','email','customer_account','street','street2','city','zip','state_id','country_id','city_id',
        'customer_properties','website_id','website_published','is_published','can_publish','website_url','message_is_follower','message_follower_ids',
         'message_partner_ids','message_ids','has_message','message_attachment_count','message_main_attachment_id','website_message_ids','email_normalized',
        'is_blacklisted','message_bounce','activity_ids','activity_state','activity_user_id','activity_type_id','activity_type_icon','activity_summary',
        'activity_exception_decoration','activity_exception_icon','title','parent_id','child_ids','ref','lang','tz','tz_offset','user_id','vat','same_vat_partner_id','same_company_registry_partner_id',
        'company_registry','bank_ids','website','comment','category_id','employee','function','type','partner_latitude','partner_longitude','email_formatted','phone','is_company','is_public','industry_id','company_type',
        'company_id','color','user_ids','partner_share','contact_address','commercial_partner_id','commercial_company_name','company_name','im_status','channel_ids','signup_token','signup_type','signup_expiration',
        'signup_valid','signup_url','employee_ids','employees_count','team_id','partner_gid','additional_info','phone_sanitized','phone_sanitized_blacklisted','phone_blacklisted','mobile_blacklisted','phone_mobile_search',
        'certifications_count','certifications_company_count','payment_token_ids','payment_token_count','credit','show_credit_limit','debit','debit_limit','currency_id','journal_item_count','ref_company_ids',
        'has_unreconciled_entries','last_time_entries_checked','invoice_ids','contract_ids','bank_account_count','invoice_warn','invoice_warn_msg','supplier_rank','customer_rank','duplicated_bank_account_partners_count',
       'task_ids','user_livechat_username','task_count','picking_warn','picking_warn_msg','visitor_ids','sale_contract_count','purchase_contract_count','supplier_invoice_count','purchase_warn','purchase_warn_msg',
        'l10n_in_gst_treatment','purchase_line_ids','on_time_rate','sale_order_count','sale_order_ids','sale_warn','sale_warn_msg','customer_type','parent_customer_id','customer_account_id','branch_id','branch_actual_id',
        'branch_id_alias','customer_region','target_group','tier_tier','customer_group','process_id','role_id','base_type_id','work_location_id','spare_category_id','customer_id_alias','reference','secondary_contact_number',
        'gst_no','hospital_name','surgeon_name','description','vendor_code','c_number','d_number','customer_properties','service_ticket_properties','properties','fax_no','asset_line_ids','location_id','loaner_ids',
        'ticket_ids','service_ticket_count','customer_attachments','dealer_distributer_ids','branc_ids','is_block_partner','parent_count','child_count','service_count'])
        for x in contact_all.values():
            del x['change_default']
            del x['company_dependent']
            if 'context' in x:
                del x['context']
            del x['default_export_compatible']
            del x['depends']
            if 'domain' in x:
                del x['domain']
            if 'help' in x:
                del x['help']
            del x['manual']
            del x['readonly']
            del x['store']
            del x['sortable']
            del x['searchable']
            if 'related' in x:
                del x['related']
            if 'selection' in x:
                del x['selection']
            if 'group_operator'in x:
                del x['group_operator']
            if 'groups' in x:
                del x['groups']

        if contact_all:
            return valid_response([contact_all], 'contact loaded successfully', 200)
        else:
            return valid_response(contact_all, 'there is no contact', 200)

