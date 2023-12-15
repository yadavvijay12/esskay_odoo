from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError


class SpareRequest(models.Model):
    _name = 'spare.request'
    _description = 'Spare Request'

    def _get_default_warehouse(self):
        warehouse_obj = self.env['stock.warehouse']
        warehouse_ids = warehouse_obj.search([('company_id', '=', self.env.company.id)])
        warehouse_id = warehouse_ids and warehouse_ids[0] or False
        return warehouse_id.id

    def _get_default_picking_type(self):
        # warehouse_id = self._get_default_warehouse()
        # if warehouse_id:
        #     warehouse_obj = self.env['stock.warehouse']
        #     warehouse_br = warehouse_obj.browse(warehouse_id)
        #     return warehouse_br and warehouse_br.int_type_id.id
        picking_type_obj = self.env['stock.picking.type']
        picking_type_ids = picking_type_obj.search(
            [('code', '=', 'internal'), ('company_id', '=', self.env.company.id)])  # , ('sequence_code', '=', 'INTR')
        print("\n\n\n--->", picking_type_ids)
        picking_type_id = picking_type_ids and picking_type_ids[0] or False
        return picking_type_id.id

    ''' 
    @api.depends('picking_ids.state')
    def _compute_state(self):
        State of a picking depends on the state of its related stock.move
        - Draft: only used for "planned pickings"
        - Waiting: if the picking is not ready to be sent so if
          - (a) no quantity could be reserved at all or if
          - (b) some quantities could be reserved and the shipping policy is "deliver all at once"
        - Waiting another move: if the picking is waiting for another move
        - Ready: if the picking is ready to be sent so if:
          - (a) all quantities are reserved or if
          - (b) some quantities could be reserved and the shipping policy is "as soon as possible"
        - Done: if the picking is done.
        - Cancelled: if the picking is cancelled
        
        for picking in self.picking_ids:

            if not picking.move_lines:
                self.state = 'draft'
            elif any(move.state == 'draft' for move in picking.move_lines):  # TDE FIXME: should be all ?
                self.state = 'draft'
            elif all(move.state == 'cancel' for move in picking.move_lines):
                self.state = 'reject'
            elif all(move.state in ['cancel', 'done'] for move in picking.move_lines):
                self.state = 'received'
            else:
                relevant_move_state = picking.move_lines._get_relevant_state_among_moves()
                print('relevant_move_state--->',relevant_move_state)

                pk
                if relevant_move_state == 'partially_available':
                    self.state = 'assigned'
                else:
                    self.state = relevant_move_state
           '''

    name = fields.Char(string="Seq", copy=False, default=lambda x: _('New'))
    sequence_id = fields.Char(string="Sequence", copy=False)
    requested_by_id = fields.Many2one('res.users', string="Requested by", default=lambda self: self.env.user.id)
    request_type = fields.Selection([('normal', 'Normal')], default='normal')
    # requested_ids = fields.Many2many("hr.employee", string="Requested Persons")

    department_id = fields.Many2one('spare.department', string="Department")
    location_id = fields.Many2one('stock.location', string="Destination Location")
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.company, readonly=True)
    indent_date = fields.Datetime('Indent Date')
    required_date = fields.Datetime('Required Date')
    approve_date = fields.Datetime('Approve Date')
    requirement = fields.Selection([('1', 'Ordinary'), ('2', 'urgent')])
    type = fields.Selection([('stock', 'Stock')], default='stock')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', required=True, default=_get_default_warehouse)
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type', required=True,
                                      default=_get_default_picking_type, copy=False, domain="[('code', '=', 'internal'), ('company_id', '=', company_id)]")
    state = fields.Selection(
        [('draft', 'Draft'), ('external_stock_check', 'External Stock Check'), ('available', 'Available'), ('not_available', 'Not Available'),
         ('partially_available', 'Partially Available'), ('confirmed', 'Confirm'),
         ('waiting_approval', 'Waiting For Approval'),
         ('approved', 'Approved'), ('reject', 'Rejected'),
         ('inprogress', 'In Progress'),
         ('partially_issued', 'Partially Issued'),
         ('issued', 'Issued')], default='draft',
        copy=False, index=True, readonly=True)
    spare_request_line = fields.One2many('spare.request.lines', 'spare_request_id', string="Spare Request Lines")
    picking_ids = fields.Many2many('stock.picking', string="Picking")
    product_from = fields.Selection([('stock', 'Stock')], default='stock')
    parent_ticket_id = fields.Many2one('parent.ticket', string="Parent Ticket", readonly=True)
    child_ticket_id = fields.Many2one('child.ticket', string="Child Ticket", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Customer", copy=False)
    customer_account_id = fields.Many2one('res.partner', string="Customer Account", related='partner_id.customer_account_id')
    team_id = fields.Many2one('crm.team', 'Team', readonly=True)
    request_count = fields.Integer(string="Request Count", compute='compute_request_count')
    request_id = fields.Many2one('request', string="Request")


    # Smart Button - requests
    def action_view_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Request',
            'view_mode': 'tree,form',
            'res_model': 'request',
            'domain': [('spare_request_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_request_count(self):
        for record in self:
            record.request_count = self.env['request'].search_count([('spare_request_id', '=', self.id)])

    def action_check_availability(self):
        if not self.spare_request_line:
            raise ValidationError("Please Select Spare Products")
        if not sum(self.spare_request_line.mapped('product_uom_qty')) > 0.00:
            raise ValidationError("Please Enter Required Quantity for Spare Products")
        if self.spare_request_line:
            if all(x.qty_available >= x.product_uom_qty for x in self.spare_request_line):
                self.state = 'available'
            elif all(x.qty_available <= x.product_uom_qty for x in self.spare_request_line):
                self.state = 'not_available'
            else:
                self.state = 'partially_available'

    @api.depends('spare_request_line.state')
    def _compute_totals(self):
        for rec in self:
            rec.state_update = not rec.state_update

            if rec.spare_request_line and any(move.state == 'partial' for move in rec.spare_request_line):
                self.state = 'partially_issued'
            elif rec.spare_request_line and all(move.state == 'done' for move in rec.spare_request_line) and sum(rec.spare_request_line.mapped('product_uom_qty')) > 0.00:
                self.state = 'issued'
            else:
                print('')

    state_update = fields.Boolean(compute='_compute_totals', store=True)
    prepared_user_id = fields.Many2one('res.users', 'Prepared by', track_visibility='onchange', copy=False,
                                       default=lambda self: self.env.user.id)
    prepared_date = fields.Datetime('Prepared on', track_visibility='onchange', copy=False,
                                    default=lambda self: fields.datetime.now())
    is_send_for_approvals = fields.Boolean(string="Is Send for Approvals", copy=False, compute='_get_approval')
    approvals_count = fields.Integer(string='Approval Count', compute='_compute_approvals_count')

    def _get_approval(self):
        for record in self:
            record.is_send_for_approvals = False
            if record.sudo().parent_ticket_id:
                if record.sudo().parent_ticket_id.parent_configuration_id.is_approval_required_spares:
                    record.is_send_for_approvals = True
            if record.sudo().child_ticket_id:
                if record.sudo().child_ticket_id.child_configuration_id.is_approval_required_spares:
                    record.is_send_for_approvals = True

    def action_request_approval(self):
        requests = None
        if not self.spare_request_line:
            raise ValidationError("Please Select Spare Products")
        if not sum(self.spare_request_line.mapped('product_uom_qty')) > 0.00:
            raise ValidationError("Please Enter Required Quantity for Spare Products")
        if self.sudo().parent_ticket_id:
            if self.sudo().parent_ticket_id.parent_configuration_id.is_approval_required_spares and self.sudo().parent_ticket_id.parent_configuration_id.spares_approval_team_ids:
                approval_type_id = self.sudo().parent_ticket_id.parent_configuration_id.spares_approval_team_ids[-1].id
                request = {
                    'name': self.name,
                    'type_id': approval_type_id or False,
                    'spare_request_id': self.id,
                }
                requests = self.env['multi.approval'].create(request)
        else:
            if self.sudo().child_ticket_id.child_configuration_id.is_approval_required_spares and self.sudo().child_ticket_id.child_configuration_id.spares_approval_team_ids:
                approval_type_id = self.sudo().child_ticket_id.child_configuration_id.spares_approval_team_ids[-1].id
                request = {
                    'name': self.name,
                    'type_id': approval_type_id or False,
                    'spare_request_id': self.id,
                }
                requests = self.env['multi.approval'].create(request)
        if requests:
            requests.action_submit()
            action_id = self.env.ref('multi_level_approval.multi_approval_approval_action', raise_if_not_found=False)
            template_id = self.env.ref('spare_request.spare_mail_template_notify_approvers')
            base_url = '/web#id=%d&action=%r&model=multi.approval&view_type=form' % (requests.id, action_id.id)
            mail = ''
            for lines in requests.line_ids:
                mail = lines.user_id.mapped('login')
                break
            if template_id:
                template_id.with_context(rec_url=base_url, email_to=mail).sudo().send_mail(requests.id, force_send=True)
            self.state ='waiting_approval'
        return True

    def action_view_approvals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send for Approvals',
            'view_mode': 'tree,form',
            'res_model': 'multi.approval',
            'domain': [('spare_request_id', '=', self.id)],
            'context': "{'create': False}"
        }
    
    def _compute_approvals_count(self):
        for record in self:
            record.approvals_count = self.env['multi.approval'].search_count([('spare_request_id', '=', record.id)])

    @api.model
    def create(self, values):
        rec = super(SpareRequest, self).create(values)
        rec.name = self.env['ir.sequence'].next_by_code('spare.request.seq') or _('New')
        task_id = self.env.ref('spare_request.task_data_spare_request')
        # PT
        if rec.parent_ticket_id:
            rec.parent_ticket_id.update({
                'task_list_ids': [(0, 0, {'task_id': task_id.id})],
            })

        # CT
        if rec.child_ticket_id:
            rec.child_ticket_id.update({
                'task_list_ids': [(0, 0, {'task_id': task_id.id})],
            })
        return rec
    
    def write(self, values):
        result = super(SpareRequest, self).write(values)
        task_id = None
        last_task_id = []
        pt_task_ids = self.parent_ticket_id.task_list_ids.mapped("task_id")
        for pt_task in pt_task_ids:
            last_task_id.append(pt_task.id)
        last_id = last_task_id.pop() if last_task_id else None
        if 'state' in values and self.parent_ticket_id or self.child_ticket_id:
            # if self.state in ['draft']:
            #     task_id = self.env.ref('spare_request.task_data_spare_request')
            if self.state in ['available']:
                task_id = self.env.ref('spare_request.task_data_spare_available')
            elif self.state in ['not_available']:
                task_id = self.env.ref('spare_request.task_data_spare_not_available')
            elif self.state in ['partially_available']:
                task_id = self.env.ref('spare_request.task_data_spare_partially_available')
                
            elif self.state in ['waiting_approval']:
                task_id = self.env.ref('spare_request.task_data_spare_delivery_requested')
            elif self.state in ['approved']:
                task_id = self.env.ref('spare_request.task_data_spare_delivery_approved')
            elif self.state in ['reject']:
                task_id = self.env.ref('spare_request.task_data_spare_delivery_rejected')
            elif self.state in ['issued']:
                task_id = self.env.ref('spare_request.task_data_spare_parts_received')
                template_id = self.env.ref('spare_request.mail_template_spare_released')
                product_part = self.parent_ticket_id.product_id.product_tmpl_id.product_part
                if template_id:
                    template_id.with_context( product_part=product_part).sudo().send_mail(self.id, force_send=True)
            if task_id and not task_id.id == last_id and self.parent_ticket_id and not self.child_ticket_id:
                self.parent_ticket_id.sudo().update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })
            # CT Task Update
            ct_last_task_id = []
            ct_task_ids = self.child_ticket_id.task_list_ids.mapped("task_id")
            for ct_task in ct_task_ids:
                ct_last_task_id.append(ct_task.id)
            ct_last_id = ct_last_task_id.pop() if ct_last_task_id else None
            if task_id and not task_id.id == ct_last_id and self.child_ticket_id:
                self.child_ticket_id.sudo().update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })
            
            # PT Configuration Notification
            if self.parent_ticket_id.parent_configuration_id and self.parent_ticket_id.parent_configuration_id.is_spares:
                email = ''
                approver_email = ''
                send = False
                if self.parent_ticket_id.parent_configuration_id.alert_spares == 'confirm' and self.state == 'confirmed':
                    send = True
                elif self.parent_ticket_id.parent_configuration_id.alert_spares == 'done' and self.state == 'issued':
                    send = True
                elif self.parent_ticket_id.parent_configuration_id.alert_spares == 'both' and self.state in ['confirmed', 'issued']:
                    send = True
                    
                team_alert_template_id = self.parent_ticket_id.parent_configuration_id.alert_spares_email_template_id
                customer_template_id = self.parent_ticket_id.parent_configuration_id.spares_cust_email_template_id
                if team_alert_template_id and send:
                    teams = self.env['hr.employee'].sudo().search([('job_id', 'in',self.parent_ticket_id.parent_configuration_id.alert_spares_approval_team_ids.ids)]).mapped('work_email')
                    email += ', '.join(teams)
                    team_alert_template_id.with_context(email_to=email).sudo().send_mail(self.parent_ticket_id.id, force_send=True)
                if customer_template_id and send:
                    customer_email = ",".join([str(self.parent_ticket_id.customer_account_id.email), str(self.parent_ticket_id.partner_id.email)])
                    customer_template_id.with_context(email_to=customer_email).sudo().send_mail(self.parent_ticket_id.id, force_send=True)
                if team_alert_template_id and self.parent_ticket_id.parent_configuration_id.is_approval_required_spares and send:
                    for teams in self.parent_ticket_id.parent_configuration_id.spares_approval_team_ids:
                        teams = teams.mapped('line_ids.user_id.login')
                        approver_email += ', '.join(teams)
                    team_alert_template_id.with_context(email_to=approver_email).sudo().send_mail(self.parent_ticket_id.id, force_send=True)
            # CT Configuration Notification
            if self.child_ticket_id.child_configuration_id and self.child_ticket_id.child_configuration_id.is_spares:
                email = ''
                approver_email = ''
                send = False
                if self.child_ticket_id.child_configuration_id.alert_spares == 'confirm' and self.state == 'confirmed':
                    send = True
                elif self.child_ticket_id.child_configuration_id.alert_spares == 'done' and self.state == 'issued':
                    send = True
                elif self.child_ticket_id.child_configuration_id.alert_spares == 'both' and self.state in ['confirmed', 'issued']:
                    send = True
                    
                team_alert_template_id = self.child_ticket_id.child_configuration_id.alert_spares_email_template_id
                customer_template_id = self.child_ticket_id.child_configuration_id.spares_cust_email_template_id
                if team_alert_template_id and send:
                    teams = self.env['hr.employee'].sudo().search([('job_id', 'in',self.child_ticket_id.child_configuration_id.alert_spares_approval_team_ids.ids)]).mapped('work_email')
                    email += ', '.join(teams)
                    team_alert_template_id.with_context(email_to=email).sudo().send_mail(self.child_ticket_id.id, force_send=True)
                if customer_template_id and send:
                    customer_email = ",".join([str(self.child_ticket_id.customer_account_id.email), str(self.child_ticket_id.partner_id.email)])
                    customer_template_id.with_context(email_to=customer_email).sudo().send_mail(self.child_ticket_id.id, force_send=True)
                if team_alert_template_id and self.child_ticket_id.child_configuration_id.is_approval_required_spares and self.state == 'waiting_approval':
                    for teams in self.child_ticket_id.child_configuration_id.spares_approval_team_ids:
                        teams = teams.mapped('line_ids.user_id.login')
                        approver_email += ', '.join(teams)
                    team_alert_template_id.with_context(email_to=approver_email).sudo().send_mail(self.child_ticket_id.id, force_send=True)

        # stop
        return result

    def action_confirm(self):
        if not self.spare_request_line:
            raise ValidationError("Please Select Spare Products")
        if not sum(self.spare_request_line.mapped('product_uom_qty')) > 0.00:
            raise ValidationError("Please Enter Required Quantity for Spare Products")
        self.state = 'confirmed'

    def action_approve(self):
        move_lines = []
        if not self.spare_request_line:
            raise ValidationError("Please Select Spare Products")
        if not sum(self.spare_request_line.mapped('product_uom_qty')) > 0.00:
            raise ValidationError("Please Enter Required Quantity for Spare Products")
        for lines in self.spare_request_line:
            move_vals = {}
            move_vals.update({
                'product_id': lines.product_id.id,
                'product_uom_qty': lines.product_uom_qty,
                'product_uom': lines.product_uom_id.id,
                'name': lines.product_id.default_code or lines.product_id.name,
                'location_id': self.picking_type_id.default_location_src_id.id,
                'location_dest_id': self.picking_type_id.default_location_dest_id.id,
                'spare_request_line_id': lines.id
            })
            move_lines.append((0, 0, move_vals))
        values = {
            'location_id': self.picking_type_id.default_location_src_id.id,
            'location_dest_id': self.picking_type_id.default_location_dest_id.id,
            'picking_type_id': self.picking_type_id.id,
            'move_type': 'one',
            'move_ids': move_lines,
            'spare_request': self.id,
            'origin': self.name,
            'state': 'draft',
        }
        if move_lines:
            stock_id = self.env['stock.picking'].create(values)
            stock_id.action_confirm()
            if stock_id and self.parent_ticket_id:
                template_id_pi = self.env.ref('spare_request.mail_template_spare_request_created')
                if template_id_pi:
                    template_id_pi.sudo().send_mail(self.id, force_send=True)
            self.picking_ids = [(6, 0, stock_id.ids)]
            # lines.picking_id = stock_id.id
        self.approve_date = datetime.now()
        self.state = 'inprogress'

    def action_reject(self):
        self.state = 'reject'

    def action_issue_products(self):
        tree_id = self.env.ref('stock.vpicktree').id
        form_id = self.env.ref('stock.view_picking_form').id
        return {
            'name': _('Internal Transfers'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'stock.picking',
            'view_id': tree_id,
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'type': 'ir.actions.act_window',
            'domain': [('spare_request', '=', self.id)],
        }

    transfer_count = fields.Integer(compute='_compute_transfer_count', default=0, string='Transfer Count')

    def _compute_transfer_count(self):
        picking = self.env['stock.picking'].search([('spare_request', '=', self.id)])
        if picking:
            for trf in picking:
                self.transfer_count = len(picking.ids)
        if not picking:
            self.transfer_count = 0

    def show_quality_checks(self):
        tree_id = self.env.ref('stock.vpicktree').id
        form_id = self.env.ref('stock.view_picking_form').id
        return {
            'name': _('Internal Transfers'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'stock.picking',
            'view_id': tree_id,
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'type': 'ir.actions.act_window',
            'domain': [('spare_request', '=', self.id)],
        }


class SpareRequestLines(models.Model):
    _name = 'spare.request.lines'
    _description = 'Spare Request Lines'

    # def _get_default_location_id(self):
    #     company_id = self.env.context.get('default_company_id') or self.env.company.id
    #     warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
    #     if warehouse:
    #         return warehouse.lot_stock_id.id
    #     return None

    name = fields.Text('Purpose')
    description = fields.Char(string="Description")
    product_id = fields.Many2one('product.product', string="Product", required=True)
    # required_on = fields.Date('Required On', required=True)
    product_uom_qty = fields.Float('Required Qty', required=True)
    product_uom_id = fields.Many2one('uom.uom', string="UOM", required=True)
    product_uom_qty_issued = fields.Float('Issued Qty', readonly=True)
    remaining_qty = fields.Float("Remaining Qty", compute='_compute_remaining_qty')
    qty_available = fields.Float('Available Qty', compute='_show_stock_qty')
    remarks = fields.Char('Remarks')
    spare_request_id = fields.Many2one('spare.request', string="Spare Request")
    state = fields.Selection([('draft', 'Draft'),
                              ('partial', 'Partially Delivered'),
                              ('done', 'Done')],
                             compute='_get_state', default='draft', copy=False, readonly=True)
    source_location_id = fields.Many2one("stock.location", string="Source", domain=[('usage', '=', 'internal')], related='spare_request_id.picking_type_id.default_location_src_id')
    destination_location_id = fields.Many2one("stock.location", string="Destination",
                                              domain=[('usage', '=', 'internal')], required=True, related='spare_request_id.picking_type_id.default_location_dest_id')
    picking_id = fields.Many2one("stock.picking", string="Picking ID")

    @api.depends('remaining_qty')
    def _get_state(self):
        for rec in self:
            if rec.remaining_qty == 0 and rec.product_uom_qty_issued == rec.product_uom_qty:
                rec.update({
                    'state': 'done',
                })
            elif rec.remaining_qty == rec.product_uom_qty:
                rec.update({
                    'state': 'draft',
                })
            else:
                rec.update({
                    'state': 'partial',
                })

    @api.depends('product_uom_qty_issued')
    def _compute_remaining_qty(self):
        for rec in self:
            rec.update({
                'remaining_qty': rec.product_uom_qty - rec.product_uom_qty_issued,
            })

    @api.depends('product_id','source_location_id')
    def _show_stock_qty(self):
        for rec in self:
            stock_qty = self.env['stock.quant'].search([('location_id', '=', rec.source_location_id.id), ('product_id', '=', rec.product_id.id)])
            if rec.product_id:
                rec.update({
                    'qty_available': sum(stock_qty.mapped('available_quantity')),
                    'product_uom_id': rec.product_id.uom_id.id
                })
            else:
                rec.qty_available = 0.0


class MultiApproval(models.Model):
    _inherit = 'multi.approval'
    
    spare_request_id = fields.Many2one('spare.request', string="Spare Request", copy=False)
    
    def action_approve(self):
        values = super(MultiApproval, self).action_approve()
        sp_id = self.env['spare.request'].sudo().search([('id', '=', self.spare_request_id.id)])
        if all(x.state == 'Approved' for x in self.line_ids):
            sp_id.state = 'approved'
        return values
    
    def action_refuse(self, reason=''):
        values = super(MultiApproval, self).action_refuse(reason='')
        sp_id = self.env['spare.request'].sudo().search([('id', '=', self.spare_request_id.id)])
        if all(x.state == 'Refused' for x in self.line_ids):
            sp_id.state = 'reject'
        return values
