from odoo import SUPERUSER_ID, _, api, fields, models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    parent_id = fields.Many2one('parent.ticket', string='Parent Ticket', help='This is field is the refernce and show the related pickings in parent ticket.')
    parent_ticket_id = fields.Many2one('parent.ticket', string="Parent Ticket ID")
    child_ticket_id = fields.Many2one('child.ticket', string="Child Ticket ID")
    is_inward_transfer = fields.Boolean('Inward Transfer', help='This field determines that this is inward transfer')
    is_outward_transfer = fields.Boolean('Outward Transfer', help='This field determines that this is outward transfer')

    def action_call_notification(self):
        # Parent Ticket Configuration Notification
        if self.parent_ticket_id and self.parent_ticket_id.parent_configuration_id.is_inward_receipts and self.is_return:
            self.action_notification_receipts_parent()
        if self.parent_ticket_id and self.parent_ticket_id.parent_configuration_id.is_outward_delivery_order and self.parent_ticket_id.parent_configuration_id.delivery_operation_type_id.id == self.picking_type_id.id :
            self.action_notification_delivery_parent()
        if self.parent_ticket_id and self.parent_ticket_id.parent_configuration_id.is_material_movement and self.parent_ticket_id.parent_configuration_id.transfer_operation_type_ids[-1].id == self.picking_type_id.id :
            self.action_notification_transfer_parent()
        # Child Ticket Configuration Notification
        if self.child_ticket_id and self.child_ticket_id.child_configuration_id.is_inward_receipts and self.is_return:
            self.action_notification_receipts_child()
        if self.child_ticket_id and self.child_ticket_id.child_configuration_id.is_outward_delivery_order and self.child_ticket_id.child_configuration_id.delivery_operation_type_id.id == self.picking_type_id.id :
            self.action_notification_delivery_child()
        if self.child_ticket_id and self.child_ticket_id.child_configuration_id.is_material_movement and self.child_ticket_id.child_configuration_id.transfer_operation_type_ids[-1].id == self.picking_type_id.id :
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
        elif self.child_ticket_id.child_configuration_id.alert_receipts == 'both' and self.state in ['assigned','done']:
            send = True
        team_alert_template_id = self.child_ticket_id.child_configuration_id.receipts_email_template_id
        customer_template_id = self.child_ticket_id.child_configuration_id.receipts_cust_email_template_id
        if team_alert_template_id and send:
            teams = self.env['hr.employee'].search([('job_id', 'in',self.child_ticket_id.child_configuration_id.receipts_approval_team_ids.ids)]).mapped('work_email')
            email += ', '.join(teams)
            team_alert_template_id.with_context(email_to=email).sudo().send_mail(self.child_ticket_id.id, force_send=True)
        if customer_template_id and send:
            customer_email = ",".join(
                [str(self.child_ticket_id.customer_account_id.email), str(self.child_ticket_id.partner_id.email)])
            customer_template_id.with_context(email_to=customer_email).sudo().send_mail(self.child_ticket_id.id, force_send=True)

    def action_notification_delivery_child(self):
        email = ''
        send = False
        if self.child_ticket_id.child_configuration_id.alert_delivery == 'waiting' and self.state == 'assigned':
            send = True
        elif self.child_ticket_id.child_configuration_id.alert_delivery == 'done' and self.state == 'done':
            send = True
        elif self.child_ticket_id.child_configuration_id.alert_delivery == 'both' and self.state in ['assigned','done']:
            send = True
        team_alert_template_id = self.child_ticket_id.child_configuration_id.delivery_email_template_id
        customer_template_id = self.child_ticket_id.child_configuration_id.delivery_cust_email_template_id
        if team_alert_template_id and send:
            teams = self.env['hr.employee'].search([('job_id', 'in',self.child_ticket_id.child_configuration_id.delivery_approval_team_ids.ids)]).mapped('work_email')
            email += ', '.join(teams)
            team_alert_template_id.with_context(email_to=email).sudo().send_mail(self.child_ticket_id.id, force_send=True)
        if customer_template_id and send:
            customer_email = ",".join(
                [str(self.child_ticket_id.customer_account_id.email), str(self.child_ticket_id.partner_id.email)])
            customer_template_id.with_context(email_to=customer_email).sudo().send_mail(self.child_ticket_id.id, force_send=True)

    def action_notification_transfer_child(self):
        email = ''
        send = False
        if self.child_ticket_id.child_configuration_id.alert_transfer == 'waiting' and self.state == 'assigned':
            send = True
        elif self.child_ticket_id.child_configuration_id.alert_transfer == 'done' and self.state == 'done':
            send = True
        elif self.child_ticket_id.child_configuration_id.alert_transfer == 'both' and self.state in ['assigned','done']:
            send = True
        team_alert_template_id = self.child_ticket_id.child_configuration_id.transfer_email_template_id
        customer_template_id = self.child_ticket_id.child_configuration_id.transfer_cust_email_template_id
        if team_alert_template_id and send:
            teams = self.env['hr.employee'].search([('job_id', 'in',self.child_ticket_id.child_configuration_id.transfer_approval_team_ids.ids)]).mapped('work_email')
            email += ', '.join(teams)
            team_alert_template_id.with_context(email_to=email).sudo().send_mail(self.child_ticket_id.id, force_send=True)
        if customer_template_id and send:
            customer_email = ",".join(
                [str(self.child_ticket_id.customer_account_id.email), str(self.child_ticket_id.partner_id.email)])
            customer_template_id.with_context(email_to=customer_email).sudo().send_mail(self.child_ticket_id.id, force_send=True)
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
                [('job_id', 'in', self.parent_ticket_id.parent_configuration_id.receipts_approval_team_ids.ids)]).mapped(
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
                [('job_id', 'in', self.parent_ticket_id.parent_configuration_id.delivery_approval_team_ids.ids)]).mapped(
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
                [('job_id', 'in', self.parent_ticket_id.parent_configuration_id.transfer_approval_team_ids.ids)]).mapped(
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
        if result.picking_id and result.picking_id.child_ticket_id and result.picking_id.picking_type_id.code != "outgoing" and not result.picking_id.sale_id.is_replacement_order:
            result.lot_id = result.picking_id.child_ticket_id.stock_lot_id.id
            result.lot_name = result.picking_id.child_ticket_id.stock_lot_id.name
        return result
