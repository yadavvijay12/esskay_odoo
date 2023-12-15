from odoo import fields, models, api, _
from datetime import datetime, timedelta
import pytz


# from odoo.http import request


class ParentTicketInherit(models.Model):
    _inherit = "parent.ticket"

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            args += ['|', ('name', operator, name), ('parent_ticket_id_alias', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    survey_id = fields.Many2one('survey.survey', string="Survey",
                                help="Please select the survey which has to be sent to the customer via Email, WhatsApp etc,.")
    ticket_closure = fields.Datetime('Ticket Closure Timing', copy=False)
    survey_sent = fields.Boolean('Survey Sent', copy=False)
    url = fields.Char('URL', copy=False)
    survey_sent_count = fields.Integer('Survey Sent Count', copy=False)
    url_two = fields.Char('URL Two', copy=False)
    success_survey_sent = fields.Boolean(default=False)
    state = fields.Selection(
        selection_add=[('esc_new', "Esc-New"), ('esc_inprogress', "Esc-Inprogress"), ('esc_closed', "Esc-Closed")])
    survey_ids = fields.Many2many('survey.survey', 'survey_pt_rel', string="Surveys", compute="_compute_survey_ids")

    def _compute_survey_ids(self):
        for record in self:
            record.survey_ids = None
            surveys = self.env['survey.user_input'].search([('parent_ticket_id', '=', record.id)]).survey_id
            if surveys:
                record.survey_ids = [(6, 0, [survey.id for survey in surveys])]

    def view_survey_feedback(self):
        feedback = self.env['survey.user_input'].search(
            [('parent_ticket_id', '=', self.id), ('survey_id', '=', self.survey_id.id)], limit=1)
        return {
            'name': ("Survey Feedback"),
            'res_model': 'survey.user_input',
            'type': 'ir.actions.act_window',
            'res_id': feedback.id,
            'view_mode': 'form',
        }

    @api.onchange('service_category_id', 'service_type_id', 'partner_id')
    def onchange_service(self):
        for rec in self:
            if rec.service_category_id.id in self.partner_id.service_category_ids.ids and rec.service_type_id.id in self.partner_id.service_type_ids.ids:
                # job_closed = self.env.ref('stryker_survey.view_job_closed')
                survey_config = self.partner_id.task_list_ids.filtered(
                    lambda x: x.condition_id.is_end_task == True and x.trigger_action == 'trigger_survey')
                rec.survey_id = survey_config[0].survey_id.id if survey_config else False


class ChildTicketInherit(models.Model):
    _inherit = "child.ticket"

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name:
            args += ['|', ('name', operator, name), ('child_ticket_id_alias', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    survey_id = fields.Many2one('survey.survey', string="Survey",
                                help="Please select the survey which has to be sent to the customer via Email, WhatsApp etc,.")
    ticket_closure = fields.Datetime('Ticket Closure Timing', copy=False)
    survey_sent = fields.Boolean('Survey Sent', copy=False)
    url = fields.Char('URL', copy=False)
    url_two = fields.Char('URL Two', copy=False)
    assign_engineer_ids = fields.Many2many('res.users', compute="_compute_assign_engineer_ids", store=True)
    success_survey_sent = fields.Boolean(default=False)
    state = fields.Selection(
        selection_add=[('esc_new', "Esc-New"), ('esc_inprogress', "Esc-Inprogress"), ('esc_closed', "Esc-Closed")])
    survey_ids = fields.Many2many('survey.survey', 'survey_pt_rel', string="Surveys", compute="_compute_survey_ids")

    def _compute_survey_ids(self):
        for record in self:
            record.survey_ids = None
            surveys = self.env['survey.user_input'].search([('parent_ticket_id', '=', record.id)]).survey_id
            if surveys:
                record.survey_ids = [(6, 0, [survey.id for survey in surveys])]

    @api.depends('child_assign_engineer_ids')
    def _compute_assign_engineer_ids(self):
        for rec in self:
            if rec.child_assign_engineer_ids:
                rec.assign_engineer_ids = rec.child_assign_engineer_ids.ids
            else:
                rec.assign_engineer_ids = [(5, 0, 0)]

    @api.onchange('service_category_id', 'service_type_id', 'partner_id')
    def onchange_service(self):
        for rec in self:
            if rec.service_category_id.id in self.partner_id.service_category_ids.ids and rec.service_type_id.id in self.partner_id.service_type_ids.ids:
                survey_config = self.partner_id.task_list_ids.filtered(
                    lambda x: x.condition_id.is_end_task == True and x.trigger_action == 'trigger_survey')
                rec.survey_id = survey_config[0].survey_id.id if survey_config else False

    def view_survey_feedback(self):
        feedback = self.env['survey.user_input'].search(
            [('child_ticket_id', '=', self.id), ('survey_id', '=', self.survey_id.id)], limit=1)
        return {
            'name': ("Survey Feedback"),
            'res_model': 'survey.user_input',
            'type': 'ir.actions.act_window',
            'res_id': feedback.id,
            'view_mode': 'form',
        }


class ServiceRequest(models.Model):
    _inherit = "service.request"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('request_type') == 'sr_survey_escalation':
            survey_esc_id = self.env['request.type'].search(
                [('ticket_type', '=', 'sr_survey_escalation'), ('team_id', 'in', self.env.user.team_ids.ids)], limit=1)
            res['request_type_id'] = survey_esc_id.id
        return res

    def _get_user(self):
        return self.env.user

    @api.model
    def _action_escalate_sr(self):
        # current_uid = request.env.context.get('uid') 
        user = self.env['service.request']._get_user()

        # Converting datetime into local timezone
        user_tz = user.tz
        user_pytz = pytz.timezone(user_tz) if user_tz else pytz.utc
        date_now = datetime.now() + timedelta(hours=5, minutes=30)
        open_requests = self.sudo().search(['|', ('escalated_lvl_one', '=', False), ('escalated_lvl_two', '=', False),
                                            ('request_type_id.ticket_type', '=', 'sr_survey_escalation'),
                                            ('state', 'in', ['se_inprogress', 'in_review'])])
        # print(open_requests, "open_requests")
        for rec in open_requests:
            if rec.state in ['draft', 'new']:
                esc_date = rec.create_date
            if rec.state in ['se_inprogress', 'in_review']:
                esc_date = rec.in_progress_date
            if esc_date:
                req_created = esc_date + timedelta(hours=5, minutes=30)
                # Fetching hours difference between ticket's closure timing and current time.
                diff = date_now - req_created
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds // 3600
                minutes = seconds // 60
                # print(days, "dayss", hours, "hours", minutes, "minutes")
                # Interval for Sending Survey which is set at General settings (Companywise).
                if rec.child_ticket_id and rec.state in ['draft', 'new']:
                    survey_config = rec.child_ticket_id.partner_id.task_list_ids.filtered(lambda
                                                                                              l: l.condition_id.is_sr_escalation_open == True and l.trigger_action == 'reassign_sr' and l.period > 0)
                if rec.child_ticket_id and rec.state in ['se_inprogress', 'in_review']:
                    survey_config = rec.child_ticket_id.partner_id.task_list_ids.filtered(lambda
                                                                                              l: l.condition_id.is_sr_escalation_progress == True and l.trigger_action == 'reassign_sr' and l.period > 0)

                if rec.parent_ticket_id and rec.state in ['draft', 'new']:
                    survey_config = rec.parent_ticket_id.partner_id.task_list_ids.filtered(lambda
                                                                                               l: l.condition_id.is_sr_escalation_open == True and l.trigger_action == 'reassign_sr' and l.period > 0)
                if rec.parent_ticket_id and rec.state in ['se_inprogress', 'in_review']:
                    survey_config = rec.parent_ticket_id.partner_id.task_list_ids.filtered(lambda
                                                                                               l: l.condition_id.is_sr_escalation_progress == True and l.trigger_action == 'reassign_sr' and l.period > 0)
                    # print(survey_config, "survey_config")

                nsm_list = []
                for nsm in rec.assign_engineer_ids:
                    employee = self.env['hr.employee'].sudo().search([('user_id', '=', nsm.id)], limit=1)
                    if employee and employee.coach_id and employee.coach_id.user_id:
                        nsm_list.append({'nsm_engineer': employee.coach_id.user_id,
                                         'rsm_engineer': nsm})

                for conf in survey_config:
                    escalation_nsm_one = self.env.ref('stryker_survey.sr_escalation_lvl_one')
                    escalation_nsm_two = self.env.ref('stryker_survey.sr_escalation_lvl_two')
                    # period = str(conf.period) + " " + str(conf.unit)
                    for obj in nsm_list:
                        # escalation_lvl_one.with_context({'email_to': obj.get('nsm_engineer').partner_id.email, 'nsm_name': obj.get('nsm_engineer').name, 'rsm_name': obj.get('rsm_engineer').name}).send_mail(rec.id, force_send=True)
                        if conf.unit == 'hour' and hours >= conf.period:
                            # if not rec.escalated_lvl_one or not rec.escalated_lvl_two:
                            if not rec.escalated_lvl_one and rec.state in ['draft', 'new']:
                                escalation_nsm_one.with_context({'email_to': obj.get('nsm_engineer').partner_id.email,
                                                                 'nsm_name': obj.get('nsm_engineer').name}).send_mail(
                                    rec.id, force_send=True)
                                rec.sudo().write({'escalated_lvl_one': True})
                            if not rec.escalated_lvl_two and rec.state in ['se_inprogress', 'in_review']:
                                escalation_nsm_two.with_context({'email_to': obj.get('nsm_engineer').partner_id.email,
                                                                 'nsm_name': obj.get('nsm_engineer').name}).send_mail(
                                    rec.id, force_send=True)
                                rec.sudo().write({'escalated_lvl_two': True})

                        elif conf.unit == 'day' and days >= conf.period:
                            # if not rec.escalated_lvl_one or not rec.escalated_lvl_two:
                            if not rec.escalated_lvl_one and rec.state in ['draft', 'new']:
                                escalation_nsm_one.with_context({'email_to': obj.get('nsm_engineer').partner_id.email,
                                                                 'nsm_name': obj.get('nsm_engineer').name}).send_mail(
                                    rec.id, force_send=True)
                                rec.sudo().write({'escalated_lvl_one': True})
                            if not rec.escalated_lvl_two and rec.state in ['se_inprogress', 'in_review']:
                                escalation_nsm_two.with_context({'email_to': obj.get('nsm_engineer').partner_id.email,
                                                                 'nsm_name': obj.get('nsm_engineer').name}).send_mail(
                                    rec.id, force_send=True)
                                rec.sudo().write({'escalated_lvl_two': True})

                        elif conf.unit == 'minute' and minutes >= conf.period:
                            # if not rec.escalated_lvl_one or not rec.escalated_lvl_two:
                            if not rec.escalated_lvl_one and rec.state in ['draft', 'new']:
                                escalation_nsm_one.with_context({'email_to': obj.get('nsm_engineer').partner_id.email,
                                                                 'nsm_name': obj.get('nsm_engineer').name}).send_mail(
                                    rec.id, force_send=True)
                                rec.sudo().write({'escalated_lvl_one': True})
                            if not rec.escalated_lvl_two and rec.state in ['se_inprogress', 'in_review']:
                                escalation_nsm_two.with_context({'email_to': obj.get('nsm_engineer').partner_id.email,
                                                                 'nsm_name': obj.get('nsm_engineer').name}).send_mail(
                                    rec.id, force_send=True)
                                rec.sudo().write({'escalated_lvl_two': True})

        parent_tickets = self.env['parent.ticket'].sudo().search(
            ['|', ('service_request_id.escalated_lvl_one', '=', False),
             ('service_request_id.escalated_lvl_two', '=', False), ('state', 'in', ['esc_new', 'esc_inprogress'])])
        print(parent_tickets, "parent_tickets-------")
        # for parent_ticket in parent_tickets:

    ticket_ref = fields.Char("Ticket Ref", copy=False)
    assign_engineer_ids = fields.Many2many(comodel_name='res.users', relation='service_request_assign_engineer_rel',
                                           string="Engineers")
    rsm_ids = fields.Many2many(comodel_name='res.users', relation='service_request_rsm_rel', string="R.S.M", copy=False,
                               compute="_compute_rsm_nsm_ids", store=True)
    nsm_ids = fields.Many2many(comodel_name='res.users', relation='service_request_nsm_rel', string="N.S.M", copy=False,
                               compute="_compute_rsm_nsm_ids", store=True)
    is_escalation = fields.Boolean("Is a survey Escalation?", copy=False)
    state = fields.Selection(
        selection_add=[('se_open', "Survey Escalation Open"), ('se_inprogress', "Survey Escalation In Progress"),
                       ('se_resolved', "Survey Escalation Resolved"), ('se_cancelled', "Survey Escalation Cancelled")])
    child_ticket_id = fields.Many2one('child.ticket', string='Child Ticket', copy=False)
    parent_ticket_id = fields.Many2one('parent.ticket', string='Parent Ticket', copy=False)
    escalated_lvl_one = fields.Boolean("Escalated One", copy=False)
    escalated_lvl_two = fields.Boolean("Escalated Two", copy=False)
    error_logs = fields.Text("Error Logs", copy=False, readonly=True)
    in_progress_date = fields.Datetime("In Progress date", copy=False, readonly=True)
    manager_comments = fields.Text("Manager Comments", copy=False)
    resolved_date = fields.Datetime("Resolved Date", copy=False, readonly=True)

    @api.depends('escalated_lvl_one', 'assign_engineer_ids', 'escalated_lvl_two')
    def _compute_rsm_nsm_ids(self):
        for rec in self:
            rsm_list = []
            rec.rsm_ids = False
            rec.nsm_ids = False
            for rsm in rec.assign_engineer_ids:
                employee = self.env['hr.employee'].sudo().search([('user_id', '=', rsm._origin.id)], limit=1)
                if employee and employee.parent_id and employee.parent_id.user_id:
                    rsm_list.append(employee.parent_id.user_id.id)
            if rsm_list:
                rec.rsm_ids = rsm_list

            if rec.escalated_lvl_one or rec.escalated_lvl_two:
                nsm_list = []
                for nsm in rec.assign_engineer_ids:
                    employee = self.env['hr.employee'].sudo().search([('user_id', '=', nsm._origin.id)], limit=1)
                    if employee and employee.coach_id and employee.coach_id.user_id:
                        nsm_list.append(employee.coach_id.user_id.id)
                if nsm_list:
                    rec.nsm_ids = nsm_list

    def action_open(self):
        return self.write({'state': 'se_open'})

    def action_inprogress(self):
        return self.write({'state': 'se_inprogress',
                           'in_progress_date': fields.Datetime.now()})

    def action_resolved(self):
        return self.write({'state': 'se_resolved',
                           'resolved_date': datetime.now()})

    def update_manager_comments(self):
        return {
            'name': "Manager Comments",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'reason.reason',
            'target': 'new',
            'context': {'default_reason_type': 'sr_escalation'}
        }

    def action_cancel(self):
        return self.write({'state': 'se_cancelled'})

    def reopen_ticket_popup(self):
        self.ensure_one()
        return {
            'name': _("Re-open Ticket"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'reopen.ticket',
            'context': {'default_ticket_type': 'child', 'default_service_request_id': self.id,
                        'default_child_ticket_id': self.child_ticket_id.id,
                        'default_parent_ticket_id': self.parent_ticket_id.id, },
            'view_id': self.env.ref('stryker_survey.reopen_ticket_view_form').id,
            'target': 'new'
        }

    def view_survey_feedback(self):
        ticket_list = []
        action = self.env['ir.actions.act_window']._for_xml_id('survey.action_survey_user_input')
        if len(ticket_list) == 1:
            action['views'] = [(self.env.ref('survey.survey_user_input_view_form').id, 'form')]
            action['view_mode'] = 'form'
            action['res_id'] = self.id
        else:
            action['domain'] = [('service_request_id', '=', self.id)]
        return action


class ReasonReasonInherit(models.TransientModel):
    _inherit = 'reason.reason'
    _description = 'Reason'

    reason_type = fields.Selection(selection_add=[('sr_escalation', 'SR Escalation')])

    def action_confirm(self):
        if self.env.context.get('active_model') == 'service.request':
            service_request = self.env['service.request'].browse(self.env.context.get('active_id'))
            if service_request:
                service_request.sudo().write({
                    'manager_comments': self.name,
                })
        return super(ReasonReasonInherit, self).action_confirm()


class TasksMasterInherit(models.Model):
    _inherit = "tasks.master"

    is_survey_passed = fields.Boolean("Survey Passed")
    is_sr_escalation_open = fields.Boolean("S.R Escalation Open")
    is_sr_escalation_progress = fields.Boolean("S.R Escalation Progress")
