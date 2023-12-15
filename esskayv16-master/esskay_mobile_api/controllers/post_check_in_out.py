from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response
from odoo import http
from odoo.http import request
import json
from odoo import api, fields, models, _

class APIController(http.Controller):

    @validate_token
    @http.route("/api/check_in", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_attencheck_in(self, **post,):
        post = json.loads(request.httprequest.data)
        action_date = fields.Datetime.now()
        # login = post.get('login')
        # user=request.env['res.users'].sudo().search([('login', '=', login)])
        uid = request.env.uid
        user = request.env.user.browse(uid)
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', uid),('company_id','=',user.company_id.id)])
        attendance = request.env['hr.attendance'].sudo().search([('employee_id', '=', employee_id.id), ('check_out', '=', False)],limit=1)
        result=[]
        if not attendance:
            vals = {
                'employee_id': employee_id.id,
                'check_in': action_date,
            }
            request.env['hr.attendance'].sudo().create(vals)
            result.append({'check_in_time':str(action_date)})
            return valid_response([result],'check in successfully added',200)
        else:
            return invalid_response('Check in','you already check IN ',200)


    @validate_token
    @http.route("/api/check_out", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_attencheck_out(self, **post,):
        post = json.loads(request.httprequest.data)
        action_date = fields.Datetime.now()
        # login = post.get('login')
        # user = request.env['res.users'].sudo().search([('login', '=', login)])
        uid = request.env.uid
        user = request.env.user.browse(uid)
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user.id),('company_id','=',user.company_id.id)])
        attendance = request.env['hr.attendance'].sudo().search([('employee_id', '=', employee_id.id), ('check_out', '=', False)],limit=1)
        result=[]
        if attendance:
            attendance.check_out = action_date
            vals={
                'check_out_time':str(action_date)
            }
            result.append(vals)
            return valid_response([result], 'check out successfully added', 200)
        else:
            return invalid_response('Check out', 'you already check out ', 200)
            # result.append({'check_out': False})
        # return json.loads(json.dumps(result))


