# -*- coding: utf-8 -*-
#############################################################################
#
#    Point Perfect Technology Solutions.
#
#############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
from odoo.exceptions import UserError, ValidationError

#Status Update
class TasksMasterLine(models.Model):
    _inherit = 'tasks.master.line'
    
    status_update_id = fields.Many2one('status.update', string='Status Update')

class StatusUpdate(models.Model):
    _name = 'status.update'

    def _default_next_task_ids(self):
        tasks_all_ids = self.env["tasks.master"].search([])
        return tasks_all_ids.ids
    
    is_ar_hold_tick = fields.Boolean(string="Is AR Hold/Release")
    workflow_id = fields.Many2one('custom.workflow', string="Workflow")
    task_list_ids = fields.One2many('tasks.master.line', 'status_update_id', string="Status")
    next_task_ids = fields.Many2many('tasks.master', string="Next Tasks", default=_default_next_task_ids)
    
    
    @api.onchange('task_list_ids')
    def _onchange_task_list_ids(self):
        for record in self:
            if self.workflow_id:
                pro =[]
                for task_line in record.task_list_ids:
                    work_flow = self.env["tasks.master.line"].search([("workflow_id", "=", self.workflow_id.id),("task_id", "=", task_line.task_id.id)])
                    if work_flow: 
                        for wk in work_flow:
                            if wk.next_task_ids:
                                pro_ids = [(6, 0, wk.next_task_ids.ids)]
                                task_line.next_task_ids = pro_ids
                                self.next_task_ids = [(6, 0, wk.next_task_ids.ids)]
                            else:
                                pro_ids = False
                                self.next_task_ids = False
                    else:
                        self.next_task_ids = False

    def action_status_update(self):
        for record in self:
            if self.env.context.get('active_model') == 'parent.ticket':
                active_id = self._context.get('active_id')
                parent_ticket_id = self.env['parent.ticket'].search([('id', '=', active_id)])
                for line in record.task_list_ids:
                    line.parent_ticket_id = parent_ticket_id.id
                    line.parent_ticket_id._onchange_task_list_ids()
            if self.env.context.get('active_model') == 'child.ticket':
                active_id = self._context.get('active_id')
                child_ticket_id = self.env['child.ticket'].search([('id', '=', active_id)])
                for line in record.task_list_ids:
                    line.child_ticket_id = child_ticket_id.id
                    line.child_ticket_id._onchange_task_list_ids()
            
    
