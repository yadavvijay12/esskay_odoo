from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response
from odoo import http
from odoo.http import request
import json
import logging
_logger = logging.getLogger(__name__)

class APIController(http.Controller):
    @http.route('/api/reset_password', type='json', auth='public',methods=["POST"], csrf=False)
    def api_auth_reset_password(self, **post):
        post = json.loads(request.httprequest.data)
        login = post.get('login')
        try:
            request.env['res.users'].sudo().reset_password(login)
        except Exception as e:
            return invalid_response("something went wrong", "Error: %s" % e,403)
        return valid_response([{"desc": "Please check the email"}])

