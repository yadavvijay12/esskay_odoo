# -*- coding: utf-8 -*-
#############################################################################
#
#    Point Perfect Technology Solutions.
#
#############################################################################
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError, ValidationError


class SLAPolicies(models.Model):
    _name = 'sla.policies'
    _rec_name = 'name'
    _description = "SLA Policies"

    name = fields.Char(string="Name", required=True, copy=False)
    description = fields.Html(string="Description", copy=False)
    team_id = fields.Many2one('sla.team', string="Team", copy=False)
    priority = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], string='Priority', default='high', copy=False)
    type = fields.Many2one('sla.type', string="Type", copy=False)
    tags = fields.Many2many('sla.tags', string="Tags", copy=False)
    customer_id = fields.Many2one('res.partner', string="Customer", copy=False)
    product_category_id = fields.Many2one('product.category', string="Product Category", copy=False)
    product_id = fields.Many2one('product.product', string="Product", copy=False, required=True)
    sale_order_id = fields.Many2one('sale.order', string="Sales Order Items", copy=False)
    start_stage_id = fields.Many2one('tasks.master', string="Start Stage", copy=False, required=True)
    reach_stage_id = fields.Many2one('tasks.master', string="Reach Stage", copy=False, required=True)
    duration = fields.Float("Duration", copy=False)
    interval_unit = fields.Selection([('hours', 'Hours'), ('days', 'Days')], string='Unit', default='hours', copy=False)
    excluding_stages_ids = fields.Many2many('tasks.master', string="Excluding Stages", copy=False)
    ticket_id = fields.Many2one('parent.ticket', string="Parent Ticket", copy=False)
    child_ticket_id = fields.Many2one('child.ticket', string="Child Ticket", copy=False)

class SLATeam(models.Model):
    _name = 'sla.team'
    _rec_name = 'name'
    _description = "SLA Team"
    
    name = fields.Char(string="Team Name", required=True)
    description = fields.Char(string="Description")


class SLAType(models.Model):
    _name = 'sla.type'
    _rec_name = 'name'
    _description = "SLA Type"
    
    name = fields.Char(string="Name", required=True)
    description = fields.Char(string="Description")


class SLATags(models.Model):
    _name = 'sla.tags'
    _rec_name = 'name'
    _description = "SLA Tags"
    
    name = fields.Char(string="Name", required=True)
    description = fields.Char(string="Description")
