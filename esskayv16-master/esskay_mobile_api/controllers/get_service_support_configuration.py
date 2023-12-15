from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response
from odoo import http
from odoo.http import request

magic_fields = ['__last_update', 'display_name', 'create_uid', 'create_date', 'write_uid', 'write_date','id']
class APIController(http.Controller):

    @validate_token
    @http.route("/api/get_service_conf", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_service_request_conf(self, **post, ):
        vals_list=[]
        call_source = request.env['call.source'].sudo().search_read([], ['code','name'])
        service_category = request.env['service.category'].sudo().search_read([], ['code', 'name'])
        service_type = request.env['service.type'].sudo().search_read([], ['code', 'name'])
        call_received = request.env['call.received'].sudo().search_read([], ['code', 'name'])
        bio_medical_engineer = request.env['bio.medical.engineer'].sudo().search_read([], ['code', 'name'])
        service_request_status = request.env['service.request.status'].sudo().search_read([], ['code', 'name'])
        dispath_location = request.env['dispatch.location'].sudo().search_read([], ['code', 'name'])
        oem_warranty_status = request.env['oem.warranty.status'].sudo().search_read([], ['code', 'name'])
        repair_warranty_status = request.env['repair.warranty.status'].sudo().search_read([], ['code', 'name'])
        repair_center_location = request.env['repair.center.location'].sudo().search_read([], ['code', 'name'])
        was_the_case_completed =  request.env['case.completed.successfully'].sudo().search_read([], ['code', 'name'])
        was_medical_intervention = request.env['medical.intervention'].sudo().search_read([], ['code', 'name'])
        was_patient_involved = request.env['patient.involved'].sudo().search_read([], ['code', 'name'])
        was_there_surgical_delay = request.env['surgical.delay'].sudo().search_read([], ['code', 'name'])
        child_ticket_type = request.env['child.ticket.type'].sudo().search_read([], ['code', 'name'])
        vals={
            'call_source':call_source,
            'service_category':service_category,
            'service_type':service_type,
            'call_received':call_received,
            'bio_medical_engineer':bio_medical_engineer,
            'service_request_status':service_request_status,
            'dispath_location':dispath_location,
            'oem_warranty_status':oem_warranty_status,
            'repair_warranty_status':repair_warranty_status,
            'repair_center_location':repair_center_location,
            'was_the_case_completed':was_the_case_completed,
            'was_medical_intervention':was_medical_intervention,
            'was_patient_involved':was_patient_involved,
            'was_there_surgical_delay':was_there_surgical_delay,
            'child_ticket_type':child_ticket_type,
        }
        vals_list.append(vals)
        return valid_response(vals, 'service request config load successfully', 200)

    @validate_token
    @http.route("/api/get_parent_ticket_conf", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_service_parent_conf(self, **post,):
        parent_ticket_conf_obj = request.env['parent.ticket.configuration']
        parent_ticket_all_keys = parent_ticket_conf_obj.sudo().fields_get().keys()
        parent_ticket_keys = list(set(parent_ticket_all_keys).difference(magic_fields))
        print(len(parent_ticket_keys))
        parent_ticket_conf = parent_ticket_conf_obj.sudo().search_read([], parent_ticket_keys)
        if parent_ticket_conf:
            return valid_response(parent_ticket_conf, 'service request parent load successfully', 200)
        else:
            return valid_response(parent_ticket_conf, 'there is not record in  service parent', 200)

    @validate_token
    @http.route("/api/get_child_ticket_conf", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_service_child_conf(self, **post,):
        child_ticket_conf_obj = request.env['child.ticket.configuration']
        child_ticket_all_keys = child_ticket_conf_obj.sudo().fields_get().keys()
        child_ticket_keys = list(set(child_ticket_all_keys).difference(magic_fields))
        print(len(child_ticket_keys))
        child_ticket_conf = child_ticket_conf_obj.sudo().search_read([], child_ticket_keys)
        if child_ticket_conf:
            return valid_response(child_ticket_conf, 'service request child load successfully', 200)
        else:
            return valid_response(child_ticket_conf, 'there is not record in  service child', 200)

    @validate_token
    @http.route("/api/get_sla_policies_conf", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_service_sla_policies_conf(self, **post,):
        sla_policies_conf_obj = request.env['sla.policies']
        sla_policies_all_keys = sla_policies_conf_obj.sudo().fields_get().keys()
        sla_policies_keys = list(set(sla_policies_all_keys).difference(magic_fields))
        print(len(sla_policies_keys))
        sla_policies_conf = sla_policies_conf_obj.sudo().search_read([], sla_policies_keys)
        if sla_policies_conf:
            return valid_response(sla_policies_conf, 'service request SLA Policies load successfully', 200)
        else:
            return valid_response(sla_policies_conf, 'there is not record in  SLA Polices child', 200)
        
