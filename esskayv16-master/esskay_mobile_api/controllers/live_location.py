from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response
from odoo import http
from odoo.http import request
import json
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class APIController(http.Controller):
    @validate_token
    @http.route("/api/live/location", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_create_live_location(self, **post):
        post = json.loads(request.httprequest.data)
        _logger.info('/api/live/location value: %s' % post)
        uid = request.env.uid
        today = date.today()
        # action_date = fields.Datetime.now()

        user = request.env.user.browse(uid)
        values_dic = {}
        try:
            employee_id = request.env['hr.employee'].sudo().search(
                [('user_id', '=', uid), ('company_id', '=', user.company_id.id)])
            attendance = request.env['hr.attendance'].sudo().search(
                [('employee_id', '=', employee_id.id), ('check_out', '=', False)], limit=1)
            if attendance:
                if post.get('latitude'):
                    values_dic['latitude'] = post.get('latitude')
                if post.get('longitude'):
                    values_dic['longitude'] = post.get('longitude')
                print(str(today))
                location = request.env['geo.location'].sudo().search([('name', '=', str(today)), ('user_id', '=', uid)])
                if not location and uid:
                    location = request.env['geo.location'].sudo().create({'name': str(today), 'user_id': uid})
                if location:
                    values_dic['lat_long_id'] = location.id
                    location.latitude_longitude_ids.create(values_dic)
                    return valid_response([[{'user': location.user_id.name}]],
                                          'location update create successfully', 200)
            else:
                return valid_response('You are not allowed to access thos API, because this user is check out','You are not Check In', 200)

        except Exception as e:
            info = "There was a problem {}".format((e))
            error = "Something went wrong"
            _logger.error(info)
            return invalid_response(info, error, 403)
