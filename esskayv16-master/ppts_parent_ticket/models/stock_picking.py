from odoo import SUPERUSER_ID, _, api, fields, models
from collections import defaultdict


class StockPicking(models.Model):
    _inherit = "stock.picking"

    parent_id = fields.Many2one('parent.ticket', string='Parent Ticket',
                                help='This is field is the refernce and show the related pickings in parent ticket.')
    parent_ticket_id = fields.Many2one('parent.ticket', string="Parent Ticket ID")
    child_ticket_id = fields.Many2one('child.ticket', string="Child Ticket ID")
    is_inward_transfer = fields.Boolean('Inward Transfer', help='This field determines that this is inward transfer')
    is_outward_transfer = fields.Boolean('Outward Transfer', help='This field determines that this is outward transfer')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('waiting_for_approval', 'Waiting For Approval'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")
    is_send_for_approvals = fields.Boolean(string="Is Send for Approvals", copy=False, compute='_get_approval')
    is_approval = fields.Boolean(string="Is Approval", copy=False, compute='approval_status')
    approvals_count = fields.Integer(string='Approval Count', compute='_compute_approvals_count')
    customer_dispatched_date = fields.Datetime(string='Customer Dispatched Date')
    customer_received_date = fields.Datetime(string='Customer Received Date')

    



    @api.depends('move_type', 'immediate_transfer', 'move_ids.state', 'move_ids.picking_id')
    def _compute_state(self):
        ''' State of a picking depends on the state of its related stock.move
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
        '''
        picking_moves_state_map = defaultdict(dict)
        picking_move_lines = defaultdict(set)
        for move in self.env['stock.move'].search([('picking_id', 'in', self.ids)]):
            picking_id = move.picking_id
            move_state = move.state
            picking_moves_state_map[picking_id.id].update({
                'any_draft': picking_moves_state_map[picking_id.id].get('any_draft', False) or move_state == 'draft',
                'all_cancel': picking_moves_state_map[picking_id.id].get('all_cancel', True) and move_state == 'cancel',
                'all_cancel_done': picking_moves_state_map[picking_id.id].get('all_cancel_done',
                                                                              True) and move_state in (
                                       'cancel', 'done'),
                'all_done_are_scrapped': picking_moves_state_map[picking_id.id].get('all_done_are_scrapped', True) and (
                    move.scrapped if move_state == 'done' else True),
                'any_cancel_and_not_scrapped': picking_moves_state_map[picking_id.id].get('any_cancel_and_not_scrapped',
                                                                                          False) or (
                                                       move_state == 'cancel' and not move.scrapped),
            })
            picking_move_lines[picking_id.id].add(move.id)
        for picking in self:
            picking_id = (picking.ids and picking.ids[0]) or picking.id
            if not picking_moves_state_map[picking_id]:
                picking.state = 'draft'
            elif picking_moves_state_map[picking_id]['any_draft']:
                picking.state = 'draft'
            elif picking_moves_state_map[picking_id]['all_cancel']:
                picking.state = 'cancel'
            elif picking_moves_state_map[picking_id]['all_cancel_done']:
                if picking_moves_state_map[picking_id]['all_done_are_scrapped'] and picking_moves_state_map[picking_id][
                    'any_cancel_and_not_scrapped']:
                    picking.state = 'cancel'
                else:
                    picking.state = 'done'
            else:
                relevant_move_state = self.env['stock.move'].browse(
                    picking_move_lines[picking_id])._get_relevant_state_among_moves()
                if picking.immediate_transfer and relevant_move_state not in ('draft', 'cancel', 'done'):
                    picking.state = 'assigned' if picking.is_approval == False else 'waiting_for_approval'
                elif relevant_move_state == 'partially_available':
                    picking.state = 'assigned' if picking.is_approval == False else 'waiting_for_approval'
                else:
                    picking.state = relevant_move_state if not picking.is_approval else 'waiting_for_approval'

    # @api.depends('is_send_for_approvals')
    def approval_status(self):
        for record in self:
            approval_ids = self.env["multi.approval"].search([('stock_id', '=', record.id)])
            if record.is_send_for_approvals and approval_ids and all(x.state == 'Approved' for x in approval_ids):
                record.is_approval = False
            elif not record.is_send_for_approvals:
                record.is_approval = False
            else:
                record.is_approval = True
            record._compute_state()

    def action_view_approvals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send for Approvals',
            'view_mode': 'tree,form',
            'res_model': 'multi.approval',
            'domain': [('stock_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def _compute_approvals_count(self):
        for record in self:
            record.approvals_count = self.env['multi.approval'].search_count([('stock_id', '=', record.id)])

    def _get_approval(self):
        for record in self:
            record.is_send_for_approvals = False
            if record.sudo().child_ticket_id:
                if record.sudo().child_ticket_id.child_configuration_id.is_approval_required_delivery and record.picking_type_id.code == 'outgoing':
                    record.is_send_for_approvals = True

    def action_request_approval(self):
        if self.sudo().child_ticket_id:
            if self.sudo().child_ticket_id.child_configuration_id.is_approval_required_delivery and self.sudo().child_ticket_id.child_configuration_id.sudo().delivery_approval_team_ids:
                approval_type_id = self.sudo().child_ticket_id.child_configuration_id.sudo().delivery_approval_team_ids[
                    -1].id
                request = {
                    'name': self.name,
                    'type_id': approval_type_id or False,
                    'stock_id': self.id,
                }
                requests = self.env['multi.approval'].sudo().create(request)
                requests.action_submit()
                # self.maintenance_state = 'waiting_for_approval'
        return True

    def action_call_notification(self):
        # Parent Ticket Configuration Notification
        if self.parent_ticket_id and self.parent_ticket_id.parent_configuration_id.is_inward_receipts and self.is_return:
            self.action_notification_receipts_parent()
        if self.parent_ticket_id and self.parent_ticket_id.parent_configuration_id.is_outward_delivery_order and self.parent_ticket_id.parent_configuration_id.delivery_operation_type_id.id == self.picking_type_id.id:
            self.action_notification_delivery_parent()
        if self.parent_ticket_id and self.parent_ticket_id.parent_configuration_id.is_material_movement and \
                self.parent_ticket_id.parent_configuration_id.transfer_operation_type_ids[
                    -1].id == self.picking_type_id.id:
            self.action_notification_transfer_parent()
        # Child Ticket Configuration Notification
        if self.child_ticket_id and self.child_ticket_id.child_configuration_id.is_inward_receipts and self.is_return:
            self.action_notification_receipts_child()
        if self.child_ticket_id and self.child_ticket_id.child_configuration_id.is_outward_delivery_order and self.child_ticket_id.child_configuration_id.delivery_operation_type_id.id == self.picking_type_id.id:
            self.action_notification_delivery_child()
        if self.child_ticket_id and self.child_ticket_id.child_configuration_id.is_material_movement and \
                self.child_ticket_id.child_configuration_id.transfer_operation_type_ids[
                    -1].id == self.picking_type_id.id:
            self.action_notification_transfer_child()

    def action_confirm(self):
        res = super().action_confirm()
        self.action_call_notification()
        return res

    def action_assign(self):
        res = super().action_assign()
        self.action_call_notification()
        return res

    def button_validate(self):
        res = super().button_validate()
        self.action_call_notification()
        return res

    # Child Ticket Configuration Notification
    def action_notification_receipts_child(self):
        email = ''
        send = False
        if self.child_ticket_id.child_configuration_id.alert_receipts == 'waiting' and self.state == 'assigned':
            send = True
        elif self.child_ticket_id.child_configuration_id.alert_receipts == 'done' and self.state == 'done':
            send = True
        elif self.child_ticket_id.child_configuration_id.alert_receipts == 'both' and self.state in ['assigned',
                                                                                                     'done']:
            send = True
        team_alert_template_id = self.child_ticket_id.child_configuration_id.receipts_email_template_id
        customer_template_id = self.child_ticket_id.child_configuration_id.receipts_cust_email_template_id
        if team_alert_template_id and send:
            teams = self.env['hr.employee'].search(
                [('job_id', 'in', self.child_ticket_id.child_configuration_id.receipts_approval_team_ids.ids)]).mapped(
                'work_email')
            email += ', '.join(teams)
            team_alert_template_id.with_context(email_to=email).sudo().send_mail(self.child_ticket_id.id,
                                                                                 force_send=True)
        if customer_template_id and send:
            customer_email = ",".join(
                [str(self.child_ticket_id.customer_account_id.email), str(self.child_ticket_id.partner_id.email)])
            customer_template_id.with_context(email_to=customer_email).sudo().send_mail(self.child_ticket_id.id,
                                                                                        force_send=True)

    def action_notification_delivery_child(self):
        email = ''
        send = False
        if self.child_ticket_id.child_configuration_id.alert_delivery == 'waiting' and self.state == 'assigned':
            send = True
        elif self.child_ticket_id.child_configuration_id.alert_delivery == 'done' and self.state == 'done':
            send = True
        elif self.child_ticket_id.child_configuration_id.alert_delivery == 'both' and self.state in ['assigned',
                                                                                                     'done']:
            send = True
        team_alert_template_id = self.child_ticket_id.child_configuration_id.delivery_email_template_id
        customer_template_id = self.child_ticket_id.child_configuration_id.delivery_cust_email_template_id
        if team_alert_template_id and send:
            teams = self.env['hr.employee'].search(
                [('job_id', 'in', self.child_ticket_id.child_configuration_id.delivery_approval_team_ids.ids)]).mapped(
                'work_email')
            email += ', '.join(teams)
            team_alert_template_id.with_context(email_to=email).sudo().send_mail(self.child_ticket_id.id,
                                                                                 force_send=True)
        if customer_template_id and send:
            customer_email = ",".join(
                [str(self.child_ticket_id.customer_account_id.email), str(self.child_ticket_id.partner_id.email)])
            customer_template_id.with_context(email_to=customer_email).sudo().send_mail(self.child_ticket_id.id,
                                                                                        force_send=True)

    def action_notification_transfer_child(self):
        email = ''
        send = False
        if self.child_ticket_id.child_configuration_id.alert_transfer == 'waiting' and self.state == 'assigned':
            send = True
        elif self.child_ticket_id.child_configuration_id.alert_transfer == 'done' and self.state == 'done':
            send = True
        elif self.child_ticket_id.child_configuration_id.alert_transfer == 'both' and self.state in ['assigned',
                                                                                                     'done']:
            send = True
        team_alert_template_id = self.child_ticket_id.child_configuration_id.transfer_email_template_id
        customer_template_id = self.child_ticket_id.child_configuration_id.transfer_cust_email_template_id
        if team_alert_template_id and send:
            teams = self.env['hr.employee'].search(
                [('job_id', 'in', self.child_ticket_id.child_configuration_id.transfer_approval_team_ids.ids)]).mapped(
                'work_email')
            email += ', '.join(teams)
            team_alert_template_id.with_context(email_to=email).sudo().send_mail(self.child_ticket_id.id,
                                                                                 force_send=True)
        if customer_template_id and send:
            customer_email = ",".join(
                [str(self.child_ticket_id.customer_account_id.email), str(self.child_ticket_id.partner_id.email)])
            customer_template_id.with_context(email_to=customer_email).sudo().send_mail(self.child_ticket_id.id,
                                                                                        force_send=True)

    # Child Ticket Configuration Notification Ends

    # Parent Ticket Configuration Notification
    def action_notification_receipts_parent(self):
        email = ''
        send = False
        if self.parent_ticket_id.parent_configuration_id.alert_receipts == 'waiting' and self.state == 'assigned':
            send = True
        elif self.parent_ticket_id.parent_configuration_id.alert_receipts == 'done' and self.state == 'done':
            send = True
        elif self.parent_ticket_id.parent_configuration_id.alert_receipts == 'both' and self.state in ['assigned',
                                                                                                       'done']:
            send = True
        team_alert_template_id = self.parent_ticket_id.parent_configuration_id.receipts_email_template_id
        customer_template_id = self.parent_ticket_id.parent_configuration_id.receipts_cust_email_template_id
        if team_alert_template_id and send:
            teams = self.env['hr.employee'].search(
                [(
                    'job_id', 'in',
                    self.parent_ticket_id.parent_configuration_id.receipts_approval_team_ids.ids)]).mapped(
                'work_email')
            email += ', '.join(teams)
            team_alert_template_id.with_context(email_to=email).sudo().send_mail(self.parent_ticket_id.id,
                                                                                 force_send=True)
        if customer_template_id and send:
            customer_email = ",".join(
                [str(self.parent_ticket_id.customer_account_id.email), str(self.parent_ticket_id.partner_id.email)])
            customer_template_id.with_context(email_to=customer_email).sudo().send_mail(self.parent_ticket_id.id,
                                                                                        force_send=True)

    def action_notification_delivery_parent(self):
        email = ''
        send = False
        if self.parent_ticket_id.parent_configuration_id.alert_delivery == 'waiting' and self.state == 'assigned':
            send = True
        elif self.parent_ticket_id.parent_configuration_id.alert_delivery == 'done' and self.state == 'done':
            send = True
        elif self.parent_ticket_id.parent_configuration_id.alert_delivery == 'both' and self.state in ['assigned',
                                                                                                       'done']:
            send = True
        team_alert_template_id = self.parent_ticket_id.parent_configuration_id.delivery_email_template_id
        customer_template_id = self.parent_ticket_id.parent_configuration_id.delivery_cust_email_template_id
        if team_alert_template_id and send:
            teams = self.env['hr.employee'].search(
                [(
                    'job_id', 'in',
                    self.parent_ticket_id.parent_configuration_id.delivery_approval_team_ids.ids)]).mapped(
                'work_email')
            email += ', '.join(teams)
            team_alert_template_id.with_context(email_to=email).sudo().send_mail(self.parent_ticket_id.id,
                                                                                 force_send=True)
        if customer_template_id and send:
            customer_email = ",".join(
                [str(self.parent_ticket_id.customer_account_id.email), str(self.parent_ticket_id.partner_id.email)])
            customer_template_id.with_context(email_to=customer_email).sudo().send_mail(self.parent_ticket_id.id,
                                                                                        force_send=True)

    def action_notification_transfer_parent(self):
        email = ''
        send = False
        if self.parent_ticket_id.parent_configuration_id.alert_transfer == 'waiting' and self.state == 'assigned':
            send = True
        elif self.parent_ticket_id.parent_configuration_id.alert_transfer == 'done' and self.state == 'done':
            send = True
        elif self.parent_ticket_id.parent_configuration_id.alert_transfer == 'both' and self.state in ['assigned',
                                                                                                       'done']:
            send = True
        team_alert_template_id = self.parent_ticket_id.parent_configuration_id.transfer_email_template_id
        customer_template_id = self.parent_ticket_id.parent_configuration_id.transfer_cust_email_template_id
        if team_alert_template_id and send:
            teams = self.env['hr.employee'].search(
                [(
                    'job_id', 'in',
                    self.parent_ticket_id.parent_configuration_id.transfer_approval_team_ids.ids)]).mapped(
                'work_email')
            email += ', '.join(teams)
            team_alert_template_id.with_context(email_to=email).sudo().send_mail(self.parent_ticket_id.id,
                                                                                 force_send=True)
        if customer_template_id and send:
            customer_email = ",".join(
                [str(self.parent_ticket_id.customer_account_id.email), str(self.parent_ticket_id.partner_id.email)])
            customer_template_id.with_context(email_to=customer_email).sudo().send_mail(self.parent_ticket_id.id,
                                                                                        force_send=True)
    # Parent Ticket Configuration Notification Ends


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # This Function Pass Stock Lot based on CT and PT
    @api.model_create_multi
    def create(self, vals):
        result = super(StockMoveLine, self).create(vals)
        # if result.picking_id and result.picking_id.child_ticket_id and result.picking_id.picking_type_id.code == "outgoing" and result.picking_id.sale_id.is_replacement_order:
        #     lot = self.env['stock.lot'].search([('name', '=',  result.picking_id.sale_id.product_serial_number)], limit=1)
        #     result.lot_id = lot.id
        #     result.lot_name = lot.name
        if result.picking_id and result.picking_id.child_ticket_id and result.picking_id.picking_type_id.code != "outgoing" and not result.picking_id.sale_id.is_replacement_order and not result.picking_id.spare_request:
            result.lot_id = result.picking_id.child_ticket_id.stock_lot_id.id
            result.lot_name = result.picking_id.child_ticket_id.stock_lot_id.name
        return result
