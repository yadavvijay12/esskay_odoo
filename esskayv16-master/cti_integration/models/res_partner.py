from odoo import models, _
from odoo.exceptions import ValidationError
import requests
import logging
_logger = logging.getLogger(__name__)
import math as m
import random as ra


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_ticket_ref(self):
        # if not self.env.context.get('parent_ticket_id'):
        #     self = self.with_context(
        #         parent_ticket_id=False
        #     )
        # if not self.env.context.get('child_ticket_id'):
        #     self = self.with_context(
        #         child_ticket_id=False
        #     )
        if not self.env.context.get('ticket_ref'):
            self = self.with_context(
                ticket_ref=' '
            )
        return self.env.context['ticket_ref']

    def _generate_call(self, number):
        api_get = self.env.ref('cti_integration.cti_integration_api')
        call_history = False
        
        if api_get:
            string = '0123456789'
            random_no = ""
            varlen = len(string)
            for i in range(6):
                random_no += string[m.floor(ra.random() * varlen)]
            ticket_ref = self._get_ticket_ref()
            # next_code = self.env['ir.sequence'].next_by_code('call.history') or str(0)
            api_con = api_get.api_url + "?api_key=" + api_get.api_key + "&username=" + api_get.username + "&agentID=" + api_get.agent_id + "&campaignName=" + api_get.campaign_name + "&customerNumber=" + number + "&UCID=true&uui=" + random_no
            try:
                r = requests.get(api_con)
            except Exception as e:
                _logger.info('Exception occurred: %s' % str(e))
                raise ValidationError(e)

            if "queued successfully" not in r.text:
                status = r.text.replace("<status>", '')
                status = status.replace("</status>", '')
                raise ValidationError(_(status))
            else:
                call_history = self.env['call.history'].sudo().create({'partner_id': self.id,
                                                                    'phone_number': number,
                                                                    'state': 'in_progress',
                                                                    'ticket_ref': ticket_ref,
                                                                    'call_type': 'outgoing',
                                                                    'uui': random_no
                                                                }) 
                
                if call_history:
                    _logger.info('Call History Created Successfully: %s' % str(call_history))
                    message = 'Call has been queued successfully'
                    self._display_message(message)

        return call_history

    def _display_message(self, message):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }


    def call_phone(self):
        return self._generate_call(self.phone)

    def call_mobile_whatsapp(self):
        template_id = self.env['watsapp.sms.template'].sudo().browse(1)
        message = []
        return self.env['watsapp.sms.gateway'].action_whatsapp_notification(template_id, self.mobile, message, partner_id=self.id)

    def call_mobile(self):
        return self._generate_call(self.mobile)
    
    # def _notify_user(self):
    #     self.env.user.notify_success(message='My success messagessss')
