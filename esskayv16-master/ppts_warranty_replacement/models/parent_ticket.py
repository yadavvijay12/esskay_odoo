import base64

from odoo import fields, models, api, _
from datetime import date

from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import pytz


class ParentTicketInherit(models.Model):
    _inherit = "parent.ticket"

    replacement_order_ids = fields.Many2many('sale.order', string="Warranty Replacement",
                                             compute='_compute_replacement_order_ids')
    is_create_wr_order = fields.Boolean(string="WR Create")
    replacement_order_count = fields.Integer(string="Replacement Count", compute='compute_replacement_order_count')
    replacement_picking_ids = fields.Many2many('stock.picking', string="Replacement Delivery Orders")

    @api.onchange('task_list_ids')
    def _onchange_task_list_ids(self):
        res = super(ParentTicketInherit, self)._onchange_task_list_ids()
        for record in self:
            mr = record.task_list_ids.task_id.filtered(lambda r: r.python_code == 'sr_wr')
            if mr:
                record.is_create_wr_order = True
            else:
                record.is_create_wr_order = False
        return res

    def wr_task_values(self):
        user_tz = self.env.user.tz or 'UTC'
        local_tz = pytz.timezone(user_tz)

        job_started_ref = self.env.ref('ppts_custom_workflow.job_start_time').id
        job_end_ref = self.env.ref('ppts_warranty_replacement.task_data_wr_transfer_delivered').id
        if job_started_ref:
            job_started = self.env['tasks.master.line'].search(
                [('task_id', '=', job_started_ref), ('parent_ticket_id', '=', self.id)], limit=1)
            job_start = (job_started.create_date.astimezone(local_tz).replace(tzinfo=None)) if job_started else ''
        if job_end_ref:
            job_end = self.env['tasks.master.line'].search(
                [('task_id', '=', job_end_ref), ('parent_ticket_id', '=', self.id)], limit=1)
            job_end_time = (job_end.create_date.astimezone(local_tz).replace(tzinfo=None)) if job_end else ''

        docargs = {
            'job_started': job_start.strftime("%d/%m/%Y %H:%M") if job_started else '',
            'job_end': job_end_time.strftime("%d/%m/%Y %H:%M") if job_end else '',
        }
        return docargs

    def compute_replacement_order_count(self):
        for record in self:
            record.replacement_order_count = self.env['sale.order'].search_count(
                [('is_replacement_order', '=', True), ('parent_ticket_id', '=', record.id)])
            replacement_picking = self.env['sale.order'].search(
                [('is_replacement_order', '=', True), ('parent_ticket_id', '=', record.id)]).delivery_number
            record.sudo().replacement_picking_ids = replacement_picking.ids

    def action_view_replacement_order(self):
        self.ensure_one()
        form_id = self.env.ref('ppts_warranty_replacement.warranty_replacement_form_view').id
        tree_id = self.env.ref('ppts_warranty_replacement.warranty_replacement_tree_view').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Warranty Replacement',
            'view_mode': 'tree,form',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'res_model': 'sale.order',
            'target': 'current',
            'domain': [('is_replacement_order', '=', True), ('parent_ticket_id', '=', self.id)],
        }

    def _compute_replacement_order_ids(self):
        for rec in self:
            replacement_order_ids = self.env['sale.order'].search(
                [('parent_ticket_id', '=', rec.id), ('is_replacement_order', '=', True)])

            rec.replacement_order_ids = replacement_order_ids.ids

    def action_create_warranty_replacement(self):
        for order in self:
            if not order.stock_lot_id:
                raise UserError(_("Please Select Asset"))
            else:
                wr_order = {
                    'is_replacement_order': True,
                    'partner_id': order.partner_id.id or False,
                    'service_category_id': order.service_category_id.id or False,
                    'service_type_id': order.service_type_id.id or False,
                    'team_id': order.team_id.id or False,
                    'service_request_id': order.id or False,
                    'reported_fault': order.problem_description or '',
                    # 'request_type_id': order.request_type_id.id or False,
                    'parent_ticket_id': order.id or False,
                    # 'child_ticket_id': order.child_ticket_id.id or False,
                    'external_reference': order.remarks,
                    'worksheet_id': order.service_request_id.survey_id.id or False,
                    'origin': order.name or '',
                    'product_serial_no': order.product_id.custom_product_serial,
                    'product_part_no': order.product_id.product_part,
                    'product_code_no': order.product_id.default_code,
                    'categ_id': order.product_id.categ_id.id,
                    'order_line': [(0, 0, {
                        'product_id': order.product_id.id,
                        'stock_lot_id': order.stock_lot_id.id,
                        'product_uom_qty': 1,
                        'product_uom': order.product_id.uom_id.id,
                    })],
                }
                order.is_create_wr_order = False
                replace_id = self.env['sale.order'].create(wr_order)
                view = self.env.ref('ppts_warranty_replacement.warranty_replacement_form_view')
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Warranty Replacement',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id': view.id,
                    'res_model': 'sale.order',
                    'res_id': replace_id.id,
                    'target': 'current',
                    'domain': [('is_replacement_order', '=', True)],
                }


class ChildTicketInherit(models.Model):
    _inherit = "child.ticket"

    replacement_picking_ids = fields.Many2many('stock.picking', string="Replacement Delivery Orders")
    is_create_wr_order = fields.Boolean(string="WR Create")
    replacement_order_count = fields.Integer(string="Replacement Count", compute='compute_replacement_order_count')
    replacement_order_ids = fields.Many2many('sale.order', string="Warranty Replacement",
                                             compute='_compute_replacement_order_ids')

    @api.onchange('task_list_ids')
    def _onchange_task_list_ids(self):
        res = super(ChildTicketInherit, self)._onchange_task_list_ids()
        for record in self:
            mr = record.task_list_ids.task_id.filtered(lambda r: r.python_code == 'sr_wr')
            if mr:
                record.is_create_wr_order = True
            else:
                record.is_create_wr_order = False
            # Transfer Validation Check on Task Update
            internal_transfer = self.env['stock.picking'].search_count(
                [('child_ticket_id', '=', record._origin.id), ('picking_type_id.code', '=', 'incoming'),
                 ('state', 'not in', ('done', 'cancel'))])
            all_transfer = self.env['stock.picking'].search_count(
                [('child_ticket_id', '=', record._origin.id), ('state', 'not in', ('done', 'cancel'))])
            is_job_closed = record.task_list_ids.task_id.filtered(lambda r: r.is_end_task == True)
            if int(internal_transfer) > 0 and record.request_type == 'sr_wr' and is_job_closed:
                raise ValidationError(_("Confirm this receipts to continue the process"))
            if int(all_transfer) > 0 and is_job_closed and record.request_type == 'sr_wr':
                raise ValidationError(_("Kindly Close all Receipts and Delivery Orders to close the job"))
        return res

    def wr_task_values(self):
        user_tz = self.env.user.tz or 'UTC'
        local_tz = pytz.timezone(user_tz)

        job_started_ref = self.env.ref('ppts_custom_workflow.job_start_time').id
        job_end_ref = self.env.ref('ppts_warranty_replacement.task_data_wr_transfer_delivered').id
        if job_started_ref:
            job_started = self.env['tasks.master.line'].search(
                [('task_id', '=', job_started_ref), ('child_ticket_id', '=', self.id)], limit=1)
            job_start = (job_started.create_date.astimezone(local_tz).replace(tzinfo=None)) if job_started else ''
        if job_end_ref:
            job_end = self.env['tasks.master.line'].search(
                [('task_id', '=', job_end_ref), ('child_ticket_id', '=', self.id)], limit=1)
            job_end_time = (job_end.create_date.astimezone(local_tz).replace(tzinfo=None)) if job_end else ''

        docargs = {
            'job_started': job_start.strftime("%d/%m/%Y %H:%M") if job_started else '',
            'job_end': job_end_time.strftime("%d/%m/%Y %H:%M") if job_end else '',
        }
        return docargs

    def compute_replacement_order_count(self):
        for record in self:
            record.replacement_order_count = self.env['sale.order'].search_count(
                [('is_replacement_order', '=', True), ('child_ticket_id', '=', record.id),
                 ('wr_state', '!=', 'cancelled')])
            replacement_picking = self.env['sale.order'].search(
                [('is_replacement_order', '=', True), ('child_ticket_id', '=', record.id)]).delivery_number
            record.sudo().replacement_picking_ids = replacement_picking.ids

    def action_view_replacement_order(self):
        self.ensure_one()
        action = {
            'name': _('Warranty Replacement(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'target': 'current',
        }
        child_ticket_ids = self.env['sale.order'].search([('child_ticket_id', '=', self.id)])
        if len(child_ticket_ids) == 1:
            action['res_id'] = child_ticket_ids.ids[0]
            action['view_mode'] = 'form'
            action['views'] = [[self.env.ref('ppts_warranty_replacement.warranty_replacement_form_view').id, 'form']]

        else:
            action['view_mode'] = 'tree,form'
            action['views'] = [(self.env.ref('ppts_warranty_replacement.warranty_replacement_tree_view').id, 'tree'),(self.env.ref('ppts_warranty_replacement.warranty_replacement_form_view').id, 'form')]
            action['domain'] = [('is_replacement_order', '=', True), ('id', 'in', child_ticket_ids.ids)]
        return action

    def _compute_replacement_order_ids(self):
        for rec in self:
            replacement_order_ids = self.env['sale.order'].search(
                [('child_ticket_id', '=', rec.id), ('is_replacement_order', '=', True)])

            rec.replacement_order_ids = replacement_order_ids.ids

    def action_create_warranty_replacement(self):
        for order in self:
            if not order.stock_lot_id:
                raise UserError(_("Please Select Asset"))
            else:
                wr_order = {
                    'is_replacement_order': True,
                    'partner_id': order.partner_id.id or False,
                    'service_category_id': order.service_category_id.id or False,
                    'service_type_id': order.service_type_id.id or False,
                    'team_id': order.team_id.id or False,
                    'service_request_id': order.service_request_id.id or False,
                    'reported_fault': order.problem_description,
                    # 'request_type_id': order.request_type_id.id or False,
                    'child_ticket_id': order.id or False,
                    # 'parent_ticket_id': order.sudo().id or False,
                    'external_reference': order.remarks,
                    'worksheet_id': order.service_request_id.survey_id.id or False,
                    'origin': order.name or '',
                    'product_serial_no': order.stock_lot_id.name,
                    'product_part_no': order.product_id.product_part,
                    'product_code_no': order.product_id.product_code,
                    'categ_id': order.product_id.categ_id.id,
                    'invoice_number': order.stock_lot_id.invoice_number,
                    'invoice_date': order.stock_lot_id.invoice_date,
                    'order_line': [(0, 0, {
                        'product_id': order.product_id.id,
                        'stock_lot_id': order.stock_lot_id.id,
                        'product_uom_qty': 1,
                        'product_uom': order.product_id.uom_id.id,
                    })],
                }
                order.is_create_wr_order = False
                replace_id = self.env['sale.order'].create(wr_order)
                # Add the CT user and engineer ids to this field to see the record using record rule.
                for parent_ticket_record in self.sudo().parent_ticket_id.assign_engineer_ids:
                    replace_id.assigned_ids = [(4, parent_ticket_record.sudo().id)]

                for ct_id in self.sudo().parent_ticket_id.child_ticket_ids:
                    for child_ticket_record in ct_id.child_assign_engineer_ids:
                        replace_id.assigned_ids = [(4, child_ticket_record.id)]
                view = self.env.ref('ppts_warranty_replacement.warranty_replacement_form_view')
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Warranty Replacement',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id': view.id,
                    'res_model': 'sale.order',
                    'res_id': replace_id.id,
                    'target': 'current',
                    'domain': [('is_replacement_order', '=', True)],
                }

    @api.model
    def create(self, vals):
        rec = super(ChildTicketInherit, self).create(vals)
        if self.env.context.get('active_model') == 'parent.ticket':
            parent_ticket = self.env['parent.ticket'].browse(self.env.context['active_id'])
            if parent_ticket.request_type_id.ticket_type == 'sr_wr':
                rec.update({'replacement_picking_ids': parent_ticket.replacement_picking_ids.ids})
        return rec


class TasksMasterLine(models.Model):
    _inherit = 'tasks.master.line'

    def button_tasks_update(self):
        values = super().button_tasks_update()
        for record in self:
            template_id = False
            employee = self.env['hr.employee'].sudo().search(
                [('job_id', 'in', record.task_id.sudo().job_ids.ids)]).mapped('work_email')
            employee_cc = self.env['hr.employee'].sudo().search(
                [('job_id', 'in', record.task_id.sudo().job_cc_ids.ids)]).mapped('work_email')
            mails = ', '.join(employee)
            mails_cc = ', '.join(employee_cc)
            template_id = self.env.ref('ppts_parent_ticket.mail_template_closed_child_ticket')
            if record.is_end_task and record.child_ticket_id and record.child_ticket_id.request_type == 'sr_wr':

                report = self.env.ref('ppts_parent_ticket.Warranty_Replacement_Form_reports_print')
                data_record = base64.b64encode(
                    self.env['ir.actions.report'].sudo()._render_qweb_pdf(report, [record.child_ticket_id.id],
                                                                          data=None)[0])
                ir_values = {
                    'name': "Replacement Completed" + record.child_ticket_id.name,
                    'type': 'binary',
                    'datas': data_record,
                    'store_fname': data_record,
                    'mimetype': 'application/pdf',
                    'res_model': 'child.ticket',
                }
                report_attachment_id = self.env['ir.attachment'].sudo().create(ir_values)
                template_id.attachment_ids.unlink()
                template_id.attachment_ids = [(4, report_attachment_id.id)]
                if template_id:
                    template_id.with_context(email_to=mails, email_cc=mails_cc).sudo().send_mail(
                        record.child_ticket_id.id, force_send=True)
            # template_id.attachment_ids.unlink()

        return values
