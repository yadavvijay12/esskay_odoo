import json
import pytz
from odoo import http, fields, _
from odoo.http import request
from datetime import datetime
from dateutil import parser
import logging
_logger = logging.getLogger(__name__)
import base64
import requests
from datetime import timedelta, datetime

req_env = request.httprequest.headers.environ

class RestApiWhatsapp(http.Controller):

    @http.route([
        '/api-whatsapp/<string:model>/<string:method>',
        '/api-whatsapp/<string:model>/<string:method>/<string:id>'
        ], type='http', auth="public", csrf=False)
    def odoo_rest_api_whatsapp(self, model=None, method=None, id=None, **kw):
        token = kw.get('token', False)
        domain = kw.get('domain', [])
        offset = kw.get('offset', 0)
        limit = kw.get('limit', 0)
        fields = kw.get('fields', [])
        vals = kw.get('vals', {})
        args = kw.get('args', [])
        is_guest = kw.get('is_guest', False)
        result = {}
        data = {}
        user_id = False
        headers = dict(request.httprequest.headers.items())
        # _logger.info('Whatsapp DLR - API Data kw-----: %s' % kw)

        # _logger.info('Whatsapp DLR - API Data-----: %s' % vals)
        
        whatsapp_callback_data = json.loads(request.httprequest.data)
        _logger.info('Whatsapp DLR - API Data-----: %s' % whatsapp_callback_data)

        # Example data format
        # {'rqst_ack_id': 1678791451543344, 'del_time': '14/03/2023 16:27:33', 'mobile_no': '919952665444', 'del_status': 'sent'}

        if model and method:
            # _logger.info('model----------: %s' % model)
            # _logger.info('method----------: %s' % method)

            # webhook_data = json.loads(request.httprequest.args)
            # _logger.info('------CALL-BACK DATA ------: %s' % str(callback_data))
            # _logger.info('dlr_data------++++++++----: %s' % whatsapp_callback_data)
            
            if model == 'whatsapp.history' and method == 'create' and whatsapp_callback_data and  whatsapp_callback_data['del_status'] != 'sent':
                _logger.info('whatsapp_callback_data[mobile_no]-------: %s' % whatsapp_callback_data['mobile_no'])
                whatsapp_history = request.env['whatsapp.history'].sudo().search([('rqst_ack_id', '=', whatsapp_callback_data['rqst_ack_id'])])
                for rec in whatsapp_history:
                    if whatsapp_callback_data['del_status'] == 'delivered':
                        del_time = datetime.strptime(whatsapp_callback_data['del_time'], '%d/%m/%Y %H:%M:%S')
                        del_time = del_time - timedelta(hours=5,minutes=30)
                        rec.sudo().write({'state': 'delivered',
                                    'status': whatsapp_callback_data['del_status'] if whatsapp_callback_data['del_status'] else ' ',
                                    'delivered_on': del_time if not rec.delivered_on else del_time,
                                    })
                    if whatsapp_callback_data['del_status'] == 'read':
                        read_time = datetime.strptime(whatsapp_callback_data['del_time'], '%d/%m/%Y %H:%M:%S')
                        read_time = read_time - timedelta(hours=5,minutes=30)
                        rec.sudo().write({'state': 'read',
                                    'status': whatsapp_callback_data['del_status'] if whatsapp_callback_data['del_status'] else ' ',
                                    'read_on': read_time if not rec.delivered_on else del_time,
                                    })

        