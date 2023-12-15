from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class BlastSurveyPopup(models.TransientModel):
    _name = 'blast.survey.popup'
    _description = "Survey Blast Pop-Up"

    name = fields.Char("Ref")
    customer_account_id = fields.Many2one('res.partner', "Customer Account")
    rating = fields.Selection([('passed', 'Passed'), ('failed', 'Failed')], string="Result")
    date_from = fields.Date("From", default=fields.Datetime.now)
    date_to = fields.Date("To", default=fields.Datetime.now) 
    service_type_id = fields.Many2one('service.type', string="Service Type")
    service_category_id = fields.Many2one('service.category', string="Service Category")
    # survey_ids = fields.Many2one('survey.survey', string="Survey")

    def action_survey_blast(self):
        action = self.env['ir.actions.act_window']._for_xml_id('stryker_survey.blast_survey_action')
        # survey_user_input = self.env['survey.user_input'].search([('survey_id', 'in', self.survey_ids.ids),('service_type_id', '=', self.service_type_id.id), ('result', '=', self.rating), ('state', '=', 'done')]).filtered(lambda x: x.create_date >= self.date_from and x.create_date <= self.date_to)
        # print(survey_user_input, "survey_user_input")
        domain = []
        if self.rating:
            domain += [('result', '=', self.rating)]
        
        if self.service_category_id:
            domain += [('service_category_id', '=', self.service_category_id.id)]  

        if self.service_type_id:
            domain += [('service_type_id', '=', self.service_type_id.id)]

        if self.date_from and self.date_to:
            date_from = datetime.combine(self.date_from, datetime.min.time())
            date_to = datetime.combine(self.date_to, datetime.max.time())
            domain += [('create_date', '>=', date_from), ('create_date', '<=', date_to)]

        survey_user_input = self.env['survey.user_input'].search(domain)   
        
        if self.customer_account_id:
            survey_user_input = survey_user_input.filtered(lambda x : x.customer_id.customer_account_id.id == self.customer_account_id.id)
        print(len(survey_user_input), "survey_user_input")
        for rec in survey_user_input:
            ticket_ref = ''
            if rec.child_ticket_id:
                ticket_ref = rec.child_ticket_id.name
            if rec.parent_ticket_id:
                ticket_ref = rec.parent_ticket_id.name

            blast_survey = self.env['blast.survey'].create({'name': ticket_ref,
                                                            'customer_id': rec.customer_id.id or False,
                                                            'customer_account_id': rec.customer_account_id.id or False,
                                                            'result': rec.result,
                                                            'service_type_id': rec.service_type_id.id or False,
                                                            'service_category_id': rec.service_category_id.id or False,
                                                            'survey_id': rec.survey_id.id,
                                                            'user_input_id': rec.id
                                                            })
            print(blast_survey, "blast_survey")

        return action