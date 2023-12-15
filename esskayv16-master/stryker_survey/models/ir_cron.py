from odoo import fields, models, api, _
from datetime import datetime
import logging
import time
import calendar
import odoo
from datetime import datetime, timedelta
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class IrCronInherit(models.Model):
    _inherit = 'ir.cron'

    exclude_holidays = fields.Boolean("Exclude holidays and Weekends?")

    @api.model
    def _callback(self, cron_name, server_action_id, job_id):
        """ Run the method associated to a given job. It takes care of logging
        and exception handling. Note that the user running the server action
        is the user calling this method. """
        cron = self.env['ir.cron'].sudo().browse(job_id)
        if not cron.exclude_holidays:
            try:
                if self.pool != self.pool.check_signaling():
                    # the registry has changed, reload self in the new registry
                    self.env.reset()
                    self = self.env()[self._name]

                log_depth = (None if _logger.isEnabledFor(logging.DEBUG) else 1)
                odoo.netsvc.log(_logger, logging.DEBUG, 'cron.object.execute', (self._cr.dbname, self._uid, '*', cron_name, server_action_id), depth=log_depth)
                start_time = False
                _logger.info('Starting job `%s`.', cron_name)
                if _logger.isEnabledFor(logging.DEBUG):
                    start_time = time.time()
                self.env['ir.actions.server'].browse(server_action_id).run()
                _logger.info('Job `%s` done.', cron_name)
                if start_time and _logger.isEnabledFor(logging.DEBUG):
                    end_time = time.time()
                    _logger.debug('%.3fs (cron %s, server action %d with uid %d)', end_time - start_time, cron_name, server_action_id, self.env.uid)
                self.pool.signal_changes()
            except Exception as e:
                self.pool.reset_changes()
                _logger.exception("Call from cron %s for server action #%s failed in Job #%s",
                                cron_name, server_action_id, job_id)
                self._handle_callback_exception(cron_name, server_action_id, job_id, e)

        else:
            resource_calendar = self.env['resource.calendar.leaves'].sudo().search([])
            nextcall = cron.nextcall + timedelta(hours=5, minutes=30)
            _logger.info('-------Nextcall----- `%s`.', nextcall)
            
            datetime_object = datetime.now() + timedelta(hours=5, minutes=30)
            day = fields.Datetime.from_string(datetime_object)
            week_day = calendar.day_name[day.weekday()]
            param = 'stryker_survey.%s' % str(week_day)
            working_day = self.env['ir.config_parameter'].sudo().get_param(param)
            
            if working_day:
                for rec in resource_calendar:
                    _logger.info('-------Holiday record----- `%s`.', rec)
                    date_from = rec.date_from + timedelta(hours=5, minutes=30)
                    date_to = rec.date_to + timedelta(hours=5, minutes=30)

                    if not date_from < nextcall < date_to:
                        _logger.info('-------Cron Executed-------')
                        try:
                            if self.pool != self.pool.check_signaling():
                                # the registry has changed, reload self in the new registry
                                self.env.reset()
                                self = self.env()[self._name]

                            log_depth = (None if _logger.isEnabledFor(logging.DEBUG) else 1)
                            odoo.netsvc.log(_logger, logging.DEBUG, 'cron.object.execute', (self._cr.dbname, self._uid, '*', cron_name, server_action_id), depth=log_depth)
                            start_time = False
                            _logger.info('Starting job `%s`.', cron_name)
                            if _logger.isEnabledFor(logging.DEBUG):
                                start_time = time.time()
                            self.env['ir.actions.server'].browse(server_action_id).run()
                            _logger.info('Job `%s` done.', cron_name)
                            if start_time and _logger.isEnabledFor(logging.DEBUG):
                                end_time = time.time()
                                _logger.debug('%.3fs (cron %s, server action %d with uid %d)', end_time - start_time, cron_name, server_action_id, self.env.uid)
                            self.pool.signal_changes()
                        except Exception as e:
                            self.pool.reset_changes()
                            _logger.exception("Call from cron %s for server action #%s failed in Job #%s",
                                            cron_name, server_action_id, job_id)
                            self._handle_callback_exception(cron_name, server_action_id, job_id, e)

