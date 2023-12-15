from odoo import api, fields, models, tools, _

import werkzeug
import re
import logging
_logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
# from odoo.http import request
from odoo.exceptions import ValidationError,UserError
emails_split = re.compile(r"[;,\n\r]+")
from urllib.parse import urlparse



class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    @api.constrains('period', 'unit')
    def _check_vals(self):
        for rec in self:
            if rec.survey_expiry < 1 and not rec.to_expire:
                raise ValidationError(_("For Survey Expiration the period must be greater than 0."))

    @api.model
    def action_survey_schedule(self):
        """This is the method that will be executed when the 'Survey Scheduler' Cron is triggered"""
        # Default template for sending Emails for both child and parent tickets
        mail_template_child = self.env.ref('stryker_survey.child_ticket_survey_generation')
        mail_template_parent = self.env.ref('stryker_survey.parent_ticket_survey_generation')

        # getting User ID through 'request' since its not possible to get from 'sel.
        # current_uid = request.env.context.get('uid') 
        user = self.env['survey.survey']._get_user()

        # Converting datetime into local timezone
        user_tz = user.tz
        user_pytz = pytz.timezone(user_tz) if user_tz else pytz.utc 
        date_now = datetime.now() + timedelta(hours=5, minutes=30)
        child_tickets = self.env['child.ticket'].sudo().search([('ticket_closure', '<=', date_now)])

        for child_ticket in child_tickets.filtered(lambda l: l.company_id.survey_notification == True):
            survey_config = child_ticket.partner_id.task_list_ids.filtered(lambda l: l.condition_id.is_end_task == True and l.trigger_action == 'trigger_survey' and l.period > 0)   
            for rec in survey_config:
                ticket_closure = child_ticket.ticket_closure + timedelta(hours=5, minutes=30)
                # Fetching hours difference between ticket's closure timing and current time.
                diff = date_now - ticket_closure 
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds // 3600
                minutes = seconds // 60
                # Interval for Sending Survey which is set at General settings (Companywise).
                url = str(rec.survey_id.survey_start_url)+'/'+str(child_ticket.id)+'/'+'child'
                whatsapp_url = url.split("start/",1)[1]
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
                if rec.unit == 'hour':
                    if hours >= rec.period and not child_ticket.survey_sent:
                        if rec.channel in ['email', 'email_whatsp']:
                            mail_template_child.with_context({'url': url}).sudo().send_mail(child_ticket.id, force_send=True)
                            rec.survey_id._create_answer(partner=child_ticket.partner_id, ticket_id=child_ticket.id, ticket_type='child',template_id=mail_template_child.id if rec.channel in ['email', 'email_whatsp'] else False)
                        if rec.channel in ['whatsapp', 'email_whatsp']:
                            if rec.whatsapp_template_id and child_ticket.partner_id.mobile:
                                try:
                                    self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(rec.whatsapp_template_id, child_ticket.partner_id.mobile, message, button_message, partner_id=child_ticket.partner_id.id)
                                except Exception as e:
                                    _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)
                        child_ticket.sudo().write({'survey_sent': True
                                            })
                            
                elif rec.unit == 'day':
                    if days >= rec.period and not child_ticket.survey_sent:
                        if rec.channel in ['email', 'email_whatsp']:
                            mail_template_child.with_context({'url': url}).sudo().send_mail(child_ticket.id, force_send=True)
                            rec.survey_id._create_answer(partner=child_ticket.partner_id, ticket_id=child_ticket.id, ticket_type='child',template_id=mail_template_child.id if rec.channel in ['email', 'email_whatsp'] else False)
                        if rec.channel in ['whatsapp', 'email_whatsp']:
                            if rec.whatsapp_template_id and child_ticket.partner_id.mobile:
                                try:
                                    self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(rec.whatsapp_template_id, child_ticket.partner_id.mobile, message, button_message, partner_id=child_ticket.partner_id.id)
                                except Exception as e:
                                    _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)
                        child_ticket.sudo().write({'survey_sent': True
                                            })

                elif rec.unit == 'minute':
                    if days >= rec.period and not child_ticket.survey_sent:
                        if rec.channel in ['email', 'email_whatsp']:
                            mail_template_child.with_context({'url': url}).sudo().send_mail(child_ticket.id, force_send=True)
                            rec.survey_id._create_answer(partner=child_ticket.partner_id, ticket_id=child_ticket.id, ticket_type='child',template_id=mail_template_child.id if rec.channel in ['email', 'email_whatsp'] else False)
                        if rec.channel in ['whatsapp', 'email_whatsp']:
                           if rec.whatsapp_template_id and child_ticket.partner_id.mobile:
                                try:
                                    self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(rec.whatsapp_template_id, child_ticket.partner_id.mobile, message, button_message, partner_id=child_ticket.partner_id.id)
                                except Exception as e:
                                    _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)
                        child_ticket.sudo().write({'survey_sent': True
                                            })

            survey_passed_child = child_ticket.partner_id.task_list_ids.filtered(lambda l: l.condition_id.is_survey_passed == True and l.trigger_action == 'trigger_survey' and l.period > 0 and l.channel in ['email', 'email_whatsp'])   
            child_success_survey = self.env.ref('stryker_survey.child_success_survey_generation')
            
            for rec in survey_passed_child:
                passed_survey = child_ticket.survey_id.user_input_ids.filtered(lambda x: x.child_ticket_id.id == child_ticket.id and x.scoring_success == True)
                if passed_survey:
                    passed_timing = passed_survey[0].create_date
                    

                    diff = date_now - passed_timing  
                    days, seconds = diff.days, diff.seconds
                    hours = days * 24 + seconds // 3600 
                    minutes = seconds // 60
                    # Interval for Sending Survey which is set at General settings (Companywise).
                    url = str(rec.survey_id.survey_start_url)+'/'+str(child_ticket.id)+'/'+'child'
                    whatsapp_url = url.split("start/",1)[1]
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
                    if rec.unit == 'hour':
                        if hours >= rec.period and not child_ticket.success_survey_sent:
                            ctx = False
                            if rec.channel in ['email', 'email_whatsp']:
                                child_success_survey.with_context({'url': url}).sudo().send_mail(child_ticket.id, force_send=True)
                                rec.survey_id._create_answer(partner=child_ticket.partner_id, ticket_id=child_ticket.id, ticket_type='child',template_id=child_success_survey.id if rec.channel in ['email', 'email_whatsp'] else False)
                                ctx = True
                            if rec.channel in ['whatsapp', 'email_whatsp']:
                                if rec.whatsapp_template_id and child_ticket.partner_id.mobile:
                                    try:
                                        self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(rec.whatsapp_template_id, child_ticket.partner_id.mobile, message, button_message, partner_id=child_ticket.partner_id.id)
                                        ctx = True
                                    except Exception as e:
                                        _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)
                                    
                            if ctx:
                                child_ticket.sudo().write({'success_survey_sent': True, 
                                                        })

                    elif rec.unit == 'day':
                        if days >= rec.period and not child_ticket.success_survey_sent:
                            ctx = False
                            if rec.channel in ['email', 'email_whatsp']:
                                child_success_survey.with_context({'url': url}).sudo().send_mail(child_ticket.id, force_send=True)
                                rec.survey_id._create_answer(partner=child_ticket.partner_id, ticket_id=child_ticket.id, ticket_type='child',template_id=child_success_survey.id if rec.channel in ['email', 'email_whatsp'] else False)
                                ctx = True
                            if rec.channel in ['whatsapp', 'email_whatsp']:
                                if rec.whatsapp_template_id and child_ticket.partner_id.mobile:
                                    try:
                                        self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(rec.whatsapp_template_id, child_ticket.partner_id.mobile, message, button_message, partner_id=child_ticket.partner_id.id)
                                        ctx = True
                                    except Exception as e:
                                        _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)
                                    
                            if ctx:
                                child_ticket.sudo().write({'success_survey_sent': True, 
                                                        })

                    elif rec.unit == 'minute':
                        if minutes >= rec.period and not child_ticket.success_survey_sent:
                            ctx = False
                            if rec.channel in ['email', 'email_whatsp']:
                                child_success_survey.with_context({'url': url}).sudo().send_mail(child_ticket.id, force_send=True)
                                rec.survey_id._create_answer(partner=child_ticket.partner_id, ticket_id=child_ticket.id, ticket_type='child',template_id=child_success_survey.id if rec.channel in ['email', 'email_whatsp'] else False)
                                ctx = True
                            if rec.channel in ['whatsapp', 'email_whatsp']:
                                if rec.whatsapp_template_id and child_ticket.partner_id.mobile:
                                    try:
                                        self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(rec.whatsapp_template_id, child_ticket.partner_id.mobile, message, button_message, partner_id=child_ticket.partner_id.id)
                                        ctx = True
                                    except Exception as e:
                                        _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)
                            if ctx:
                                child_ticket.sudo().write({'success_survey_sent': True, 
                                                        })

        # Repeating the same process as above for parent tickets.
        parent_tickets = self.env['parent.ticket'].sudo().search([('ticket_closure', '<=', date_now)])
        # Generate the Email for Parent ticket customers based on above search and below filtered criteria.
        for parent_ticket in parent_tickets.filtered(lambda l: l.company_id.survey_notification == True):     
            #print(parent_ticket, "parent_ticket")       
            survey_config = parent_ticket.partner_id.task_list_ids.filtered(lambda l: l.condition_id.is_end_task == True and l.trigger_action == 'trigger_survey' and l.period > 0 and l.channel in ['email', 'email_whatsp']) 
            for rec in survey_config:
                ticket_closure = parent_ticket.ticket_closure + timedelta(hours=5, minutes=30)
                # Fetching hours difference between ticket's closure timing and current time.
                diff = date_now - ticket_closure 
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds // 3600
                minutes = seconds // 60
                # Interval for Sending Survey which is set at General settings (Companywise).
                url = str(rec.survey_id.survey_start_url)+'/'+str(parent_ticket.id)+'/'+'parent'
                whatsapp_url = url.split("start/",1)[1]
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
                if rec.unit == 'hour':
                    if hours >= rec.period and not parent_ticket.survey_sent:
                        if rec.channel in ['email', 'email_whatsp']:
                            mail_template_parent.with_context({'url': url}).sudo().send_mail(parent_ticket.id, force_send=True)
                        if rec.channel in ['whatsapp', 'email_whatsp']:
                            if rec.whatsapp_template_id and parent_ticket.partner_id.mobile:
                                try:
                                    self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(rec.whatsapp_template_id, parent_ticket.partner_id.mobile, message, button_message, partner_id=parent_ticket.partner_id.id)
                                except Exception as e:
                                    _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)
                        rec.survey_id._create_answer(partner=parent_ticket.partner_id, ticket_id=parent_ticket.id, ticket_type='parent',template_id=mail_template_parent.id if rec.channel in ['email', 'email_whatsp'] else False)
                        parent_ticket.sudo().write({'survey_sent': True
                                            })

                elif rec.unit == 'day':
                    if days >= rec.period and not parent_ticket.survey_sent:
                        if rec.channel in ['email', 'email_whatsp']:
                            mail_template_parent.with_context({'url': url}).sudo().send_mail(parent_ticket.id, force_send=True)
                        if rec.channel in ['whatsapp', 'email_whatsp']:
                            if rec.whatsapp_template_id and parent_ticket.partner_id.mobile:
                                try:
                                    self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(rec.whatsapp_template_id, parent_ticket.partner_id.mobile, message, button_message, partner_id=parent_ticket.partner_id.id)
                                except Exception as e:
                                    _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)
                        rec.survey_id._create_answer(partner=parent_ticket.partner_id, ticket_id=parent_ticket.id, ticket_type='parent',template_id=mail_template_parent.id if rec.channel in ['email', 'email_whatsp'] else False)

                        parent_ticket.sudo().write({'survey_sent': True
                                            })

                elif rec.unit == 'minute':
                    if days >= rec.period and not parent_ticket.survey_sent:
                        if rec.channel in ['email', 'email_whatsp']:
                            mail_template_parent.with_context({'url': url}).sudo().send_mail(parent_ticket.id, force_send=True)
                        if rec.channel in ['whatsapp', 'email_whatsp']:
                            if rec.whatsapp_template_id and parent_ticket.partner_id.mobile:
                                try:
                                    self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(rec.whatsapp_template_id, parent_ticket.partner_id.mobile, message, button_message, partner_id=parent_ticket.partner_id.id)
                                except Exception as e:
                                    _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)
                        rec.survey_id._create_answer(partner=parent_ticket.partner_id, ticket_id=parent_ticket.id, ticket_type='parent',template_id=mail_template_parent.id if rec.channel in ['email', 'email_whatsp'] else False)

                        parent_ticket.sudo().write({'survey_sent': True
                                            })


            survey_passed_parent = parent_ticket.partner_id.task_list_ids.filtered(lambda l: l.condition_id.is_survey_passed == True and l.trigger_action == 'trigger_survey' and l.channel in ['email', 'email_whatsp'])   
            # print(survey_passed_parent, "survey_passed_parent")
            parent_success_survey = self.env.ref('stryker_survey.parent_success_survey_generation')
            passed_survey = parent_ticket.survey_id.user_input_ids.filtered(lambda x: x.parent_ticket_id.id == parent_ticket.id and x.scoring_success == True)
            for rec in survey_passed_parent:
                
                for se in passed_survey:
                    
                    # passed_timing = se.create_date.astimezone(user_pytz).replace(tzinfo=None)
                    passed_timing = se.create_date + timedelta(hours=5, minutes=30)
                    #print(passed_timing, "passed_timing",se)
                    url =  str(rec.survey_id.survey_start_url)+'/'+str(parent_ticket.id)+'/'+'parent'
                    whatsapp_url = url.split("start/",1)[1]
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
                    # Fetching hours difference between ticket's closure timing and current time.
                    diff = date_now - passed_timing 
                    # print(diff, "diff++++++++")
                    days, seconds = diff.days, diff.seconds
                    hours = days * 24 + seconds // 3600
                    minutes = seconds // 60
                    # print(hours, "hours", minutes, "minutes", days, "days" )
                    # print(rec.unit,  rec.period, "wwww",parent_ticket)

                    if rec.unit == 'hour':
                        if hours >= rec.period and not parent_ticket.success_survey_sent:
                            ctx = False
                            if rec.channel in ['email', 'email_whatsp']:
                                parent_success_survey.with_context({'url': url}).sudo().send_mail(parent_ticket.id, force_send=True)
                                ctx = True
                            if rec.channel in ['whatsapp', 'email_whatsp']:
                                if rec.whatsapp_template_id and parent_ticket.partner_id.mobile:
                                    try:
                                        self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(rec.whatsapp_template_id, parent_ticket.partner_id.mobile, message, button_message, partner_id=parent_ticket.partner_id.id)
                                        ctx = True
                                    except Exception as e:
                                        _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)
                                    
                            if ctx:
                                rec.survey_id._create_answer(partner=parent_ticket.partner_id, ticket_id=parent_ticket.id, ticket_type='parent',template_id=parent_success_survey.id if rec.channel in ['email', 'email_whatsp'] else False)
                                parent_ticket.sudo().write({'success_survey_sent': True 
                                                    })


                    elif rec.unit == 'day':
                        if days >= rec.period and not parent_ticket.success_survey_sent:
                            ctx = False
                            if rec.channel in ['email', 'email_whatsp']:
                                parent_success_survey.with_context({'url': url}).sudo().send_mail(parent_ticket.id, force_send=True)
                                ctx = True
                            if rec.channel in ['whatsapp', 'email_whatsp']:
                                if rec.whatsapp_template_id and parent_ticket.partner_id.mobile:
                                    try:
                                        self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(rec.whatsapp_template_id, parent_ticket.partner_id.mobile, message, button_message, partner_id=parent_ticket.partner_id.id)
                                        ctx = True
                                    except Exception as e:
                                        _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)
                            if ctx:
                                rec.survey_id._create_answer(partner=parent_ticket.partner_id, ticket_id=parent_ticket.id, ticket_type='parent',template_id=parent_success_survey.id if rec.channel in ['email', 'email_whatsp'] else False)
                                parent_ticket.sudo().write({'success_survey_sent': True 
                                                    })

                    elif rec.unit == 'minute':
                        if minutes >= rec.period and not parent_ticket.success_survey_sent:
                            ctx = False
                            if rec.channel in ['email', 'email_whatsp']:
                                parent_success_survey.with_context({'url': url}).sudo().send_mail(parent_ticket.id, force_send=True)
                                ctx = True
                            if rec.channel in ['whatsapp', 'email_whatsp']:
                                if rec.whatsapp_template_id and parent_ticket.partner_id.mobile:
                                    try:
                                        self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(rec.whatsapp_template_id, parent_ticket.partner_id.mobile, message, button_message, partner_id=parent_ticket.partner_id.id)
                                        ctx = True
                                    except Exception as e:
                                        _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)
                            if ctx:
                                rec.survey_id._create_answer(partner=parent_ticket.partner_id, ticket_id=parent_ticket.id, ticket_type='parent',template_id=parent_success_survey.id if rec.channel in ['email', 'email_whatsp'] else False)
                                parent_ticket.sudo().write({'success_survey_sent': True 
                                                    })

    @api.model
    def _survey_followup_remainder(self):
        surveys = self.env['survey.survey'].sudo().search([('enable_follow', '=', True)])
        # print(surveys, "surveys")
        # user = self.env['survey.survey']._get_user()
        # Converting datetime into local timezone
        # user_tz = user.tz
        # user_pytz = pytz.timezone(user_tz) if user_tz else pytz.utc
        date_now = datetime.now() + timedelta(hours=5, minutes=30)
        for survey in surveys:
            for feedback in survey.user_input_ids.filtered(lambda l: l.state == 'new'):
                ticket_id = False
                if feedback.child_ticket_id:
                    ticket_id = feedback.child_ticket_id
                    url =  str(survey.survey_start_url)+'/'+str(feedback.child_ticket_id.id)+'/'+'child'
                    
                    # mail_template = self.env.ref('stryker_survey.child_ticket_survey_generation')
                if feedback.parent_ticket_id:
                    ticket_id = feedback.parent_ticket_id
                    url =  str(survey.survey_start_url)+'/'+str(feedback.parent_ticket_id.id)+'/'+'parent'
                    # mail_template = self.env.ref('stryker_survey.parent_ticket_survey_generation')
                if url:
                    whatsapp_url = url.split("start/",1)[1]
                    message = [
                        {
                            "type": "text",
                            "text": feedback.customer_id.name
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
                if survey.followup_type == 'once' and feedback.reach_limit == 0 or survey.followup_type == 'repeat' and feedback.reach_limit == 0:
                    survey_sent_date = feedback.create_date + timedelta(hours=5, minutes=30)
                    diff = date_now - survey_sent_date
                    days, seconds = diff.days, diff.seconds
                    hours = days * 24 + seconds // 3600
                    weeks = (days//7)
                    r = relativedelta(feedback.create_date , date_now)
                    months = (r.years * 12) + r.months
                    ctx = False
                    # print(days, "dayssssss", weeks, "weekssssss", months, "monthsssss")
                    if ticket_id and url:
                        if survey.followup == 'days' and days >= survey.followup_after:
                            if survey.followup_via in ['email', 'email_whatspp']:
                                survey.email_tmpl_id.with_context({'url': url}).sudo().send_mail(ticket_id.id, force_send=True)
                                ctx = True
                            if survey.followup_via in ['whatsapp', 'email_whatsp']:
                                if survey.whatsapp_template_id and feedback.customer_id and feedback.customer_id.mobile :
                                    ctx = True
                                    try:
                                        self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(survey.whatsapp_template_id, feedback.customer_id.mobile, message, button_message, partner_id=feedback.customer_id.id)
                                        ctx = True
                                    except Exception as e:
                                        _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)

                        if survey.followup == 'week' and weeks >= survey.followup_after:
                            if survey.followup_via in ['email', 'email_whatspp']:
                                survey.email_tmpl_id.with_context({'url': url}).sudo().send_mail(ticket_id.id, force_send=True)
                                ctx = True
                            if survey.followup_via in ['whatsapp', 'email_whatsp']:
                                if survey.whatsapp_template_id and feedback.customer_id and feedback.customer_id.mobile :
                                    try:
                                        self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(survey.whatsapp_template_id, feedback.customer_id.mobile, message, button_message, partner_id=feedback.customer_id.id)
                                        ctx = True
                                    except Exception as e:
                                        _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)

                        if survey.followup == 'month' and months >= survey.followup_after:
                            if survey.followup_via in ['email', 'email_whatspp']:
                                survey.email_tmpl_id.with_context({'url': url}).sudo().send_mail(ticket_id.id, force_send=True)
                                ctx = True
                            if survey.followup_via in ['whatsapp', 'email_whatsp']:
                                if survey.whatsapp_template_id and feedback.customer_id and feedback.customer_id.mobile :
                                    try:
                                        self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(survey.whatsapp_template_id, feedback.customer_id.mobile, message, button_message, partner_id=feedback.customer_id.id)
                                        ctx = True
                                    except Exception as e:
                                        _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)

                        if ctx:
                            followup_history = self.env['followup.history'].sudo().create({
                                'name': ticket_id.name,
                                'customer_id': ticket_id.partner_id.id,
                                'survey_id': survey.id,
                                'user_input_id': feedback.id
                            })
                            feedback.reach_limit += 1

                if survey.followup_type == 'repeat' and feedback.reach_limit > 0:
                    followup_history = self.env['followup.history'].sudo().search([
                            ('user_input_id', '=', feedback.id),
                            ('survey_id', '=', survey.id)], order='followup_date desc')
                    if followup_history:
                        if feedback.reach_limit < survey.followup_limit:
                            # current_uid = request.env.context.get('uid') 
                            followup_date = followup_history[0].followup_date + timedelta(hours=5, minutes=30)
                            diff = date_now - followup_date
                            days, seconds = diff.days, diff.seconds
                            hours = days * 24 + seconds // 3600
                            weeks = (days//7)
                            r = relativedelta(followup_date , date_now)
                            months = (r.years * 12) + r.months
                            # print(days, "dayssssss", weeks, "weekssssss", months, "monthsssss", survey.followup_after)
                            if ticket_id and url:
                                ctx = False
                                if survey.followup == 'days' and days >= survey.followup_after:
                                    if survey.followup_via in ['email', 'email_whatsp']:
                                        survey.email_tmpl_id.with_context({'url': url}).sudo().send_mail(ticket_id.id, force_send=True)
                                        ctx = True
                                    if survey.followup_via in ['whatsapp', 'email_whatsp']:
                                        if survey.whatsapp_template_id and feedback.customer_id and feedback.customer_id.mobile :
                                            try:
                                                self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(survey.whatsapp_template_id, feedback.customer_id.mobile, message, button_message, partner_id=feedback.customer_id.id)
                                                ctx = True
                                            except Exception as e:
                                                _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)
                                
                                if survey.followup == 'week' and weeks >= survey.followup_after:
                                    if survey.followup_via in ['email', 'email_whatsp']:
                                        survey.email_tmpl_id.with_context({'url': url}).sudo().send_mail(ticket_id.id, force_send=True)
                                        ctx = True
                                    if survey.followup_via in ['whatsapp', 'email_whatsp']:
                                        if survey.whatsapp_template_id and feedback.customer_id and feedback.customer_id.mobile :
                                            try:
                                                self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(survey.whatsapp_template_id, feedback.customer_id.mobile, message, button_message, partner_id=feedback.customer_id.id)
                                                ctx = True
                                            except Exception as e:
                                                _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)
                                
                                if survey.followup == 'month' and months >= survey.followup_after:
                                    if survey.followup_via in ['email', 'email_whatsp']:
                                        survey.email_tmpl_id.with_context({'url': url}).sudo().send_mail(ticket_id.id, force_send=True)
                                        ctx = True
                                    if survey.followup_via in ['whatsapp', 'email_whatsp']:
                                        if survey.whatsapp_template_id and feedback.customer_id and feedback.customer_id.mobile :
                                            try:
                                                self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(survey.whatsapp_template_id, feedback.customer_id.mobile, message, button_message, partner_id=feedback.customer_id.id)
                                                ctx = True
                                            except Exception as e:
                                                _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)
                                
                                if ctx:
                                    followup_history = self.env['followup.history'].sudo().create({
                                        'name': ticket_id.name,
                                        'customer_id': ticket_id.partner_id.id,
                                        'survey_id': survey.id,
                                        'user_input_id': feedback.id
                                        # 'followup_date': date_now
                                    })
                                    feedback.reach_limit += 1
                                    print(followup_history, "fllowwww")
                    
        return True

    def _get_user(self):
        return self.env.user 
    
    survey_start_url = fields.Char('Survey URL', compute='_compute_survey_start_url')
    survey_expiry = fields.Integer('Survey Expiry In')
    unit = fields.Selection([('hour', 'Hours'), ('day', 'Days'),('month', 'Months')], string='Unit')
    to_expire = fields.Boolean("Survey expiry after submission")
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.company)
    survey_properties = fields.Properties('Properties', definition='user_id.survey_properties_definition', copy=True)
    
    # survey follow ups
    enable_follow = fields.Boolean("Enable Followups", default=False)
    followup_type = fields.Selection([('once', 'Once'), ('repeat', 'Repeatedly')], string="Followup Type", required=True, default='once')
    followup_after = fields.Integer("Follow up after")
    followup = fields.Selection([('days', 'Days'), ('week', 'Week'),('month', 'Month')], string='Unit', required=True, default='days')
    followup_limit = fields.Integer("Follow Up Limit")
    followup_count = fields.Integer("Followup Count", compute="_compute_followup_count")
    followup_via = fields.Selection([('email', 'E-mail'), ('whatsapp', 'WhatsApp'),('email_whatsp', 'Email & Whatsapp')], string="Followup Via")
    email_tmpl_id = fields.Many2one('mail.template', "E-Mail Template")
    whatsapp_template_id = fields.Many2one('watsapp.sms.template', "Whatsapp Template")
    
    def _compute_followup_count(self):
        followup_count = self.env['followup.history'].search_count([('survey_id', '=', self.id)]) or 0
        for rec in self:
            rec.followup_count = followup_count

    def action_survey_followup(self):
        action = self.env['ir.actions.actions']._for_xml_id('stryker_survey.followup_history_action')
        action['domain'] = [('survey_id', '=', self.id)]
        return action

    @api.depends('access_token')
    def _compute_survey_start_url(self):
        for survey in self:
            url = werkzeug.urls.url_join(survey.get_base_url(), survey.get_start_url()) if survey else False
            # print(url, "url-------")
            parser_url = urlparse(url)
            out_url = parser_url._replace(netloc=parser_url.netloc.replace(':'+str(parser_url.port), "")).geturl()
            survey.survey_start_url = out_url or ''
            
    def fill_survey_ct(self):
        self.ensure_one()
        return {
                'name':  _("Fill Survey"),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'fill.survey.ticket',
                'context': {'default_survey_id': self.id, 'default_url': self.survey_start_url},
                'view_id': self.env.ref('stryker_survey.fill_survey_view_form').id,
                'target': 'new'
            }
    
    def _create_answer(self, user=False, partner=False, email=False, test_entry=False, check_attempts=True, ticket_id=None, ticket_type=None, template_id=None, **additional_vals):
        """ Main entry point to get a token back or create a new one. This method
        does check for current user access in order to explicitely validate
        security.

          :param user: target user asking for a token; it might be void or a
                       public user in which case an email is welcomed;
          :param email: email of the person asking the token is no user exists;
        """
        self.check_access_rights('read')
        self.check_access_rule('read')

        user_inputs = self.env['survey.user_input']
        for survey in self:
            if partner and not user and partner.user_ids:
                user = partner.user_ids[0]

            invite_token = additional_vals.pop('invite_token', False)
            survey._check_answer_creation(user, partner, email, test_entry=test_entry, check_attempts=check_attempts, invite_token=invite_token)
            answer_vals = {
                'survey_id': survey.id,
                'test_entry': test_entry,
                'is_session_answer': survey.session_state in ['ready', 'in_progress'],
                'child_ticket_id': ticket_id if ticket_type == 'child' else False,
                'parent_ticket_id': ticket_id if ticket_type == 'parent' else False,
                'template_id': template_id if template_id else False
            }
            if survey.session_state == 'in_progress':
                # if the session is already in progress, the answer skips the 'new' state
                answer_vals.update({
                    'state': 'in_progress',
                    'start_datetime': fields.Datetime.now(),
                })
            if user and not user._is_public():
                answer_vals['partner_id'] = user.partner_id.id
                answer_vals['email'] = user.email
                answer_vals['nickname'] = user.name
            elif partner:
                answer_vals['partner_id'] = partner.id
                answer_vals['email'] = partner.email
                answer_vals['nickname'] = partner.name
            else:
                answer_vals['email'] = email
                answer_vals['nickname'] = email

            if invite_token:
                answer_vals['invite_token'] = invite_token
            elif survey.is_attempts_limited and survey.access_mode != 'public':
                # attempts limited: create a new invite_token
                # exception made for 'public' access_mode since the attempts pool is global because answers are
                # created every time the user lands on '/start'
                answer_vals['invite_token'] = self.env['survey.user_input']._generate_invite_token()

            answer_vals.update(additional_vals)
            user_inputs += user_inputs.create(answer_vals)

        for question in self.mapped('question_ids').filtered(
                lambda q: q.question_type == 'char_box' and (q.save_as_email or q.save_as_nickname)):
            for user_input in user_inputs:
                if question.save_as_email and user_input.email:
                    user_input.save_lines(question, user_input.email)
                if question.save_as_nickname and user_input.nickname:
                    user_input.save_lines(question, user_input.nickname)

        return user_inputs


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"
    
    @api.model
    def create(self, vals):
        res = super(SurveyUserInput, self).create(vals)
        if not res.survey_id.to_expire and res.survey_id.survey_expiry > 0:
            if res.survey_id.unit == 'hour':
                res.deadline = res.create_date + timedelta(hours=res.survey_id.survey_expiry)
            if res.survey_id.unit == 'day':
                res.deadline = res.create_date + relativedelta(days=res.survey_id.survey_expiry)
            if res.survey_id.unit == 'month':
                res.deadline = res.create_date + relativedelta(months=res.survey_id.survey_expiry)
        return res
    
    @api.model
    def _action_create_sr(self):
        failed_survey = self.env['survey.user_input'].sudo().search([('imported', '=', True), ('result', '=', 'failed'), ('escalated_rsm', '=', False)])              
        for rec in failed_survey:
            rec.sudo().action_create_sr()
        passed_survey = self.env['survey.user_input'].sudo().search([('imported', '=', True), ('result', '=', 'passed')])
        for obj in passed_survey:
            parent_ticket = obj.parent_ticket_id 
            if parent_ticket:
                survey_passed_parent = parent_ticket.partner_id.task_list_ids.filtered(lambda l: l.condition_id.is_survey_passed == True and l.trigger_action == 'trigger_survey')   
                parent_success_survey = self.env.ref('stryker_survey.parent_success_survey_generation')
                for rec in survey_passed_parent:
                    url =  str(rec.survey_id.survey_start_url)+'/'+str(parent_ticket.id)+'/'+'parent'
                    whatsapp_url = url.split("start/",1)[1]
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
                    if not parent_ticket.success_survey_sent:
                        ctx = False
                        if rec.channel in ['email', 'email_whatsp']:
                            parent_success_survey.with_context({'url': url}).sudo().send_mail(parent_ticket.id, force_send=True)
                            ctx = True
                        if rec.channel in ['whatsapp', 'email_whatsp']:
                            if rec.whatsapp_template_id and parent_ticket.partner_id.mobile:
                                try:
                                    self.env['watsapp.sms.gateway'].sudo().action_whatsapp_notification(rec.whatsapp_template_id, parent_ticket.partner_id.mobile, message, button_message, partner_id=parent_ticket.partner_id.id)
                                    ctx = True
                                except Exception as e:
                                    _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)

                        if ctx:
                            rec.survey_id._create_answer(partner=parent_ticket.partner_id, ticket_id=parent_ticket.id, ticket_type='parent',template_id=parent_success_survey.id if rec.channel in ['email', 'email_whatsp'] else False)
                            parent_ticket.sudo().write({'success_survey_sent': True 
                                                })

    child_ticket_id = fields.Many2one('child.ticket', string='Child Ticket')
    parent_ticket_id = fields.Many2one('parent.ticket', string='Parent Ticket')
    escalated_rsm = fields.Boolean(string='Escalated RSM')
    url = fields.Char("Url", compute="_compute_ticket_details", store=True)
    customer_id = fields.Many2one('res.partner', string="Customer", compute="_compute_ticket_details", store=True)
    # customer_account = fields.Char(string="Customer Account", related='customer_id.customer_account')
    customer_account_id = fields.Many2one('res.partner', compute="_compute_ticket_details", store=True)
    service_category_id = fields.Many2one('service.category', string="Service Category", compute="_compute_ticket_details", store=True)
    service_type_id = fields.Many2one('service.type', string="Service Type", compute="_compute_ticket_details", store=True)
    service_request_id = fields.Many2one('service.request', string="Service Request")
    attempt_no = fields.Integer('Attempt No')
    filled_by = fields.Many2one('res.users', "Filled By", default=lambda self: self.env.user)
    notes = fields.Text("Notes")
    state = fields.Selection([('new', 'Not Submitted'),('in_progress','In Progress'),('done','Completed'),('expired','Expired'),('no_answer','Not Submitted & Not reachable')], string="Status")
    result = fields.Selection([('passed', 'Passed'), ('failed', 'Failed')], string="Result", compute="_compute_result", store=True)
    sr_status = fields.Selection(related='service_request_id.state')
    company_id = fields.Many2one('res.company', "Company", related='survey_id.company_id', store=True)
    expired = fields.Boolean("Expired", compute="_compute_exp")
    reach_limit = fields.Integer("ResendLimit")
    template_id = fields.Many2one('mail.template', "Mail Template")
    # deadline = fields.Datetime('Deadline', help="Datetime until customer can open the survey and submit answers", compute="_compute_deadline", store=True)
    imported = fields.Boolean("Is Imported")
    change_state = fields.Boolean("Boolean", compute="_compute_change_state", store=True)

    @api.depends('child_ticket_id', 'parent_ticket_id')
    def _compute_ticket_details(self):
        for rec in self:
            if rec.child_ticket_id:
                rec.customer_id = rec.child_ticket_id.partner_id.id if rec.child_ticket_id.partner_id else False
                rec.customer_account_id = rec.child_ticket_id.customer_account_id.id if rec.child_ticket_id.customer_account_id else False
                rec.service_type_id = rec.child_ticket_id.service_type_id.id if rec.child_ticket_id.service_type_id else False
                rec.service_category_id = rec.child_ticket_id.service_category_id.id if rec.child_ticket_id.service_category_id else False
                rec.url = str(rec.survey_id.survey_start_url)+'/'+str(rec.child_ticket_id.id)+'/'+'child'
            
            elif rec.parent_ticket_id:
                rec.customer_id = rec.parent_ticket_id.partner_id.id if rec.parent_ticket_id.partner_id else False
                rec.customer_account_id = rec.parent_ticket_id.customer_account_id.id if rec.parent_ticket_id.customer_account_id else False
                rec.service_type_id = rec.parent_ticket_id.service_type_id.id if rec.parent_ticket_id.service_type_id else False
                rec.service_category_id = rec.parent_ticket_id.service_category_id.id if rec.parent_ticket_id.service_category_id else False
                rec.url = str(rec.survey_id.survey_start_url)+'/'+str(rec.parent_ticket_id.id)+'/'+'parent'
            
            else:
                rec.customer_id = False
                rec.customer_account_id = False
                rec.service_type_id = False
                rec.service_category_id = False
                rec.url = str(rec.survey_id.survey_start_url)

    @api.depends('imported')
    def _compute_change_state(self):
        for rec in self:
            if rec.imported:
                rec.change_state = True
                rec.state = 'done'
            else:
                rec.change_state = False
                rec.state = rec.state
                
    def _compute_exp(self):
        for rec in self:
            rec.expired = False
            if rec.deadline:
                if rec.deadline < datetime.now() and rec.state != 'done':
                    rec.state = 'expired'
                    rec.expired = True

    @api.depends('scoring_success')
    def _compute_result(self):
        for rec in self:
            if rec.scoring_success:
                rec.result = 'passed'
            else:
                rec.result = 'failed'

    def view_child_ticket(self):
        return {
            'name': _("Child Ticket"),
            'res_model': 'child.ticket',
            'type': 'ir.actions.act_window',
            'res_id': self.child_ticket_id.id,
            'view_mode': 'form',
        }

    def view_parent_ticket(self):
        return {
            'name': _("Parent Ticket"),
            'res_model': 'parent.ticket',
            'type': 'ir.actions.act_window',
            'res_id': self.parent_ticket_id.id,
            'view_mode': 'form',
        }

    def view_service_request(self):
        service_req = self.env['service.request'].search([('id', '=', self.service_request_id.id)])
        action = self.env['ir.actions.act_window']._for_xml_id('stryker_survey.action_service_request_sr_survey')
        print(service_req, "service_req---")
        if len(service_req) == 1:
            action['views'] = [(self.env.ref('stryker_survey.service_request_sr_survey_form_view').id, 'form')]
            action['view_mode'] = 'form'
            action['res_id'] = self.service_request_id.id
        else:
            action['domain'] = [('id', '=', self.service_request_id.id)]
        return action
    
    
    def action_create_sr(self):
        ticket_id = self.parent_ticket_id if self.parent_ticket_id else self.child_ticket_id
        #print(ticket_id, "ticket_id---")
        if ticket_id:
            request_type_id = self.env['request.type'].search([('ticket_type', '=', 'sr_survey_escalation')], limit=1)
            if request_type_id:
                service_req = self.env['service.request'].create({
                    'customer_name': ticket_id.partner_id.name,
                    'service_category_id': ticket_id.service_category_id.id if ticket_id.service_category_id else False,
                    'service_type_id': ticket_id.service_type_id.id if ticket_id.service_type_id else False,
                    'state': 'new',
                    'request_type_id': request_type_id.id, 
                    'requested_by_contact_number': ticket_id.requested_by_contact_number or ticket_id.partner_id.mobile,
                    'ticket_ref': ticket_id.name if ticket_id else False,
                    'parent_ticket_id': self.parent_ticket_id.id if self.parent_ticket_id else False,
                    'child_ticket_id': self.child_ticket_id.id if self.child_ticket_id else False,
                    'assign_engineer_ids': ticket_id.assign_engineer_ids.ids,
                    'is_escalation': True,
                    'partner_id': ticket_id.partner_id.id if ticket_id.partner_id else False,
                    'dealer_distributor_id': ticket_id.dealer_distributor_id.id if ticket_id.dealer_distributor_id else False,
                    'customer_asset_ids': [(0, 0, {'stock_lot_id': ticket_id.stock_lot_id.id, 'product_id': ticket_id.product_id.id if ticket_id.product_id else False})] if ticket_id.stock_lot_id else False,
                    'call_source_id': ticket_id.call_source_id.id if ticket_id.call_source_id else False,
                    'remarks': ticket_id.remarks if ticket_id.remarks else '',
                    'survey_id': ticket_id.survey_id.id if ticket_id.survey_id else False,
                    'requested_by_name': ticket_id.requested_by_name if ticket_id.requested_by_name else '',
                    'call_received_id': ticket_id.call_received_id.id if ticket_id.call_received_id else False
                })
                if service_req:
                    template_id = self.env.ref('stryker_survey.rsm_survey_escalation')
                    service_req._onchange_partner()
                    self.service_request_id = service_req.id
                    self.escalated_rsm = True
                    for rec in service_req.assign_engineer_ids:
                        template_id.with_context({'email_to': rec.partner_id.email, 'partner_name': rec.partner_id.name}).sudo().send_mail(service_req.id, force_send=True)
            else:
                raise ValidationError(_("Please configure 'SR-Survey Escalation' in Request type"))

        return True

    def view_assets(self):
        ticket_id = self.parent_ticket_id if self.parent_ticket_id else self.child_ticket_id
        asset = self.env['stock.lot'].search([('id', '=', ticket_id.stock_lot_id.id)], limit=1)
        if asset:
            return {
                'name': _("Assets"),
                'res_model': 'stock.lot',
                'type': 'ir.actions.act_window',
                'res_id': asset.id,
                'view_mode': 'form'
            }

    def view_products(self):
        ticket_id = self.parent_ticket_id if self.parent_ticket_id else self.child_ticket_id
        product = self.env['product.template'].search([('id', '=', ticket_id.product_id.product_tmpl_id.id)], limit=1)
        if product:
            return {
                'name': _("Products"),
                'res_model': 'product.template',
                'type': 'ir.actions.act_window',
                'res_id': product.id,
                'view_mode': 'form'
            }
        
# class SurveyInputLine(models.Model):
#     _inherit = 'survey.user_input.line'

    # customer_account_id = fields.Many2one('res.partner', related='user_input_id.customer_account_id', store=True)
    # service_category_id = fields.Many2one('service.category', string="Service Category", related='user_input_id.service_category_id', store=True)
    # service_type_id = fields.Many2one('service.type', string="Service Type", related='user_input_id.service_category_id', store=True)

class FollowupHistory(models.Model):
    _name = 'followup.history'

    name = fields.Char("Name")
    customer_id = fields.Many2one('res.partner', string="Customer")
    survey_id = fields.Many2one('survey.survey', "Survey")
    followup_date = fields.Datetime("Followup Date", default=datetime.now())
    user_input_id = fields.Many2one('survey.user_input', "Survey feedback")

class SurveyInvite(models.TransientModel):
    _inherit = 'survey.invite'

    channel = fields.Selection([('email', 'E-mail'), ('whatsapp', 'WhatsApp'),('email_whatsp', 'Email & Whatsapp')], string="Send Via")
    whatsapp_template_id = fields.Many2one('watsapp.sms.template', "Whatsapp Template")

    def action_invite(self):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed """
        self.ensure_one()
        if self.channel in ['email', 'email_whatsp']:
            Partner = self.env['res.partner']
            # compute partners and emails, try to find partners for given emails
            valid_partners = self.partner_ids
            langs = set(valid_partners.mapped('lang')) - {False}
            if len(langs) == 1:
                self = self.with_context(lang=langs.pop())
            valid_emails = []
            for email in emails_split.split(self.emails or ''):
                partner = False
                email_normalized = tools.email_normalize(email)
                if email_normalized:
                    limit = None if self.survey_users_login_required else 1
                    partner = Partner.search([('email_normalized', '=', email_normalized)], limit=limit)
                if partner:
                    valid_partners |= partner
                else:
                    email_formatted = tools.email_split_and_format(email)
                    if email_formatted:
                        valid_emails.extend(email_formatted)

            if not valid_partners and not valid_emails:
                raise UserError(_("Please enter at least one valid recipient."))

            answers = self._prepare_answers(valid_partners, valid_emails)
            for answer in answers:
                self._send_mail(answer)
            
        if self.channel in ['whatsapp', 'email_whatsp']:
            url = str(self.survey_id.survey_start_url)
            whatsapp_url = url.split("start/",1)[1]

            for obj in self.partner_ids:
                message = [
                    {
                        "type": "text",
                        "text": obj.name
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
                if not obj.mobile:
                    raise ValidationError(_("No mobile number found for %s." % obj.name))
                try:
                    self.env['watsapp.sms.gateway'].action_whatsapp_notification(self.whatsapp_template_id, obj.mobile, message, button_message, partner_id=obj.id)
                except Exception as e:
                    _logger.info("Exception occured while sending Whatsapp mesaage: %s", e)
        if self.env.context['blast_history']:
            for rec in self.env.context['blast_history']:
                self.env['survey.blast.history'].create(rec)

        return {'type': 'ir.actions.act_window_close'}

    #     name = fields.Char("Ticket Ref")
    # partner_id = fields.Many2one('res.partner', string="Customer")
    # customer_account_id = fields.Many2one('res.partner', string="Customer Account")
    # mail_sent_date = fields.Datetime("Mail Sent Date", default=datetime.now())
    # survey_id = fields.Many2one('survey.survey', string="Survey")

