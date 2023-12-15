# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models, exceptions
from datetime import timedelta
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, ValidationError

import requests
import json


class WatsappSmsGateway(models.Model):   
    _name = "watsapp.sms.gateway"
    
    name = fields.Char(required=True, string='Name')
    gateway_url = fields.Char(required=True, string='GateWay Url')
    channel = fields.Char('Channel')
    source = fields.Char('Source')
    content_type = fields.Char('Content Type')
    apikey = fields.Char('Api-key')
    category = fields.Char('Category')
    whatsapp_account_uid = fields.Char('Whatsapp Account Uid')
    language_code = fields.Char('Language Code')
    api_version = fields.Char('API Version')
    username = fields.Char('Username')
    password = fields.Char('Password')
    is_opt_in = fields.Boolean('Is Opt-in')

    def action_whatsapp_notification(self, template, mobile, message, button_message=[], partner_id=False):
        # get the value from the template and pass ACL 10-10-22
        optin_url = str(template.template_gateway_id.gateway_url)
        optin_content = str(template.template_gateway_id.content_type)
        optin_enterprise_id = (template.template_gateway_id.username)
        optin_token = str(template.template_gateway_id.password)
        optin_body = json.dumps({'enterpriseId':optin_enterprise_id,'msisdn': mobile, 'token': optin_token})
        optin_header = {'Content-Type': optin_content}
        # get the response from acl 10-10-22
        try:
            optin_response = requests.post(optin_url, headers = optin_header, data = optin_body)
            acl_response_value = json.loads(optin_response.content)
        except Exception as e:
            raise exceptions.ValidationError(e)
        # based on the success response send the whatsapp message 10-10-22 
        if acl_response_value['status'] == 'OK':
            url = str(template.gateway_id.gateway_url)
            content_type = str(template.gateway_id.content_type)
            channel = str(template.gateway_id.channel)
            source = str(template.gateway_id.source)
            acl_type = 'template'
            template_name = str(template.name)
            language_code = str(template.language.iso_code)    
            username = str(template.gateway_id.username)
            password = str(template.gateway_id.password)
            destination = str(mobile)
            destination = destination.replace(" ", "")
            h = {'Content-Type': content_type, 'user': username, 'pass': password}
            d = json.dumps({
                "messages": [
                {"sender": source,"to": destination,"messageId": "","transactionId": "","channel": channel,"type": acl_type,
                "template": {
                "body": message,
                "buttons": button_message,
                "templateId":template_name,
                "langCode": language_code,
               }
               }
            ],
              "responseType": "json"
            })
            try:
                response = requests.post(url, headers = h, data = d)
                res = json.loads(response.content)
                _logger.info("------Response Whatsapp------: %s", res)
                if res['success'] == 'true':
                    self.env['whatsapp.history'].sudo().create({
                                'rqst_ack_id': res['responseId'] if res['responseId'] else '',
                                'sent_to': mobile if mobile else '',
                                'partner_id': partner_id if partner_id else False
                                # 'delivered_on': whatsapp_callback_data['del_time'] if whatsapp_callback_data['del_time'] else '',
                                })
            except Exception as e:
                raise exceptions.ValidationError(e)
        
        return True