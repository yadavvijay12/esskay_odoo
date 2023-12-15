# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class CRMClaimRejectMessage(models.Model):
    _name = 'claim.reject.message'
    _description = 'CRM Claim Reject Message'

    name = fields.Char("Reject Reason", required=1)

class CRMReason(models.Model):
    _name = 'rma.reason.ppts'
    _description = 'CRM Reason'

    name = fields.Char("RMA Reason", required=1)
    action = fields.Selection([
        ('refund', 'Refund'),
        ('replace_same_product', 'Replace With Same Product'),
        ('replace_other_product', 'Replace With Other Product'),
        ('repair', 'Repair')], string="Related Action", required=1)
