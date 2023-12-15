from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response
from odoo import http
from odoo.http import request
import json
from odoo import api, fields, models, _

class APIController(http.Controller):

    @validate_token
    @http.route("/api/get_request_type", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_request_type(self, **post,):
        request_obj = request.env['request.type']
        user = request.env.user
        company_id = request.env.company.id
        request_type = request_obj.sudo().search_read([],['code','name','ticket_type','team_id','is_required_approval'])
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url = base_url.replace(':8071','')
        Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
        CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
        Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
            'ppts_service_request.service_request_group_manager')
        National_Head = user.has_group('ppts_service_request.service_request_national_head')
        service_request_obj = request.env['service.request']
        for rec in request_type:
            rec_type=request_obj.sudo().browse(rec.get('id'))
            # image = rec_type.image_icon
            # image_icon = image.decode('UTF-8') if image else None
            # rec['image_icon']=image_icon
            # rec.pop('id')
            domain = []
            if CT_Users:
                domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
            elif Show_Service_Request_Service_Engineer:
                domain += [('user_id', '=', user.id)]
            elif Manager_CT_Repair_Manager_Service_Manager_RSM:
                domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
            elif National_Head:
                domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
            else:
                domain += [('id', '=', False)]
            domain+=[('company_id','=',company_id),('request_type_id','=',rec_type.id),('state','in',['new'])]

            count = service_request_obj.sudo().search_count(domain)
            rec['open_count'] = count
            if rec_type.image_icon:
                rec['image_icon_url'] = base_url + '/web/image?' + 'model=request.type&id=' + str(rec_type.id) + '&field=image_icon'
            else:
                rec['image_icon_url']=False
        if request_type:
            return valid_response([request_type], 'Request Type load successfully', 200)
        else:
            return valid_response(request_type, 'there is no request type', 200)


    @validate_token
    @http.route("/api/get_request_type_v2", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_request_type_v2(self, **post,):
        request_obj = request.env['request.type']
        user = request.env.user
        company_id = request.env.company.id
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
        CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
        Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
            'ppts_service_request.service_request_group_manager')
        National_Head = user.has_group('ppts_service_request.service_request_national_head')
        service_request_obj = request.env['service.request']

        request_type_list = []
        domain_all = []
        if CT_Users:
            domain_all += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
        elif Show_Service_Request_Service_Engineer:
            domain_all += [('user_id', '=', user.id)]
        elif Manager_CT_Repair_Manager_Service_Manager_RSM:
            domain_all += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
        elif National_Head:
            domain_all += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
        else:
            domain_all += [('id', '=', False)]
        domain_all += [('company_id', '=', company_id), ('state', 'in', ['new'])]
        sr_all_open_total = service_request_obj.sudo().search_count(domain_all)
        sr_all={
            'ticket_type':'sr_all',
            'ticket_name':'SR-ALL',
            'image_icon_url':base_url+'/esskay_mobile_api/static/src/icon/all.png',
            'total_count':sr_all_open_total,
            'data':[]
        }
        request_type_list.append(sr_all)
        ticket_type_dict = dict(request_obj._fields['ticket_type'].selection)
        for key, val in ticket_type_dict.items():
            request_type_dict = {"ticket_type": key}
            request_type_dict.update({'ticket_name': val})
            rec = request_obj.sudo().search([('ticket_type', '=', key)],limit=1)
            request_type_dict.update({'image_icon_url': base_url + '/web/image?' + 'model=request.type&id=' + str(
                        rec.id) + '&field=ticket_type_image' if rec.ticket_type_image else False})
            approval_type = request_obj.sudo().search([('ticket_type', '=', key)])
            approval_list = []
            open_count = 0
            for res in approval_type:
                domain = []
                if CT_Users:
                    domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
                elif Show_Service_Request_Service_Engineer:
                    domain += [('user_id', '=', user.id)]
                elif Manager_CT_Repair_Manager_Service_Manager_RSM:
                    domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
                elif National_Head:
                    domain += ['|', ('user_id', '=', user.id), ('team_id', 'in', user.team_ids.ids)]
                else:
                    domain += [('id', '=', False)]
                domain += [('company_id', '=', company_id), ('request_type_id', '=', res.id),
                           ('state', 'in', ['new'])]

                count = service_request_obj.sudo().search_count(domain)
                open_count +=count
                approval_list.append({
                    'id': res.id,
                    'code': res.code,
                    'name': res.name,
                    'ticket_type': res.ticket_type,
                    'open_count':count,
                    'team_id':res.team_id.id,
                    'is_required_approval':res.is_required_approval,
                    'image_icon_url': base_url + '/web/image?' + 'model=request.type&id=' + str(
                        res.id) + '&field=image_icon' if res.image_icon else False
                })
            request_type_dict.update({'total_count' : open_count})
            request_type_dict.update({'data': approval_list})
            request_type_list.append(request_type_dict)

        if request_type_list:
            return valid_response([request_type_list], 'Request Type load successfully', 200)
        else:
            return valid_response([request_type_list], 'there is no request type', 200)


    @validate_token
    @http.route("/api/get_request_type_v3", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_request_type_v3(self, **post,):
        request_obj = request.env['request.type']
        parent_obj = request.env['parent.ticket']
        user = request.env.user
        company_id = request.env.company.id
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        Show_Service_Request_Service_Engineer = user.has_group('ppts_service_request.service_request_group_user')
        CT_Users = user.has_group('ppts_service_request.service_request_group_ct_user')
        Manager_CT_Repair_Manager_Service_Manager_RSM = user.has_group(
            'ppts_service_request.service_request_group_manager')
        National_Head = user.has_group('ppts_service_request.service_request_national_head')

        request_type_list = []

        domain_all = []
        if CT_Users:
            domain_all += [('team_id', 'in', user.team_ids.ids)]
        elif Show_Service_Request_Service_Engineer:
            domain_all += [('team_id', 'in', user.team_ids.ids)]
        elif Manager_CT_Repair_Manager_Service_Manager_RSM:
            domain_all += [('team_id', 'in', user.team_ids.ids)]
        elif National_Head:
            domain_all += [('team_id', 'in', user.team_ids.ids)]
        else:
            domain_all += [('id', '=', False)]
        domain_all += [('company_id', '=', company_id), ('state', 'in', ['new'])]
        tk_all_open_total = parent_obj.sudo().search_count(domain_all)
        tk_all={
            'ticket_type':'tk_all',
            'ticket_name':'TK-ALL',
            'image_icon_url':base_url+'/esskay_mobile_api/static/src/icon/all.png',
            'open_count':tk_all_open_total,
        }
        request_type_list.append(tk_all)
        ticket_type_dict = dict(request_obj._fields['ticket_type'].selection)

        for key, val in ticket_type_dict.items():
            request_type_dict = {"ticket_type": key}
            request_type_dict.update({'ticket_name': val.replace('SR-','')})
            rec = request_obj.sudo().search([('ticket_type', '=', key)], limit=1)
            request_type_dict.update({'image_icon_url': base_url + '/web/image?' + 'model=request.type&id=' + str(
                rec.id) + '&field=ticket_type_image' if rec.ticket_type_image else False})
            approval_type = request_obj.sudo().search([('ticket_type', '=', key)])
            # domain_all+=[('request_type_id.ticket_type', '=', key)]
            # open_count= parent_obj.sudo().search_count(domain_all)
            open_count = 0
            for res in approval_type:
                domain = []
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
                domain += [('company_id', '=', company_id), ('state', 'in', ['new']),('request_type_id', '=', res.id)]
                count = parent_obj.sudo().search_count(domain)
                open_count += count
            request_type_dict.update({'open_count': open_count})
            request_type_list.append(request_type_dict)
        if request_type_list:
            return valid_response([request_type_list], 'Request Type load successfully', 200)
        else:
            return valid_response([request_type_list], 'there is no request type', 200)
