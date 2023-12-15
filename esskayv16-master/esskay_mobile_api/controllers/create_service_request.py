from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response
from odoo import http
from odoo.http import request
from datetime import datetime,timedelta
from odoo import fields, models
import json
import pytz
import logging
_logger = logging.getLogger(__name__)

class APIController(http.Controller):

    @validate_token
    @http.route("/api/create_service_request", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_create_service_request(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('/api/create_service_request value: %s' % post)
        ticket_type = post.get('ticket_type')
        request_type_code = post.get('code')
        uid = request.env.uid
        print(uid,'uid')
        service_req_obj=request.env['service.request']
        call_source_obj = request.env['call.source'].sudo().search([])
        service_type_obj = request.env['service.type'].sudo().search([('ticket_type','=',ticket_type)])
        service_category_ids = request.env['service.category'].sudo().search([])
        request_type_ids = request.env['request.type'].sudo().search([('ticket_type','=',ticket_type)])
        call_received_ids = request.env['call.received'].sudo().search([])
        user_team_ids = request.env.user.team_ids
        team_ids = request.env['crm.team'].sudo().search([('is_service_request', '=', True),('id', 'in', user_team_ids.ids)])
        oem_warranty_status_ids = request.env['oem.warranty.status'].sudo().search([])
        repair_warranty_status_ids = request.env['repair.warranty.status'].sudo().search([])
        user_ids = request.env['res.users'].sudo().browse(int(uid))
        company_ids = request.env['res.company'].sudo().search([('id','=',user_ids.company_id.id)])
        approver_obj = request.env['multi.approval.type'].sudo().search([])
        child_ticket_type = request.env['child.ticket.type'].sudo().search([])
        custoemr_city_obj = request.env['res.city'].sudo().search([])
        customer_country_obj = request.env['res.country'].sudo().search([('code','=','IN')],limit=1)
        customer_state_obj = request.env['res.country.state'].sudo().search([('country_id','=',customer_country_obj.id)])
        survey_obj = request.env['survey.survey'].sudo().search([])
        case_completed_successfully_obj = request.env['case.completed.successfully'].sudo().search([])
        medical_intervention_obj = request.env['medical.intervention'].sudo().search([])
        patient_involved_obj = request.env['patient.involved'].sudo().search([])
        surgical_delay_obj = request.env['surgical.delay'].sudo().search([])
        select_adverse_consequences_values = dict(service_req_obj._fields['select_adverse_consequences'].selection)
        complaint_type_values = dict(service_req_obj._fields['complaint_type'].selection)

        service_list = []
        if ticket_type =='sr_installation':
            # SERVICE REQUEST INFORMATION
            service_request_id_alias = {'key':'service_request_id_alias','type':service_req_obj._fields['service_request_id_alias'].type,'title':service_req_obj._fields['service_request_id_alias'].string,'required':service_req_obj._fields['service_request_id_alias'].required}
            service_request_date = {'key':'service_request_date','type':service_req_obj._fields['service_request_date'].type,'title':service_req_obj._fields['service_request_date'].string,'required':service_req_obj._fields['service_request_date'].required,'value':str(fields.Datetime.now())}
            # approver_id = {'key':'approver_id','type':service_req_obj._fields['approver_id'].type,'title':service_req_obj._fields['approver_id'].string,
            #                'required':service_req_obj._fields['approver_id'].required,
            #                'value':[{'id':field.id,'value':field.name,} for field in approver_obj]}
            # child_ticket_type_id = {'key':'child_ticket_type_id','type':service_req_obj._fields['child_ticket_type_id'].type,'title':service_req_obj._fields['child_ticket_type_id'].string,
            #                'required':service_req_obj._fields['child_ticket_type_id'].required,
            #                'value':[{'id':field.id,'value':field.name,} for field in child_ticket_type]}
            # CUSTOMER INFORMATION
            customer_name = {'key':'customer_name','type':service_req_obj._fields['customer_name'].type,'title':service_req_obj._fields['customer_name'].string,'required':True}
            customer_email = {'key':'customer_email','type':service_req_obj._fields['customer_email'].type,'title':service_req_obj._fields['customer_email'].string,'required':service_req_obj._fields['customer_email'].required}
            customer_street = {'key':'customer_street','type':service_req_obj._fields['customer_street'].type,'title':service_req_obj._fields['customer_street'].string,'required':service_req_obj._fields['customer_street'].required}
            customer_street2 = {'key':'customer_street2','type':service_req_obj._fields['customer_street2'].type,'title':service_req_obj._fields['customer_street2'].string,'required':service_req_obj._fields['customer_street2'].required}
            customer_city_id = {'key':'customer_city_id','type':service_req_obj._fields['customer_city_id'].type,'title':service_req_obj._fields['customer_city_id'].string,
                           'required':service_req_obj._fields['customer_city_id'].required,
                           'value':[{'id':field.id,'value':field.name,'state_id':field.state_id.id} for field in custoemr_city_obj]}
            customer_state_id = {'key':'customer_state_id','type':service_req_obj._fields['customer_state_id'].type,'title':service_req_obj._fields['customer_state_id'].string,
                           'required':service_req_obj._fields['customer_state_id'].required,
                           'value':[{'id':field.id,'value':field.name,} for field in customer_state_obj]}
            customer_zip = {'key':'customer_zip','type':service_req_obj._fields['customer_zip'].type,'title':service_req_obj._fields['customer_zip'].string,'required':service_req_obj._fields['customer_zip'].required}
            customer_country_id = {'key':'customer_country_id','type':service_req_obj._fields['customer_country_id'].type,'title':service_req_obj._fields['customer_country_id'].string,
                           'required':service_req_obj._fields['customer_country_id'].required,
                           'value':[{'id':field.id,'value':field.name,} for field in customer_country_obj]}
            is_same_customer_address = {'key':'is_same_customer_address','type':'boolean','title':'Is same as customer Address','required':False}
            install_addr_street = {'key':'install_addr_street','type':service_req_obj._fields['install_addr_street'].type,'title':service_req_obj._fields['install_addr_street'].string,'required':service_req_obj._fields['install_addr_street'].required}
            install_addr_street2 = {'key':'install_addr_street2','type':service_req_obj._fields['install_addr_street2'].type,'title':service_req_obj._fields['install_addr_street2'].string,'required':service_req_obj._fields['install_addr_street2'].required}
            install_addr_city_id = {'key':'install_addr_city_id','type':service_req_obj._fields['install_addr_city_id'].type,'title':service_req_obj._fields['install_addr_city_id'].string,
                           'required':service_req_obj._fields['install_addr_city_id'].required,
                           'value':[{'id':field.id,'value':field.name,'state_id':field.state_id.id} for field in custoemr_city_obj]}
            install_addr_state_id = {'key':'install_addr_state_id','type':service_req_obj._fields['install_addr_state_id'].type,'title':service_req_obj._fields['install_addr_state_id'].string,
                           'required':service_req_obj._fields['install_addr_state_id'].required,
                           'value':[{'id':field.id,'value':field.name,} for field in customer_state_obj]}
            install_addr_zip = {'key':'install_addr_zip','type':service_req_obj._fields['install_addr_zip'].type,'title':service_req_obj._fields['install_addr_zip'].string,'required':service_req_obj._fields['install_addr_zip'].required}
            install_addr_country_id = {'key':'install_addr_country_id','type':service_req_obj._fields['install_addr_country_id'].type,'title':service_req_obj._fields['install_addr_country_id'].string,
                           'required':service_req_obj._fields['install_addr_country_id'].required,
                           'value':[{'id':field.id,'value':field.name,} for field in customer_country_obj]}
            dealer_distributor_name = {'key':'dealer_distributor_name','type':service_req_obj._fields['dealer_distributor_name'].type,'title':service_req_obj._fields['dealer_distributor_name'].string,'required':service_req_obj._fields['dealer_distributor_name'].required}
            # CALL DETAILS
            call_source_id = {'key':'call_source_id','type':service_req_obj._fields['call_source_id'].type,'title':service_req_obj._fields['call_source_id'].string,'required':service_req_obj._fields['email'].required,'value':[{'id':field.id,'value':field.name,} for field in call_source_obj]}
            service_type_id= {'key':'service_type_id','type':service_req_obj._fields['service_type_id'].type,
                              'title':service_req_obj._fields['service_type_id'].string,
                              'required':service_req_obj._fields['service_type_id'].required,
                              'value':[{'id':field.id,'value':field.name,} for field in service_type_obj]}
            service_category_id = {'key':'service_category_id','type':service_req_obj._fields['service_category_id'].type,'title':service_req_obj._fields['service_category_id'].string,'required':service_req_obj._fields['service_category_id'].required,'value':[{'id':field.id,'value':field.name,} for field in service_category_ids]}
            request_type_id = {'key':'request_type_id','type':service_req_obj._fields['request_type_id'].type,'title':service_req_obj._fields['request_type_id'].string,'required':service_req_obj._fields['request_type_id'].required,'value':[{'id':field.id,'value':field.name,} for field in request_type_ids]}
            reason = {'key':'reason','type':service_req_obj._fields['reason'].type,'title':service_req_obj._fields['reason'].string,'required':False}
            problem_reported = {'key':'problem_reported','type':service_req_obj._fields['problem_reported'].type,
                                'title':service_req_obj._fields['problem_reported'].string,'required': False}
            requested_by_name = {'key':'requested_by_name','type':service_req_obj._fields['requested_by_name'].type,'title':service_req_obj._fields['requested_by_name'].string,'required':service_req_obj._fields['requested_by_name'].required}
            requested_by_contact_number = {'key':'requested_by_contact_number','type':service_req_obj._fields['requested_by_contact_number'].type,'title':service_req_obj._fields['requested_by_contact_number'].string,'required':service_req_obj._fields['requested_by_contact_number'].required}
            requested_by_email = {'key': 'requested_by_email',
                                  'type': service_req_obj._fields['requested_by_email'].type,
                                  'title': service_req_obj._fields['requested_by_email'].string,
                                  'required': service_req_obj._fields['requested_by_email'].required}
            requested_by_title = {'key': 'requested_by_title',
                                  'type': service_req_obj._fields['requested_by_title'].type,
                                  'title': service_req_obj._fields['requested_by_title'].string,
                                  'required': service_req_obj._fields['requested_by_title'].required}
            call_received_id = {'key':'call_received_id','type':service_req_obj._fields['call_received_id'].type,'title':service_req_obj._fields['call_received_id'].string,'required':service_req_obj._fields['call_received_id'].required,'value':[{'id':field.id,'value':field.name,} for field in call_received_ids]}
            team_id = {'key':'team_id','type':service_req_obj._fields['team_id'].type,'title':service_req_obj._fields['team_id'].string,'required':service_req_obj._fields['team_id'].required,'value':[{'id':field.id,'value':field.name,} for field in team_ids]}
            # ASSET DETAILS
            product_name = {'key':'product_name','type':service_req_obj._fields['product_name'].type,'title':service_req_obj._fields['product_name'].string,'required':service_req_obj._fields['product_name'].required}
            custom_product_serial = {'key':'custom_product_serial','type':service_req_obj._fields['custom_product_serial'].type,'title':service_req_obj._fields['custom_product_serial'].string,'required':service_req_obj._fields['custom_product_serial'].required}
            product_part_number = {'key':'product_part_number','type':service_req_obj._fields['product_part_number'].type,'title':service_req_obj._fields['product_part_number'].string,'required':service_req_obj._fields['product_part_number'].required}
            product_part_code = {'key':'product_part_code','type':service_req_obj._fields['product_part_code'].type,'title':service_req_obj._fields['product_part_code'].string,'required':service_req_obj._fields['product_part_code'].required}
            # INSTALLATION INFORMATION
            location_contact_person = {'key':'location_contact_person','type':service_req_obj._fields['location_contact_person'].type,'title':service_req_obj._fields['location_contact_person'].string,'required':service_req_obj._fields['location_contact_person'].required}
            customer_po_number = {'key':'customer_po_number','type':service_req_obj._fields['customer_po_number'].type,'title':service_req_obj._fields['customer_po_number'].string,'required':service_req_obj._fields['customer_po_number'].required}
            customer_po_date = {'key':'customer_po_date','type':service_req_obj._fields['customer_po_date'].type,'title':service_req_obj._fields['customer_po_date'].string,'required':service_req_obj._fields['customer_po_date'].required,'value':str(fields.Datetime.now().strftime('%Y-%m-%d'))}
            tender_refer_number = {'key':'tender_refer_number','type':service_req_obj._fields['tender_refer_number'].type,'title':service_req_obj._fields['tender_refer_number'].string,'required':service_req_obj._fields['tender_refer_number'].required}
            order_number = {'key':'order_number','type':service_req_obj._fields['order_number'].type,'title':service_req_obj._fields['order_number'].string,'required':service_req_obj._fields['order_number'].required}
            installation_date = {'key':'installation_date','type':service_req_obj._fields['installation_date'].type,'title':service_req_obj._fields['installation_date'].string,'required':service_req_obj._fields['installation_date'].required,'value':str(fields.Datetime.now().strftime('%Y-%m-%d'))}
            invoice_number = {'key':'invoice_number','type':service_req_obj._fields['invoice_number'].type,'title':service_req_obj._fields['invoice_number'].string,'required':service_req_obj._fields['invoice_number'].required}
            invoice_date = {'key':'invoice_date','type':service_req_obj._fields['invoice_date'].type,'title':service_req_obj._fields['invoice_date'].string,'required':service_req_obj._fields['invoice_date'].required,'value':str(fields.Datetime.now().strftime('%Y-%m-%d'))}
            extended_invoice_number = {'key':'extended_invoice_number','type':service_req_obj._fields['extended_invoice_number'].type,'title':service_req_obj._fields['extended_invoice_number'].string,'required':service_req_obj._fields['extended_invoice_number'].required}
            extended_invoice_date = {'key':'extended_invoice_date','type':service_req_obj._fields['extended_invoice_date'].type,'title':service_req_obj._fields['extended_invoice_date'].string,'required':service_req_obj._fields['extended_invoice_date'].required,'value':str(fields.Datetime.now().strftime('%Y-%m-%d'))}
            # OTHER INFORMATION
            remarks = {'key': 'remarks', 'type': service_req_obj._fields['remarks'].type,
                       'title': service_req_obj._fields['remarks'].string,
                       'required': service_req_obj._fields['remarks'].required}
            # survey_id = {'key':'survey_id','type':service_req_obj._fields['survey_id'].type,'title':service_req_obj._fields['survey_id'].string,
            #              'required':service_req_obj._fields['survey_id'].required,
            #              'value':[{'id':field.id,'value':field.title,} for field in survey_obj]}
            company_id = {'key': 'company_id', 'type': service_req_obj._fields['company_id'].type,
                          'title': service_req_obj._fields['company_id'].string,
                          'required': service_req_obj._fields['company_id'].required,
                          'value': [{'id': field.id, 'value': field.name, } for field in company_ids]}
            user_id = {'key': 'user_id', 'type': service_req_obj._fields['user_id'].type,
                       'title': service_req_obj._fields['user_id'].string,
                       'required': service_req_obj._fields['user_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in user_ids]}
            # oem_warranty_status_id = {'key':'oem_warranty_status_id','type':service_req_obj._fields['oem_warranty_status_id'].type,'title':service_req_obj._fields['oem_warranty_status_id'].string,'required':service_req_obj._fields['oem_warranty_status_id'].required,'value':[{'id':field.id,'value':field.name,} for field in oem_warranty_status_ids]}
            # repair_warranty_status_id = {'key':'repair_warranty_status_id','type':service_req_obj._fields['repair_warranty_status_id'].type,'title':service_req_obj._fields['repair_warranty_status_id'].string,'required':service_req_obj._fields['repair_warranty_status_id'].required,'value':[{'id':field.id,'value':field.name,} for field in repair_warranty_status_ids]}
            # phone = {'key': 'phone', 'type': service_req_obj._fields['phone'].type,
            #            'title': service_req_obj._fields['phone'].string,
            #            'required': service_req_obj._fields['phone'].required}

            service_list.append([service_request_date,
                                 customer_name,customer_email,customer_street,customer_street2,customer_city_id,
                                 customer_state_id,customer_zip,customer_country_id,is_same_customer_address,install_addr_street,install_addr_street2,
                                 install_addr_city_id,install_addr_state_id,install_addr_zip,install_addr_country_id,dealer_distributor_name,
                                 call_source_id,service_type_id,service_category_id,request_type_id,reason,problem_reported,
                                 requested_by_name,requested_by_contact_number,requested_by_email,requested_by_title,call_received_id,team_id,
                                 product_name,custom_product_serial,product_part_number,product_part_code,
                                 location_contact_person,customer_po_number,customer_po_date,tender_refer_number,order_number,installation_date,
                                 invoice_number,invoice_date,extended_invoice_number,extended_invoice_date,
                                 remarks,company_id,user_id,])
        elif ticket_type == 'sr_fsm':
            # SERVICE REQUEST INFORMATION
            service_request_id_alias = {'key': 'service_request_id_alias',
                                        'type': service_req_obj._fields['service_request_id_alias'].type,
                                        'title': service_req_obj._fields['service_request_id_alias'].string,
                                        'required': service_req_obj._fields['service_request_id_alias'].required}
            service_request_date = {'key': 'service_request_date',
                                    'type': service_req_obj._fields['service_request_date'].type,
                                    'title': service_req_obj._fields['service_request_date'].string,
                                    'required': service_req_obj._fields['service_request_date'].required,
                                    'value': str(fields.Datetime.now())}
            # approver_id = {'key': 'approver_id', 'type': service_req_obj._fields['approver_id'].type,
            #                'title': service_req_obj._fields['approver_id'].string,
            #                'required': service_req_obj._fields['approver_id'].required,
            #                'value': [{'id': field.id, 'value': field.name, } for field in approver_obj]}
            # child_ticket_type_id = {'key': 'child_ticket_type_id',
            #                         'type': service_req_obj._fields['child_ticket_type_id'].type,
            #                         'title': service_req_obj._fields['child_ticket_type_id'].string,
            #                         'required': service_req_obj._fields['child_ticket_type_id'].required,
            #                         'value': [{'id': field.id, 'value': field.name, } for field in child_ticket_type]}

            # CUSTOMER INFORMATION
            customer_name = {'key': 'customer_name', 'type': service_req_obj._fields['customer_name'].type,
                             'title': service_req_obj._fields['customer_name'].string,
                             'required': True}
            customer_email = {'key': 'customer_email', 'type': service_req_obj._fields['customer_email'].type,
                              'title': service_req_obj._fields['customer_email'].string,
                              'required': service_req_obj._fields['customer_email'].required}
            customer_street = {'key': 'customer_street', 'type': service_req_obj._fields['customer_street'].type,
                               'title': service_req_obj._fields['customer_street'].string,
                               'required': service_req_obj._fields['customer_street'].required}
            customer_street2 = {'key': 'customer_street2', 'type': service_req_obj._fields['customer_street2'].type,
                                'title': service_req_obj._fields['customer_street2'].string,
                                'required': service_req_obj._fields['customer_street2'].required}
            customer_city_id = {'key': 'customer_city_id', 'type': service_req_obj._fields['customer_city_id'].type,
                                'title': service_req_obj._fields['customer_city_id'].string,
                                'required': service_req_obj._fields['customer_city_id'].required,
                                'value': [{'id': field.id, 'value': field.name,'state_id':field.state_id.id} for field in custoemr_city_obj]}
            customer_state_id = {'key': 'customer_state_id', 'type': service_req_obj._fields['customer_state_id'].type,
                                 'title': service_req_obj._fields['customer_state_id'].string,
                                 'required': service_req_obj._fields['customer_state_id'].required,
                                 'value': [{'id': field.id, 'value': field.name, } for field in customer_state_obj]}
            customer_zip = {'key': 'customer_zip', 'type': service_req_obj._fields['customer_zip'].type,
                            'title': service_req_obj._fields['customer_zip'].string,
                            'required': service_req_obj._fields['customer_zip'].required}
            customer_country_id = {'key': 'customer_country_id',
                                   'type': service_req_obj._fields['customer_country_id'].type,
                                   'title': service_req_obj._fields['customer_country_id'].string,
                                   'required': service_req_obj._fields['customer_country_id'].required,
                                   'value': [{'id': field.id, 'value': field.name, } for field in customer_country_obj]}
            dealer_distributor_name = {'key': 'dealer_distributor_name',
                                       'type': service_req_obj._fields['dealer_distributor_name'].type,
                                       'title': service_req_obj._fields['dealer_distributor_name'].string,
                                       'required': service_req_obj._fields['dealer_distributor_name'].required}
            # CALL DETAILS
            call_source_id = {'key': 'call_source_id', 'type': service_req_obj._fields['call_source_id'].type,
                              'title': service_req_obj._fields['call_source_id'].string,
                              'required': service_req_obj._fields['email'].required,
                              'value': [{'id': field.id, 'value': field.name, } for field in call_source_obj]}
            service_type_id = {'key': 'service_type_id', 'type': service_req_obj._fields['service_type_id'].type,
                               'title': service_req_obj._fields['service_type_id'].string,
                               'required': service_req_obj._fields['service_type_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in service_type_obj]}
            service_category_id = {'key': 'service_category_id',
                                   'type': service_req_obj._fields['service_category_id'].type,
                                   'title': service_req_obj._fields['service_category_id'].string,
                                   'required': service_req_obj._fields['service_category_id'].required,
                                   'value': [{'id': field.id, 'value': field.name, } for field in service_category_ids]}
            request_type_id = {'key': 'request_type_id', 'type': service_req_obj._fields['request_type_id'].type,
                               'title': service_req_obj._fields['request_type_id'].string,
                               'required': service_req_obj._fields['request_type_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in request_type_ids]}
            reason = {'key': 'reason', 'type': service_req_obj._fields['reason'].type,
                      'title': service_req_obj._fields['reason'].string,
                      'required': service_req_obj._fields['reason'].required}
            problem_reported = {'key': 'problem_reported', 'type': service_req_obj._fields['problem_reported'].type,
                                'title': service_req_obj._fields['problem_reported'].string,
                                'required': service_req_obj._fields['problem_reported'].required}
            requested_by_name = {'key': 'requested_by_name', 'type': service_req_obj._fields['requested_by_name'].type,
                                 'title': service_req_obj._fields['requested_by_name'].string,
                                 'required': service_req_obj._fields['requested_by_name'].required}
            requested_by_contact_number = {'key': 'requested_by_contact_number',
                                           'type': service_req_obj._fields['requested_by_contact_number'].type,
                                           'title': service_req_obj._fields['requested_by_contact_number'].string,
                                           'required': service_req_obj._fields['requested_by_contact_number'].required}
            requested_by_email = {'key': 'requested_by_email',
                                  'type': service_req_obj._fields['requested_by_email'].type,
                                  'title': service_req_obj._fields['requested_by_email'].string,
                                  'required': service_req_obj._fields['requested_by_email'].required}
            requested_by_title = {'key': 'requested_by_title',
                                  'type': service_req_obj._fields['requested_by_title'].type,
                                  'title': service_req_obj._fields['requested_by_title'].string,
                                  'required': service_req_obj._fields['requested_by_title'].required}
            call_received_id = {'key': 'call_received_id', 'type': service_req_obj._fields['call_received_id'].type,
                                'title': service_req_obj._fields['call_received_id'].string,
                                'required': service_req_obj._fields['call_received_id'].required,
                                'value': [{'id': field.id, 'value': field.name, } for field in call_received_ids]}
            team_id = {'key': 'team_id', 'type': service_req_obj._fields['team_id'].type,
                       'title': service_req_obj._fields['team_id'].string,
                       'required': service_req_obj._fields['team_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in team_ids]}

            # ASSET DETAILS
            product_name = {'key': 'product_name', 'type': service_req_obj._fields['product_name'].type,
                            'title': service_req_obj._fields['product_name'].string,
                            'required': service_req_obj._fields['product_name'].required}
            custom_product_serial = {'key': 'custom_product_serial',
                                     'type': service_req_obj._fields['custom_product_serial'].type,
                                     'title': service_req_obj._fields['custom_product_serial'].string,
                                     'required': service_req_obj._fields['custom_product_serial'].required}
            product_part_number = {'key': 'product_part_number',
                                   'type': service_req_obj._fields['product_part_number'].type,
                                   'title': service_req_obj._fields['product_part_number'].string,
                                   'required': service_req_obj._fields['product_part_number'].required}
            product_part_code = {'key': 'product_part_code', 'type': service_req_obj._fields['product_part_code'].type,
                                 'title': service_req_obj._fields['product_part_code'].string,
                                 'required': service_req_obj._fields['product_part_code'].required}
            # OTHER INFORMATION
            remarks = {'key': 'remarks', 'type': service_req_obj._fields['remarks'].type,
                       'title': service_req_obj._fields['remarks'].string,
                       'required': service_req_obj._fields['remarks'].required}
            event_date = {'key': 'event_date',
                                    'type': service_req_obj._fields['event_date'].type,
                                    'title': service_req_obj._fields['event_date'].string,
                                    'required': service_req_obj._fields['event_date'].required,
                                    'value': str(fields.Datetime.now().strftime('%Y-%m-%d'))}
            issue_noticed = {'key': 'issue_noticed', 'type': service_req_obj._fields['issue_noticed'].type,
                       'title': service_req_obj._fields['issue_noticed'].string,
                       'required': service_req_obj._fields['issue_noticed'].required}
            case_completed_successfully_id = {'key': 'team_id', 'type': service_req_obj._fields['case_completed_successfully_id'].type,
                       'title': service_req_obj._fields['case_completed_successfully_id'].string,
                       'required': service_req_obj._fields['case_completed_successfully_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in case_completed_successfully_obj]}
            medical_intervention_id = {'key': 'medical_intervention_id', 'type': service_req_obj._fields['medical_intervention_id'].type,
                       'title': service_req_obj._fields['medical_intervention_id'].string,
                       'required': service_req_obj._fields['medical_intervention_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in medical_intervention_obj]}
            patient_involved_id = {'key': 'patient_involved_id', 'type': service_req_obj._fields['patient_involved_id'].type,
                       'title': service_req_obj._fields['patient_involved_id'].string,
                       'required': service_req_obj._fields['patient_involved_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in patient_involved_obj]}
            surgical_delay_id = {'key': 'surgical_delay_id', 'type': service_req_obj._fields['surgical_delay_id'].type,
                       'title': service_req_obj._fields['surgical_delay_id'].string,
                       'required': service_req_obj._fields['surgical_delay_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in surgical_delay_obj]}
            select_adverse_consequences = {'key':'select_adverse_consequences','type':service_req_obj._fields['select_adverse_consequences'].type,
                                           'title':service_req_obj._fields['select_adverse_consequences'].string,
                                           'required':service_req_obj._fields['select_adverse_consequences'].required,
                                           'value':[{'id':field,'value':select_adverse_consequences_values.get(field),} for field in select_adverse_consequences_values]}
            complaint_type = {'key':'complaint_type','type':service_req_obj._fields['complaint_type'].type,
                                           'title':service_req_obj._fields['complaint_type'].string,
                                           'required':service_req_obj._fields['complaint_type'].required,
                                           'value':[{'id':field,'value':complaint_type_values.get(field),} for field in complaint_type_values]}
            # survey_id = {'key': 'survey_id', 'type': service_req_obj._fields['survey_id'].type,
            #              'title': service_req_obj._fields['survey_id'].string,
            #              'required': service_req_obj._fields['survey_id'].required,
            #              'value': [{'id': field.id, 'value': field.title, } for field in survey_obj]}
            company_id = {'key': 'company_id', 'type': service_req_obj._fields['company_id'].type,
                          'title': service_req_obj._fields['company_id'].string,
                          'required': service_req_obj._fields['company_id'].required,
                          'value': [{'id': field.id, 'value': field.name, } for field in company_ids]}
            user_id = {'key': 'user_id', 'type': service_req_obj._fields['user_id'].type,
                       'title': service_req_obj._fields['user_id'].string,
                       'required': service_req_obj._fields['user_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in user_ids]}
            service_list.append([service_request_id_alias,service_request_date,
                                 customer_name,customer_email,customer_street,customer_street2,customer_city_id,
                                 customer_state_id,customer_zip,customer_country_id,dealer_distributor_name,
                                 call_source_id,service_type_id,service_category_id,request_type_id,reason,
                                 problem_reported,requested_by_name,requested_by_contact_number,requested_by_email,
                                 requested_by_title,call_received_id,team_id,
                                 product_name,custom_product_serial,product_part_number,product_part_code,
                                 remarks,event_date,issue_noticed,case_completed_successfully_id,medical_intervention_id,
                                 patient_involved_id,surgical_delay_id,select_adverse_consequences,complaint_type,
                                 company_id,user_id])

        elif ticket_type == 'sr_loaner':
            # SERVICE REQUEST INFORMATION
            service_request_id_alias = {'key': 'service_request_id_alias',
                                        'type': service_req_obj._fields['service_request_id_alias'].type,
                                        'title': service_req_obj._fields['service_request_id_alias'].string,
                                        'required': service_req_obj._fields['service_request_id_alias'].required}
            service_request_date = {'key': 'service_request_date',
                                    'type': service_req_obj._fields['service_request_date'].type,
                                    'title': service_req_obj._fields['service_request_date'].string,
                                    'required': service_req_obj._fields['service_request_date'].required,
                                    'value': str(fields.Datetime.now())}
            # approver_id = {'key': 'approver_id', 'type': service_req_obj._fields['approver_id'].type,
            #                'title': service_req_obj._fields['approver_id'].string,
            #                'required': service_req_obj._fields['approver_id'].required,
            #                'value': [{'id': field.id, 'value': field.name, } for field in approver_obj]}
            child_ticket_type_id = {'key': 'child_ticket_type_id',
                                    'type': service_req_obj._fields['child_ticket_type_id'].type,
                                    'title': service_req_obj._fields['child_ticket_type_id'].string,
                                    'required': service_req_obj._fields['child_ticket_type_id'].required,
                                    'value': [{'id': field.id, 'value': field.name, } for field in child_ticket_type]}
            # CALL DETAILS
            call_source_id = {'key': 'call_source_id', 'type': service_req_obj._fields['call_source_id'].type,
                              'title': service_req_obj._fields['call_source_id'].string,
                              'required': service_req_obj._fields['email'].required,
                              'value': [{'id': field.id, 'value': field.name, } for field in call_source_obj]}
            service_type_id = {'key': 'service_type_id', 'type': service_req_obj._fields['service_type_id'].type,
                               'title': service_req_obj._fields['service_type_id'].string,
                               'required': service_req_obj._fields['service_type_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in service_type_obj]}
            service_category_id = {'key': 'service_category_id',
                                   'type': service_req_obj._fields['service_category_id'].type,
                                   'title': service_req_obj._fields['service_category_id'].string,
                                   'required': service_req_obj._fields['service_category_id'].required,
                                   'value': [{'id': field.id, 'value': field.name, } for field in service_category_ids]}
            request_type_id = {'key': 'request_type_id', 'type': service_req_obj._fields['request_type_id'].type,
                               'title': service_req_obj._fields['request_type_id'].string,
                               'required': service_req_obj._fields['request_type_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in request_type_ids]}
            reason = {'key': 'reason', 'type': service_req_obj._fields['reason'].type,
                      'title': service_req_obj._fields['reason'].string,
                      'required': service_req_obj._fields['reason'].required}
            requested_by_name = {'key': 'requested_by_name', 'type': service_req_obj._fields['requested_by_name'].type,
                                 'title': service_req_obj._fields['requested_by_name'].string,
                                 'required': service_req_obj._fields['requested_by_name'].required}
            call_received_id = {'key': 'call_received_id', 'type': service_req_obj._fields['call_received_id'].type,
                                'title': service_req_obj._fields['call_received_id'].string,
                                'required': service_req_obj._fields['call_received_id'].required,
                                'value': [{'id': field.id, 'value': field.name, } for field in call_received_ids]}
            team_id = {'key': 'team_id', 'type': service_req_obj._fields['team_id'].type,
                       'title': service_req_obj._fields['team_id'].string,
                       'required': service_req_obj._fields['team_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in team_ids]}
            # OTHER INFORMATION
            remarks = {'key': 'remarks', 'type': service_req_obj._fields['remarks'].type,
                       'title': service_req_obj._fields['remarks'].string,
                       'required': service_req_obj._fields['remarks'].required}
            survey_id = {'key': 'survey_id', 'type': service_req_obj._fields['survey_id'].type,
                         'title': service_req_obj._fields['survey_id'].string,
                         'required': service_req_obj._fields['survey_id'].required,
                         'value': [{'id': field.id, 'value': field.title, } for field in survey_obj]}
            user_id = {'key': 'user_id', 'type': service_req_obj._fields['user_id'].type,
                       'title': service_req_obj._fields['user_id'].string,
                       'required': service_req_obj._fields['user_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in user_ids]}
            service_list.append([service_request_id_alias,service_request_date,child_ticket_type_id,
                                 call_source_id,service_type_id,service_category_id,request_type_id,reason,
                                 requested_by_name,call_received_id,team_id,remarks,survey_id,user_id])
        elif ticket_type == 'sr_wr':
            # SERVICE REQUEST INFORMATION
            # service_request_id_alias = {'key': 'service_request_id_alias',
            #                             'type': service_req_obj._fields['service_request_id_alias'].type,
            #                             'title': service_req_obj._fields['service_request_id_alias'].string,
            #                             'required': service_req_obj._fields['service_request_id_alias'].required}
            service_request_date = {'key': 'service_request_date',
                                    'type': service_req_obj._fields['service_request_date'].type,
                                    'title': service_req_obj._fields['service_request_date'].string,
                                    'required': service_req_obj._fields['service_request_date'].required,
                                    'value': str(fields.Datetime.now())}
            # CALL DETAILS
            call_source_id = {'key': 'call_source_id', 'type': service_req_obj._fields['call_source_id'].type,
                              'title': service_req_obj._fields['call_source_id'].string,
                              'required': service_req_obj._fields['email'].required,
                              'value': [{'id': field.id, 'value': field.name, } for field in call_source_obj]}
            service_type_id = {'key': 'service_type_id', 'type': service_req_obj._fields['service_type_id'].type,
                               'title': service_req_obj._fields['service_type_id'].string,
                               'required': service_req_obj._fields['service_type_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in service_type_obj]}
            service_category_id = {'key': 'service_category_id',
                                   'type': service_req_obj._fields['service_category_id'].type,
                                   'title': service_req_obj._fields['service_category_id'].string,
                                   'required': service_req_obj._fields['service_category_id'].required,
                                   'value': [{'id': field.id, 'value': field.name, } for field in service_category_ids]}
            request_type_id = {'key': 'request_type_id', 'type': service_req_obj._fields['request_type_id'].type,
                               'title': service_req_obj._fields['request_type_id'].string,
                               'required': service_req_obj._fields['request_type_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in request_type_ids]}
            reason = {'key': 'reason', 'type': service_req_obj._fields['reason'].type,
                      'title': service_req_obj._fields['reason'].string,
                      'required': service_req_obj._fields['reason'].required}
            requested_by_name = {'key': 'requested_by_name', 'type': service_req_obj._fields['requested_by_name'].type,
                                 'title': service_req_obj._fields['requested_by_name'].string,
                                 'required': service_req_obj._fields['requested_by_name'].required}
            requested_by_email = {'key': 'requested_by_email', 'type': service_req_obj._fields['requested_by_email'].type,
                                 'title': service_req_obj._fields['requested_by_email'].string,
                                 'required': service_req_obj._fields['requested_by_email'].required}
            requested_by_title = {'key': 'requested_by_title', 'type': service_req_obj._fields['requested_by_title'].type,
                                 'title': service_req_obj._fields['requested_by_title'].string,
                                 'required': service_req_obj._fields['requested_by_title'].required}
            alternate_contact_name = {'key': 'alternate_contact_name', 'type': service_req_obj._fields['alternate_contact_name'].type,
                                 'title': service_req_obj._fields['alternate_contact_name'].string,
                                 'required': service_req_obj._fields['alternate_contact_name'].required }
            alternate_contact_number = {'key': 'alternate_contact_number', 'type': service_req_obj._fields['alternate_contact_number'].type,
                                 'title': service_req_obj._fields['alternate_contact_number'].string,
                                 'required': service_req_obj._fields['alternate_contact_number'].required }
            alternate_contact_email = {'key': 'alternate_contact_email',
                                        'type': service_req_obj._fields['alternate_contact_email'].type,
                                        'title': service_req_obj._fields['alternate_contact_email'].string,
                                        'required': service_req_obj._fields['alternate_contact_email'].required}
            call_received_id = {'key': 'call_received_id', 'type': service_req_obj._fields['call_received_id'].type,
                                'title': service_req_obj._fields['call_received_id'].string,
                                'required': service_req_obj._fields['call_received_id'].required,
                                'value': [{'id': field.id, 'value': field.name, } for field in call_received_ids]}
            team_id = {'key': 'team_id', 'type': service_req_obj._fields['team_id'].type,
                       'title': service_req_obj._fields['team_id'].string,
                       'required': service_req_obj._fields['team_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in team_ids]}
            # OTHER INFORMATION
            remarks = {'key': 'remarks', 'type': service_req_obj._fields['remarks'].type,
                       'title': service_req_obj._fields['remarks'].string,
                       'required': service_req_obj._fields['remarks'].required}
            # survey_id = {'key': 'survey_id', 'type': service_req_obj._fields['survey_id'].type,
            #              'title': service_req_obj._fields['survey_id'].string,
            #              'required': service_req_obj._fields['survey_id'].required,
            #              'value': [{'id': field.id, 'value': field.title, } for field in survey_obj]}
            user_id = {'key': 'user_id', 'type': service_req_obj._fields['user_id'].type,
                       'title': service_req_obj._fields['user_id'].string,
                       'required': service_req_obj._fields['user_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in user_ids]}
            service_list.append([ service_request_date,
                                 call_source_id, service_type_id, service_category_id, request_type_id,reason,requested_by_name,
                                  requested_by_email,
                                  requested_by_title,alternate_contact_name,alternate_contact_number,alternate_contact_email,
                                  call_received_id, team_id, remarks, user_id])
        elif ticket_type == 'sr_factory_repair':
            # SERVICE REQUEST INFORMATION
            service_request_id_alias = {'key': 'service_request_id_alias',
                                        'type': service_req_obj._fields['service_request_id_alias'].type,
                                        'title': service_req_obj._fields['service_request_id_alias'].string,
                                        'required': service_req_obj._fields['service_request_id_alias'].required}
            service_request_date = {'key': 'service_request_date',
                                    'type': service_req_obj._fields['service_request_date'].type,
                                    'title': service_req_obj._fields['service_request_date'].string,
                                    'required': service_req_obj._fields['service_request_date'].required,
                                    'value': str(fields.Datetime.now())}
            # CALL DETAILS
            call_source_id = {'key': 'call_source_id', 'type': service_req_obj._fields['call_source_id'].type,
                              'title': service_req_obj._fields['call_source_id'].string,
                              'required': service_req_obj._fields['email'].required,
                              'value': [{'id': field.id, 'value': field.name, } for field in call_source_obj]}
            service_type_id = {'key': 'service_type_id', 'type': service_req_obj._fields['service_type_id'].type,
                               'title': service_req_obj._fields['service_type_id'].string,
                               'required': service_req_obj._fields['service_type_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in service_type_obj]}
            service_category_id = {'key': 'service_category_id',
                                   'type': service_req_obj._fields['service_category_id'].type,
                                   'title': service_req_obj._fields['service_category_id'].string,
                                   'required': service_req_obj._fields['service_category_id'].required,
                                   'value': [{'id': field.id, 'value': field.name, } for field in service_category_ids]}
            request_type_id = {'key': 'request_type_id', 'type': service_req_obj._fields['request_type_id'].type,
                               'title': service_req_obj._fields['request_type_id'].string,
                               'required': service_req_obj._fields['request_type_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in request_type_ids]}
            reason = {'key': 'reason', 'type': service_req_obj._fields['reason'].type,
                      'title': service_req_obj._fields['reason'].string,
                      'required': service_req_obj._fields['reason'].required}
            problem_reported = {'key': 'problem_reported', 'type': service_req_obj._fields['problem_reported'].type,
                                'title': service_req_obj._fields['problem_reported'].string,
                                'required': service_req_obj._fields['problem_reported'].required}
            requested_by_name = {'key': 'requested_by_name', 'type': service_req_obj._fields['requested_by_name'].type,
                                 'title': service_req_obj._fields['requested_by_name'].string,
                                 'required': service_req_obj._fields['requested_by_name'].required}
            requested_by_contact_number = {'key': 'requested_by_contact_number',
                                           'type': service_req_obj._fields['requested_by_contact_number'].type,
                                           'title': service_req_obj._fields['requested_by_contact_number'].string,
                                           'required': service_req_obj._fields['requested_by_contact_number'].required}
            call_received_id = {'key': 'call_received_id', 'type': service_req_obj._fields['call_received_id'].type,
                                'title': service_req_obj._fields['call_received_id'].string,
                                'required': service_req_obj._fields['call_received_id'].required,
                                'value': [{'id': field.id, 'value': field.name, } for field in call_received_ids]}
            team_id = {'key': 'team_id', 'type': service_req_obj._fields['team_id'].type,
                       'title': service_req_obj._fields['team_id'].string,
                       'required': service_req_obj._fields['team_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in team_ids]}
            # OTHER INFORMATION
            remarks = {'key': 'remarks', 'type': service_req_obj._fields['remarks'].type,
                       'title': service_req_obj._fields['remarks'].string,
                       'required': service_req_obj._fields['remarks'].required}
            issue_noticed = {'key': 'issue_noticed', 'type': service_req_obj._fields['issue_noticed'].type,
                             'title': service_req_obj._fields['issue_noticed'].string,
                             'required': service_req_obj._fields['issue_noticed'].required}
            case_completed_successfully_id = {'key': 'team_id',
                                              'type': service_req_obj._fields['case_completed_successfully_id'].type,
                                              'title': service_req_obj._fields['case_completed_successfully_id'].string,
                                              'required': service_req_obj._fields[
                                                  'case_completed_successfully_id'].required,
                                              'value': [{'id': field.id, 'value': field.name, } for field in
                                                        case_completed_successfully_obj]}
            medical_intervention_id = {'key': 'medical_intervention_id',
                                       'type': service_req_obj._fields['medical_intervention_id'].type,
                                       'title': service_req_obj._fields['medical_intervention_id'].string,
                                       'required': service_req_obj._fields['medical_intervention_id'].required,
                                       'value': [{'id': field.id, 'value': field.name, } for field in
                                                 medical_intervention_obj]}
            patient_involved_id = {'key': 'patient_involved_id',
                                   'type': service_req_obj._fields['patient_involved_id'].type,
                                   'title': service_req_obj._fields['patient_involved_id'].string,
                                   'required': service_req_obj._fields['patient_involved_id'].required,
                                   'value': [{'id': field.id, 'value': field.name, } for field in patient_involved_obj]}
            surgical_delay_id = {'key': 'surgical_delay_id', 'type': service_req_obj._fields['surgical_delay_id'].type,
                                 'title': service_req_obj._fields['surgical_delay_id'].string,
                                 'required': service_req_obj._fields['surgical_delay_id'].required,
                                 'value': [{'id': field.id, 'value': field.name, } for field in surgical_delay_obj]}
            complaint_type = {'key': 'complaint_type', 'type': service_req_obj._fields['complaint_type'].type,
                              'title': service_req_obj._fields['complaint_type'].string,
                              'required': service_req_obj._fields['complaint_type'].required,
                              'value': [{'id': field, 'value': complaint_type_values.get(field), } for field in
                                        complaint_type_values]}
            # CUSTOMER INFORMATION
            customer_name = {'key': 'customer_name', 'type': service_req_obj._fields['customer_name'].type,
                             'title': service_req_obj._fields['customer_name'].string,
                             'required': service_req_obj._fields['customer_name'].required}
            customer_email = {'key': 'customer_email', 'type': service_req_obj._fields['customer_email'].type,
                              'title': service_req_obj._fields['customer_email'].string,
                              'required': service_req_obj._fields['customer_email'].required}
            customer_street = {'key': 'customer_street', 'type': service_req_obj._fields['customer_street'].type,
                               'title': service_req_obj._fields['customer_street'].string,
                               'required': service_req_obj._fields['customer_street'].required}
            customer_street2 = {'key': 'customer_street2', 'type': service_req_obj._fields['customer_street2'].type,
                                'title': service_req_obj._fields['customer_street2'].string,
                                'required': service_req_obj._fields['customer_street2'].required}
            customer_city_id = {'key': 'customer_city_id', 'type': service_req_obj._fields['customer_city_id'].type,
                                'title': service_req_obj._fields['customer_city_id'].string,
                                'required': service_req_obj._fields['customer_city_id',].required,
                                'value': [{'id': field.id, 'value': field.name,'state_id':field.state_id.id } for field in custoemr_city_obj]}
            customer_state_id = {'key': 'customer_state_id', 'type': service_req_obj._fields['customer_state_id'].type,
                                 'title': service_req_obj._fields['customer_state_id'].string,
                                 'required': service_req_obj._fields['customer_state_id'].required,
                                 'value': [{'id': field.id, 'value': field.name, } for field in customer_state_obj]}
            customer_zip = {'key': 'customer_zip', 'type': service_req_obj._fields['customer_zip'].type,
                            'title': service_req_obj._fields['customer_zip'].string,
                            'required': service_req_obj._fields['customer_zip'].required}
            customer_country_id = {'key': 'customer_country_id',
                                   'type': service_req_obj._fields['customer_country_id'].type,
                                   'title': service_req_obj._fields['customer_country_id'].string,
                                   'required': service_req_obj._fields['customer_country_id'].required,
                                   'value': [{'id': field.id, 'value': field.name, } for field in customer_country_obj]}
            dealer_distributor_name = {'key': 'dealer_distributor_name',
                                       'type': service_req_obj._fields['dealer_distributor_name'].type,
                                       'title': service_req_obj._fields['dealer_distributor_name'].string,
                                       'required': service_req_obj._fields['dealer_distributor_name'].required}
            # ASSET DETAILS
            product_name = {'key': 'product_name', 'type': service_req_obj._fields['product_name'].type,
                            'title': service_req_obj._fields['product_name'].string,
                            'required': service_req_obj._fields['product_name'].required}
            custom_product_serial = {'key': 'custom_product_serial',
                                     'type': service_req_obj._fields['custom_product_serial'].type,
                                     'title': service_req_obj._fields['custom_product_serial'].string,
                                     'required': service_req_obj._fields['custom_product_serial'].required}
            product_part_number = {'key': 'product_part_number',
                                   'type': service_req_obj._fields['product_part_number'].type,
                                   'title': service_req_obj._fields['product_part_number'].string,
                                   'required': service_req_obj._fields['product_part_number'].required}
            product_part_code = {'key': 'product_part_code', 'type': service_req_obj._fields['product_part_code'].type,
                                 'title': service_req_obj._fields['product_part_code'].string,
                                 'required': service_req_obj._fields['product_part_code'].required}
            # OTHER INFORMATION
            survey_id = {'key': 'survey_id', 'type': service_req_obj._fields['survey_id'].type,
                         'title': service_req_obj._fields['survey_id'].string,
                         'required': service_req_obj._fields['survey_id'].required,
                         'value': [{'id': field.id, 'value': field.title, } for field in survey_obj]}
            company_id = {'key': 'company_id', 'type': service_req_obj._fields['company_id'].type,
                          'title': service_req_obj._fields['company_id'].string,
                          'required': service_req_obj._fields['company_id'].required,
                          'value': [{'id': field.id, 'value': field.name, } for field in company_ids]}
            user_id = {'key': 'user_id', 'type': service_req_obj._fields['user_id'].type,
                       'title': service_req_obj._fields['user_id'].string,
                       'required': service_req_obj._fields['user_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in user_ids]}
            service_list.append([service_request_id_alias, service_request_date,
                                 call_source_id, service_type_id, service_category_id, request_type_id, reason,
                                problem_reported,requested_by_name,requested_by_contact_number,call_received_id,team_id,
                                remarks,issue_noticed,case_completed_successfully_id,medical_intervention_id,patient_involved_id,
                                 surgical_delay_id,complaint_type,customer_name,customer_email,customer_street,customer_street2,
                                 customer_city_id,customer_state_id,customer_zip,customer_country_id,dealer_distributor_name,product_name,
                                 custom_product_serial,product_part_number,product_part_code,survey_id,company_id,user_id])

        elif ticket_type == 'sr_maintenance':
            # SERVICE REQUEST INFORMATION
            # service_request_id_alias = {'key': 'service_request_id_alias',
            #                             'type': service_req_obj._fields['service_request_id_alias'].type,
            #                             'title': service_req_obj._fields['service_request_id_alias'].string,
            #                             'required': service_req_obj._fields['service_request_id_alias'].required}
            service_request_date = {'key': 'service_request_date',
                                    'type': service_req_obj._fields['service_request_date'].type,
                                    'title': service_req_obj._fields['service_request_date'].string,
                                    'required': service_req_obj._fields['service_request_date'].required,
                                    'value': str(fields.Datetime.now())}
            # CALL DETAILS
            call_source_id = {'key': 'call_source_id', 'type': service_req_obj._fields['call_source_id'].type,
                              'title': service_req_obj._fields['call_source_id'].string,
                              'required': service_req_obj._fields['email'].required,
                              'value': [{'id': field.id, 'value': field.name, } for field in call_source_obj]}
            service_type_id = {'key': 'service_type_id', 'type': service_req_obj._fields['service_type_id'].type,
                               'title': service_req_obj._fields['service_type_id'].string,
                               'required': service_req_obj._fields['service_type_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in service_type_obj]}
            service_category_id = {'key': 'service_category_id',
                                   'type': service_req_obj._fields['service_category_id'].type,
                                   'title': service_req_obj._fields['service_category_id'].string,
                                   'required': service_req_obj._fields['service_category_id'].required,
                                   'value': [{'id': field.id, 'value': field.name, } for field in service_category_ids]}
            request_type_id = {'key': 'request_type_id', 'type': service_req_obj._fields['request_type_id'].type,
                               'title': service_req_obj._fields['request_type_id'].string,
                               'required': service_req_obj._fields['request_type_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in request_type_ids]}
            reason = {'key': 'reason', 'type': service_req_obj._fields['reason'].type,
                      'title': service_req_obj._fields['reason'].string,
                      'required': service_req_obj._fields['reason'].required}
            problem_reported = {'key': 'problem_reported', 'type': service_req_obj._fields['problem_reported'].type,
                                'title': service_req_obj._fields['problem_reported'].string,
                                'required': service_req_obj._fields['problem_reported'].required}
            requested_by_name = {'key': 'requested_by_name', 'type': service_req_obj._fields['requested_by_name'].type,
                                 'title': service_req_obj._fields['requested_by_name'].string,
                                 'required': service_req_obj._fields['requested_by_name'].required}
            requested_by_contact_number = {'key': 'requested_by_contact_number',
                                           'type': service_req_obj._fields['requested_by_contact_number'].type,
                                           'title': service_req_obj._fields['requested_by_contact_number'].string,
                                           'required': service_req_obj._fields['requested_by_contact_number'].required}
            requested_by_email = {'key': 'requested_by_email',
                                  'type': service_req_obj._fields['requested_by_email'].type,
                                  'title': service_req_obj._fields['requested_by_email'].string,
                                  'required': service_req_obj._fields['requested_by_email'].required}
            requested_by_title = {'key': 'requested_by_title',
                                  'type': service_req_obj._fields['requested_by_title'].type,
                                  'title': service_req_obj._fields['requested_by_title'].string,
                                  'required': service_req_obj._fields['requested_by_title'].required}
            call_received_id = {'key': 'call_received_id', 'type': service_req_obj._fields['call_received_id'].type,
                                'title': service_req_obj._fields['call_received_id'].string,
                                'required': service_req_obj._fields['call_received_id'].required,
                                'value': [{'id': field.id, 'value': field.name, } for field in call_received_ids]}
            team_id = {'key': 'team_id', 'type': service_req_obj._fields['team_id'].type,
                       'title': service_req_obj._fields['team_id'].string,
                       'required': service_req_obj._fields['team_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in team_ids]}

            # CUSTOMER INFORMATION
            customer_name = {'key': 'customer_name', 'type': service_req_obj._fields['customer_name'].type,
                             'title': service_req_obj._fields['customer_name'].string,
                             'required': True}
            customer_email = {'key': 'customer_email', 'type': service_req_obj._fields['customer_email'].type,
                              'title': service_req_obj._fields['customer_email'].string,
                              'required': service_req_obj._fields['customer_email'].required}
            customer_street = {'key': 'customer_street', 'type': service_req_obj._fields['customer_street'].type,
                               'title': service_req_obj._fields['customer_street'].string,
                               'required': service_req_obj._fields['customer_street'].required}
            customer_street2 = {'key': 'customer_street2', 'type': service_req_obj._fields['customer_street2'].type,
                                'title': service_req_obj._fields['customer_street2'].string,
                                'required': service_req_obj._fields['customer_street2'].required}
            customer_city_id = {'key': 'customer_city_id', 'type': service_req_obj._fields['customer_city_id'].type,
                                'title': service_req_obj._fields['customer_city_id'].string,
                                'required': service_req_obj._fields['customer_city_id'].required,
                                'value': [{'id': field.id, 'value': field.name,'state_id':field.state_id.id, } for field in custoemr_city_obj]}
            customer_state_id = {'key': 'customer_state_id', 'type': service_req_obj._fields['customer_state_id'].type,
                                 'title': service_req_obj._fields['customer_state_id'].string,
                                 'required': service_req_obj._fields['customer_state_id'].required,
                                 'value': [{'id': field.id, 'value': field.name, } for field in customer_state_obj]}
            customer_zip = {'key': 'customer_zip', 'type': service_req_obj._fields['customer_zip'].type,
                            'title': service_req_obj._fields['customer_zip'].string,
                            'required': service_req_obj._fields['customer_zip'].required}
            customer_country_id = {'key': 'customer_country_id',
                                   'type': service_req_obj._fields['customer_country_id'].type,
                                   'title': service_req_obj._fields['customer_country_id'].string,
                                   'required': service_req_obj._fields['customer_country_id'].required,
                                   'value': [{'id': field.id, 'value': field.name, } for field in customer_country_obj]}
            dealer_distributor_name = {'key': 'dealer_distributor_name',
                                       'type': service_req_obj._fields['dealer_distributor_name'].type,
                                       'title': service_req_obj._fields['dealer_distributor_name'].string,
                                       'required': service_req_obj._fields['dealer_distributor_name'].required}
            # ASSET DETAILS
            product_name = {'key': 'product_name', 'type': service_req_obj._fields['product_name'].type,
                            'title': service_req_obj._fields['product_name'].string,
                            'required': service_req_obj._fields['product_name'].required}
            custom_product_serial = {'key': 'custom_product_serial',
                                     'type': service_req_obj._fields['custom_product_serial'].type,
                                     'title': service_req_obj._fields['custom_product_serial'].string,
                                     'required': service_req_obj._fields['custom_product_serial'].required}
            product_part_number = {'key': 'product_part_number',
                                   'type': service_req_obj._fields['product_part_number'].type,
                                   'title': service_req_obj._fields['product_part_number'].string,
                                   'required': service_req_obj._fields['product_part_number'].required}
            product_part_code = {'key': 'product_part_code', 'type': service_req_obj._fields['product_part_code'].type,
                                 'title': service_req_obj._fields['product_part_code'].string,
                                 'required': service_req_obj._fields['product_part_code'].required}
            # OTHER INFORMATION
            remarks = {'key': 'remarks', 'type': service_req_obj._fields['remarks'].type,
                       'title': service_req_obj._fields['remarks'].string,
                       'required': service_req_obj._fields['remarks'].required}
            survey_id = {'key': 'survey_id', 'type': service_req_obj._fields['survey_id'].type,
                         'title': service_req_obj._fields['survey_id'].string,
                         'required': service_req_obj._fields['survey_id'].required,
                         'value': [{'id': field.id, 'value': field.title, } for field in survey_obj]}
            company_id = {'key': 'company_id', 'type': service_req_obj._fields['company_id'].type,
                          'title': service_req_obj._fields['company_id'].string,
                          'required': service_req_obj._fields['company_id'].required,
                          'value': [{'id': field.id, 'value': field.name, } for field in company_ids]}
            user_id = {'key': 'user_id', 'type': service_req_obj._fields['user_id'].type,
                       'title': service_req_obj._fields['user_id'].string,
                       'required': service_req_obj._fields['user_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in user_ids]}

            service_list.append([ service_request_date,
                                 call_source_id, service_type_id, service_category_id, request_type_id, reason,
                                 problem_reported, requested_by_name, requested_by_contact_number,requested_by_email,
                                 requested_by_title, call_received_id,
                                 team_id,customer_name, customer_email, customer_street,
                                 customer_street2,
                                 customer_city_id, customer_state_id, customer_zip, customer_country_id,
                                 dealer_distributor_name, product_name,
                                 custom_product_serial, product_part_number, product_part_code,remarks, survey_id, company_id,
                                 user_id])

        elif ticket_type == 'sr_remote_support':
            # SERVICE REQUEST INFORMATION
            service_request_id_alias = {'key': 'service_request_id_alias',
                                        'type': service_req_obj._fields['service_request_id_alias'].type,
                                        'title': service_req_obj._fields['service_request_id_alias'].string,
                                        'required': service_req_obj._fields['service_request_id_alias'].required}
            service_request_date = {'key': 'service_request_date',
                                    'type': service_req_obj._fields['service_request_date'].type,
                                    'title': service_req_obj._fields['service_request_date'].string,
                                    'required': service_req_obj._fields['service_request_date'].required,
                                    'value': str(fields.Datetime.now())}
            # approver_id = {'key': 'approver_id', 'type': service_req_obj._fields['approver_id'].type,
            #                'title': service_req_obj._fields['approver_id'].string,
            #                'required': service_req_obj._fields['approver_id'].required,
            #                'value': [{'id': field.id, 'value': field.name, } for field in approver_obj]}
            child_ticket_type_id = {'key': 'child_ticket_type_id',
                                    'type': service_req_obj._fields['child_ticket_type_id'].type,
                                    'title': service_req_obj._fields['child_ticket_type_id'].string,
                                    'required': service_req_obj._fields['child_ticket_type_id'].required,
                                    'value': [{'id': field.id, 'value': field.name, } for field in child_ticket_type]}
            # CALL DETAILS
            call_source_id = {'key': 'call_source_id', 'type': service_req_obj._fields['call_source_id'].type,
                              'title': service_req_obj._fields['call_source_id'].string,
                              'required': service_req_obj._fields['email'].required,
                              'value': [{'id': field.id, 'value': field.name, } for field in call_source_obj]}
            service_type_id = {'key': 'service_type_id', 'type': service_req_obj._fields['service_type_id'].type,
                               'title': service_req_obj._fields['service_type_id'].string,
                               'required': service_req_obj._fields['service_type_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in service_type_obj]}
            service_category_id = {'key': 'service_category_id',
                                   'type': service_req_obj._fields['service_category_id'].type,
                                   'title': service_req_obj._fields['service_category_id'].string,
                                   'required': service_req_obj._fields['service_category_id'].required,
                                   'value': [{'id': field.id, 'value': field.name, } for field in service_category_ids]}
            request_type_id = {'key': 'request_type_id', 'type': service_req_obj._fields['request_type_id'].type,
                               'title': service_req_obj._fields['request_type_id'].string,
                               'required': service_req_obj._fields['request_type_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in request_type_ids]}
            reason = {'key': 'reason', 'type': service_req_obj._fields['reason'].type,
                      'title': service_req_obj._fields['reason'].string,
                      'required': service_req_obj._fields['reason'].required}
            problem_reported = {'key': 'problem_reported', 'type': service_req_obj._fields['problem_reported'].type,
                                'title': service_req_obj._fields['problem_reported'].string,
                                'required': service_req_obj._fields['problem_reported'].required}
            requested_by_name = {'key': 'requested_by_name', 'type': service_req_obj._fields['requested_by_name'].type,
                                 'title': service_req_obj._fields['requested_by_name'].string,
                                 'required': service_req_obj._fields['requested_by_name'].required}
            requested_by_contact_number = {'key': 'requested_by_contact_number',
                                           'type': service_req_obj._fields['requested_by_contact_number'].type,
                                           'title': service_req_obj._fields['requested_by_contact_number'].string,
                                           'required': service_req_obj._fields['requested_by_contact_number'].required}
            call_received_id = {'key': 'call_received_id', 'type': service_req_obj._fields['call_received_id'].type,
                                'title': service_req_obj._fields['call_received_id'].string,
                                'required': service_req_obj._fields['call_received_id'].required,
                                'value': [{'id': field.id, 'value': field.name, } for field in call_received_ids]}
            team_id = {'key': 'team_id', 'type': service_req_obj._fields['team_id'].type,
                       'title': service_req_obj._fields['team_id'].string,
                       'required': service_req_obj._fields['team_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in team_ids]}
            # OTHER INFORMATION
            remarks = {'key': 'remarks', 'type': service_req_obj._fields['remarks'].type,
                       'title': service_req_obj._fields['remarks'].string,
                       'required': service_req_obj._fields['remarks'].required}
            survey_id = {'key': 'survey_id', 'type': service_req_obj._fields['survey_id'].type,
                         'title': service_req_obj._fields['survey_id'].string,
                         'required': service_req_obj._fields['survey_id'].required,
                         'value': [{'id': field.id, 'value': field.title, } for field in survey_obj]}
            company_id = {'key': 'company_id', 'type': service_req_obj._fields['company_id'].type,
                          'title': service_req_obj._fields['company_id'].string,
                          'required': service_req_obj._fields['company_id'].required,
                          'value': [{'id': field.id, 'value': field.name, } for field in company_ids]}
            user_id = {'key': 'user_id', 'type': service_req_obj._fields['user_id'].type,
                       'title': service_req_obj._fields['user_id'].string,
                       'required': service_req_obj._fields['user_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in user_ids]}
            # CUSTOMER INFORMATION
            customer_name = {'key': 'customer_name', 'type': service_req_obj._fields['customer_name'].type,
                             'title': service_req_obj._fields['customer_name'].string,
                             'required': service_req_obj._fields['customer_name'].required}
            customer_email = {'key': 'customer_email', 'type': service_req_obj._fields['customer_email'].type,
                              'title': service_req_obj._fields['customer_email'].string,
                              'required': service_req_obj._fields['customer_email'].required}
            customer_street = {'key': 'customer_street', 'type': service_req_obj._fields['customer_street'].type,
                               'title': service_req_obj._fields['customer_street'].string,
                               'required': service_req_obj._fields['customer_street'].required}
            customer_street2 = {'key': 'customer_street2', 'type': service_req_obj._fields['customer_street2'].type,
                                'title': service_req_obj._fields['customer_street2'].string,
                                'required': service_req_obj._fields['customer_street2'].required}
            customer_city_id = {'key': 'customer_city_id', 'type': service_req_obj._fields['customer_city_id'].type,
                                'title': service_req_obj._fields['customer_city_id'].string,
                                'required': service_req_obj._fields['customer_city_id'].required,
                                'value': [{'id': field.id, 'value': field.name,'state_id':field.state_id.id } for field in custoemr_city_obj]}
            customer_state_id = {'key': 'customer_state_id', 'type': service_req_obj._fields['customer_state_id'].type,
                                 'title': service_req_obj._fields['customer_state_id'].string,
                                 'required': service_req_obj._fields['customer_state_id'].required,
                                 'value': [{'id': field.id, 'value': field.name, } for field in customer_state_obj]}
            customer_zip = {'key': 'customer_zip', 'type': service_req_obj._fields['customer_zip'].type,
                            'title': service_req_obj._fields['customer_zip'].string,
                            'required': service_req_obj._fields['customer_zip'].required}
            customer_country_id = {'key': 'customer_country_id',
                                   'type': service_req_obj._fields['customer_country_id'].type,
                                   'title': service_req_obj._fields['customer_country_id'].string,
                                   'required': service_req_obj._fields['customer_country_id'].required,
                                   'value': [{'id': field.id, 'value': field.name, } for field in customer_country_obj]}
            dealer_distributor_name = {'key': 'dealer_distributor_name',
                                       'type': service_req_obj._fields['dealer_distributor_name'].type,
                                       'title': service_req_obj._fields['dealer_distributor_name'].string,
                                       'required': service_req_obj._fields['dealer_distributor_name'].required}
            # ASSET DETAILS
            product_name = {'key': 'product_name', 'type': service_req_obj._fields['product_name'].type,
                            'title': service_req_obj._fields['product_name'].string,
                            'required': service_req_obj._fields['product_name'].required}
            custom_product_serial = {'key': 'custom_product_serial',
                                     'type': service_req_obj._fields['custom_product_serial'].type,
                                     'title': service_req_obj._fields['custom_product_serial'].string,
                                     'required': service_req_obj._fields['custom_product_serial'].required}
            product_part_number = {'key': 'product_part_number',
                                   'type': service_req_obj._fields['product_part_number'].type,
                                   'title': service_req_obj._fields['product_part_number'].string,
                                   'required': service_req_obj._fields['product_part_number'].required}
            product_part_code = {'key': 'product_part_code', 'type': service_req_obj._fields['product_part_code'].type,
                                 'title': service_req_obj._fields['product_part_code'].string,
                                 'required': service_req_obj._fields['product_part_code'].required}
            service_list.append([service_request_id_alias, service_request_date,child_ticket_type_id,
                                 call_source_id, service_type_id, service_category_id, request_type_id, reason,
                                 problem_reported, requested_by_name, requested_by_contact_number, call_received_id,
                                 team_id, customer_name, customer_email, customer_street,
                                 customer_street2,
                                 customer_city_id, customer_state_id, customer_zip, customer_country_id,
                                 dealer_distributor_name, product_name,
                                 custom_product_serial, product_part_number, product_part_code, remarks, survey_id,
                                 company_id,
                                 user_id])
        elif ticket_type == 'sr_survey_escalation':
            # SERVICE REQUEST INFORMATION
            service_request_id_alias = {'key': 'service_request_id_alias',
                                        'type': service_req_obj._fields['service_request_id_alias'].type,
                                        'title': service_req_obj._fields['service_request_id_alias'].string,
                                        'required': service_req_obj._fields['service_request_id_alias'].required}
            service_request_date = {'key': 'service_request_date',
                                    'type': service_req_obj._fields['service_request_date'].type,
                                    'title': service_req_obj._fields['service_request_date'].string,
                                    'required': service_req_obj._fields['service_request_date'].required,
                                    'value': str(fields.Datetime.now())}
            # approver_id = {'key': 'approver_id', 'type': service_req_obj._fields['approver_id'].type,
            #                'title': service_req_obj._fields['approver_id'].string,
            #                'required': service_req_obj._fields['approver_id'].required,
            #                'value': [{'id': field.id, 'value': field.name, } for field in approver_obj]}
            # CALL DETAILS
            call_source_id = {'key': 'call_source_id', 'type': service_req_obj._fields['call_source_id'].type,
                              'title': service_req_obj._fields['call_source_id'].string,
                              'required': service_req_obj._fields['email'].required,
                              'value': [{'id': field.id, 'value': field.name, } for field in call_source_obj]}
            service_type_id = {'key': 'service_type_id', 'type': service_req_obj._fields['service_type_id'].type,
                               'title': service_req_obj._fields['service_type_id'].string,
                               'required': service_req_obj._fields['service_type_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in service_type_obj]}
            service_category_id = {'key': 'service_category_id',
                                   'type': service_req_obj._fields['service_category_id'].type,
                                   'title': service_req_obj._fields['service_category_id'].string,
                                   'required': service_req_obj._fields['service_category_id'].required,
                                   'value': [{'id': field.id, 'value': field.name, } for field in service_category_ids]}
            request_type_id = {'key': 'request_type_id', 'type': service_req_obj._fields['request_type_id'].type,
                               'title': service_req_obj._fields['request_type_id'].string,
                               'required': service_req_obj._fields['request_type_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in request_type_ids]}
            reason = {'key': 'reason', 'type': service_req_obj._fields['reason'].type,
                      'title': service_req_obj._fields['reason'].string,
                      'required': service_req_obj._fields['reason'].required}
            problem_reported = {'key': 'problem_reported', 'type': service_req_obj._fields['problem_reported'].type,
                                'title': service_req_obj._fields['problem_reported'].string,
                                'required': service_req_obj._fields['problem_reported'].required}
            requested_by_name = {'key': 'requested_by_name', 'type': service_req_obj._fields['requested_by_name'].type,
                                 'title': service_req_obj._fields['requested_by_name'].string,
                                 'required': service_req_obj._fields['requested_by_name'].required}
            requested_by_contact_number = {'key': 'requested_by_contact_number',
                                           'type': service_req_obj._fields['requested_by_contact_number'].type,
                                           'title': service_req_obj._fields['requested_by_contact_number'].string,
                                           'required': service_req_obj._fields['requested_by_contact_number'].required}
            call_received_id = {'key': 'call_received_id', 'type': service_req_obj._fields['call_received_id'].type,
                                'title': service_req_obj._fields['call_received_id'].string,
                                'required': service_req_obj._fields['call_received_id'].required,
                                'value': [{'id': field.id, 'value': field.name, } for field in call_received_ids]}
            team_id = {'key': 'team_id', 'type': service_req_obj._fields['team_id'].type,
                       'title': service_req_obj._fields['team_id'].string,
                       'required': service_req_obj._fields['team_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in team_ids]}
            # OTHER INFORMATION
            remarks = {'key': 'remarks', 'type': service_req_obj._fields['remarks'].type,
                       'title': service_req_obj._fields['remarks'].string,
                       'required': service_req_obj._fields['remarks'].required}
            survey_id = {'key': 'survey_id', 'type': service_req_obj._fields['survey_id'].type,
                         'title': service_req_obj._fields['survey_id'].string,
                         'required': service_req_obj._fields['survey_id'].required,
                         'value': [{'id': field.id, 'value': field.title, } for field in survey_obj]}
            company_id = {'key': 'company_id', 'type': service_req_obj._fields['company_id'].type,
                          'title': service_req_obj._fields['company_id'].string,
                          'required': service_req_obj._fields['company_id'].required,
                          'value': [{'id': field.id, 'value': field.name, } for field in company_ids]}
            user_id = {'key': 'user_id', 'type': service_req_obj._fields['user_id'].type,
                       'title': service_req_obj._fields['user_id'].string,
                       'required': service_req_obj._fields['user_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in user_ids]}
            # assign_engineer_ids = {'key': 'assign_engineer_ids', 'type': service_req_obj._fields['assign_engineer_ids'].type,
            #            'title': service_req_obj._fields['assign_engineer_ids'].string,
            #            'required': service_req_obj._fields['assign_engineer_ids'].required,
            #            'value': [{'id': field.id, 'value': field.name, } for field in user_ids]}
            service_list.append([service_request_id_alias, service_request_date,
                                 call_source_id, service_type_id, service_category_id, request_type_id, reason,
                                 problem_reported, requested_by_name, requested_by_contact_number, call_received_id,
                                 team_id, remarks, survey_id,
                                 company_id,
                                 user_id])
        elif ticket_type == 'so_call':
            # SERVICE REQUEST INFORMATION
            service_request_id_alias = {'key': 'service_request_id_alias',
                                        'type': service_req_obj._fields['service_request_id_alias'].type,
                                        'title': service_req_obj._fields['service_request_id_alias'].string,
                                        'required': service_req_obj._fields['service_request_id_alias'].required}
            service_request_date = {'key': 'service_request_date',
                                    'type': service_req_obj._fields['service_request_date'].type,
                                    'title': service_req_obj._fields['service_request_date'].string,
                                    'required': service_req_obj._fields['service_request_date'].required,
                                    'value': str(fields.Datetime.now())}
            # CALL DETAILS
            call_source_id = {'key': 'call_source_id', 'type': service_req_obj._fields['call_source_id'].type,
                              'title': service_req_obj._fields['call_source_id'].string,
                              'required': service_req_obj._fields['email'].required,
                              'value': [{'id': field.id, 'value': field.name, } for field in call_source_obj]}
            service_type_id = {'key': 'service_type_id', 'type': service_req_obj._fields['service_type_id'].type,
                               'title': service_req_obj._fields['service_type_id'].string,
                               'required': service_req_obj._fields['service_type_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in service_type_obj]}
            service_category_id = {'key': 'service_category_id',
                                   'type': service_req_obj._fields['service_category_id'].type,
                                   'title': service_req_obj._fields['service_category_id'].string,
                                   'required': service_req_obj._fields['service_category_id'].required,
                                   'value': [{'id': field.id, 'value': field.name, } for field in service_category_ids]}
            request_type_id = {'key': 'request_type_id', 'type': service_req_obj._fields['request_type_id'].type,
                               'title': service_req_obj._fields['request_type_id'].string,
                               'required': service_req_obj._fields['request_type_id'].required,
                               'value': [{'id': field.id, 'value': field.name, } for field in request_type_ids]}
            reason = {'key': 'reason', 'type': service_req_obj._fields['reason'].type,
                      'title': service_req_obj._fields['reason'].string,
                      'required': service_req_obj._fields['reason'].required}
            problem_reported = {'key': 'problem_reported', 'type': service_req_obj._fields['problem_reported'].type,
                                'title': service_req_obj._fields['problem_reported'].string,
                                'required': service_req_obj._fields['problem_reported'].required}
            requested_by_name = {'key': 'requested_by_name', 'type': service_req_obj._fields['requested_by_name'].type,
                                 'title': service_req_obj._fields['requested_by_name'].string,
                                 'required': service_req_obj._fields['requested_by_name'].required}
            requested_by_contact_number = {'key': 'requested_by_contact_number',
                                           'type': service_req_obj._fields['requested_by_contact_number'].type,
                                           'title': service_req_obj._fields['requested_by_contact_number'].string,
                                           'required': service_req_obj._fields['requested_by_contact_number'].required}
            call_received_id = {'key': 'call_received_id', 'type': service_req_obj._fields['call_received_id'].type,
                                'title': service_req_obj._fields['call_received_id'].string,
                                'required': service_req_obj._fields['call_received_id'].required,
                                'value': [{'id': field.id, 'value': field.name, } for field in call_received_ids]}
            team_id = {'key': 'team_id', 'type': service_req_obj._fields['team_id'].type,
                       'title': service_req_obj._fields['team_id'].string,
                       'required': service_req_obj._fields['team_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in team_ids]}
            # OTHER INFORMATION
            remarks = {'key': 'remarks', 'type': service_req_obj._fields['remarks'].type,
                       'title': service_req_obj._fields['remarks'].string,
                       'required': service_req_obj._fields['remarks'].required}
            survey_id = {'key': 'survey_id', 'type': service_req_obj._fields['survey_id'].type,
                         'title': service_req_obj._fields['survey_id'].string,
                         'required': service_req_obj._fields['survey_id'].required,
                         'value': [{'id': field.id, 'value': field.title, } for field in survey_obj]}
            company_id = {'key': 'company_id', 'type': service_req_obj._fields['company_id'].type,
                          'title': service_req_obj._fields['company_id'].string,
                          'required': service_req_obj._fields['company_id'].required,
                          'value': [{'id': field.id, 'value': field.name, } for field in company_ids]}
            user_id = {'key': 'user_id', 'type': service_req_obj._fields['user_id'].type,
                       'title': service_req_obj._fields['user_id'].string,
                       'required': service_req_obj._fields['user_id'].required,
                       'value': [{'id': field.id, 'value': field.name, } for field in user_ids]}
            # CUSTOMER INFORMATION
            customer_name = {'key': 'customer_name', 'type': service_req_obj._fields['customer_name'].type,
                             'title': service_req_obj._fields['customer_name'].string,
                             'required': service_req_obj._fields['customer_name'].required}
            customer_email = {'key': 'customer_email', 'type': service_req_obj._fields['customer_email'].type,
                              'title': service_req_obj._fields['customer_email'].string,
                              'required': service_req_obj._fields['customer_email'].required}
            customer_street = {'key': 'customer_street', 'type': service_req_obj._fields['customer_street'].type,
                               'title': service_req_obj._fields['customer_street'].string,
                               'required': service_req_obj._fields['customer_street'].required}
            customer_street2 = {'key': 'customer_street2', 'type': service_req_obj._fields['customer_street2'].type,
                                'title': service_req_obj._fields['customer_street2'].string,
                                'required': service_req_obj._fields['customer_street2'].required}
            customer_city_id = {'key': 'customer_city_id', 'type': service_req_obj._fields['customer_city_id'].type,
                                'title': service_req_obj._fields['customer_city_id'].string,
                                'required': service_req_obj._fields['customer_city_id'].required,
                                'value': [{'id': field.id, 'value': field.name,'state_id':field.state_id.id } for field in custoemr_city_obj]}
            customer_state_id = {'key': 'customer_state_id', 'type': service_req_obj._fields['customer_state_id'].type,
                                 'title': service_req_obj._fields['customer_state_id'].string,
                                 'required': service_req_obj._fields['customer_state_id'].required,
                                 'value': [{'id': field.id, 'value': field.name, } for field in customer_state_obj]}
            customer_zip = {'key': 'customer_zip', 'type': service_req_obj._fields['customer_zip'].type,
                            'title': service_req_obj._fields['customer_zip'].string,
                            'required': service_req_obj._fields['customer_zip'].required}
            customer_country_id = {'key': 'customer_country_id',
                                   'type': service_req_obj._fields['customer_country_id'].type,
                                   'title': service_req_obj._fields['customer_country_id'].string,
                                   'required': service_req_obj._fields['customer_country_id'].required,
                                   'value': [{'id': field.id, 'value': field.name, } for field in customer_country_obj]}
            dealer_distributor_name = {'key': 'dealer_distributor_name',
                                       'type': service_req_obj._fields['dealer_distributor_name'].type,
                                       'title': service_req_obj._fields['dealer_distributor_name'].string,
                                       'required': service_req_obj._fields['dealer_distributor_name'].required}
            # ASSET DETAILS
            product_name = {'key': 'product_name', 'type': service_req_obj._fields['product_name'].type,
                            'title': service_req_obj._fields['product_name'].string,
                            'required': service_req_obj._fields['product_name'].required}
            custom_product_serial = {'key': 'custom_product_serial',
                                     'type': service_req_obj._fields['custom_product_serial'].type,
                                     'title': service_req_obj._fields['custom_product_serial'].string,
                                     'required': service_req_obj._fields['custom_product_serial'].required}
            product_part_number = {'key': 'product_part_number',
                                   'type': service_req_obj._fields['product_part_number'].type,
                                   'title': service_req_obj._fields['product_part_number'].string,
                                   'required': service_req_obj._fields['product_part_number'].required}
            product_part_code = {'key': 'product_part_code', 'type': service_req_obj._fields['product_part_code'].type,
                                 'title': service_req_obj._fields['product_part_code'].string,
                                 'required': service_req_obj._fields['product_part_code'].required}
            service_list.append([service_request_id_alias, service_request_date,
                                 call_source_id, service_type_id, service_category_id, request_type_id, reason,
                                 problem_reported, requested_by_name, requested_by_contact_number, call_received_id,
                                 team_id, customer_name, customer_email, customer_street,
                                 customer_street2,
                                 customer_city_id, customer_state_id, customer_zip, customer_country_id,
                                 dealer_distributor_name, product_name,
                                 custom_product_serial, product_part_number, product_part_code, remarks, survey_id,
                                 company_id,
                                 user_id])



        if service_list:
            return valid_response(service_list, 'service request create load successfully', 200)
        else:
            return valid_response(service_list, 'there is no record', 200)

    @validate_token
    @http.route("/api/create_service_request/submit", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_create_service_request_submit(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('/api/create_service_request/submit value: %s' % post)
        values_dic={}
        try:
            #installation
            if post.get('service_request_id_alias'):
                values_dic['service_request_id_alias'] = post.get('service_request_id_alias')
            if post.get('service_request_date'):
                values_dic['service_request_date'] = datetime.strptime(str(post.get('service_request_date')),'%Y-%m-%dT%H:%M:%S.%f').astimezone(pytz.utc).replace(tzinfo=None) - timedelta(hours=5,minutes=30)
            if post.get('child_ticket_type_id'):
                values_dic['child_ticket_type_id'] = post.get('child_ticket_type_id')
            if post.get('customer_name'):
                values_dic['customer_name'] = post.get('customer_name')
            if post.get('customer_email'):
                values_dic['customer_email'] = post.get('customer_email')
            if post.get('customer_street'):
                values_dic['customer_street'] = post.get('customer_street')
            if post.get('customer_street2'):
                values_dic['customer_street2'] = post.get('customer_street2')
            if post.get('customer_city_id'):
                values_dic['customer_city_id'] = post.get('customer_city_id')
            if post.get('customer_state_id'):
                values_dic['customer_state_id'] = post.get('customer_state_id')
            if post.get('customer_zip'):
                values_dic['customer_zip'] = post.get('customer_zip')
            if post.get('customer_country_id'):
                values_dic['customer_country_id'] = post.get('customer_country_id')
            if post.get('install_addr_street'):
                values_dic['install_addr_street'] = post.get('install_addr_street')
            if post.get('install_addr_street2'):
                values_dic['install_addr_street2'] = post.get('install_addr_street2')
            if post.get('install_addr_city_id'):
                values_dic['install_addr_city_id'] = post.get('install_addr_city_id')
            if post.get('install_addr_state_id'):
                values_dic['install_addr_state_id'] = post.get('install_addr_state_id')
            if post.get('install_addr_zip'):
                values_dic['install_addr_zip'] = post.get('install_addr_zip')
            if post.get('install_addr_country_id'):
                values_dic['install_addr_country_id'] = post.get('install_addr_country_id')
            if post.get('dealer_distributor_name'):
                values_dic['dealer_distributor_name'] = post.get('dealer_distributor_name')
            if post.get('call_source_id'):
                values_dic['call_source_id'] = post.get('call_source_id')
            if post.get('service_type_id'):
                values_dic['service_type_id'] = post.get('service_type_id')
            if post.get('service_category_id'):
                values_dic['service_category_id'] = post.get('service_category_id')
            if post.get('request_type_id'):
                values_dic['request_type_id'] = post.get('request_type_id')
            if post.get('reason'):
                values_dic['reason'] = post.get('reason')
            if post.get('problem_reported'):
                values_dic['problem_reported'] = post.get('problem_reported')
            if post.get('requested_by_name'):
                values_dic['requested_by_name'] = post.get('requested_by_name')
            if post.get('requested_by_contact_number'):
                values_dic['requested_by_contact_number'] = post.get('requested_by_contact_number')
            if post.get('call_received_id'):
                values_dic['call_received_id'] = post.get('call_received_id')
            if post.get('team_id'):
                values_dic['team_id'] = post.get('team_id')
            if post.get('product_name'):
                values_dic['product_name'] = post.get('product_name')
            if post.get('custom_product_serial'):
                values_dic['custom_product_serial'] = post.get('custom_product_serial')
            if post.get('product_part_number'):
                values_dic['product_part_number'] = post.get('product_part_number')
            if post.get('product_part_code'):
                values_dic['product_part_code'] = post.get('product_part_code')
            if post.get('location_contact_person'):
                values_dic['location_contact_person'] = post.get('location_contact_person')
            if post.get('customer_po_number'):
                values_dic['customer_po_number'] = post.get('customer_po_number')
            if post.get('customer_po_date'):
                values_dic['customer_po_date'] = datetime.strptime(str(post.get('customer_po_date')),'%Y-%m-%dT%H:%M:%S.%f')
            if post.get('tender_refer_number'):
                values_dic['tender_refer_number'] = post.get('tender_refer_number')
            if post.get('order_number'):
                values_dic['order_number'] = post.get('order_number')
            if post.get('installation_date'):
                values_dic['installation_date'] = datetime.strptime(str(post.get('installation_date')),'%Y-%m-%dT%H:%M:%S.%f')
            if post.get('invoice_number'):
                values_dic['invoice_number'] = post.get('invoice_number')
            if post.get('invoice_date'):
                values_dic['invoice_date'] = datetime.strptime(str(post.get('invoice_date')),'%Y-%m-%dT%H:%M:%S.%f')
            if post.get('extended_invoice_number'):
                values_dic['extended_invoice_number'] = post.get('extended_invoice_number')
            if post.get('extended_invoice_date'):
                values_dic['extended_invoice_date'] = datetime.strptime(str(post.get('extended_invoice_date')),'%Y-%m-%dT%H:%M:%S.%f')
            if post.get('remarks'):
                values_dic['remarks'] = post.get('remarks')
            if post.get('survey_id'):
                values_dic['survey_id'] = post.get('survey_id')
            if post.get('company_id'):
                values_dic['company_id'] = post.get('company_id')
            if post.get('user_id'):
                values_dic['user_id'] = post.get('user_id')
            #fsm
            if post.get('event_date'):
                values_dic['event_date'] = datetime.strptime(str(post.get('event_date')),'%Y-%m-%dT%H:%M:%S.%f')
            if post.get('issue_noticed'):
                values_dic['issue_noticed'] = post.get('issue_noticed')
            if post.get('case_completed_successfully_id'):
                values_dic['case_completed_successfully_id'] = post.get('case_completed_successfully_id')
            if post.get('medical_intervention_id'):
                values_dic['medical_intervention_id'] = post.get('medical_intervention_id')
            if post.get('patient_involved_id'):
                values_dic['patient_involved_id'] = post.get('patient_involved_id')
            if post.get('surgical_delay_id'):
                values_dic['surgical_delay_id'] = post.get('surgical_delay_id')
            if post.get('select_adverse_consequences'):
                values_dic['select_adverse_consequences'] = post.get('select_adverse_consequences')
            if post.get('complaint_type'):
                values_dic['complaint_type'] = post.get('complaint_type')
            #fsm_wr
            if post.get('requested_by_email'):
                values_dic['requested_by_email']= post.get('requested_by_email')
            if post.get('requested_by_title'):
                values_dic['requested_by_title'] = post.get('requested_by_title')
            if post.get('alternate_contact_name'):
                values_dic['alternate_contact_name'] = post.get('alternate_contact_name')
            if post.get('alternate_contact_number'):
                values_dic['alternate_contact_number'] = post.get('alternate_contact_number')
            if post.get('alternate_contact_email'):
                values_dic['alternate_contact_email'] = post.get('alternate_contact_email')
            # values_list=[]
            # values_list.append({
            #     'service_request_id_alias' : str(post.get('service_request_id_alias')),
            #     # 'service_request_date' : post.get('service_request_date'),
            #     'call_source_id' : int(post.get('call_source_id')),
            #     'service_type_id' : int(post.get('service_type_id')),
            #     'service_category_id':int(post.get('service_category_id')),
            #     'request_type_id' : int(post.get('request_type_id')),
            #     'reason' : post.get('reason'),
            #     'requested_by_name':post.get('requested_by_name'),
            #     'call_received_id' : int(post.get('call_received_id')),
            #     'team_id': int(post.get('team_id')),
            #     'oem_warranty_status_id': int(post.get('oem_warranty_status_id')),
            #     # 'repair_warranty_status_id': int(post.get('repair_warranty_status_id')),
            #     'remarks':str(post.get('remarks')),
            #     'user_id':int(post.get('user_id')),
            #     'company_id': int(post.get('company_id')),
            #     'phone': post.get('phone'),
            #     })
            create_service_request_id = request.env['service.request'].sudo().create([values_dic])
            create_service_request_id.action_submit()
            if create_service_request_id:
                return valid_response([[{'create_service_request_id':create_service_request_id.name}]], 'serviece request create successfully', 200)
        except Exception as e:
            info = "There was a problem {}".format((e))
            error = "Something went wrong"
            _logger.error(info)
            return invalid_response(info, error, 403)

    @validate_token
    @http.route("/api/service_type/service_category_filter",type="json",auth="none",methods=['POST'],csrf=False)
    def _api_service_type_category_filter(self,**post):
        service_type_ids = request.env['service.type'].sudo().search([])
        vals_list=[]
        for rec in service_type_ids:
            service_type_id = {'key': rec.id,
                               'name': rec.name,
                               'value': [{'id': field.id, 'value': field.name, } for field in rec.service_category_ids]}
            vals_list.append(service_type_id)
        return valid_response([vals_list], 'service request type load successfully', 200)


    # @validate_token
    # @http.route("/api/create_service_request", type="json", auth="user", methods=["POST"], csrf=False)
    # def _api_create_service_request(self, **post):
    #     service_req_obj=request.env['service.request']
    #     service_state = service_req_obj.sudo().fields_get(allfields=['state'])['state']['selection']
    #     # service_request_all_fields = service_req_obj.sudo()._fields.values()
    #
    #     service_request_status_obj = request.env['service.request.status'].sudo().search([])
    #     service_request_status_vlaues=[{'name': field.name, 'id': field.id,'string':'Service Request Status'} for field in service_request_status_obj]
    #
    #     approver_obj=request.env['multi.approval.type'].sudo().search([])
    #     approver_value=[{'name':field.name,'id':field.id,'string':'Approval Level'} for field in approver_obj]
    #
    #     call_source_obj=request.env['call.source'].sudo().search([])
    #     call_source_value=[{'name':field.name,'id':field.id,'string':'Call Source/Type'} for field in call_source_obj]
    #
    #     service_category_obj = request.env['service.category'].sudo().search([])
    #     service_category_value=[{'name':field.name,'id':field.id,'string':'Service Category'} for field in service_category_obj]
    #
    #     service_type_obj = request.env['service.type'].sudo().search([])
    #     service_type_value= [{'name':field.name,'id':field.id,'string':'Service Type'} for field in service_type_obj]
    #
    #     request_type_obj = request.env['request.type'].sudo().search([])
    #     request_type_value = [{'name':field.name,'id':field.id,'string':'Request Type'} for field in request_type_obj]
    #
    #     call_received_obj = request.env['call.received'].sudo().search([])
    #     call_received_value = [{'name':field.name,'id':field.id,'string':'Call Received by'} for field in call_received_obj]
    #
    #     team_obj = request.env['crm.team'].sudo().search([('is_service_request', '=', True)])
    #     team_value = [{'name':field.name,'id':field.id,'string':'Team'} for field in team_obj]
    #
    #     case_completed_successfully_obj = request.env['crm.team'].sudo().search([])
    #     case_completed_successfully_value = [{'name':field.name,'id':field.id,'string':'Was the case completed successfully'} for field in case_completed_successfully_obj]
    #
    #     medical_intervention_obj = request.env['medical.intervention'].sudo().search([])
    #     medical_intervention_value= [{'name':field.name,'id':field.id,'string':'Was medical intervention needed'} for field in medical_intervention_obj]
    #
    #     patient_involved_obj = request.env['patient.involved'].sudo().search([])
    #     patient_involved_value = [{'name':field.name,'id':field.id,'string':'Was a patient involved'} for field in patient_involved_obj]
    #
    #     surgical_delay_obj = request.env['surgical.delay'].sudo().search([])
    #     surgical_delay_value = [{'name':field.name,'id':field.id,'string':'Was there a surgical delay'} for field in surgical_delay_obj]
    #
    #     city_obj = request.env['customer.city'].sudo().search([])
    #     city_value = [{'name':field.name,'id':field.id,'string':'City'} for field in city_obj]
    #
    #     state_obj = request.env['res.country.state'].sudo().search([])
    #     state_value = [{'name':field.name,'id':field.id,'string':'State'} for field in state_obj]
    #
    #     country_obj = request.env['res.country'].sudo().search([])
    #     country_value = [{'name':field.name,'id':field.id,'string':'Country'} for field in country_obj]
    #
    #     oem_warranty_status_obj = request.env['oem.warranty.status'].sudo().search([])
    #     oem_warranty_status_value = [{'name':field.name,'id':field.id,'string':'OEM Warranty Status (As per customer)'} for field in oem_warranty_status_obj]
    #
    #     repair_warranty_status_obj = request.env['repair.warranty.status'].sudo().search([])
    #     repair_warranty_status_value = [{'name':field.name,'id':field.id,'string':'Repair Warranty Status (As per customer)'} for field in repair_warranty_status_obj]
    #
    #     survey_obj = request.env['survey.survey'].sudo().search([])
    #     survey_value = [{'name':field.title,'id':field.id,'string':'Worksheet'} for field in survey_obj]
    #
    #     # uid = request.session.uid
    #     # if uid:
    #     #     user_obj=request.env['res.users'].sudo().browse(uid)
    #     # company_obj = request.env['res.company'].sudo().search([('partner_id','=',user_obj.partner_id.id)])
    #     company_obj = request.env['res.company'].sudo().search([])
    #     company_value = [{'name':field.name,'id':field.id,'string':'Company'} for field in company_obj]
    #
    #     partner_obj = request.env['res.partner'].sudo().search([('is_block_partner', '!=', 'blocked')])
    #     partner_value = [{'name':field.name,'id':field.id,'string':'Customer'} for field in partner_obj]
    #
    #     customer_type_obj = request.env['customer.type'].sudo().search([])
    #     customer_value = [{'name':field.name,'id':field.id,'string':'Customer Type'} for field in customer_type_obj]
    #
    #     customer_region_obj = request.env['customer.region'].sudo().search([])
    #     customer_region_value = [{'name':field.name,'id':field.id,'string':'Region'} for field in customer_region_obj]
    #
    #     tier_tier_obj = request.env['tier.tier'].sudo().search([])
    #     tier_tier_value = [{'name':field.name,'id':field.id,'string':'Tier'} for field in tier_tier_obj]
    #
    #     customer_group_obj = request.env['customer.group'].sudo().search([])
    #     customer_group_value = [{'name':field.name,'id':field.id,'string':'Customer Group'} for field in customer_group_obj]
    #
    #     dealer_distributor_obj = request.env['customer.group'].sudo().search([])
    #     dealer_distributor_value = [{'name':field.name,'id':field.id,'string' : 'Dealer/Distributor Name'} for field in dealer_distributor_obj]
    #
    #     customer_asset=[]
    #     stock_lot_obj = request.env['stock.lot'].sudo().search([])
    #     stock_lot_value= [{'name':field.name,'id':field.id,'string' : 'Asset/Product Serial Number'} for field in stock_lot_obj]
    #     product_obj = request.env['product.product'].sudo().search([])
    #     product_value = [{'name':field.name,'id':field.id,'string' : 'Product'} for field in product_obj]
    #     customer_asset.append({
    #         'stock_lot_id':stock_lot_value,
    #         'product_id':product_value
    #     })
    #
    #
    #
    #     service_list=[]
    #     service_list.append({
    #         'state' : service_state,
    #         'service_request_status_id': service_request_status_vlaues,
    #         'approver_id' : approver_value,
    #         'call_source_id' : call_source_value,
    #         'service_category_id':service_category_value,
    #         'service_type_id' : service_type_value,
    #         'request_type_id' : request_type_value,
    #         'call_received_id' : call_received_value,
    #         'team_id': team_value,
    #         'case_completed_successfully_id' : case_completed_successfully_value,
    #         'medical_intervention_id': medical_intervention_value,
    #         'patient_involved_id': patient_involved_value,
    #         'surgical_delay_id' :surgical_delay_value,
    #         'city_id' : city_value,
    #         'state_id': state_value,
    #         'country_id' : country_value,
    #         'oem_warranty_status_id': oem_warranty_status_value,
    #         'repair_warranty_status_id' : repair_warranty_status_value,
    #         'survey_id' : survey_value,
    #         'company_id': company_value,
    #         'partner_id':partner_value,
    #         'customer_type_id':customer_value,
    #         'customer_region_id' : customer_region_value,
    #         'tier_tier_id': tier_tier_value,
    #         'customer_group_id': customer_group_value,
    #         'dealer_distributor_id':dealer_distributor_value,
    #         'customer_asset_ids': customer_asset,
    #     })
    #
    #     return valid_response(service_list, 'Service request create load successfully', 200)
    #
    # @validate_token
    # @http.route("/api/create_service_request/submit", type="json", auth="none", methods=["POST"], csrf=False)
    # def _api_create_service_request_submit(self, **post,):
    #     post = json.loads(request.httprequest.data)
    #     customer_name=post.get('customer_name')
    #     service_category_id =int(post.get('service_category_id'))
    #     service_type_id = int(post.get('service_type_id'))
    #     request_type_id = int(post.get('request_type_id'))
    #     requested_by_contact_number = post.get('requested_by_contact_number')
    #     team_id = int(post.get('team_id'))
    #     bio_medical_engineer_id =post.get('bio_medical_engineer_id')
    #
    #     try:
    #         values_list=[]
    #         values_list.append({
    #             'customer_name' : post.get('customer_name'),
    #             'service_category_id' : int(post.get('service_category_id')),
    #             'service_type_id' : int(post.get('service_type_id')),
    #             'request_type_id' : int(post.get('request_type_id')),
    #             'partner_id':int(post.get('partner_id')),
    #             'requested_by_contact_number' : str(post.get('requested_by_contact_number')),
    #             'team_id' : int(post.get('team_id')),
    #             'bio_medical_engineer_id' : post.get('bio_medical_engineer_id'),
    #             'company_id': int(post.get('company_id'))
    #             })
    #         create_service_request_id = request.env['service.request'].sudo().create(values_list)
    #         create_service_request_id.action_submit()
    #         if create_service_request_id:
    #             return valid_response([{'create_service_request_id':create_service_request_id.name}], 'serviece request create successfully', 200)
    #     except Exception as e:
    #         info = "There was a problem {}".format((e))
    #         error = "Something went wrong"
    #         _logger.error(info)
    #         return invalid_response(info, error, 403)





    @validate_token
    @http.route("/api/create_service_request/fields", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_create_service_request_fields(self, **post,):
        service_req_obj=request.env['service.request']
        service_all = service_req_obj.sudo().fields_get([])
        if service_all:
            return valid_response([service_all], 'contact loaded successfully', 200)
        else:
            return valid_response(service_all, 'there is no contact', 200)





