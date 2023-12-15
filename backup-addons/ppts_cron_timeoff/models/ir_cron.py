from odoo import fields, models, api, _
from datetime import datetime,date
import logging
import time
import calendar
import odoo
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import pytz

_logger = logging.getLogger(__name__)

class IrCronInherit(models.Model):
    _inherit = 'ir.cron'

    exclude_holidays = fields.Boolean("Exclude holidays and Weekends?")

    def _get_user(self):
        return self.env.user

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
            user_tz = cron.user_id.tz or False
            user_pytz = pytz.timezone(user_tz) if user_tz else pytz.utc
            datetime_object = datetime.now().astimezone(user_pytz).replace(tzinfo=None)
            day = fields.Datetime.from_string(datetime_object)
            week_day = calendar.day_name[day.weekday()]
            param = 'ppts_cron_timeoff.%s' % str(week_day)
            working_day = self.env['ir.config_parameter'].sudo().get_param(param)
            if working_day:
                nextcall = cron.nextcall.astimezone(user_pytz).replace(tzinfo=None)
                holidays = self.env['resource.calendar.leaves'].sudo().search([('resource_id', '=', False)]).filtered(lambda l: l.date_from.astimezone(user_pytz).replace(tzinfo=None) < nextcall < l.date_to.astimezone(user_pytz).replace(tzinfo=None))
                _logger.info('-------Holidays Rec-------: %s' % holidays)
                if not holidays:
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
                
