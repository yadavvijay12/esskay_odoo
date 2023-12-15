from odoo import models, fields, api, _


class StockLot(models.Model):
    _inherit = "stock.lot"

    survey_count = fields.Integer(compute="_compute_survey_count")

    def action_view_survey_feedbacks(self):
        survey_data = self.env['survey.user_input'].search(
            ['|', ('child_ticket_id.stock_lot_id', '=', self.id), ('parent_ticket_id.stock_lot_id', '=', self.id)])
        return {
            'name': "Surveys",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'survey.user_input',
            'domain': [('id', 'in', survey_data.ids)],
            'views': [[False, 'list'], [False, 'form']]
        }

    def _compute_survey_count(self):
        for record in self:
            survey_count = 0
            # if record.name:
            survey_data = self.env['survey.user_input'].search(['|', ('child_ticket_id.stock_lot_id', '=', self.id), ('parent_ticket_id.stock_lot_id', '=', self.id)])
            if survey_data:
                survey_count = len(survey_data)
            record.survey_count = survey_count