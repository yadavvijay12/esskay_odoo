from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError, ValidationError


class WarrantyReplacement(models.Model):
    _inherit = 'sale.order'

    is_replacement_order = fields.Boolean('Is Replacement Order', help='Segregate Replacement Orders')
    wr_process_alias_id = fields.Char(string="WR Process ID Alias", copy=False)
    wr_install_start_date = fields.Date(string="WR Installation Start date", copy=False,
                                        default=fields.Date.context_today)
    wr_install_end_date = fields.Date(string="WR Installation End date", copy=False, default=fields.Date.context_today)
    reported_fault = fields.Char(string="Reported Fault", copy=False)
    parent_ticket_id = fields.Many2one('parent.ticket', string="Parent Ticket ID", copy=False)
    child_ticket_id = fields.Many2one('child.ticket', string="Child Ticket ID", copy=False)
    external_reference = fields.Char(string="External Reference")
    service_category_id = fields.Many2one('service.category', string="Service Category", copy=False)
    service_type_id = fields.Many2one('service.type', string="Service Type", copy=False)
    child_ticket_type_id = fields.Many2one('child.ticket.type', string="Child Ticket Type", copy=False)
    categ_id = fields.Many2one('product.category', 'Product Categories', copy=False)
    customer_account_id = fields.Many2one('res.partner', string="Customer Account",
                                          related='partner_id.customer_account_id')
    install_status = fields.Selection([('new', 'New'), ('done', 'Done')], string="Installation Status")
    team_id = fields.Many2one('crm.team', string='Team', copy=False)
    worksheet_id = fields.Many2one('survey.survey', string="Worksheet", copy=False)
    wr_properties_definition = fields.Properties('WR Ticket Properties',
                                                 definition='partner_id.service_ticket_properties', copy=True)
    image_1920 = fields.Image("Image", copy=False)
    wr_state = fields.Selection(
        [('new', 'New'), ('asset_updated', 'Asset Details Updated'), ('start', 'WR Delivery Started'),
         ('in_progress', 'WR Delivery In Progress'),
         ('waiting_for_approval', 'Waiting For Approval'), ('on_hold', 'WR Delivery Onhold'),
         ('approved', 'Approved'), ('rejected', 'Rejected'), ('completed', 'WR Delivery Completed'),
         ('cancelled', 'WR Delivery Cancelled')], string="WR Milestone", default='new', copy=False)
    approver_ids = fields.One2many('wr.approval', 'wr_id', string="Approvers")
    # request_type_id = fields.Many2one('request.type', string="Request Type", copy=False, required=True)
    # is_required_approval = fields.Boolean(string="Request Type", copy=False, related="request_type_id.is_required_approval")
    service_request_id = fields.Many2one('service.request', string="Service Request")
    sr_count = fields.Integer(compute='compute_sr_count')
    installation_count = fields.Integer(compute='compute_install_count')
    # New as per Sheet
    product_serial_no = fields.Char(string='Serial Number(Old)', copy=False, readonly=True)
    product_code_no = fields.Char(string='Product Code No(old)', copy=False, readonly=True)
    product_part_no = fields.Char(string='Product Part No(old)', copy=False, readonly=True)
    po_number = fields.Char(string="PO Number", copy=False)
    po_date = fields.Date(string="PO Date", copy=False)
    invoice_number = fields.Char(string="Invoice Number", copy=False)
    invoice_date = fields.Date(string="Invoice Date", copy=False)
    delivery_number = fields.Many2one('stock.picking', string="Delivery Order Number", copy=False)
    delivery_order_date = fields.Datetime('Delivery Order Date', copy=False)
    product_serial_number = fields.Char(string="Serial Number (New)", required=True)
    product_part_number = fields.Char(string='Part Number (New)', copy=False)
    product_part_code = fields.Char(string='Part Code (New)', copy=False)
    billing_type = fields.Char(string='Billing Type', copy=False)
    is_send_for_approvals = fields.Boolean(string="Is Send for Approvals", copy=False, compute='_get_approval')
    approvals_count = fields.Integer(string='Approval Count', compute='_compute_approvals_count')
    spare_request_ids = fields.Many2many('spare.request', string="Spare Request", compute='_compute_spare_request')
    task_list_ids = fields.One2many('tasks.master.line', 'wr_id', string="Task Lists")
    wr_asset_ids = fields.One2many('wr.request.asset.line', 'wr_request_id', string='Assets')

    def _get_approval(self):
        for record in self:
            record.is_send_for_approvals = False
            if record.sudo().parent_ticket_id:
                if record.sudo().parent_ticket_id.parent_configuration_id.is_approval_required_warranty:
                    record.is_send_for_approvals = True
            if record.sudo().child_ticket_id:
                if record.sudo().child_ticket_id.child_configuration_id.is_approval_required_warranty:
                    record.is_send_for_approvals = True

    def _compute_spare_request(self):
        lists = []
        for record in self:
            if record.parent_ticket_id:
                spare_ids = self.env["spare.request"].search([("parent_ticket_id", "=", record.parent_ticket_id.id)])
                if spare_ids:
                    record.spare_request_ids = spare_ids.ids
                else:
                    record.spare_request_ids = None
            else:
                record.spare_request_ids = None

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_replacement_order') and not vals.get('name'):
                sequence = self.env['ir.sequence'].next_by_code('warranty.replacement')
                vals['name'] = sequence
                if vals.get('parent_ticket_id'):
                    task_id = self.env.ref('ppts_warranty_replacement.task_data_wr_transfer_request')
                    pt_id = self.env["parent.ticket"].search([("id", "=", vals.get('parent_ticket_id'))])
                    pt_id.update({
                        'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                    })
                if vals.get('child_ticket_id'):
                    task_id = self.env.ref('ppts_warranty_replacement.task_data_wr_transfer_request')
                    pt_id = self.env["child.ticket"].search([("id", "=", vals.get('child_ticket_id'))])
                    pt_id.update({
                        'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                    })
        return super(WarrantyReplacement, self).create(vals_list)

    def write(self, vals_list):
        rec = super(WarrantyReplacement, self).write(vals_list)
        if 'wr_state' in vals_list and self.sudo().parent_ticket_id or self.child_ticket_id and self.is_replacement_order:
            # PT Configuration Notification
            if self.sudo().parent_ticket_id.parent_configuration_id and self.sudo().parent_ticket_id.parent_configuration_id.is_warranty_replacement:
                email = ''
                approver_email = ''
                send = False
                if self.sudo().parent_ticket_id.parent_configuration_id.alert_warranty == 'confirm' and self.wr_state == 'start':
                    send = True
                elif self.sudo().parent_ticket_id.parent_configuration_id.alert_warranty == 'done' and self.wr_state == 'completed':
                    send = True
                elif self.sudo().parent_ticket_id.parent_configuration_id.alert_warranty == 'both' and self.wr_state in [
                    'start', 'completed']:
                    send = True

                team_alert_template_id = self.sudo().parent_ticket_id.parent_configuration_id.alert_warranty_email_template_id
                customer_template_id = self.sudo().parent_ticket_id.parent_configuration_id.warranty_cust_email_template_id
                if team_alert_template_id and send:
                    teams = self.env['hr.employee'].search([('job_id', 'in',
                                                             self.sudo().parent_ticket_id.parent_configuration_id.alert_warranty_approval_team_ids.ids)]).mapped(
                        'work_email')
                    email += ', '.join(teams)
                    team_alert_template_id.with_context(email_to=email).sudo().send_mail(
                        self.sudo().parent_ticket_id.id,
                        force_send=True)
                if customer_template_id and send:
                    customer_email = ",".join([str(self.sudo().parent_ticket_id.customer_account_id.email),
                                               str(self.sudo().parent_ticket_id.partner_id.email)])
                    customer_template_id.with_context(email_to=customer_email).sudo().send_mail(
                        self.sudo().parent_ticket_id.id, force_send=True)
                if team_alert_template_id and self.sudo().parent_ticket_id.parent_configuration_id.is_approval_required_warranty and send:
                    for teams in self.sudo().parent_ticket_id.parent_configuration_id.warranty_approval_team_ids:
                        teams = teams.mapped('line_ids.user_id.login')
                        approver_email += ', '.join(teams)
                    team_alert_template_id.with_context(email_to=approver_email).sudo().send_mail(
                        self.sudo().parent_ticket_id.id, force_send=True)
            # CT Configuration Notification
            if self.child_ticket_id.child_configuration_id and self.child_ticket_id.child_configuration_id.is_warranty_replacement:
                email = ''
                approver_email = ''
                send = False
                if self.child_ticket_id.child_configuration_id.alert_warranty == 'confirm' and self.wr_state == 'start':
                    send = True
                elif self.child_ticket_id.child_configuration_id.alert_warranty == 'done' and self.wr_state == 'completed':
                    send = True
                elif self.child_ticket_id.child_configuration_id.alert_warranty == 'both' and self.wr_state in ['start',
                                                                                                                'completed']:
                    send = True

                team_alert_template_id = self.child_ticket_id.child_configuration_id.alert_warranty_email_template_id
                customer_template_id = self.child_ticket_id.child_configuration_id.warranty_cust_email_template_id
                if team_alert_template_id and send:
                    teams = self.env['hr.employee'].search([('job_id', 'in',
                                                             self.child_ticket_id.child_configuration_id.alert_warranty_approval_team_ids.ids)]).mapped(
                        'work_email')
                    email += ', '.join(teams)
                    team_alert_template_id.with_context(email_to=email).sudo().send_mail(self.child_ticket_id.id,
                                                                                         force_send=True)
                if customer_template_id and send:
                    customer_email = ",".join([str(self.child_ticket_id.customer_account_id.email),
                                               str(self.child_ticket_id.partner_id.email)])
                    customer_template_id.with_context(email_to=customer_email).sudo().send_mail(self.child_ticket_id.id,
                                                                                                force_send=True)
                if team_alert_template_id and self.child_ticket_id.child_configuration_id.is_approval_required_warranty and self.wr_state == 'waiting_for_approval':
                    for teams in self.child_ticket_id.child_configuration_id.warranty_approval_team_ids:
                        teams = teams.mapped('line_ids.user_id.login')
                        approver_email += ', '.join(teams)
                    team_alert_template_id.with_context(email_to=approver_email).sudo().send_mail(
                        self.child_ticket_id.id, force_send=True)
            # Warranty Replacement Status Update
            task_id = None
            last_task_id = []
            pt_task_ids = self.sudo().parent_ticket_id.task_list_ids.mapped("task_id")
            for pt_task in pt_task_ids:
                last_task_id.append(pt_task.id)
            last_id = last_task_id.pop() if last_task_id else None
            if self.wr_state == 'approved' and any(self.sudo().parent_ticket_id or self.child_ticket_id):
                task_id = self.env.ref('ppts_warranty_replacement.task_data_wr_transfer_approved')
            elif self.wr_state == 'rejected' and any(self.sudo().parent_ticket_id or self.child_ticket_id):
                task_id = self.env.ref('ppts_warranty_replacement.task_data_wr_transfer_rejected')
            elif self.wr_state == 'completed' and any(self.sudo().parent_ticket_id or self.child_ticket_id):
                task_id = self.env.ref('ppts_warranty_replacement.task_data_wr_transfer_delivered')
            # Parent ticket Status Update
            if task_id and not task_id.id == last_id:
                pt_id = self.env["parent.ticket"].search([("id", "=", self.sudo().parent_ticket_id.id)])
                pt_id.update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })
            # Child ticket Status Update
            ct_task_ids = self.child_ticket_id.task_list_ids.mapped("task_id")
            for ct_task in ct_task_ids:
                last_task_id.append(ct_task.id)
            last_id = last_task_id.pop() if last_task_id else None
            if task_id and not task_id.id == last_id:
                ct_id = self.env["child.ticket"].search([("id", "=", self.child_ticket_id.id)])
                ct_id.update({
                    'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                })
        return rec

    def _prepare_invoice(self):
        invoice_vals = super(WarrantyReplacement, self)._prepare_invoice()
        if self.is_replacement_order:
            invoice_vals['journal_id'] = self.company_id.replacement_order_journal_id.id
        return invoice_vals

    def action_start_wr_process(self):
        self.wr_state = 'start'

    def action_wr_in_progress(self):
        self.wr_state = 'in_progress'

    def action_wr_complete(self):
        open_order = self.env['stock.picking'].search(
            [('child_ticket_id', '=', self.child_ticket_id.id), ('child_ticket_id', '!=', False),
             ('picking_type_id.code', '=', 'outgoing'), ('state', '!=', 'done')], limit=1)
        open_order.sale_id = self.id
        # Since the New serial number is given need to create under Assets to map the same on the delivery order
        self.env['stock.lot'].sudo().create({
            'name': self.product_serial_number,
            'customer_id': self.child_ticket_id.stock_lot_id.customer_id.id or self.parent_ticket_id.stock_lot_id.customer_id.id,
            'product_id': self.child_ticket_id.stock_lot_id.product_id.id or self.parent_ticket_id.stock_lot_id.product_id.id,
            'asset_type_id': self.child_ticket_id.stock_lot_id.asset_type_id.id or self.parent_ticket_id.stock_lot_id.asset_type_id.id,
            'company_id': self.env.user.company_id.id,
            'warranty_start_date': self.wr_install_start_date,
            'warranty_end_date': self.wr_install_end_date,
            'asset_location_id': 104,
        })

        if open_order and open_order.picking_type_id.code == "outgoing" and open_order.sale_id.is_replacement_order:
            for stock_move in open_order.move_ids.filtered(
                    lambda l: l.product_id.id == self.child_ticket_id.product_id.id):
                move_line_vals = self.prepare_move_line_values_wr(stock_move)
                self.env['stock.move.line'].create(move_line_vals)
                # open_order.action_confirm()
                # open_order.button_validate()
        template_id = self.env.ref('ppts_warranty_replacement.mail_template_confirmed_replacement')
        if template_id:
            template_id.sudo().send_mail(self.id, force_send=True)
        # While click on this button the below function will call and create Receipts to get the product inside the warehouse and DO to send the product out.
        # self.action_confirm()
        self.wr_state = 'completed'

    def prepare_move_line_values_wr(self, stock_move):
        """This method is used to prepare values for stock move lines."""
        lot = self.env['stock.lot'].search([('name', '=', self.product_serial_number)], limit=1)
        return {
            'move_id': stock_move.id,
            'location_id': stock_move.location_id.id,
            'location_dest_id': stock_move.location_dest_id.id,
            'product_uom_id': stock_move.product_id.uom_id.id,
            'product_id': stock_move.product_id.id,
            'picking_id': stock_move.picking_id.id,
            'lot_id': lot.id,
            'qty_done': 1
        }

    def action_ready_for_testing(self):
        pass

    def action_ready_for_qc(self):
        pass

    def action_wr_return(self):
        pass

    def _action_cancel(self):
        res = super(WarrantyReplacement, self)._action_cancel()
        self.action_wr_cancel()
        return res

    def action_wr_cancel(self):
        self.wr_state = 'cancelled'

    def action_wr_request_approval(self):
        if self.sudo().parent_ticket_id:
            if self.sudo().parent_ticket_id.parent_configuration_id.is_approval_required_warranty and self.sudo().parent_ticket_id.parent_configuration_id.warranty_approval_team_ids:
                approval_type_id = self.sudo().parent_ticket_id.parent_configuration_id.warranty_approval_team_ids[
                    -1].id
                request = {
                    'name': self.name,
                    'type_id': approval_type_id or False,
                    'wr_id': self.id,
                }
                requests = self.env['multi.approval'].create(request)
                requests.action_submit()
                self.wr_state = 'waiting_for_approval'
        else:
            if self.sudo().child_ticket_id.child_configuration_id.is_approval_required_warranty and self.sudo().child_ticket_id.child_configuration_id.warranty_approval_team_ids:
                approval_type_id = self.sudo().child_ticket_id.child_configuration_id.warranty_approval_team_ids[-1].id
                request = {
                    'name': self.name,
                    'type_id': approval_type_id or False,
                    'wr_id': self.id,
                }
                requests = self.env['multi.approval'].create(request)
                requests.action_submit()
                self.wr_state = 'waiting_for_approval'
        return True

    def action_wr_return_spares(self):
        pass

    def action_wr_update_asset(self):
        pass

    def action_wr_generate_report(self):
        pass

    def _check_user_exist(self):
        if self.env['wr.approval'].search(
                [('user_id', '=', self.env.user.id), ('wr_id', '=', self.id)]):
            return True
        else:
            return False

    def _show_notification(self, message):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ('Pay attention'),
                'message': message,
                'type': 'danger',
                'sticky': False,
            },
        }
        return notification

    def action_create_service_request_wizard(self):
        return {
            'name': _('Service Request'),
            'view_mode': 'form',
            'res_model': 'wr.sr.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            "context": self.env.context,
        }

    def action_view_service_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Request',
            'view_mode': 'tree,form',
            'res_model': 'service.request',
            'domain': [('wr_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_sr_count(self):
        for record in self:
            record.sr_count = self.env['service.request'].search_count([('wr_id', '=', self.id)])

    def action_create_installation(self):
        for order in self:
            if not order.order_line:
                raise UserError(_("Please Select Product Selection"))
            for line in order.order_line:
                record = {
                    'is_project_installation': True,
                    # 'installation_stock_lot_id': line.stock_lot_id.id,
                    # 'installation_product_id': line.product_id.id,
                    'installation_customer_id': order.partner_id.id or False,
                    'partner_id': order.partner_id.id or False,
                    'installation_customer_account_id': order.partner_id.customer_account_id.id or False,
                    'installation_service_category_id': order.service_category_id.id or False,
                    'installation_service_type_id': order.service_type_id.id or False,
                    # 'installation_request_type_id': order.request_type_id.id or False,
                    # 'installation_team_id': order.team_id.id or False,
                    'installation_parent_ticket_id': order.parent_ticket_id.id or False,
                    'installation_child_ticket_id': order.child_ticket_id.id or False,
                    'installation_external_reference': order.external_reference,
                    'installation_reported_fault': order.reported_fault or '',
                    'installation_categ_id': line.product_id.categ_id.id or False,
                    # 'installation_custom_product_serial': line.product_id.custom_product_serial,
                    'installation_product_code_no': line.product_id.product_code,
                    'installation_product_part': line.product_id.product_part,
                    # 'installation_worksheet_id': order.survey_id.id or False,
                    'installation_origin': order.name,
                    'service_request_id': order.service_request_id.id,
                }
                record = self.env['project.task'].create(record)
        view = self.env.ref('ppts_project_sr_installation.view_task_form2_sr_installation')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Installation',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view.id,
            'res_model': 'project.task',
            'res_id': record.id,
            'target': 'current',
            'domain': [('is_project_installation', '=', True)],
        }

    def action_view_installations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Installation',
            'view_mode': 'tree,form',
            'views': [(self.env.ref('ppts_project_sr_installation.view_task_tree2_sr_installation').id, 'tree'),
                      (self.env.ref('ppts_project_sr_installation.view_task_form2_sr_installation').id, 'form')],
            'res_model': 'project.task',
            'domain': [('is_project_installation', '=', True), ('service_request_id', '=', self.service_request_id.id)],
            'context': "{'create': False}"
        }

    # Smart Button - Approvals
    def action_view_approvals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send for Approvals',
            'view_mode': 'tree,form',
            'res_model': 'multi.approval',
            'domain': [('wr_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def _compute_approvals_count(self):
        for record in self:
            record.approvals_count = self.env['multi.approval'].search_count([('wr_id', '=', record.id)])

    # Smart Button - Reports
    def action_view_reports(self):
        return True

    # Smart Button - Survey
    def action_view_survey(self):
        return True

    def compute_install_count(self):
        for record in self:
            record.installation_count = self.env['project.task'].search_count([('is_project_installation', '=', True), (
                'installation_child_ticket_id', '=', self.child_ticket_id.id)])


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    stock_lot_id = fields.Many2one('stock.lot', string="Products/Assets", required=True)

    def action_open_product_template(self):
        self.ensure_one()
        return {
            'name': 'Product',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.template',
            'res_id': self.product_id.product_tmpl_id.id,
        }


class MultiApproval(models.Model):
    _inherit = 'multi.approval'

    wr_id = fields.Many2one('sale.order', string="Warranty Replacement ID", copy=False)

    def action_approve(self):
        values = super(MultiApproval, self).action_approve()
        wr_id = self.env['sale.order'].sudo().search([('id', '=', self.wr_id.id)])
        if all(x.state == 'Approved' for x in self.line_ids):
            wr_id.wr_state = 'approved'
        return values

    def action_refuse(self, reason=''):
        values = super(MultiApproval, self).action_refuse(reason='')
        wr_id = self.env['sale.order'].sudo().search([('id', '=', self.wr_id.id)])
        if all(x.state == 'Refused' for x in self.line_ids):
            wr_id.wr_state = 'rejected'
        return values


class TasksMasterLine(models.Model):
    _inherit = 'tasks.master.line'

    wr_id = fields.Many2one('sale.order', string='Warranty Replacement')


class WrRequestAssetLine(models.Model):
    _name = 'wr.request.asset.line'
    _description = ' Wr Request Asset Line'

    # name = fields.Char(string="Description")
    product_id = fields.Many2one('product.product', string="Product")
    description = fields.Char(string="Description")
    stock_lot_id = fields.Many2one('stock.lot', string="Asset Lot/Serial Number")
    wr_request_id = fields.Many2one('sale.order', string='Request', ondelete='cascade')
    # notes = fields.Char('Notes')
    quantity = fields.Integer(string="Quantity", default=1)
    available = fields.Integer(string="Available Quantity")
    product_uom_id = fields.Many2one('uom.uom', string="UOM")
    part_number = fields.Char(string="Part No")
    serial_number = fields.Char(string="Serial No")
