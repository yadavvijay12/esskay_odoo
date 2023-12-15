from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import date, datetime


class WhatsappHistory(models.Model):
    _name = 'whatsapp.history'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'about whatsapp_history history'

    # field creation
    sent_to = fields.Char("Sent To",required=True)
    sent_on = fields.Datetime(string='Sent On', required=True, copy=False, default=fields.Datetime.now)
    sent_by = fields.Many2one('res.users', string='Sent by', index=True, default=lambda self: self.env.user, copy=False)
    status = fields.Char("Callback Status")
    state = fields.Selection([('sent', 'Sent'),('delivered', 'Delivered'),('read', 'Read')], string="Status", default="sent", tracking=True)
    delivered_on = fields.Datetime(string='Delivered On', copy=False)
    rqst_ack_id = fields.Char("Request Acknowledgement ID")
    partner_id = fields.Many2one('res.partner', "Customer")
    read_on = fields.Datetime(string='Read On', copy=False)
