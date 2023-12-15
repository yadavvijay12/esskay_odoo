from odoo import models, fields


class CtiIntegration(models.Model):
    _name = 'cti.integration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "API For Calls Integration"
    _rec_name = 'agent_id'

    _sql_constraints = [
        ('code_uniq', 'unique (code)', "Code already exists !"),
    ]

    name = fields.Char("Name")
    api_url = fields.Char(string="API URL", required=True, size=250, tracking=True)
    api_key = fields.Char(string="API Key", required=True, size=250, tracking=True)
    username = fields.Char(string="Username", required=True, size=255, tracking=True)
    agent_id = fields.Char(string="Agent ID", required=True, size=255, tracking=True)
    campaign_name = fields.Char(string="Campaign Name", required=True, size=255, tracking=True)
    uui = fields.Char(string="UUI", size=500, tracking=True)
    code = fields.Char(string="Unique Code", tracking=True)

    
