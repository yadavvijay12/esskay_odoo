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
        request_type = request_obj.sudo().search_read([],['code','name','ticket_type','team_id','is_required_approval'])
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url = base_url.replace(':8071','')
        for rec in request_type:
            rec_type=request_obj.sudo().browse(rec.get('id'))
            # image = rec_type.image_icon
            # image_icon = image.decode('UTF-8') if image else None
            # rec['image_icon']=image_icon
            # rec.pop('id')
            if rec_type.image_icon:
                rec['image_icon_url'] = base_url + '/web/image?' + 'model=request.type&id=' + str(rec_type.id) + '&field=image_icon'
            else:
                rec['image_icon_url']=False
        if request_type:
            return valid_response([request_type], 'Request Type load successfully', 200)
        else:
            return valid_response(request_type, 'there is no request type', 200)