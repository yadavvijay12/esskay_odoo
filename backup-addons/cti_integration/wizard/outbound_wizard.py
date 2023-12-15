from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class OutboundWizard(models.TransientModel):
    _name = 'outbound.wizard'
    _description = "Outbound Wizard"

    name = fields.Char("Ref")
    state = fields.Selection([('new', 'Not Sumbitted'),('no_answer','Not Submitted & Not reachable')], string="Status",default="new")
    date_from = fields.Date("From")
    date_to = fields.Date("To") 


    def action_outbound_call_list(self):
        start_date = self.date_from.strftime('%Y-%m-%d 00:00:00')
        end_date = self.date_to.strftime('%Y-%m-%d 23:59:59')
        get_survey_status = self.env['survey.user_input'].search([('create_date','>=',start_date),('create_date','<=',end_date),('state','=', self.state)])
        for rec in get_survey_status:
            get_call_history = self.env['outbound.call.list'].search([('survey_user_input_id','=',rec.id)])
            get_call_history.unlink()
            ticket_ref = ''
            if rec.child_ticket_id:
                ticket_ref = rec.child_ticket_id.name
            if rec.parent_ticket_id:
                ticket_ref = rec.parent_ticket_id.name
            call_list = self.env['outbound.call.list'].create({
                'survey_id':rec.survey_id.id,
                'customer_id':rec.customer_id.id,
                'customer_account_id':rec.customer_account_id.id,
                'state': rec.state,
                'service_category_id':rec.service_category_id.id,
                'service_type_id':rec.service_type_id.id,
                'survey_url': rec.url,
                # 'child_ticket_id':rec.child_ticket_id.id,
                # 'parent_ticket_id':rec.parent_ticket_id.id,
                'ticket_ref': ticket_ref,
                'survey_user_input_id':rec.id,
                'survey_create_date':rec.create_date
                })
        return {
            "name": 'Outbound Call List History',
            "view_mode": "tree,form",
            "res_model": "outbound.call.list",
            "type": "ir.actions.act_window",
        }
