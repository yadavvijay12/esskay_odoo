import os
import hashlib
import logging

from odoo import models, fields, api
from datetime import datetime, timedelta


class ResUsers(models.Model):
    _inherit = 'res.users'

    team_ids = fields.Many2many("crm.team", string="Assigned Teams", compute="_get_sale_team")
    customer_account_ids = fields.Many2many("res.partner", string="Customer Accounts")

    def action_delete_engineer(self):
        return {
            'name': "Reason",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'reason.engineer',
            'target': 'new',
            'context': {'child_id': self.env.context['params']['id']}
        }

    def _get_sale_team(self):
        sale_team = self.env['crm.team'].sudo().search(
            ['|', ('user_id', '=', self.id), ('member_ids', 'in', [self.id])])
        if sale_team:
            self.team_ids = sale_team.ids
        else:
            self.team_ids = False


class Menu(models.Model):
    _inherit = "website.menu"
    _description = "Website Menu"

    is_web_form = fields.Boolean(string="Web form", help="Use to filter web-form menu on company")


class ResCompany(models.Model):
    _inherit = 'res.company'

    website_menu_id = fields.Many2one("website.menu", tring="Web Form",
                                      help="The request will submitted to company based on this webform field",
                                      domain="[('is_web_form', '=', True)]")
    is_word_end_fields_shown = fields.Boolean(string="Work End")
    is_word_end_report = fields.Boolean(string="Work End Report")



