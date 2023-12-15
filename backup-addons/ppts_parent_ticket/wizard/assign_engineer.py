# -*- coding: utf-8 -*-
#############################################################################
#
#    Point Perfect Technology Solutions.
#
#############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
from odoo.exceptions import UserError, ValidationError


# Parent Assign Engineer
class AssignEngineer(models.Model):
    _name = 'assign.engineer'

    assign_engineer_id = fields.Many2one('res.users', string="User", copy=False, required=True)
    assign_engineer_ids = fields.Many2many('res.users', compute='_compute_assign_engineer_ids',
                                           string="Assign Engineer IDS", store=True, precompute=True, )
    is_assign_to_user = fields.Boolean(string="Is Assign to User")
    is_request_reassign = fields.Boolean(string="Is Request Reassign")

    @api.onchange('assign_engineer_id', 'assign_engineer_ids')
    def onchange_assign_engineer_id_domain(self):
        # engineer_ids = self.assign_engineer_ids
        pt = self.env['parent.ticket'].sudo().browse(self.env.context['active_id'])
        domain = [('groups_id', 'in', self.env.ref('ppts_service_request.service_request_group_ct_user').id),
                  ('id', 'not in', self.assign_engineer_ids.ids), ('id', 'in', pt.team_id.member_ids.ids)]
        return {'domain': {'assign_engineer_id': domain}}

    @api.depends('assign_engineer_id')
    def _compute_assign_engineer_ids(self):
        ass_eng_ids = []
        active_id = self._context.get('active_id')
        pt = self.env['parent.ticket'].sudo().search([('id', '=', active_id)])
        for each in pt.assign_engineer_ids:
            ass_eng_ids.append(each.id)
        self.assign_engineer_ids = ass_eng_ids

    def action_assign_engineer(self):
        enginner_ids = []
        for record in self:
            active_id = self._context.get('active_id')
            parent_ticket_id = self.env['parent.ticket'].sudo().search([('id', '=', active_id)])
            tasks_master_line = self.env['tasks.master.line'].sudo().search([('id', '=', active_id)])
            if parent_ticket_id:
                enginner_ids.append(record.assign_engineer_id.id)
                parent_ticket_id.assign_engineer_ids = [(4, x, None) for x in enginner_ids]
                parent_ticket_id.is_assigned_user = True
                # parent_ticket_id.state = 'confirm'
                parent_ticket_id.is_assign_to_user = True
                parent_ticket_id.is_confirm_assign_user = False
                parent_ticket_id.is_request_reassign = True
                if parent_ticket_id.is_assign_to_user == True:
                    task_id = self.env.ref('ppts_custom_workflow.task_data_assigned_to_user')
                    status_data = [(0, 0, {
                        'task_id': task_id.id,
                        'parent_ticket_id': parent_ticket_id.id,
                    })]
                    parent_ticket_id.write({'task_list_ids': status_data})
                    request_data = {
                        'name': task_id.name,
                        'parent_ticket_id': parent_ticket_id.id,
                        'team_id': parent_ticket_id.team_id.id,
                        'user_id': self.assign_engineer_id.id
                    }
                    request = self.env['request'].create(request_data)
            if tasks_master_line:
                enginner_ids.append(record.assign_engineer_id.id)
                tasks_master_line.parent_ticket_id.assign_engineer_ids = [(4, x, None) for x in enginner_ids]
                tasks_master_line.parent_ticket_id.is_assigned_user = True
                # tasks_master_line.parent_ticket_id.state = 'confirm'
                tasks_master_line.parent_ticket_id.is_assign_to_user = True
                tasks_master_line.parent_ticket_id.is_request_reassign = True

    def action_reassign_engineer(self):
        enginner_ids = []
        for record in self:
            active_id = self._context.get('active_id')
            parent_ticket_id = self.env['parent.ticket'].sudo().search([('id', '=', active_id)])
            tasks_master_line = self.env['tasks.master.line'].sudo().search([('id', '=', active_id)])
            if parent_ticket_id:
                enginner_ids.append(record.assign_engineer_id.id)
                parent_ticket_id.assign_engineer_ids = [(4, x, None) for x in enginner_ids]
                parent_ticket_id.is_assigned_user = True
                parent_ticket_id.state = 'confirm'
                parent_ticket_id.is_request_reassign = True
                if parent_ticket_id.is_request_reassign == True:
                    task_id = self.env.ref('ppts_custom_workflow.task_data_request_reassign')
                    status_data = [(0, 0, {
                        'task_id': task_id.id,
                        'parent_ticket_id': parent_ticket_id.id,
                    })]
                    parent_ticket_id.write({'task_list_ids': status_data})
                    request_data = {
                        'name': task_id.name,
                        'parent_ticket_id': parent_ticket_id.id,
                        'team_id': parent_ticket_id.team_id.id,
                        'user_id': self.assign_engineer_id.id
                    }
                    request = self.env['request'].create(request_data)
            if tasks_master_line:
                enginner_ids.append(record.assign_engineer_id.id)
                tasks_master_line.parent_ticket_id.assign_engineer_ids = [(4, x, None) for x in enginner_ids]
                tasks_master_line.parent_ticket_id.is_assigned_user = True
                # tasks_master_line.parent_ticket_id.state = 'confirm'
                tasks_master_line.parent_ticket_id.is_request_reassign = True


# Child Assign Engineer
class ChildAssignEngineer(models.Model):
    _name = 'child.assign.engineer'

    assign_engineer_id = fields.Many2one('res.users', string="Engineer", copy=False, required=True)
    assign_engineer_ids = fields.Many2many('res.users', compute='_compute_child_assign_engineer_ids',
                                           string="Assign Engineer IDS", store=True, precompute=True, )
    is_assign_to_user = fields.Boolean(string="Is Assign to User")
    is_request_reassign = fields.Boolean(string="Is Request Reassign")

    @api.onchange('assign_engineer_id', 'assign_engineer_ids')
    def onchange_assign_engineer_id_domain(self):
        # engineer_ids = self.assign_engineer_ids
        ct = self.env['child.ticket'].sudo().browse(self.env.context['active_id'])
        domain = [('groups_id', 'in', self.env.ref('ppts_service_request.service_request_group_user').id),
                  ('id', 'not in', self.assign_engineer_ids.ids), ('id', 'in', ct.team_id.member_ids.ids)]
        return {'domain': {'assign_engineer_id': domain}}

    @api.depends('assign_engineer_id')
    def _compute_child_assign_engineer_ids(self):
        ass_child_eng_ids = []
        active_id = self._context.get('active_id')
        ct = self.env['child.ticket'].sudo().search([('id', '=', active_id)])
        for each in ct.child_assign_engineer_ids:
            ass_child_eng_ids.append(each.id)
        self.assign_engineer_ids = ass_child_eng_ids

    def action_child_assign_engineer(self):
        enginner_ids = []
        for record in self:
            active_id = self._context.get('active_id')
            child_ticket_id = self.env['child.ticket'].sudo().search([('id', '=', active_id)])
            enginner_ids.append(record.assign_engineer_id.id)
            child_ticket_id.child_assign_engineer_ids = [(4, x, None) for x in enginner_ids]
            child_ticket_id.is_assign_to_user = True
            child_ticket_id.is_request_reassign = True
            if child_ticket_id.sudo().service_request_id.is_website_order:
                child_ticket_id.sudo().service_request_id.assign_engineer_ids = [(4, x, None) for x in enginner_ids]
            if child_ticket_id.is_assign_to_user == True:
                task_id = self.env.ref('ppts_custom_workflow.task_data_assigned_to_user')
                status_data = [(0, 0, {
                    'task_id': task_id.id,
                    'child_ticket_id': child_ticket_id.id,
                })]
                child_ticket_id.write({'task_list_ids': status_data})
                request_data = {
                    'name': task_id.name,
                    'child_ticket_id': child_ticket_id.id,
                    'team_id': child_ticket_id.team_id.id,
                    'user_id': self.assign_engineer_id.id
                }
                request = self.env['request'].create(request_data)
            child_ticket_id.is_request_reassign = False

    def action_child_reassign_engineer(self):
        enginner_ids = []
        for record in self:
            active_id = self._context.get('active_id')
            child_ticket_id = self.env['child.ticket'].sudo().search([('id', '=', active_id)])
            enginner_ids.append(record.assign_engineer_id.id)
            child_ticket_id.child_assign_engineer_ids = [(4, x, None) for x in enginner_ids]
            child_ticket_id.is_request_reassign = True
            if child_ticket_id.is_request_reassign == True:
                task_id = self.env.ref('ppts_custom_workflow.task_data_request_reassign')
                status_data = [(0, 0, {
                    'task_id': task_id.id,
                    'child_ticket_id': child_ticket_id.id,
                })]
                child_ticket_id.write({'task_list_ids': status_data})
                request_data = {
                    'name': task_id.name,
                    'child_ticket_id': child_ticket_id.id,
                    'team_id': child_ticket_id.team_id.id,
                    'user_id': self.assign_engineer_id.id
                }
                request = self.env['request'].create(request_data)
            child_ticket_id.is_request_reassign = False
