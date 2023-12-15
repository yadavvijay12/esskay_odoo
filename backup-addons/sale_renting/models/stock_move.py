# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.tools import float_compare


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    parent_ticket_id = fields.Many2one('parent.ticket', string="Parent Ticket ID")
    child_ticket_id = fields.Many2one('child.ticket', string="Parent Ticket ID")
    lr_from_pt = fields.Boolean(string="Is Loaner Delivery Order From PT")
    
    @api.model_create_multi
    def create(self, vals):
        result = super(StockPicking, self).create(vals)
        picking_id = self.env["stock.picking.type"].search([("id", "=", result.picking_type_id.id)], limit=1)
        task_id = None
        last_task_id = []
        order = self.env["sale.order"].search([("name", "=", result.origin)], limit=1)
        pt_task_ids = order.parent_ticket_id.task_list_ids.mapped("task_id")
        for pt_task in pt_task_ids:
            last_task_id.append(pt_task.id)
        last_id = last_task_id.pop() if last_task_id else None
        if order.is_rental_order:
            if picking_id.code == 'outgoing':
                if result.state in ['draft', 'waiting','confirmed'] and any(order.parent_ticket_id or order.child_ticket_id):
                    task_id = self.env.ref('ppts_custom_workflow.task_data_loaner_transfer_waiting')
                elif result.state in ['assigned'] and any(order.parent_ticket_id or order.child_ticket_id):
                    task_id = self.env.ref('ppts_custom_workflow.task_data_loaner_transfer_ready')
            elif picking_id.code == 'incoming':
                if result.state in ['draft', 'waiting','confirmed'] and any(order.parent_ticket_id or order.child_ticket_id):
                    task_id = self.env.ref('ppts_custom_workflow.task_data_loaner_return_transfer_waiting')
                elif result.state in ['assigned'] and any(order.parent_ticket_id or order.child_ticket_id):
                    task_id = self.env.ref('ppts_custom_workflow.task_data_loaner_return_transfer_ready')
            if task_id and not task_id.id == last_id:
                pt_id = self.env["parent.ticket"].search([("id", "=", order.parent_ticket_id.id)])
                pt_id.update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })
            # Child Ticket Status Update
            ct_last_task_id = []
            ct_task_ids = order.child_ticket_id.task_list_ids.mapped("task_id")
            for ct_task in ct_task_ids:
                ct_last_task_id.append(ct_task.id)
            ct_last_id = ct_last_task_id.pop() if ct_last_task_id else None
            if task_id and not task_id.id == ct_last_id:
                ct_id = self.env["child.ticket"].search([("id", "=", order.child_ticket_id.id)])
                ct_id.update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })
        return result

    def write(self, vals):
        result = super(StockPicking, self).write(vals)
        for record in self:
            # if 'state' in vals:
            picking_id = self.env["stock.picking.type"].search([("id", "=", record.picking_type_id.id)], limit=1)
            task_id = None
            last_task_id = []
            order = self.env["sale.order"].search([("name", "=", record.origin)], limit=1)
            pt_task_ids = order.parent_ticket_id.task_list_ids.mapped("task_id")
            for pt_task in pt_task_ids:
                last_task_id.append(pt_task.id)
            last_id = last_task_id.pop() if last_task_id else None
            if order.is_rental_order:
                if picking_id.code == 'outgoing':
                    if record.state == 'assigned' and any(order.parent_ticket_id or order.child_ticket_id):
                        task_id = self.env.ref('ppts_custom_workflow.task_data_loaner_transfer_ready')
                    elif record.state == 'done' and any(order.parent_ticket_id or order.child_ticket_id):
                        task_id = self.env.ref('ppts_custom_workflow.task_data_loaner_transfer_done')
                elif picking_id.code == 'incoming':
                    if record.state == 'assigned' and any(order.parent_ticket_id or order.child_ticket_id):
                        task_id = self.env.ref('ppts_custom_workflow.task_data_loaner_return_transfer_ready')
                    elif record.state == 'done' and any(order.parent_ticket_id or order.child_ticket_id):
                        task_id = self.env.ref('ppts_custom_workflow.task_data_loaner_return_transfer_done')
                if task_id and not task_id.id == last_id:
                    pt_id = self.env["parent.ticket"].search([("id", "=", order.parent_ticket_id.id)])
                    pt_id.update({
                        'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                    })
                # Child Ticket Status Update
                ct_last_task_id = []
                ct_task_ids = order.child_ticket_id.task_list_ids.mapped("task_id")
                for ct_task in ct_task_ids:
                    ct_last_task_id.append(ct_task.id)
                ct_last_id = ct_last_task_id.pop() if ct_last_task_id else None
                if task_id and not task_id.id == ct_last_id:
                    ct_id = self.env["child.ticket"].search([("id", "=", order.child_ticket_id.id)])
                    ct_id.update({
                        'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                    })
        return result

    def button_validate(self):
        res=super(StockPicking, self).button_validate()
        if self.sale_id.rental_status =='pickup':
            for move in self.move_ids:
                order_line_p=self.sale_id.order_line.filtered(lambda  x:x.product_id ==move.product_id)
                if order_line_p:
                    order_line_p.qty_delivered += move.quantity_done
        elif self.sale_id.rental_status =='return':
            for move in self.move_ids:
                order_line_obj=self.sale_id.order_line.filtered(lambda  x:x.product_id ==move.product_id)
                if order_line_obj:
                    order_line_obj.qty_returned += move.product_uom_qty
        return res


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    rental_route_id = fields.Many2one("stock.route", string="Loaner Route")
    rental_out_location_id = fields.Many2one(
        "stock.location",
        "Loaner Customer Location",
        check_company=True,
        domain="[('usage', '=', 'customer'), ('company_id', '=', company_id)]",
    )
   
    
class StockLocation(models.Model):
    _inherit = 'stock.location'

    wh_id = fields.Many2one('stock.warehouse', string="Repair Center Location", copy=False)
