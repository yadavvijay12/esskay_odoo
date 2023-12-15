from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import requests
import logging
_logger = logging.getLogger(__name__)
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta
import json


class OutboundCallList(models.Model):
    _name = 'outbound.call.list'
    _description = 'Outbound Call List'
    _order = "create_date desc"

    name = fields.Char(string="Name")
    survey_id = fields.Many2one('survey.survey',string="Survey")
    customer_id = fields.Many2one('res.partner',string="Customer")
    customer_account_id = fields.Many2one('res.partner',string="Customer Account")
    state = fields.Selection([('new', 'Not Submitted'),('in_progress','In Progress'),('done','Completed'),('expired','Expired'),('no_answer','Not Submitted & Not reachable')],string="Status")
    service_category_id = fields.Many2one('service.category',string="Service Category")
    service_type_id= fields.Many2one('service.type',string="Service Type")
    # child_ticket_id = fields.Many2one('child.ticket',string="Child Ticket")
    call_history_id = fields.Many2one('call.history',string="Call History")
    ticket_ref = fields.Char("Ticket Ref")
    survey_user_input_id =fields.Many2one('survey.user_input',string="Participations")
    survey_create_date = fields.Datetime(string="Create Date")
    phone = fields.Char(string="Phone",related="customer_id.phone")
    mobile = fields.Char(string="Mobile",related="customer_id.mobile")
    # disposition = fields.Selection([('rnr1', "RNR1"), ('rnr2', "RNR2"), ('rnr3', "RNR3")], string="Disposition Tags")
    disposition = fields.Char(string="Disposition")
    survey_url = fields.Char(string="Survey URL")
    call_scheduled = fields.Boolean(string="Call scheduled")

    # Progressive bulk campaign calls
    def _bulk_campaign_calls(self):        
        contact_details = []
        priority = 0
        for rec in self.filtered(lambda l: l.customer_id and l.customer_id.mobile or l.customer_id.phone).mapped('customer_id'):
            number = ''
            if rec.mobile:
                number = rec.mobile
            else:
                number = rec.phone or False
            if number:
                expiry_date = datetime.now() + timedelta(hours=8)
                expiry_date = expiry_date.strftime("%Y-%m-%d %H:%M:%S")
                priority += 1
                contact_details.append([str(number), str(rec.name), priority, expiry_date])

        api_get = self.env.ref('cti_integration.cti_integration_api_bulkdata')
        if contact_details and api_get:
            bulk_data = {"map":["PhoneNumber","Name","Priority","ExpiryDate"],"data": contact_details}
            bulk_data = json.dumps(bulk_data)
            api_con = api_get.api_url + "api_key=" + api_get.api_key + "&campaign_name=" + api_get.campaign_name + "&bulkData=" + str(bulk_data)
            try:
                r = requests.post(api_con)
            except Exception as e:
                _logger.info('Exception occurred: %s' % str(e))
                raise ValidationError(e)
            response = json.loads(r.text)
            
            if response:
                if "status" in response:
                    raise ValidationError(_(response['message']))
        for obj in self:
            obj.call_scheduled = True

    def view_survey(self):
        return {
            'type': 'ir.actions.act_url',
            'name': "Survey Link",
            'target': 'new',
            'url': self.survey_url,
        }

    # Call button for mobile
    def action_call_mobile(self):
        for rec in self:
            # ticket_ref = ''
            # if rec.child_ticket_id:
            #     ticket_ref = rec.child_ticket_id.name
            # if rec.parent_ticket_id:
            ticket_ref = rec.ticket_ref or ' '
            if rec.mobile:
                res = rec.customer_id.with_context({'ticket_ref': ticket_ref})._generate_call(rec.mobile)
                if res:
                    rec.call_history_id = res.id
            else:
                raise ValidationError(_("No Mobile number available"))

    # Call button for phone
    def action_call_phone(self):
        for rec in self:
            ticket_ref = rec.ticket_ref or ' '
            if rec.phone:
                res = rec.customer_id.with_context({'ticket_ref': ticket_ref})._generate_call(rec.phone)
                if res:
                    rec.call_history_id = res.id
            else:
                raise ValidationError(_("No Phone number available"))


    def unlink(self):
        for rec in self:
            api_get = self.env.ref('cti_integration.cti_integration_api_delete_data')
            if rec.call_scheduled:
                api_con = "%sapi_key=%s&user_name=%s&campaign_name=%s&caller_number=%s&format=json" % (api_get.api_url, api_get.api_key, api_get.username, api_get.campaign_name, rec.mobile)
                try:
                    requests.get(api_con)
                except Exception as E:
        return super(OutboundCallList, self).unlink()

