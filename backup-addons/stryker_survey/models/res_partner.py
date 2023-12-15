from odoo import fields, models, api, _
from odoo.exceptions import ValidationError 
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    survey_count = fields.Integer(compute="_compute_survey_count")
    task_list_ids = fields.One2many('tasks.master.line', 'partner_id', string="Survey Configurations")
    service_category_ids = fields.Many2many('service.category', 'service_categ_partner_rel', string="Service Category")
    service_type_ids = fields.Many2many('service.type', 'service_type_partner_rel', string="Service Type")
    
    def action_view_survey_feedbacks(self):
        survey_data = self.env['survey.user_input'].search(
            [('customer_id', '=', self.id)])
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
            survey_data = self.env['survey.user_input'].search([('customer_id', '=', self.id)])
            if survey_data:
                survey_count = len(survey_data)
            record.survey_count = survey_count

    @api.onchange('customer_account_id')
    def onchange_customer_account_id(self):
        for rec in self:
            # rec.task_list_ids = [(5, 0, 0)]
            rec.task_list_ids = False
            task_list = []
            rec.service_category_ids = [(5, 0, 0)]
            rec.service_type_ids = [(5, 0, 0)]
            if rec.customer_account_id:
                if rec.customer_account_id.task_list_ids:

                    for vals in rec.customer_account_id.task_list_ids:
                        line_vals = (0, 0, {
                                'condition_id':vals.condition_id.id,
                                'resend_limit':vals.resend_limit,
                                'period':vals.period,
                                'unit':vals.unit,
                                'trigger_action':vals.trigger_action,
                                'escalation': vals.escalation,
                                'channel':vals.channel,
                                'survey_id': vals.survey_id.id,
                                'request_type': vals.request_type.id,
                                'partner_id': rec.id
                                })
                        task_list.append(line_vals)

                    rec.task_list_ids = task_list
                    
                if rec.customer_account_id.service_category_ids:
                    rec.service_category_ids = rec.customer_account_id.service_category_ids.ids
                if rec.customer_account_id.service_type_ids:
                    rec.service_type_ids = rec.customer_account_id.service_type_ids.ids


class SurveyConfiguration(models.Model):
    _inherit = 'tasks.master.line'

    # @api.constrains('period', 'unit')
    # def _check_vals(self):
    #     for rec in self:
    #         if rec.period < 1 and rec.unit != 'immediate':
    #             raise ValidationError(_("Survey Configuration: For 'minutes/hours/days' the period must be greater than 0"))

    condition_id = fields.Many2one('tasks.master', string='Condition', domain="['|','|','|','|',('is_end_task', '=', True),('is_create_service_request', '=', True),('is_survey_passed', '=', True),('is_sr_escalation_open', '=', True),('is_sr_escalation_progress', '=', True)]", required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', ondelete='cascade')
    period = fields.Integer(string='Period')
    unit = fields.Selection([('immediate', 'Immediately'),('minute', 'Minutes'), ('hour', 'Hours'), ('day', 'Days')], string='Unit', required=True)
    trigger_action = fields.Selection([('trigger_survey', 'Trigger Survey'), ('create_sr', 'Create Service Request'), ('reassign_sr', 'Reassign Service Request')], string="Trigger Action", required=True)
    escalation = fields.Selection([('1', 'Level 1'), ('2', 'Level 2')], string="Escalation")
    channel = fields.Selection([('email', 'E-mail'), ('whatsapp', 'WhatsApp'),('email_whatsp', 'Email & Whatsapp')], string="Channel")
    survey_id = fields.Many2one('survey.survey', "Survey")
    request_type = fields.Many2one('request.type', "Request", domain="[('ticket_type', '=', 'sr_survey_escalation')]")
    resend_limit = fields.Integer("Resend Limit")
    sent_count = fields.Integer("Sent Count")
    restrict_channel = fields.Boolean("Restrict Channel", compute="_compute_vals")
    restrict_escalation = fields.Boolean("Restrict Esc", compute="_compute_vals")
    whatsapp_template_id = fields.Many2one('watsapp.sms.template', "Whatsapp Template")

    @api.onchange('condition_id')
    def _compute_vals(self):
        for rec in self:
            if rec.condition_id.is_create_service_request:
                rec.restrict_channel = True
            else:
                rec.restrict_channel = False
            if rec.condition_id.is_survey_passed:
                rec.restrict_escalation = True
            else:
                rec.restrict_escalation = False

    @api.onchange('unit')
    def _onchange_trigger_action(self):
        for rec in self:
            if rec.unit == 'immediate':
                rec.period = 0
            else:
                rec.period = rec.period

    def button_tasks_update(self):
        super(SurveyConfiguration, self).button_tasks_update()
        for line in self:
            parent_ticket = line.parent_ticket_id
            if parent_ticket.company_id.survey_notification:
                if line.parent_ticket_id and line.task_id.is_end_task and line.is_end_task:
                    mail_template_parent = self.env.ref('stryker_survey.parent_ticket_survey_generation')
                    if parent_ticket.survey_id:
                        survey_config = parent_ticket.partner_id.task_list_ids.filtered(lambda x: x.condition_id.is_end_task == True and x.trigger_action == 'trigger_survey' and x.unit == 'immediate' and x.survey_id.id == parent_ticket.survey_id.id )
                        if survey_config and not parent_ticket.survey_sent and parent_ticket.service_category_id.id in parent_ticket.partner_id.service_category_ids.ids and parent_ticket.service_type_id.id in parent_ticket.partner_id.service_type_ids.ids:
                            for conf in survey_config:
                                url = str(conf.survey_id.survey_start_url)+'/'+str(parent_ticket.id)+'/'+'parent'
                                if conf.trigger_action == 'trigger_survey' and conf.period <= 0 and conf.channel:
                                    # Sending Survey Email
                                    if conf.channel in ['email', 'email_whatsp']:
                                        mail_template_parent.with_context({'url': url}).send_mail(parent_ticket.id, force_send=True)
                                    # Sending Whatsapp SMS
                                    whatsapp_url = url.split("start/",1)[1]
                                    print(whatsapp_url, "whatsapp_url----")
                                    if conf.channel in ['whatsapp', 'email_whatsp']:
                                        if conf.whatsapp_template_id and parent_ticket.partner_id.mobile:
                                            message = [
                                                {
                                                    "type": "text",
                                                    "text": parent_ticket.partner_id.name
                                                }
                                                ]
                                            button_message = [
                                                {
                                                    "index": "0",
                                                    "subType": "callToAction",
                                                    "parameters": {
                                                        "type": "text",
                                                        "text": whatsapp_url
                                                    }
                                                }
                                            ]
                                            try:
                                                self.env['watsapp.sms.gateway'].action_whatsapp_notification(conf.whatsapp_template_id, parent_ticket.partner_id.mobile, message, button_message, partner_id=parent_ticket.partner_id.id)
                                            except Exception as e:
                                                _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)

                                    conf.survey_id._create_answer(user=self.env.user, partner=parent_ticket.partner_id, ticket_id=parent_ticket.id, ticket_type='parent',template_id=mail_template_parent.id)
                                    parent_ticket.survey_sent = True
                    parent_ticket.ticket_closure = datetime.now()

            child_ticket = line.child_ticket_id
            if child_ticket.company_id.survey_notification:
                if line.child_ticket_id and line.task_id.is_end_task and line.is_end_task:
                    mail_template_child = self.env.ref('stryker_survey.child_ticket_survey_generation')
                    # job_closed = self.env.ref('stryker_survey.view_job_closed')
                    if child_ticket.survey_id:
                        survey_config = child_ticket.partner_id.task_list_ids.filtered(lambda x: x.condition_id.is_end_task == True and x.trigger_action == 'trigger_survey' and x.unit == 'immediate' and x.survey_id.id == child_ticket.survey_id.id)
                        if survey_config and not child_ticket.survey_sent and child_ticket.service_category_id.id in child_ticket.partner_id.service_category_ids.ids and child_ticket.service_type_id.id in child_ticket.partner_id.service_type_ids.ids:
                            for conf in survey_config:
                                url = str(conf.survey_id.survey_start_url)+'/'+str(child_ticket.id)+'/'+'child'
                                if conf.trigger_action == 'trigger_survey' and conf.period <= 0 and conf.channel:
                                    # Sending Survey Email
                                    if conf.channel in ['email', 'email_whatsp']:
                                        mail_template_child.with_context({'url': url}).send_mail(child_ticket.id, force_send=True)
                                    # Sending Whatsapp SMS
                                    whatsapp_url = url.split("start/",1)[1]
                                    if conf.channel in ['whatsapp', 'email_whatsp']:
                                        if conf.whatsapp_template_id and child_ticket.partner_id.mobile:
                                            message = [
                                                {
                                                    "type": "text",
                                                    "text": child_ticket.partner_id.name
                                                }
                                                ]
                                            button_message = [
                                                {
                                                    "index": "0",
                                                    "subType": "callToAction",
                                                    "parameters": {
                                                        "type": "text",
                                                        "text": whatsapp_url
                                                    }
                                                }
                                            ]
                                            try:
                                                self.env['watsapp.sms.gateway'].action_whatsapp_notification(conf.whatsapp_template_id, child_ticket.partner_id.mobile, message, button_message, partner_id=child_ticket.partner_id.id)
                                            except Exception as e:
                                                _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)

                                    conf.survey_id._create_answer(user=self.env.user, partner=child_ticket.partner_id, ticket_id=child_ticket.id, ticket_type='child', template_id=mail_template_child.id)
                                    child_ticket.survey_sent = True
                    child_ticket.ticket_closure = datetime.now()
