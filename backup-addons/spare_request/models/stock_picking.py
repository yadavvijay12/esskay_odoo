from odoo import models, fields, api
from datetime import datetime, timedelta, date


class Picking(models.Model):
    _inherit = "stock.picking"

    spare_request = fields.Many2one('spare.request', string="Spare Request")
    is_return = fields.Boolean(string="Is Return Order", copy=False)

    @api.model
    def create(self, vals):
        res = super(Picking, self).create(vals)
        if res.backorder_id:
            if res.backorder_id.spare_request:
                res.spare_request = res.backorder_id.spare_request.id
                res.spare_request.write({'picking_ids': [(4, res.id)]})
        #'''STATUS UPDATE'''
        task_id = None
        last_task_id = []
        pt_task_ids = res.spare_request.parent_ticket_id.task_list_ids.mapped("task_id")
        for pt_task in pt_task_ids:
            last_task_id.append(pt_task.id)
        last_id = last_task_id.pop() if last_task_id else None

        if 'state' in vals:
            if not res.is_return and res.spare_request.parent_ticket_id:
                if res.state in ['draft', 'waiting', 'confirmed']:
                    task_id = self.env.ref('spare_request.task_data_spare_delivery_waiting')
            elif res.is_return and res.spare_request.parent_ticket_id:
                if res.state in ['draft', 'waiting', 'confirmed']:
                    task_id = self.env.ref('spare_request.task_data_spare_return_waiting')
                    
            if task_id and not task_id.id == last_id:
                pt_id = self.env["parent.ticket"].search([("id", "=", res.spare_request.parent_ticket_id.id)])
                pt_id.update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })
        return res

    def action_confirm(self):
        res = super().action_confirm()
        self.action_status_update_and_notifications()
        return res

    def action_assign(self):
        res = super().action_assign()
        self.action_status_update_and_notifications()
        return res

    def button_validate(self):
        res = super().button_validate()
        self.action_status_update_and_notifications()
        return res
    
    def action_status_update_and_notifications(self):
        for record in self:
            # stop
            task_id = None
            return_task_id = None
            last_task_id = []
            pt_task_ids = record.spare_request.parent_ticket_id.task_list_ids.mapped("task_id")
            for pt_task in pt_task_ids:
                last_task_id.append(pt_task.id)
            last_id = last_task_id.pop() if last_task_id else None

            # if 'state' in vals:
            if not record.is_return and (record.spare_request.parent_ticket_id or record.spare_request.child_ticket_id):
                if record.state in ['draft', 'waiting', 'confirmed']:
                    task_id = self.env.ref('spare_request.task_data_spare_delivery_waiting')
                elif record.state in ['assigned']:
                    task_id = self.env.ref('spare_request.task_data_spare_delivery_ready')
                elif record.state in ['done']:
                    task_id = self.env.ref('spare_request.task_data_spare_delivery_done')
            elif record.is_return and (record.spare_request.parent_ticket_id or record.spare_request.child_ticket_id):
                if record.state in ['draft', 'waiting', 'confirmed']:
                    task_id = self.env.ref('spare_request.task_data_spare_return_waiting')
                elif record.state in ['assigned']:
                    task_id = self.env.ref('spare_request.task_data_spare_return_ready')
                elif record.state in ['done']:
                    task_id = self.env.ref('spare_request.task_data_spare_return_done')
                if record.state in ['done']:
                    return_task_id = self.env.ref('spare_request.task_data_spare_parts_returned')

            if task_id and not task_id.id == last_id and record.spare_request.parent_ticket_id and not record.spare_request.child_ticket_id:
                record.spare_request.parent_ticket_id.update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })
            if return_task_id and not return_task_id.id == last_id and record.spare_request.parent_ticket_id and not record.spare_request.child_ticket_id:
                record.spare_request.parent_ticket_id.update({
                    'task_list_ids': [(0, 0, {'task_id': return_task_id.id})],
                })
            # CT
            ct_last_task_id = []
            ct_task_ids = record.spare_request.child_ticket_id.task_list_ids.mapped("task_id")
            for ct_task in ct_task_ids:
                ct_last_task_id.append(ct_task.id)
            ct_last_id = ct_last_task_id.pop() if ct_last_task_id else None
            if task_id and not task_id.id == ct_last_id and record.spare_request.child_ticket_id:
                record.spare_request.child_ticket_id.update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })
            if return_task_id and not return_task_id.id == ct_last_id and record.spare_request.child_ticket_id:
                record.spare_request.child_ticket_id.update({
                    'task_list_ids': [(0, 0, {'task_id': return_task_id.id})],
                })


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'
    _description = 'Return Picking'

    def _prepare_picking_default_values(self):
        res = super(ReturnPicking, self)._prepare_picking_default_values()
        vals = {
            'is_return': True,
            'state': 'draft',
        }
        res.update(vals)
        if self.picking_id.spare_request:
            task_id = self.env.ref('spare_request.task_data_spare_return_requested')
            ct_id = self.env["child.ticket"].search([("id", "=", self.picking_id.spare_request.child_ticket_id.id)])
            if ct_id:
                ct_id.update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })
            pt_id = self.env["parent.ticket"].search([("id", "=", self.picking_id.spare_request.parent_ticket_id.id)])
            if pt_id and not ct_id:
                pt_id.update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })
        return res
