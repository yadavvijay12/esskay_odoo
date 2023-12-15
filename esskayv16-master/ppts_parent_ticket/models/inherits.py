# -*- coding: utf-8 -*-
#############################################################################
#
#    Point Perfect Technology Solutions.
#
#############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class TasksMasterLine(models.Model):
    _inherit = 'tasks.master.line'

    def button_tasks_update(self):
        # values = super().button_tasks_update()
        for record in self:
            if record.is_check_oem_warranty and (record.parent_ticket_id or record.child_ticket_id):
                # Status update for OEM Warranty Check
                warranty_status_task = None
                if record.parent_ticket_id.oem_warranty_status == 'in_oem_warranty' or record.child_ticket_id.oem_warranty_status == 'in_oem_warranty':
                    warranty_status_task = self.env.ref('ppts_custom_workflow.task_data_in_oem_warranty')
                elif record.parent_ticket_id.oem_warranty_status == 'out_oem_warranty' or record.child_ticket_id.oem_warranty_status == 'out_oem_warranty':
                    warranty_status_task = self.env.ref('ppts_custom_workflow.task_data_oo_oem_warranty')
                else:
                    warranty_status_task = self.env.ref('ppts_custom_workflow.task_data_warranty_not_available')
                if record.parent_ticket_id and warranty_status_task:
                    warranty_status_task_id = record.parent_ticket_id.parent_configuration_id.work_flow_id.task_list_ids.task_id.filtered(
                        lambda r: r.id == warranty_status_task.id)
                    if warranty_status_task_id:
                        record.parent_ticket_id.sudo().write(
                            {'task_list_ids': [(0, 0, {'task_id': warranty_status_task.id})]})
                    else:
                        raise UserError(_('There is no "%s" Task available on workflow to update on ticket status',
                                          warranty_status_task.name))
                elif record.child_ticket_id and warranty_status_task:
                    warranty_status_task_id = record.child_ticket_id.child_configuration_id.work_flow_id.task_list_ids.task_id.filtered(
                        lambda r: r.id == warranty_status_task.id)
                    if warranty_status_task_id:
                        record.child_ticket_id.sudo().write(
                            {'task_list_ids': [
                                (0, 0, {'task_id': warranty_status_task.id, 'Commants': 'OEM Warranty'})]})
                    else:
                        raise UserError(_('There is no "%s" Task available on workflow to update on ticket status',
                                          warranty_status_task.name))

            if record.is_check_oem_repair_status and (record.parent_ticket_id or record.child_ticket_id):
                # Status update for Repair Warranty Check
                repair_status_task = None
                if record.parent_ticket_id.oem_repair_status == 'in_repair_warranty' or record.child_ticket_id.oem_repair_status == 'in_repair_warranty':
                    repair_status_task = self.env.ref('ppts_custom_workflow.task_data_in_repair_warranty')
                elif record.parent_ticket_id.oem_repair_status == 'out_repair_warranty' or record.child_ticket_id.oem_repair_status == 'out_repair_warranty':
                    repair_status_task = self.env.ref('ppts_custom_workflow.task_data_oo_repair_warranty')
                else:
                    repair_status_task = self.env.ref('ppts_custom_workflow.task_data_warranty_not_available')
                if record.parent_ticket_id and repair_status_task:
                    repair_status_task_id = record.parent_ticket_id.parent_configuration_id.work_flow_id.task_list_ids.task_id.filtered(
                        lambda r: r.id == repair_status_task.id)
                    if repair_status_task_id:
                        record.parent_ticket_id.sudo().write(
                            {'task_list_ids': [(0, 0, {'task_id': repair_status_task.id})]})
                    else:
                        raise UserError(_('There is no "%s" Task available on workflow to update on ticket status',
                                          repair_status_task.name))
                elif record.child_ticket_id and repair_status_task:
                    repair_status_task_id = record.child_ticket_id.child_configuration_id.work_flow_id.task_list_ids.task_id.filtered(
                        lambda r: r.id == repair_status_task.id)
                    if repair_status_task_id:
                        record.child_ticket_id.sudo().write(
                            {'task_list_ids': [
                                (0, 0, {'task_id': repair_status_task.id, 'Commants': 'Repair Warranty'})]})
                    else:
                        raise UserError(_('There is no "%s" Task available on workflow to update on ticket status',
                                          repair_status_task.name))
                # Status update for Repair Warranty Check ---END---

            if record.check_extended_warranty_status and (record.parent_ticket_id or record.child_ticket_id):
                # Status update for Extended Warranty Check
                extended_status_task = None
                if record.parent_ticket_id.extended_warranty_status == 'in_repair_warranty' or record.child_ticket_id.extended_warranty_status == 'in_repair_warranty':
                    extended_status_task = self.env.ref('ppts_custom_workflow.task_data_in_repair_warranty')
                elif record.parent_ticket_id.extended_warranty_status == 'out_repair_warranty' or record.child_ticket_id.extended_warranty_status == 'out_repair_warranty':
                    extended_status_task = self.env.ref('ppts_custom_workflow.task_data_oo_repair_warranty')
                else:
                    extended_status_task = self.env.ref('ppts_custom_workflow.task_data_warranty_not_available')

                if record.parent_ticket_id and extended_status_task:
                    extended_status_task_id = record.parent_ticket_id.parent_configuration_id.work_flow_id.task_list_ids.task_id.filtered(
                        lambda r: r.id == extended_status_task.id)
                    if extended_status_task_id:
                        record.parent_ticket_id.sudo().write(
                            {'task_list_ids': [(0, 0, {'task_id': extended_status_task.id})]})
                    else:
                        raise UserError(_('There is no "%s" Task available on workflow to update on ticket status',
                                          extended_status_task.name))
                elif record.child_ticket_id and extended_status_task:
                    extended_status_task_id = record.child_ticket_id.child_configuration_id.work_flow_id.task_list_ids.task_id.filtered(
                        lambda r: r.id == extended_status_task.id)
                    if extended_status_task_id:
                        record.child_ticket_id.sudo().write(
                            {'task_list_ids': [
                                (0, 0, {'task_id': extended_status_task.id, 'Commants': 'Extended Warranty'})]})
                    else:
                        raise UserError(_('There is no "%s" Task available on workflow to update on ticket status',
                                          extended_status_task.name))
        return super().button_tasks_update()
