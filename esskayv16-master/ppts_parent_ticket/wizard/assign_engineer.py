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
            title = _("Ticket Assigning!")
            message = _("Engineer has been assigned to ticket successfully.")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': title,
                    'message': message,
                    'next': {'type': 'ir.actions.act_window_close'}

                }
            }

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
            if child_ticket_id:
                child_ticket_id.is_request_reassign = False
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
            # Assign the same user on the parent ticket to show only those tickets to the child ticket engineers
            child_ticket_id.parent_ticket_id.ct_engineer_ids = [(4, self.assign_engineer_id.id)]
            # Assign engineer mail notification
            if child_ticket_id.child_assign_engineer_ids:
                assign_engineer_email = child_ticket_id.child_assign_engineer_ids[-1].login
                template_id = self.env.ref('ppts_parent_ticket.notify_email_template')
                if template_id:
                    template_id.with_context(email_to=assign_engineer_email).sudo().send_mail(child_ticket_id.id,
                                                                                              force_send=True)

            # assing_engineer_email=record.assign_engineer_id.login
            # template_id = self.env.ref('ppts_parent_ticket.assign_engineer_email_template')
            # if template_id:
            #     template_id.with_context(email_to=assing_engineer_email).sudo().send_mail(
            #         record.assign_engineer_id.id, force_send=True)

            title = _("Ticket Assigning!")
            message = _("Engineer has been assigned to ticket successfully.")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': title,
                    'message': message,
                    'next': {'type': 'ir.actions.act_window_close'}

                }
            }

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
            child_ticket_id.present_engineer_id = record.assign_engineer_id.id
            # Assign the same user on the parent ticket to show only those tickets to the child ticket engineers
            child_ticket_id.parent_ticket_id.ct_engineer_ids = [(4, self.assign_engineer_id.id)]
            # Re-Assign engineer mail notification
            if child_ticket_id.child_assign_engineer_ids:
                assign_engineer_email = child_ticket_id.child_assign_engineer_ids[-1].login
                template_id = self.env.ref('ppts_parent_ticket.notify_email_template')
                if template_id:
                    template_id.with_context(email_to=assign_engineer_email).sudo().send_mail(child_ticket_id.id,
                                                                                              force_send=True)


# Check Availability Engineer
class CheckAvailabilityEngineer(models.TransientModel):
    _name = 'check.availability.engineer'
    _description = 'Availabilty'

    name = fields.Char('Name')
    check_engineer_ids = fields.One2many('availability.engineer', 'assign_id', string="Engineer", copy=False)

    # @api.model
    # def default_get(self, default_fields):
    #     res = super().default_get(default_fields)
    #     if self._context.get('active_id'):
    #         child_id = self.env['child.ticket'].browse(self._context.get('active_id'))
    #     res_users = self.env['res.users'].search(
    #         [('groups_id', 'in', self.env.ref('ppts_service_request.service_request_group_user').id),
    #          ('groups_id', 'not in', self.env.ref('ppts_service_request.service_request_group_ct_user').id),
    #          ('id', 'in', child_id.team_id.member_ids.ids)])
    #     vals = []
    #     for rec in res_users:
    #         engineer_count = self.env['child.ticket'].search(
    #             [('child_assign_engineer_ids.name', '=', rec.name), ('state', '!=', 'closed')])
    #         vals.append((0, 0, {'user_assign_id': rec.id, 'engineer_tickets_count': len(engineer_count),
    #                             'child_tickets_ids': engineer_count.ids}))
    #     res['check_engineer_ids'] = vals
    #     return res


# Availability Engineer
class AvailabilityEngineer(models.TransientModel):
    _name = 'availability.engineer'
    _description = 'Availabilty Engineer'

    assign_id = fields.Many2one(
        string="New Approver",
        comodel_name="check.availability.engineer")

    user_assign_id = fields.Many2one('res.users', string="User", copy=False)
    engineer_tickets_count = fields.Integer(string='Count')
    child_tickets_ids = fields.Many2many('child.ticket', 'engineer_tickets_rel', 'availability_engineer_id',
                                         'child_ticket_id', string="Child Ticket")

    def action_to_assign_engineer(self):
        # call the assign engineer button to add it under assigned user tab in child ticket
        active_id = self._context.get('active_id')
        child_ticket_id = self.env['child.ticket'].sudo().search([('id', '=', active_id)])
        engineer_id = self.env['child.assign.engineer'].create({'assign_engineer_id': self.user_assign_id.id})
        vals = engineer_id.action_child_assign_engineer()
        return vals


# View Warranty Tickets
class ViewWarrantyTickets(models.TransientModel):
    _name = 'view.warranty.tickets'
    _description = 'View Warranty Tickets'

    child_tickets_ids = fields.Many2many('child.ticket', string="Child Tickets")

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        if self._context.get('active_id'):
            stock_id = self.env['stock.lot'].browse(self._context.get('active_id'))
            if stock_id:
                if self._context.get('is_warranty_tickets'):
                    warranty = self.env['child.ticket'].search(
                        [('warranty_start_dates', '>=', stock_id.warranty_start_date),
                         ('warranty_end_dates', '<=', stock_id.warranty_end_date),
                         ('stock_lot_id', '=', stock_id.name)])
                if self._context.get('is_repair_warranty_tickets'):
                    warranty = self.env['child.ticket'].search(
                        [('repair_warranty_start_date', '>=', stock_id.repair_warranty_start_date),
                         ('repair_warranty_end_date', '<=', stock_id.repair_warranty_end_date),
                         ('stock_lot_id', '=', stock_id.name)])

                if self._context.get('is_extend_warranty_tickets'):
                    warranty = self.env['child.ticket'].search(
                        [('extended_warranty_start_date', '>=', stock_id.extended_warranty_start_date),
                         ('extended_warranty_end_date', '<=', stock_id.extended_warranty_end_date),
                         ('stock_lot_id', '=', stock_id.name)])
                res['child_tickets_ids'] = [(4, rec.id, False) for rec in warranty]
        return res
