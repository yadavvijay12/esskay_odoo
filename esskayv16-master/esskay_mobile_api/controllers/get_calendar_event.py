from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response
from odoo import http
from odoo.http import request
import json
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

class APIController(http.Controller):

    @validate_token
    @http.route("/api/get_calendar_event", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_calendar_event_details(self, **post,):
        # uid = request.session.uid
        uid = request.env.uid
        calendar_obj = request.env['calendar.event']
        calendar_event = calendar_obj.sudo().search_read([('active','=',True),('user_id', '=',uid)],fields=['name', 'partner_ids','description','allday','duration','alarm_ids','location','videocall_location','categ_ids','recurrency','privacy','show_as'])
        for rec in calendar_event:
            cal_event = calendar_obj.sudo().browse(rec.get('id'))
            rec['start_date'] = str(cal_event.start_date)
            rec['stop_date'] = str(cal_event.stop_date)
            if rec.get('description'):
                rec['description'] = BeautifulSoup(rec.get('description'), "lxml").text
            if rec.get('partner_ids'):
                rec['partner_ids']=request.env['res.partner'].sudo().search_read([('id','in',rec.get('partner_ids'))],fields=['name'])
            if rec.get('categ_ids'):
                rec['categ_ids'] = request.env['calendar.event.type'].sudo().search_read([('id','in',rec.get('categ_ids'))],fields=['name'])
        if calendar_event:
            return valid_response([calendar_event], 'calendar loaded successfully', 200)
        else:
            return valid_response(calendar_event, 'there is no calender event', 200)

