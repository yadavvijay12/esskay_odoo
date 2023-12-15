from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class QuestionWiseReportFilter(models.TransientModel):
    _name = 'questionwise.report.filter'
    _description = "Filter report question wise"

    customer_account_id = fields.Many2one('res.partner', "Customer Account")
    service_type_id = fields.Many2one('service.type', string="Service Type")
    service_category_id = fields.Many2one('service.category', string="Service Category")
    question_id = fields.Many2one('survey.question', string="Question")

    def action_confirm(self):
        get_tree = self.env.ref('stryker_survey.question_wise_reports_view_tree').id
        domain = []
        if self.customer_account_id:
            domain += [('user_input_id.customer_id.customer_account_id', '=', self.customer_account_id.id)]
        if self.service_type_id:
            domain += [('user_input_id.service_type_id', '=', self.service_type_id.id)]
        if self.service_category_id:
            domain += [('user_input_id.service_category_id', '=', self.service_category_id.id)]
        if self.question_id:
            domain += [('question_id', '=', self.question_id.id)]
        detailed_answers = self.env['survey.user_input.line'].search(domain)
        for rec in detailed_answers:
            self.env['questionwise.report'].create({
                'customer_id': rec.user_input_id.customer_id.id,
                'customer_account_id': rec.user_input_id.customer_account_id.id,
                'service_type_id': rec.user_input_id.service_type_id.id,
                'service_category_id': rec.user_input_id.service_category_id.id,
                'question_id': rec.question_id.id,
                'answer_score': rec.answer_score,
                'answer': rec.display_name,
                'survey_id':  rec.survey_id.id,
                'user_input_id': rec.user_input_id.id
            })
        return {
            'name': _("Question Wise Report"),
            'view_mode': 'tree',
            'res_model': 'questionwise.report',
            'type': 'ir.actions.act_window',
            'views': [[get_tree, 'tree']],
            'domain': domain,
        }


class QuestionWiseReport(models.TransientModel):
    _name = 'questionwise.report'
    _description = 'Questionwise Report'

    customer_id = fields.Many2one('res.partner', string="Customer")
    customer_account_id = fields.Many2one('res.partner', string="Customer Account")
    service_category_id = fields.Many2one('service.category', string="Service Category")
    service_type_id = fields.Many2one('service.type', string="Service Type")
    question_id = fields.Many2one('survey.question', string="Question")
    survey_id = fields.Many2one('survey.survey', string="Survey")
    user_input_id = fields.Many2one('survey.user_input', string="Survey User Input")
    answer = fields.Char("Answer")
    answer_score = fields.Float("Answer Score")


