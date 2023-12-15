from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class FillSurveyTicket(models.TransientModel):
    _name = 'fill.survey.ticket'

    name = fields.Char("Ref")
    url = fields.Char("URL")
    ticket_type = fields.Selection([('child', 'Child'), ('parent', 'Parent')], string="Ticket Type", default="child", required=True)
    child_ticket_id = fields.Many2one('child.ticket', "Child Ticket") 
    survey_id = fields.Many2one('survey.survey', "Survey")
    parent_ticket_id = fields.Many2one('parent.ticket', "Parent Ticket")

    @api.onchange('ticket_type')
    def onchange_ticket_type(self):
        if self.ticket_type == 'child':
            self.parent_ticket_id = False
        if self.ticket_type == 'parent':
            self.child_ticket_id = False
    
    def open_survey_page(self):
        ticket_id = self.child_ticket_id if self.child_ticket_id else self.parent_ticket_id
        existing_feedback = False
        if self.parent_ticket_id:
            existing_feedback = self.survey_id.user_input_ids.filtered(lambda l: l.state in ['done', 'expired'] and l.parent_ticket_id.id == self.parent_ticket_id.id)
        if self.child_ticket_id:
            existing_feedback = self.survey_id.user_input_ids.filtered(lambda l: l.state in ['done', 'expired'] and l.child_ticket_id.id == self.child_ticket_id.id)

        if existing_feedback:
            raise ValidationError(_("Survey has been submitted already for the ticket '%s'", ticket_id.name)) 
        else:
            if self.ticket_type == 'child':
                url = str(self.survey_id.survey_start_url)+'/'+str(self.child_ticket_id.id)+'/'+'child'
            else:
                url = str(self.survey_id.survey_start_url)+'/'+str(self.parent_ticket_id.id)+'/'+'parent'
        return {
            'type': 'ir.actions.act_url',
            'name': "CT Team Survey",
            'target': 'new',
            'url': url,
        }
