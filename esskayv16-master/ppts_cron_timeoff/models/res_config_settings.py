# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    Sunday = fields.Boolean('Sunday', default=False, config_parameter="ppts_cron_timeoff.Sunday")
    Monday = fields.Boolean('Monday', default=False, config_parameter="ppts_cron_timeoff.Monday")
    Tuesday = fields.Boolean('Tuesday', default=False, config_parameter="ppts_cron_timeoff.Tuesday")
    Wednesday = fields.Boolean('Wednesday', default=False, config_parameter="ppts_cron_timeoff.Wednesday")
    Thursday = fields.Boolean('Thursday', default=False, config_parameter="ppts_cron_timeoff.Thursday")
    Friday = fields.Boolean('Friday', default=False, config_parameter="ppts_cron_timeoff.Friday")
    Saturday = fields.Boolean('Saturday', default=False, config_parameter="ppts_cron_timeoff.Saturday")
    