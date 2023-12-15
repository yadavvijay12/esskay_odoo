from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response
from odoo import http
from odoo.http import request
from odoo.tools.misc import format_duration
import json

class APIController(http.Controller):

    @validate_token
    @http.route("/api/get_attendances", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_attendances_details(self, **post):
        post = json.loads(request.httprequest.data)
        user = request.env.user.browse(int(post.get('uid')))
        attendance_obj = request.env['hr.attendance']
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)],limit=1)
        if employee_id:
            attendance = attendance_obj.sudo().search_read([('employee_id','=',employee_id.id)],fields=['employee_id'])
            for rec in attendance:
                att = attendance_obj.sudo().browse(rec.get('id'))
                rec['check_in']= str(att.check_in)
                rec['check_out'] = str(att.check_out)
                rec['worked_hours'] = format_duration(att.worked_hours)
        else:
            return invalid_response('there is no employee', "employee id not fount", 403)
        if attendance:
            return valid_response([attendance], 'attendance loaded successfully', 200)
        else:
            return valid_response(attendance, 'there is no attendance', 200)






