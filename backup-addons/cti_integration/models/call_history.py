from odoo import models, fields, api, _
from datetime import date, datetime


class CallHistory(models.Model):
    _name = 'call.history'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Call History"
    _rec_name = "agent_name"
    _order = 'create_date desc'

    @api.model
    def create(self, vals):
        vals['unique_code'] = self.env['ir.sequence'].next_by_code('call.history') or str(0)
        result = super(CallHistory, self).create(vals)
        return result

    unique_code = fields.Char(string="Unique ID")
    partner_id = fields.Many2one('res.partner', string="Customer", readonly=True)
    ticket_ref = fields.Char("Ticket Reference", readonly=True)
    # child_ticket_id = fields.Many2one('child.ticket', string='Child Ticket',copy=False, readonly=True)
    # parent_ticket_id = fields.Many2one('parent.ticket', string='Parent Ticket',copy=False, readonly=True)
    state = fields.Selection([('in_progress', 'Call In-Progress'), ('closed', 'Call Closed')], string="Status", copy=False, default="in_progress")
    agent_id = fields.Char(string="Agent ID", size=255, readonly=True)
    agent_name = fields.Char(string="Agent Name", size=255, readonly=True)
    agent_phone_number = fields.Char(string="Agent Phone Number", size=20, readonly=True)
    agent_status = fields.Char(string="Agent Status", size=50, readonly=True)
    agent_unique_id = fields.Char(string="Agent Unique ID", size=20, readonly=True)
    api_key = fields.Char(string="Apikey", size=250, readonly=True)
    audio_file = fields.Char(string="Audio File", readonly=True)
    # file_audio = fields.Binary("Call Recording")
    caller_audio_file = fields.Char(string="Caller Conf Audio File", size=500, readonly=True)
    caller_id = fields.Char(string="Caller ID", size=255, readonly=True)
    campaign_name = fields.Char(string="Campaign Name", size=255, readonly=True)
    campaign_status = fields.Char(string="Campaign status", size=20, readonly=True)
    comments = fields.Text(string="Comments", readonly=True)
    conf_duration = fields.Char(string="Conference Duration", readonly=True)
    customer_status = fields.Char(string="Customer Status", size=50, readonly=True)
    dial_status = fields.Char(string="Dial Status", size=100, readonly=True)
    dialed_number = fields.Char(string="Dialed Number", size=20, readonly=True)
    did = fields.Char(string="DID", size=30, readonly=True)
    disposition = fields.Char(string="Disposition", size=100, readonly=True)
    duration = fields.Char(string="Total Duration", readonly=True)
    end_times = fields.Char(string="End Time", readonly=True)
    fall_back_rule = fields.Char(string="Fall Back Rule", size=255, readonly=True)
    hangup_by = fields.Char(string="Hangup By", size=100, readonly=True)
    location = fields.Char(string="Location", size=255, readonly=True)
    monitor_ucid = fields.Char(string="Monitor UCID", size=20, readonly=True)
    phone_number = fields.Char(string="Phone Number", size=20, readonly=True)
    skill = fields.Char(string="Skill", size=255, readonly=True)
    start_datetime = fields.Char(string="Start Time", readonly=True)
    status = fields.Char(string="Status", readonly=True)
    answered_datetime = fields.Char(string="Time To Answer", readonly=True)
    transfer_type = fields.Char(string="Transfer Type", size=30, readonly=True)
    transfer_to = fields.Char(string="Transfer To", size=30, readonly=True)
    type = fields.Char(string="Type", size=20, readonly=True)
    username = fields.Char(string="Username", size=50, readonly=True)
    uui = fields.Char(string="UUI", size=500, readonly=True)
    call_duration = fields.Char(string="Call Duration", readonly=True)
    call_type = fields.Selection([('incoming', 'Incoming Call'),('outgoing', 'Outgoing Call')], string="Call Type")
    created_date = fields.Date("Created Date", default=date.today())
    
    # @api.depends("start_time", "end_time")
    # def calculate_duration(self):
    #     for rec in self:
    #         duration = 0
    #         if rec.start_time and rec.end_time:
    #             delta = rec.end_time - rec.start_time
    #             duration += delta.total_seconds() / 3600.0
    #         rec.call_duration = duration

    def action_play_recording(self):
        url = self.audio_file
        if url:
            return {
                'type': 'ir.actions.act_url',
                'name': "CT Team Survey",
                'target': 'new',
                'url': url,
            }

    def action_close(self):
        user = self.env.user
        message = 'Thank you'
        return user.sudo().notify_success(message='My success message')
        # return self.env['bus.bus']._sendone(user.partner_id, 'success_notify', {
        #         'type': "success",
        #         'title': _("Incoming Call"),
        #         'message': message,
        #         'sticky': True
        #     })
        
        # return self.write({'state': 'closed'})
