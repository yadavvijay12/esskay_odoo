# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import api, models, fields
import logging

_logger = logging.getLogger(__name__)


class MultiApprovalTypeLine(models.Model):
    _name = 'multi.approval.type.line'
    _description = 'Multi Aproval Type Lines'
    _order = 'sequence'

    name = fields.Char(string='Title', required=True)
    user_id = fields.Many2one(string='User', comodel_name="res.users",
                              required=True)
    sequence = fields.Integer(string='Sequence')
    is_mandatory = fields.Boolean(string='Mandatory')

    require_opt = fields.Selection(
        [('Required', 'Required'),
         ('Optional', 'Optional'),
         ], string="Type of Approval", default='Required')
    type_id = fields.Many2one(
        string="Type", comodel_name="multi.approval.type")

    def get_user(self):
        self.ensure_one()
        return self.user_id.id
