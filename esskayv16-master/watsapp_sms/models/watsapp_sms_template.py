# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
import requests
from odoo import api, exceptions, fields, models, _
from requests.auth import HTTPBasicAuth
import json

class WatsappSmsTemplate(models.Model):   
    _name = "watsapp.sms.template"
    
    name = fields.Char(required=True, string='Name', placeholder='Please specify the name in lowercase letters...')
    template_gateway_id = fields.Many2one('watsapp.sms.gateway',required=True,string='Template Gateway')
    gateway_id = fields.Many2one('watsapp.sms.gateway',required=True,string='SMS Gateway')
    model_id = fields.Many2one('ir.model', string='Applies to', help="The kind of document with with this template can be used")
    language = fields.Many2one('res.lang',string="Language")
    is_customer = fields.Boolean('Customer',copy=False)
    is_internal = fields.Boolean('Internal',copy=False)
    mobile_int = fields.Char('Mobile')
    sms_html = fields.Text('Body')
    quote_usage = fields.Boolean('Quotation')
    quote_revision_usage = fields.Boolean('Quotation Revision')
    state = fields.Selection([('to_be_sent','To Be Sent'),('pending','Sent For Approval'),('approved','Approved')], default='to_be_sent', string='Status')
    active = fields.Boolean(string='Active', default=True)
    response = fields.Text('Response', readonly=True)
    watsapp_dynamic_line = fields.One2many('watsapp.dynamic.value','watsapp_dynamic_id',string="Whatsapp Dynamic")

    def action_send_approval(self):
        url = str(self.template_gateway_id.gateway_url)
        content_type = str(self.template_gateway_id.content_type)
        api_version = str(self.template_gateway_id.api_version)
        category = str(self.template_gateway_id.category)
        whatsapp_account_uid = str(self.template_gateway_id.whatsapp_account_uid)
        language_code = str(self.template_gateway_id.language_code)
        template_name = str(self.name)
        message = str(self.sms_html)
        username = str(self.template_gateway_id.username)
        password = str(self.template_gateway_id.password)
        
  #       requests.get(
        #   'https://api.github.com/user', 
        #   auth=HTTPBasicAuth('19e460ce-a39d-484e-8146-fae210bf7dfe', 'fb385a0e-14b7-450c-8e1b-ebba0e916fa2')
        # )

        h = {'Content-Type': content_type, 'api-version': api_version}
        d = json.dumps({'category': category, 'whatsapp_account_uid': whatsapp_account_uid, 'language_code': language_code, 'name': template_name, 'text': message})
        auth = HTTPBasicAuth(username, password)
        # response= requests.post(url, headers = h, data=d)
        try:
            response = requests.post(url, headers = h, data = d, auth = auth)
            self.state = 'pending'
            self.response = response.text
        except Exception as e:
            raise exceptions.ValidationError(e)
        return True


    def action_status(self):
        url = str(self.template_gateway_id.gateway_url)
        content_type = str(self.template_gateway_id.content_type)
        api_version = str(self.template_gateway_id.api_version)
        category = str(self.template_gateway_id.category)
        whatsapp_account_uid = str(self.template_gateway_id.whatsapp_account_uid)
        language_code = str(self.template_gateway_id.language_code)
        template_name = str(self.name)
        message = str(self.sms_html)
        username = str(self.template_gateway_id.username)
        password = str(self.template_gateway_id.password)
        
  #       requests.get(
        #   'https://api.github.com/user', 
        #   auth=HTTPBasicAuth('19e460ce-a39d-484e-8146-fae210bf7dfe', 'fb385a0e-14b7-450c-8e1b-ebba0e916fa2')
        # )

        h = {'Content-Type': content_type, 'api-version': api_version}
        d = json.dumps({'category': category, 'whatsapp_account_uid': whatsapp_account_uid, 'language_code': language_code, 'name': template_name})
        auth = HTTPBasicAuth(username, password)
        # response= requests.post(url, headers = h, data=d)
        try:
            response = requests.get(url, headers = h, data = d, auth = auth)
            res_json = response.json()

            # res_json['results'][0]['geometry']['location']['lat']
            res_json_data = res_json['objects']
            for rec in res_json_data:
                if rec['name'] == self.name and rec['status'] == 'approved':
                    self.state = 'approved'
            
            # self.state = 'approved'
            # self.response = response.text
        except Exception as e:
            raise exceptions.ValidationError(e)
        return True

class WatsappDynamicValue(models.Model):
    _name = "watsapp.dynamic.value"
    _description = "Watsapp Dynamic Value"
    _order = 'sequence desc'

    name = fields.Char(string="Name")
    watsapp_dynamic_id = fields.Many2one('watsapp.sms.template')
    sequence = fields.Integer(string="Sequence",compute="_sequence_ref")
    seq_no = fields.Integer(string="No")

    # Automatically create the sequence based on the line items 11-10-22
    @api.depends('watsapp_dynamic_id.watsapp_dynamic_line','watsapp_dynamic_id.watsapp_dynamic_line.name')
    def _sequence_ref(self):
        for line in self:
            no = 0
            line.sequence = no
            for l in line.watsapp_dynamic_id.watsapp_dynamic_line:
                no += 1
                l.sequence = no

