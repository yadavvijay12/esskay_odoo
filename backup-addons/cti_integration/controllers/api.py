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

req_env = request.httprequest.headers.environ

class RestApi(http.Controller):

    def get_as_base64(self, url):
        res = base64.b64encode(requests.get(url).content)
        # _logger.info('------Image ------: %s' % str(res))
        return res

    @http.route([
        '/api/<string:model>/<string:method>',
        '/api/<string:model>/<string:method>/<string:id>'
        ], type='http', auth="none", csrf=False)
    def odoo_rest_api(self, model=None, method=None, id=None, **kw):
        print('+++++++++++++++')
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
        print(kw)
        # print('-------',type(kw))
        # print('----1111--',kw['data'])
        # print('----1111-type-',type(kw['data']))
        
        # print('----ss--',callback_data)
        # print('----ss--4',type(callback_data))
        # print('----3333333--',ss['monitorUCID'])
        # stop


        _logger.info('CTI Callback - API Data kw-----: %s' % kw)
        _logger.info('CTI Callback - API Data-----: %s' % vals)
        # Webhook part starts

        if model and method:
            webhook_vals = {}
            helpdesk_tickets = {}
            _logger.info('model----------: %s' % model)
            _logger.info('method----------: %s' % method)

            # webhook_data = json.loads(request.httprequest.args)
            # print('webhook_data',webhook_data)
            # callback_data = json.loads(request.httprequest.data)
            print(kw['data'], "kw['data']------")
            callback_data = json.loads(kw['data'])
            _logger.info('------CALL-BACK DATA ------: %s' % str(callback_data))
            if model == 'call.history' and method == 'create' and callback_data:
                print('111111111111',callback_data['UUI'])
                print('111111111111',callback_data['CallDuration'])
                print('111111111111',callback_data['Type'])
                print('111111111111',callback_data['Status'])
                print('111111111111',callback_data['TransferType'])
                print('111111111111',callback_data['DialStatus'])
                call_history = request.env['call.history'].sudo().search([('uui', '=', callback_data['UUI'])])
                _logger.info('Call History---------- :- %s' % str(call_history))
                # url = callback_data['AudioFile']
                # aud = self.get_as_base64(url)
                for rec in call_history:
                    if callback_data['Type'] == 'Manual':
                        try:
                            rec.sudo().write({
                                'agent_id': callback_data['AgentID'] if callback_data['AgentID'] else '',
                                'agent_name':callback_data['AgentName'] if callback_data['AgentName'] else '',
                                'agent_phone_number':callback_data['AgentPhoneNumber'] if callback_data['AgentPhoneNumber'] else '',
                                'agent_status':callback_data['AgentStatus'] if callback_data['AgentStatus'] else '',
                                'agent_unique_id':callback_data['AgentUniqueID'] if callback_data['AgentUniqueID'] else '',
                                'api_key':callback_data['Apikey'] if callback_data['Apikey'] else '',
                                'audio_file':callback_data['AudioFile'] if callback_data['AudioFile'] else '',
                                # 'file_audio':callback_data['AudioFile'] if callback_data['AudioFile'] else '',
                                'caller_audio_file':callback_data['CallerConfAudioFile'] if callback_data['CallerConfAudioFile'] else '',
                                'caller_id':callback_data['CallerID'] if callback_data['CallerID'] else '',
                                'campaign_name':callback_data['CampaignName'] if callback_data['CampaignName'] else '',
                                'campaign_status':callback_data['CampaignStatus'] if callback_data['CampaignStatus'] else '',
                                'comments':callback_data['Comments'] if callback_data['Comments'] else '',
                                'conf_duration':callback_data['ConfDuration'] if callback_data['ConfDuration'] else '',
                                'customer_status':callback_data['CustomerStatus'] if callback_data['CustomerStatus'] else '',
                                'dial_status':callback_data['DialStatus'] if callback_data['DialStatus'] else '',
                                'dialed_number':callback_data['DialedNumber'] if callback_data['DialedNumber'] else '',
                                'did':callback_data['Did'] if callback_data['Did'] else '',
                                'disposition':callback_data['Disposition'] if callback_data['Disposition'] else '',
                                'duration':callback_data['Duration'] if callback_data['Duration'] else '',
                                'end_times':callback_data['EndTime'] if callback_data['EndTime'] else '',
                                'fall_back_rule':callback_data['FallBackRule'] if callback_data['FallBackRule'] else '',
                                'hangup_by':callback_data['HangupBy'] if callback_data['HangupBy'] else '',
                                'location':callback_data['Location'] if callback_data['Location'] else '',
                                'monitor_ucid':str(callback_data['monitorUCID']) if callback_data['monitorUCID'] else '',
                                'phone_number':callback_data['CallerID'] if callback_data['PhoneName'] else '',
                                'skill':callback_data['Skill'] if callback_data['Skill'] else '',
                                'start_datetime':callback_data['StartTime'] if callback_data['StartTime'] else '',
                                'status':callback_data['Status'] if callback_data['Status'] else '',
                                'answered_datetime':callback_data['TimeToAnswer'] if callback_data['TimeToAnswer'] else '',
                                'transfer_type':callback_data['TransferType'] if callback_data['TransferType'] else '',
                                'transfer_to':callback_data['TransferredTo'] if callback_data['TransferredTo'] else '',
                                'type':callback_data['Type'] if callback_data['Type'] else '',
                                'username':callback_data['UserName'] if callback_data['UserName'] else '',
                                'state': 'closed'
                            })
                            outbound_call = request.env['outbound.call.list'].sudo().search([('call_history_id', '=', rec.id)])
                            for obj in outbound_call:
                                obj.sudo().write({'disposition': callback_data['Disposition'] if callback_data['Disposition'] else ''})
                                if callback_data['Disposition'] == 'RNR3':
                                    obj.sudo().write({'state':'no_answer'})
                                    obj.survey_user_input_id.sudo().write({'state':'no_answer'})

                        except Exception as e:
                            _logger.info('Exception-------------------%s' %e)

                partner_name = request.env['res.partner'].sudo().search(['|',('mobile','like', callback_data['CallerID']), ('phone','like', callback_data['CallerID'])], limit=1)
                if callback_data['Type'] != 'Manual':
                    partner = request.env['call.history'].sudo().create({
                            'agent_id': callback_data['AgentID'] if callback_data['AgentID'] else '',
                            'partner_id': partner_name.id if partner_name.id else False,
                            'agent_name':callback_data['AgentName'] if callback_data['AgentName'] else '',
                            'agent_phone_number':callback_data['AgentPhoneNumber'] if callback_data['AgentPhoneNumber'] else '',
                            'agent_status':callback_data['AgentStatus'] if callback_data['AgentStatus'] else '',
                            'agent_unique_id':callback_data['AgentUniqueID'] if callback_data['AgentUniqueID'] else '',
                            'api_key':callback_data['Apikey'] if callback_data['Apikey'] else '',
                            'audio_file':callback_data['AudioFile'] if callback_data['AudioFile'] else '',
                            # 'file_audio':aud if url else False,
                            'caller_audio_file':callback_data['CallerConfAudioFile'] if callback_data['CallerConfAudioFile'] else '',
                            'caller_id':callback_data['CallerID'] if callback_data['CallerID'] else '',
                            'campaign_name':callback_data['CampaignName'] if callback_data['CampaignName'] else '',
                            'campaign_status':callback_data['CampaignStatus'] if callback_data['CampaignStatus'] else '',
                            'comments':callback_data['Comments'] if callback_data['Comments'] else '',
                            'conf_duration':callback_data['ConfDuration'] if callback_data['ConfDuration'] else '',
                            'customer_status':callback_data['CustomerStatus'] if callback_data['CustomerStatus'] else '',
                            'dial_status':callback_data['DialStatus'] if callback_data['DialStatus'] else '',
                            'dialed_number':callback_data['DialedNumber'] if callback_data['DialedNumber'] else '',
                            'did':callback_data['Did'] if callback_data['Did'] else '',
                            'disposition':callback_data['Disposition'] if callback_data['Disposition'] else '',
                            'duration':callback_data['Duration'] if callback_data['Duration'] else '',
                            'end_times':callback_data['EndTime'] if callback_data['EndTime'] else '',
                            'fall_back_rule':callback_data['FallBackRule'] if callback_data['FallBackRule'] else '',
                            'hangup_by':callback_data['HangupBy'] if callback_data['HangupBy'] else '',
                            'location':callback_data['Location'] if callback_data['Location'] else '',
                            'monitor_ucid':str(callback_data['monitorUCID']) if callback_data['monitorUCID'] else '',
                            'phone_number':callback_data['CallerID'] if callback_data['PhoneName'] else '',
                            'skill':callback_data['Skill'] if callback_data['Skill'] else '',
                            'start_datetime':callback_data['StartTime'] if callback_data['StartTime'] else '',
                            'status':callback_data['Status'] if callback_data['Status'] else '',
                            'answered_datetime':callback_data['TimeToAnswer'] if callback_data['TimeToAnswer'] else '',
                            'transfer_type':callback_data['TransferType'] if callback_data['TransferType'] else '',
                            'transfer_to':callback_data['TransferredTo'] if callback_data['TransferredTo'] else '',
                            'type':callback_data['Type'] if callback_data['Type'] else '',
                            'username':callback_data['UserName'] if callback_data['UserName'] else '',
                            'uui':callback_data['UUI'] if callback_data['UUI'] else '',
                            'call_type': 'incoming', 'state': 'closed'
                        })
                    print(partner, "partner-------")

    @http.route([
        '/api2/<string:model>/<string:method>',
        '/api2/<string:model>/<string:method>/<string:id>'
        ], type='http', auth="none", csrf=False)
    def odoo_rest_api_pop_up(self, model=None, method=None, id=None, **kw):
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
        print(kw)
        _logger.info('-----CTI Screen POP Up - API Data kw -----: %s' % kw)
        # callback_data = json.loads(kw['data'])
        callback_data = kw
        # _logger.info('-----CTI Screen POP Up - API Data-----: %s' % vals)
        _logger.info('-----CTI Screen POP Up - API Data-----: %s' % callback_data)
        if model and method:
            _logger.info('model----------: %s' % model)
            _logger.info('method----------: %s' % method)
            # webhook_data = json.loads(request.httprequest.args)
            # popup_data = json.loads(request.httprequest.data)
            # res = eval(callback_data['UUI']) 
            # print(res['user'], "callback_data['res']")
            # print(callback_data['customer'], "callback_data['customer']-------")
            # user = request.env['res.users'].sudo().browse(int(callback_data['UUI']))
            # print('000000000000',callback_data)
            # print('000000000000',callback_data['callerID'])
            # partner_id = request.env['res.partner'].sudo().search([('mobile','like',str(callback_data['callerID']))])
            # print('partner_id',partner_id)
            user = request.env['res.users'].sudo().browse(2)
            print('000000000000',user)
            # print('000000000000',type(callback_data['callerID']))
            # dd = callback_data['callerID']
            # message = '%s' + '%s' (dd, dd)
            message = 'Thank you'
            print(message, "message=====")
            request.env['bus.bus'].sudo()._sendone(request._cr.dbname, user.partner_id, 'success_notify', {
                'type': "success",
                'title': _("Incoming Call"),
                'message': message,
                'sticky': True
            })

            # request.env['bus.bus']._sendone((request._cr.dbname, 'res.partner', user.partner_id.id),
            #         {'type': 'simple_notification', 'title': 'Missing Success', 'message': message, 'sticky': True, 'warning': False})


    # @http.route([
    #     '/api-whatsapp/<string:model>/<string:method>',
    #     '/api-whatsapp/<string:model>/<string:method>/<string:id>'
    #     ], type='http', auth="public", csrf=False)
    # def odoo_rest_api_whatsapp(self, model=None, method=None, id=None, **kw):
    #     from datetime import datetime
    #     print('+++++++++++++++')
    #     token = kw.get('token', False)
    #     domain = kw.get('domain', [])
    #     offset = kw.get('offset', 0)
    #     limit = kw.get('limit', 0)
    #     fields = kw.get('fields', [])
    #     vals = kw.get('vals', {})
    #     args = kw.get('args', [])
    #     is_guest = kw.get('is_guest', False)
    #     result = {}
    #     data = {}
    #     user_id = False
    #     headers = dict(request.httprequest.headers.items())
    #     # _logger.info('Whatsapp DLR - API Data kw-----: %s' % kw)

    #     # _logger.info('Whatsapp DLR - API Data-----: %s' % vals)
        
    #     whatsapp_callback_data = json.loads(request.httprequest.data)
    #     _logger.info('Whatsapp DLR - API Data-----: %s' % whatsapp_callback_data)

    #     # Example data format
    #     # {'rqst_ack_id': 1678791451543344, 'del_time': '14/03/2023 16:27:33', 'mobile_no': '919952665444', 'del_status': 'sent'}

    #     if model and method:
    #         _logger.info('model----------: %s' % model)
    #         _logger.info('method----------: %s' % method)

    #         # webhook_data = json.loads(request.httprequest.args)
    #         # print('webhook_data',webhook_data)
    #         # callback_data = json.loads(request.httprequest.data)
    #         # print(kw['data'], "kw['data']------")
    #         # callback_data = json.loads(kw)
    #         # dlr_data = whatsapp_callback_data
    #         # _logger.info('------CALL-BACK DATA ------: %s' % str(callback_data))
    #         # _logger.info('dlr_data------++++++++----: %s' % whatsapp_callback_data)
    #         if model == 'whatsapp.history' and method == 'create' and whatsapp_callback_data:
    #             _logger.info('whatsapp_callback_data[mobile_no]-------: %s' % whatsapp_callback_data['mobile_no'])
    #             print('--',whatsapp_callback_data['del_time'])
    #             print('--',type(whatsapp_callback_data['del_time']))

    #             # datetime_object = datetime.strtime(whatsapp_callback_data['del_time'], '%d/%m/%y %H:%M:%S')
    #             # datetime_object = datetime.strptime(whatsapp_callback_data['del_time'], '%Y-%m-%d %H:%M:%S')
    #             # print('datetime_object',datetime_object)
    #             # ss = datetime.strptime(whatsapp_callback_data['del_time'], '%Y-%m-%d %H:%M:%S')
    #             # print('ss',ss)
    #             whatsapp_history_id = request.env['whatsapp.history'].sudo().create({
    #                         'rqst_ack_id': whatsapp_callback_data['rqst_ack_id'] if whatsapp_callback_data['rqst_ack_id'] else '',
    #                         'sent_to': whatsapp_callback_data['mobile_no'] if whatsapp_callback_data['mobile_no'] else '',
    #                         'status': whatsapp_callback_data['del_status'] if whatsapp_callback_data['del_status'] else '',
    #                         'delivered_on': '2023-03-04 10:00:00',
    #                         # 'delivered_on': whatsapp_callback_data['del_time'] if whatsapp_callback_data['del_time'] else '',
    #                         })

    #             # whatspp_history = request.env['whatsapp.history'].sudo().search([('phone_number', '=', dlr_data['mobile_no']),('rqst_ack_id','=',dlr_data['rqst_ack_id'])])
    #             # _logger.info('Call History---------- :- %s' % str(whatspp_history))
    #             # for rec in call_history:
    #             #     url = callback_data['AudioFile']
    #             #     aud = self.get_as_base64(url)

    #             #     try:
    #             #         rec.sudo().write({
    #             #             'agent_id': callback_data['AgentID'] if callback_data['AgentID'] else '',
    #             #             'agent_name':callback_data['AgentName'] if callback_data['AgentName'] else '',
                
    #             #         })

    #             #     except Exception as e:
    #             #         _logger.info('Exception-------------------%s' %e)