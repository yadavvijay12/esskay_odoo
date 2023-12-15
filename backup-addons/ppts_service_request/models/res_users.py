import os
import hashlib
import logging

from odoo import models, fields, api
from datetime import datetime, timedelta


class ResUsers(models.Model):
    _inherit = 'res.users'

    team_ids = fields.Many2many("crm.team", string="Assigned Teams", compute="_get_sale_team")
    customer_account_ids = fields.Many2many("res.partner", string="Customer Accounts")

    def _get_sale_team(self):
        sale_team = self.env['crm.team'].sudo().search(
            ['|', ('user_id', '=', self.id), ('member_ids', 'in', [self.id])])
        if sale_team:
            self.team_ids = sale_team.ids
        else:
            self.team_ids = False
