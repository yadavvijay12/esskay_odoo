# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    survey_notification = fields.Boolean(string="Survey Notification", related="company_id.survey_notification", readonly=False)
    # Sunday = fields.Boolean('Sunday', default=False, config_parameter="stryker_survey.Sunday")
    # Monday = fields.Boolean('Monday', default=False, config_parameter="stryker_survey.Monday")
    # Tuesday = fields.Boolean('Tuesday', default=False, config_parameter="stryker_survey.Tuesday")
    # Wednesday = fields.Boolean('Wednesday', default=False, config_parameter="stryker_survey.Wednesday")
    # Thursday = fields.Boolean('Thursday', default=False, config_parameter="stryker_survey.Thursday")
    # Friday = fields.Boolean('Friday', default=False, config_parameter="stryker_survey.Friday")
    # Saturday = fields.Boolean('Saturday', default=False, config_parameter="stryker_survey.Saturday")
    