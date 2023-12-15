from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class BlastSurvey(models.TransientModel):
    _name = 'blast.survey'
    _description = "Blast Survey"

    def action_blast_survey(self):
        # mail_template_parent = self.env.ref('stryker_survey.parent_ticket_survey_generation')
        customers = []
        blast_history = []
        for rec in self:
            if rec.customer_id.id not in customers:
                customers.append(rec.customer_id.id)
                history = {
                    'partner_id': rec.customer_id.id or False,
                    'customer_account_id': rec.customer_account_id.id or False,
                    'survey_id': rec.survey_id.id or False,
                    'name': rec.name,
                    'service_type_id':rec.service_type_id.id or False,
                    'service_category_id': rec.service_category_id.id or False,
                    'user_input_id': rec.user_input_id.id
                }
                blast_history.append(history)

        template = self.env.ref('survey.mail_template_user_input_invite', raise_if_not_found=False)
        local_context = dict(
            self.env.context,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_email_layout_xmlid='mail.mail_notification_light',
        )
        if blast_history:
            local_context.update({'blast_history': blast_history})
        if customers:
            local_context.update({'default_partner_ids': customers})
            
        view = self.env.ref('stryker_survey.survey_blast_view_form')
        return {
            'type': 'ir.actions.act_window',
            'name': _("Blast Survey"),
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_model': 'survey.invite',
            'target': 'new',
            'context': local_context,
        }

    name = fields.Char("Ticket Ref")
    customer_id = fields.Many2one('res.partner', string="Customer")
    customer_account_id = fields.Many2one('res.partner', string="Customer Account")
    result = fields.Selection([('passed', 'Passed'), ('failed', 'Failed')], string="Result")
    service_type_id = fields.Many2one('service.type', string="Service Type")
    service_category_id = fields.Many2one('service.category', string="Service Category")
    survey_id = fields.Many2one('survey.survey', string="Survey")
    user_input_id = fields.Many2one('survey.user_input', string="Survey User")

class BlastSurveyHistory(models.Model):
    _name = 'survey.blast.history'
    _description = "Survey Blast History"

    name = fields.Char("Ticket Ref")
    partner_id = fields.Many2one('res.partner', string="Customer")
    customer_account_id = fields.Many2one('res.partner', string="Customer Account")
    sent_date = fields.Datetime("Sent Date", default=datetime.now())
    survey_id = fields.Many2one('survey.survey', string="Survey")
    service_type_id = fields.Many2one('service.type', string="Service Type")
    service_category_id = fields.Many2one('service.category', string="Service Category")
    user_input_id = fields.Many2one('survey.user_input', string="Survey User")
 
 
    