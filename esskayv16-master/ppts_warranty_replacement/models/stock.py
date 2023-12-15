# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api,_
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res=super(StockPicking, self).button_validate()
        if self.sale_id.is_replacement_order and self.picking_type_id.code == 'outgoing':
            lot = self.env['stock.lot'].search([('name', '=', self.sale_id.product_serial_number)],limit=1)
            default_lot = self.move_line_ids_without_package.mapped("lot_id")
            if default_lot.id != lot.id:
                raise UserError(_('The Given Asset number is wrong, '
                                  '\n kindly use New Asset as - %s that attached on Warranty Replacement Order') % (lot.name))
            self.sale_id.delivery_number = self.id
            self.sale_id.delivery_order_date = date.today()
        return res

    @api.model_create_multi
    def create(self, vals):
        result = super(StockPicking, self).create(vals)
        # Status Update
        picking_id = self.env["stock.picking.type"].search([("id", "=", result.picking_type_id.id)], limit=1)
        task_id = None
        last_task_id = []
        order = self.env["sale.order"].search([("name", "=", result.origin)], limit=1)
        if order.is_replacement_order:
            result.parent_id = order.parent_ticket_id.id
            result.child_ticket_id = order.child_ticket_id.id
            # Parent ticket Status Update
            pt_task_ids = order.parent_ticket_id.task_list_ids.mapped("task_id")
            for pt_task in pt_task_ids:
                last_task_id.append(pt_task.id)
            last_id = last_task_id.pop() if last_task_id else None
            if picking_id.code == 'outgoing' and order.parent_ticket_id:
                if result.state in ['draft', 'waiting','confirmed']:
                    task_id = self.env.ref('ppts_warranty_replacement.task_data_wr_transfer_waiting')
                elif result.state in ['assigned']:
                    task_id = self.env.ref('ppts_warranty_replacement.task_data_wr_transfer_ready')
            if task_id and not task_id.id == last_id:
                pt_id = self.env["parent.ticket"].search([("id", "=", order.parent_ticket_id.id)])
                pt_id.update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })
            # Child ticket Status Update
            ct_task_ids = order.child_ticket_id.task_list_ids.mapped("task_id")
            for ct_task in ct_task_ids:
                last_task_id.append(ct_task.id)
            last_id = last_task_id.pop() if last_task_id else None
            if picking_id.code == 'outgoing' and order.child_ticket_id:
                if result.state in ['draft', 'waiting', 'confirmed']:
                    task_id = self.env.ref('ppts_warranty_replacement.task_data_wr_transfer_waiting')
                elif result.state in ['assigned']:
                    task_id = self.env.ref('ppts_warranty_replacement.task_data_wr_transfer_ready')
            if task_id and not task_id.id == last_id:
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
            task_id1 = None
            last_task_id = []
            order = self.env["sale.order"].search([("name", "=", record.origin)], limit=1)
            pt_task_ids = order.parent_ticket_id.task_list_ids.mapped("task_id")
            for pt_task in pt_task_ids:
                last_task_id.append(pt_task.id)
            last_id = last_task_id.pop() if last_task_id else None
            if order.is_replacement_order:
                if picking_id.code == 'outgoing':
                    if record.state == 'assigned':
                        task_id = self.env.ref('ppts_warranty_replacement.task_data_wr_transfer_ready')
                    elif record.state == 'done':
                        task_id = self.env.ref('ppts_warranty_replacement.task_data_wr_transfer_done')
                        task_id1 = self.env.ref('ppts_warranty_replacement.task_data_wr_transfer_delivered')
                if task_id and not task_id.id == last_id:
                    pt_id = self.env["parent.ticket"].search([("id", "=", order.parent_ticket_id.id)])
                    pt_id.update({
                        'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                    })
                    if task_id1:
                        pt_id.update({
                            'task_list_ids': [(0, 0, {'task_id': task_id1.id})],
                        })
                # Child ticket Status Update
                if task_id and not task_id.id == last_id:
                    ct_id = self.env["child.ticket"].search([("id", "=", order.child_ticket_id.id)])
                    ct_id.update({
                        'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                    })
                    if task_id1:
                        ct_id.update({
                            'task_list_ids': [(0, 0, {'task_id': task_id1.id})],
                        })
        return result
