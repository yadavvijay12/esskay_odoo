from odoo import models, fields, api, _

ALERT_INVENTORY_SELECTION = [('waiting', 'On Todo/Waiting'),
                             ('done', 'On Validate/Done'),
                             ('both', 'Both')]
ALERT_TABS_SELECTION = [('confirm', 'On Ack/Confirm'),
                        ('done', 'On Release/Done'),
                        ('both', 'Both')]


class AdditionalAccessories(models.Model):
    _name = 'wk.additional.accessories'

    name = fields.Char(string="Additional Accessories")
    tasks_master_id = fields.Many2one('tasks.master.line', string="Task Master Line")
    aa_cat_no = fields.Char(string="Cat No")
    aa_stock_lot = fields.Char(string="S.No/Lot No")
    aa_quantity = fields.Float(string="Quantity")
    aa_description = fields.Char(string="Description")


class TicketConfiguration(models.Model):
    _name = 'ticket.configuration'

    # Parent Ticket Configuration


class ParentTicketConfiguration(models.Model):
    _name = 'parent.ticket.configuration'
    _rec_name = 'parent_config_name'

    active = fields.Boolean(string='active', default=True)
    parent_config_name = fields.Char(string="Parent Ticket Name", required=True)
    service_type_id = fields.Many2one('service.type', string="Parent Service Type")
    service_category_id = fields.Many2one('service.category', string="Parent Service Category")
    is_child_ticket_auto = fields.Boolean(string="Create Child Ticket Automatically")
    child_ticket_type_id = fields.Many2one('child.ticket.configuration', string="Child Ticket Type")
    control_point_id = fields.Many2one('quality.measure', string="Control Point")
    task_id = fields.Many2one('tasks.master', string="Workflow's Task")
    # Inventory
    is_inventory = fields.Boolean(string="Inventory")
    is_inward_receipts = fields.Boolean(string="Receipts")
    is_outward_delivery_order = fields.Boolean(string="Delivery")
    is_material_movement = fields.Boolean(string="Transfer(Material Movement)")
    is_spares = fields.Boolean(string="Spare Request")
    is_loaners = fields.Boolean(string="Loaner Request")
    is_warranty_replacement = fields.Boolean(string="Warranty Replacement Request")
    is_inward_inspection = fields.Boolean(string="Inward Inspection(Receipts)")
    is_outward_inspection = fields.Boolean(string="Outward Inspection(Delivery)")
    # Inventory(incoming,outgoing and Internal transfer)
    receipts_operation_type_id = fields.Many2one('stock.picking.type', string="RO Type", help="Receipts Operaion Type",
                                                 domain=[('code', '=', 'incoming')])
    delivery_operation_type_id = fields.Many2one('stock.picking.type', string="DO Type", help="Delivery Operaion Type",
                                                 domain=[('code', '=', 'outgoing')])
    transfer_operation_type_ids = fields.Many2many('stock.picking.type', 'to_type_rel',
                                                   'parent_ticket_configuration_id', 'stock_picking_type_id',
                                                   string="TO Type", help="Transfer Operaion Type",
                                                   domain=[('code', '=', 'internal')])
    # Alert Inventory
    alert_receipts = fields.Selection(ALERT_INVENTORY_SELECTION, string="Alert Notification")
    alert_delivery = fields.Selection(ALERT_INVENTORY_SELECTION, string="Alert Notification")
    alert_transfer = fields.Selection(ALERT_INVENTORY_SELECTION, string="Alert Notification")
    alert_spares = fields.Selection(ALERT_TABS_SELECTION, string="Alert Notification")
    alert_loaners = fields.Selection(ALERT_TABS_SELECTION, string="Alert Notification")
    alert_warranty = fields.Selection(ALERT_TABS_SELECTION, string="Alert Notification")
    # Approval Required?
    is_approval_required_receipts = fields.Boolean(string="Approval Required?")
    is_approval_required_delivery = fields.Boolean(string="Approval Required?")
    is_approval_required_transfer = fields.Boolean(string="Approval Required?")
    is_approval_required_spares = fields.Boolean(string="Approval Required?")
    is_approval_required_loaners = fields.Boolean(string="Approval Required?")
    is_approval_required_warranty = fields.Boolean(string="Approval Required?")
    # alert team_ids
    alert_receipts_approval_team_ids = fields.Many2many('hr.job', 'parent_ticket_configuration_rel', 'job_id',
                                                        'parent_ticket_configuration_id', string="Team")
    alert_delivery_approval_team_ids = fields.Many2many('hr.job', 'parent_ticket_configuration_rel', 'job_id',
                                                        'parent_ticket_configuration_id', string="Team")
    alert_transfer_approval_team_ids = fields.Many2many('hr.job', 'parent_ticket_configuration_rel', 'job_id',
                                                        'parent_ticket_configuration_id', string="Team")
    alert_spares_approval_team_ids = fields.Many2many('hr.job', 'parent_ticket_configuration_rel', 'job_id',
                                                      'parent_ticket_configuration_id', string="Team")
    alert_loaners_approval_team_ids = fields.Many2many('hr.job', 'parent_ticket_configuration_rel', 'job_id',
                                                       'parent_ticket_configuration_id', string="Team")
    alert_warranty_approval_team_ids = fields.Many2many('hr.job', 'parent_ticket_configuration_rel', 'job_id',
                                                        'parent_ticket_configuration_id', string="Team")
    # Approval Team ID
    receipts_approval_team_ids = fields.Many2many('multi.approval.type', 'approval_receipts_operation_type_rel',
                                                  'parent_ticket_configuration_id', 'multi_approval_type_id',
                                                  string="Team")
    delivery_approval_team_ids = fields.Many2many('multi.approval.type', 'approval_delivery_operation_type__rel',
                                                  'parent_ticket_configuration_id', 'multi_approval_type_id',
                                                  string="Team")
    transfer_approval_team_ids = fields.Many2many('multi.approval.type', 'approval_transfer_operation_type_rel',
                                                  'parent_ticket_configuration_id', 'multi_approval_type_id',
                                                  string="Team")
    spares_approval_team_ids = fields.Many2many('multi.approval.type', 'approval_spares_rel',
                                                'parent_ticket_configuration_id', 'multi_approval_type_id',
                                                string="Team")
    loaners_approval_team_ids = fields.Many2many('multi.approval.type', 'approval_loaners_rel',
                                                 'parent_ticket_configuration_id', 'multi_approval_type_id',
                                                 string="Team")
    warranty_approval_team_ids = fields.Many2many('multi.approval.type', 'approval_warranty_replacement_rel',
                                                  'parent_ticket_configuration_id', 'multi_approval_type_id',
                                                  string="Team")
    oem_approval_team_ids = fields.Many2many('multi.approval.type', 'oem_inwarranty_approval_rel',
                                             'parent_ticket_configuration_id', 'multi_approval_type_id',
                                             string="Approval Team")
    repair_approval_team_ids = fields.Many2many('multi.approval.type', 'outwarranty_approval_rel',
                                                'parent_ticket_configuration_id', 'multi_approval_type_id',
                                                string="Approval Team")
    warrantyvoid_approval_team_ids = fields.Many2many('multi.approval.type', 'oem_warranty_void_approval_rel',
                                                      'parent_ticket_configuration_id', 'multi_approval_type_id',
                                                      string="Team")
    # Email Template ID
    email_template_id = fields.Many2one('mail.template', string="Email Template",
                                        domain="[('model', '=', 'parent.ticket')]")
    receipts_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                 domain="[('model', '=', 'parent.ticket')]")
    delivery_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                 domain="[('model', '=', 'parent.ticket')]")
    transfer_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                 domain="[('model', '=', 'parent.ticket')]")
    spares_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                               domain="[('model', '=', 'parent.ticket')]")
    loaners_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                domain="[('model', '=', 'parent.ticket')]")
    warranty_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                 domain="[('model', '=', 'parent.ticket')]")
    notification_oem_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                         domain="[('model', '=', 'parent.ticket')]")
    notification_repair_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                            domain="[('model', '=', 'parent.ticket')]")
    alert_receipts_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                       domain="[('model', '=', 'parent.ticket')]")
    alert_delivery_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                       domain="[('model', '=', 'parent.ticket')]")
    alert_transfer_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                       domain="[('model', '=', 'parent.ticket')]")
    alert_spares_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                     domain="[('model', '=', 'parent.ticket')]")
    alert_loaners_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                      domain="[('model', '=', 'parent.ticket')]")
    alert_warranty_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                       domain="[('model', '=', 'parent.ticket')]")
    # Customer Email Template ID
    receipts_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                      domain="[('model', '=', 'parent.ticket')]")
    delivery_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                      domain="[('model', '=', 'parent.ticket')]")
    transfer_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                      domain="[('model', '=', 'parent.ticket')]")
    spares_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                    domain="[('model', '=', 'parent.ticket')]")
    loaners_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                     domain="[('model', '=', 'parent.ticket')]")
    warranty_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                      domain="[('model', '=', 'parent.ticket')]")
    # parent ticket
    # is_parent_ticket = fields.Boolean(string="Parent Ticket")
    is_create_alert = fields.Boolean(string="On Ticket Create Alert / Notification")
    customer_type = fields.Selection([('oem', 'OEM'), ('end_customer', 'End Customer'), ('both', 'Both')],
                                     string="Customer Type")
    # quality
    is_quality = fields.Boolean(string="Quality Module")

    # report_quality_check = fields.Selection(
    #     [('inward_inspection', 'Inward Inspection'), ('outward_inspection', 'Outward Inspection'), ('both', 'Both')],
    #     string="Report Quality Check")
    report_quality_check = fields.Selection(
        [('inward_inspection', 'Inward Inspection'), ('outward_inspection', 'Outward Inspection'), ('both', 'Both')],
        string="Report Quality Check")
    is_general = fields.Boolean(string="General")
    # general(oem)
    oem_warranty_check = fields.Selection([('yes', 'Yes'), ('no', 'No')], default="no",
                                          string="OEM warranty check Required?")
    oem_inwarranty_approval = fields.Selection([('yes', 'Yes'), ('no', 'No')], default="no",
                                               string="In warranty Approval Required?")
    oem_outwarranty_approval = fields.Selection([('yes', 'Yes'), ('no', 'No')], default="no",
                                                string="Out of warranty Approval Required?")
    void_oem_approval_team_ids = fields.Many2many('multi.approval.type', 'general_oem_warranty_void_approval_rel',
                                                  'parent_ticket_configuration_id', 'multi_approval_type_id',
                                                  string="Team")
    notification_oem_approval_team_ids = fields.Many2many('multi.approval.type', 'general_oem_outwarranty_approval_rel',
                                                          'parent_ticket_configuration_id', 'multi_approval_type_id',
                                                          string="Team")
    # general(repair)
    repair_warranty_check = fields.Selection([('yes', 'Yes'), ('no', 'No')], default="no",
                                             string="Repair warranty check Required?")
    repair_inwarranty_approval = fields.Selection([('yes', 'Yes'), ('no', 'No')], default="no",
                                                  string="In warranty Approval Required?")
    repair_outwarranty_approval = fields.Selection([('yes', 'Yes'), ('no', 'No')], default="no",
                                                   string="Out of warranty Approval Required?")
    oem_warranty_void_approval = fields.Selection([('yes', 'Yes'), ('no', 'No')], default="no",
                                                  string="OEM Warranty Void Approval Required?")
    repair_warranty_void_approval = fields.Selection([('yes', 'Yes'), ('no', 'No')], default="no",
                                                     string="Repair Warranty Void Approval Required?")
    is_send_notification_auto_oem = fields.Boolean(string="Send Notification Automatically")
    is_send_notification_auto_repair = fields.Boolean(string="Send Notification Automatically")
    void_repair_approval_team_ids = fields.Many2many('multi.approval.type', 'repair_warranty_void_approval_rel',
                                                     'parent_ticket_configuration_id', 'multi_approval_type_id',
                                                     string="Team")
    notification_repair_approval_team_ids = fields.Many2many('multi.approval.type', 'repair_outwarranty_approval_rel',
                                                             'parent_ticket_configuration_id', 'multi_approval_type_id',
                                                             string="Team")
    is_job_not_resolved = fields.Selection([('scrap', 'Scrap'), ('return', 'Return'), ('both', 'Both')],
                                           string="If Job not resolved?")
    # child ticket
    is_child_ticket = fields.Boolean(string="Child Ticket")
    is_create_child_ticket_auto = fields.Boolean(string="Create Child Ticket Automatically")
    notification_template_id = fields.Many2one('mail.template', string="Notification Template",
                                               domain="[('model', '=', 'parent.ticket')]")
    # logical check
    is_logical_check = fields.Boolean(string="Logical Check")
    in_oem_warranty_approved = fields.Boolean(string="In OEM Warranty && Approved")
    in_oo_warranty_approved = fields.Boolean(string="OO OEM Warranty && Approved")
    in_repair_warranty_approved = fields.Boolean(string="In Repair Warranty && Approved")
    oo_repair_warranty_approved = fields.Boolean(string="OO Repair Warranty && Approved")
    paid_repair_approved = fields.Boolean(string="Paid Repair & Approved")
    work_flow_id = fields.Many2one('custom.workflow', string="Work Flow(Selection)")
    child_ticket_ids = fields.One2many('child.ticket.line', 'child_ticket_id', string='Assets')
    is_outward_receipts = fields.Boolean(string="Outward Inspection(Delivery)")
    inward_receipts = fields.Boolean(string="Inward Inspection(Receipts)")

    @api.onchange('service_type_id')
    def onchange_service_type_domain(self):
        category_ids = self.service_type_id.service_category_ids.mapped('id')
        domain = [('id', 'in', category_ids)]
        return {'domain': {'service_category_id': domain}}

    @api.onchange('is_child_ticket_auto')
    def _onchange_is_child_ticket_auto(self):
        if self.is_child_ticket_auto == False:
            self.child_ticket_type_id = False
            self.control_point_id = False

    @api.onchange('is_inventory')
    def _onchange_is_inventory(self):
        inventory_check = self.env['parent.ticket'].search(
            [('parent_configuration_id', '=', self.parent_config_name)])
        for record in inventory_check:
            if record and self.is_inventory == False:
                self.is_inward_receipts = False
                self.receipts_operation_type_id = False
                self.alert_receipts = False
                self.is_approval_required_receipts = False
                self.receipts_approval_team_ids = False
                self.alert_receipts_approval_team_ids = False
                self.alert_receipts_email_template_id
                self.receipts_email_template_id = False
                self.receipts_cust_email_template_id = False
                self.delivery_operation_type_id = False
                self.alert_delivery = False
                self.is_approval_required_delivery = False
                self.delivery_approval_team_ids = False
                self.alert_delivery_approval_team_ids = False
                self.alert_delivery_email_template_id
                self.delivery_email_template_id = False
                self.delivery_cust_email_template_id = False
                self.transfer_operation_type_ids = False
                self.alert_transfer = False
                self.is_approval_required_transfer = False
                self.transfer_approval_team_ids = False
                self.alert_transfer_approval_team_ids = False
                self.alert_transfer_email_template_id
                self.transfer_email_template_id = False
                self.transfer_cust_email_template_id = False
                self.alert_spares = False
                self.is_approval_required_spares = False
                self.spares_approval_team_ids = False
                self.alert_spares_approval_team_ids = False
                self.alert_spares_email_template_id
                self.spares_email_template_id = False
                self.spares_cust_email_template_id = False
                self.alert_loaners = False
                self.is_approval_required_loaners = False
                self.loaners_approval_team_ids = False
                self.alert_loaners_approval_team_ids = False
                self.alert_loaners_email_template_id
                self.loaners_email_template_id = False
                self.loaners_cust_email_template_id = False
                self.alert_warranty = False
                self.is_approval_required_warranty = False
                self.warranty_approval_team_ids = False
                self.alert_warranty_approval_team_ids = False
                self.alert_warranty_email_template_id
                self.warranty_email_template_id = False
                self.warranty_cust_email_template_id = False
                record.is_inventory_check = False

            elif record and self.is_inventory == True:
                record.is_inventory_check = True

    @api.onchange('is_inward_receipts')
    def _onchange_is_inward_receipts(self):
        if self.is_inward_receipts == False:
            self.receipts_operation_type_id = False
            self.alert_receipts = False
            self.is_approval_required_receipts = False
            self.receipts_approval_team_ids = False
            self.alert_receipts_approval_team_ids = False
            self.alert_receipts_email_template_id
            self.receipts_email_template_id = False
            self.receipts_cust_email_template_id = False

    @api.onchange('is_approval_required_receipts')
    def _onchange_is_approval_required_receipts(self):
        if self.is_approval_required_receipts == False:
            self.receipts_approval_team_ids = False
            self.receipts_email_template_id = False

    @api.onchange('is_outward_delivery_order')
    def _onchange_is_outward_delivery_order(self):
        if self.is_outward_delivery_order == False:
            self.delivery_operation_type_id = False
            self.alert_delivery = False
            self.is_approval_required_delivery = False
            self.delivery_approval_team_ids = False
            self.alert_delivery_approval_team_ids = False
            self.alert_delivery_email_template_id
            self.delivery_email_template_id = False
            self.delivery_cust_email_template_id = False

    @api.onchange('is_approval_required_delivery')
    def _onchange_is_approval_required_delivery(self):
        if self.is_approval_required_delivery == False:
            self.delivery_approval_team_ids = False
            self.delivery_email_template_id = False

    @api.onchange('is_material_movement')
    def _onchange_is_material_movement(self):
        if self.is_material_movement == False:
            self.transfer_operation_type_ids = False
            self.alert_transfer = False
            self.is_approval_required_transfer = False
            self.transfer_approval_team_ids = False
            self.alert_transfer_approval_team_ids = False
            self.alert_transfer_email_template_id
            self.transfer_email_template_id = False
            self.transfer_cust_email_template_id = False

    @api.onchange('is_approval_required_transfer')
    def _onchange_is_approval_required_transfer(self):
        if self.is_approval_required_transfer == False:
            self.transfer_approval_team_ids = False
            self.transfer_email_template_id = False

    @api.onchange('is_spares')
    def _onchange_is_spares(self):
        spare_check = self.env['parent.ticket'].search(
            [('parent_configuration_id', '=', self.parent_config_name)])
        for record in spare_check:
            if record and self.is_spares == False:
                self.alert_spares = False
                self.is_approval_required_spares = False
                self.spares_approval_team_ids = False
                self.alert_spares_approval_team_ids = False
                self.alert_spares_email_template_id
                self.spares_email_template_id = False
                self.spares_cust_email_template_id = False
                record.is_spare_check = False

            elif record and self.is_spares == True:
                record.is_spare_check = True

    @api.onchange('is_approval_required_spares')
    def _onchange_is_approval_required_spares(self):
        if self.is_approval_required_spares == False:
            self.spares_approval_team_ids = False
            self.spares_email_template_id = False

    @api.onchange('is_loaners')
    def _onchange_is_loaners(self):
        loaner_check = self.env['parent.ticket'].search(
            [('parent_configuration_id', '=', self.parent_config_name)])
        for record in loaner_check:
            if record and self.is_loaners == False:
                self.alert_loaners = False
                self.is_approval_required_loaners = False
                self.loaners_approval_team_ids = False
                self.alert_loaners_approval_team_ids = False
                self.alert_loaners_email_template_id
                self.loaners_email_template_id = False
                self.loaners_cust_email_template_id = False
                record.is_loaners_check = False

            elif record and self.is_loaners == True:
                record.is_loaners_check = True

    @api.onchange('is_approval_required_loaners')
    def _onchange_is_approval_required_loaners(self):
        if self.is_approval_required_loaners == False:
            self.loaners_approval_team_ids = False
            self.loaners_email_template_id = False

    @api.onchange('is_warranty_replacement')
    def _onchange_is_warranty_replacement(self):
        if self.is_warranty_replacement == False:
            self.alert_warranty = False
            self.is_approval_required_warranty = False
            self.warranty_approval_team_ids = False
            self.alert_warranty_approval_team_ids = False
            self.alert_warranty_email_template_id
            self.warranty_email_template_id = False
            self.warranty_cust_email_template_id = False

    @api.onchange('is_approval_required_warranty')
    def _onchange_is_approval_required_warranty(self):
        if self.is_approval_required_warranty == False:
            self.warranty_approval_team_ids = False
            self.warranty_email_template_id = False

    @api.onchange('is_create_alert')
    def _onchange_is_create_alert(self):
        if self.is_create_alert == False:
            self.notification_template_id = False
            self.customer_type = False

    @api.onchange('is_quality')
    def _onchange_is_quality(self):
        if self.is_quality == False:
            self.inward_receipts = False
            self.is_outward_receipts = False

    @api.onchange('is_logical_check')
    def _onchange_is_logical_check(self):
        if self.is_logical_check == False:
            self.in_oem_warranty_approved = False
            self.in_oo_warranty_approved = False
            self.in_repair_warranty_approved = False
            self.oo_repair_warranty_approved = False
            self.paid_repair_approved = False
            self.work_flow_id = False

    @api.onchange('is_general')
    def _onchange_is_general(self):
        if self.is_general == False:
            self.oem_warranty_check = 'no'
            self.repair_warranty_check = 'no'
            self.is_job_not_resolved = False

    @api.onchange('oem_warranty_check')
    def _onchange_oem_warranty_check(self):
        if self.oem_warranty_check == 'no':
            self.oem_inwarranty_approval = False
            self.oem_outwarranty_approval = False
            self.oem_approval_team_ids = False
            self.oem_warranty_void_approval = 'no'
            self.is_send_notification_auto_oem = False
            self.is_job_not_resolved = False

    @api.onchange('repair_warranty_check')
    def _onchange_repair_warranty_check(self):
        if self.repair_warranty_check == 'no':
            self.repair_inwarranty_approval = False
            self.repair_outwarranty_approval = False
            self.repair_approval_team_ids = False
            self.repair_warranty_void_approval = 'no'
            self.is_send_notification_auto_repair = False

            # End Parent Ticket Configuration

            # Child Ticket Configuration


class ChildTicketLine(models.Model):
    _name = 'child.ticket.line'

    child_ticket_id = fields.Many2one('parent.ticket.configuration', string='Child')
    child_ids = fields.Many2many('child.ticket.configuration', 'child_config_name', string='Tickets from Child')


class ChildTicketConfiguration(models.Model):
    _name = 'child.ticket.configuration'
    _rec_name = 'child_config_name'

    active = fields.Boolean(string='active', default=True)
    child_config_name = fields.Char(string="Child Ticket Name", required=True)
    child_ticket_type = fields.Many2one('child.ticket.type', string="Child Ticket Type")
    is_inventory = fields.Boolean(string="Inventory")
    is_inward_receipts = fields.Boolean(string="Receipts")
    is_outward_delivery_order = fields.Boolean(string="Delivery")
    is_material_movement = fields.Boolean(string="Transfer(Material Movement")
    # Inventory(incoming,outgoing and Internal transfer)
    receipts_operation_type_id = fields.Many2one('stock.picking.type', string="RO Type", help="Receipts Operaion Type",
                                                 domain=[('code', '=', 'incoming')])
    delivery_operation_type_id = fields.Many2one('stock.picking.type', string="DO Type", help="Delivery Operaion Type",
                                                 domain=[('code', '=', 'outgoing')])
    transfer_operation_type_ids = fields.Many2many('stock.picking.type', 'transfer_type_rel',
                                                   'parent_ticket_configuration_id', 'stock_picking_type_id',
                                                   string="TO Type", help="Transfer Operaion Type",
                                                   domain=[('code', '=', 'internal')])
    # Alert Inventory
    alert_receipts = fields.Selection(ALERT_INVENTORY_SELECTION, string="Alert Notification")
    alert_delivery = fields.Selection(ALERT_INVENTORY_SELECTION, string="Alert Notification")
    alert_transfer = fields.Selection(ALERT_INVENTORY_SELECTION, string="Alert Notification")
    alert_spares = fields.Selection(ALERT_TABS_SELECTION, string="Alert Notification")
    alert_loaners = fields.Selection(ALERT_TABS_SELECTION, string="Alert Notification")
    alert_warranty = fields.Selection(ALERT_TABS_SELECTION, string="Alert Notification")
    # Approval Required?
    is_approval_required_receipts = fields.Boolean(string="Approval Required?")
    is_approval_required_delivery = fields.Boolean(string="Approval Required?")
    is_approval_required_transfer = fields.Boolean(string="Approval Required?")
    is_approval_required_spares = fields.Boolean(string="Approval Required?")
    is_approval_required_loaners = fields.Boolean(string="Approval Required?")
    is_approval_required_warranty = fields.Boolean(string="Approval Required?")
    is_approval_required_repair_quality = fields.Boolean(string="Approval Required?")
    # report_quality_check = fields.Selection(
    #     [('inward_inspection', 'Inward Inspection'), ('outward_inspection', 'Outward Inspection'), ('both', 'Both')],
    #     string="Report Quality Check")
    # Approval Team IDs
    receipts_approval_team_ids = fields.Many2many('multi.approval.type', 'child_inward_receipts_rel',
                                                  'child_ticket_configuration_id', 'multi_approval_type_id',
                                                  string="Team")
    delivery_approval_team_ids = fields.Many2many('multi.approval.type', 'child_outward_delivery_order_rel',
                                                  'child_ticket_configuration_id', 'multi_approval_type_id',
                                                  string="Team")
    transfer_approval_team_ids = fields.Many2many('multi.approval.type', 'child_material_movement_rel',
                                                  'child_ticket_configuration_id', 'multi_approval_type_id',
                                                  string="Team")
    spares_approval_team_ids = fields.Many2many('multi.approval.type', 'child_approval_required_spares_rel',
                                                'child_ticket_configuration_id', 'multi_approval_type_id',
                                                string="Team")
    loaners_approval_team_ids = fields.Many2many('multi.approval.type', 'child_approval_required_loaners_rel',
                                                 'child_ticket_configuration_id', 'multi_approval_type_id',
                                                 string="Team")
    warranty_approval_team_ids = fields.Many2many('multi.approval.type', 'child_approval_required_warranty_rel',
                                                  'child_ticket_configuration_id', 'multi_approval_type_id',
                                                  string="Team")
    repair_quality_approval_team_ids = fields.Many2many('multi.approval.type',
                                                        'child_approval_required_repair_quality_rel',
                                                        'child_ticket_configuration_id', 'multi_approval_type_id',
                                                        string="Team")
    # Alert Team IDs
    alert_receipts_approval_team_ids = fields.Many2many('hr.job', 'child_ticket_configuration_rel', 'job_id',
                                                        'child_ticket_configuration_id', string="Team")
    alert_delivery_approval_team_ids = fields.Many2many('hr.job', 'child_ticket_configuration_rel', 'job_id',
                                                        'child_ticket_configuration_id', string="Team")
    alert_transfer_approval_team_ids = fields.Many2many('hr.job', 'child_ticket_configuration_rel', 'job_id',
                                                        'child_ticket_configuration_id', string="Team")
    alert_spares_approval_team_ids = fields.Many2many('hr.job', 'child_ticket_configuration_rel', 'job_id',
                                                      'child_ticket_configuration_id', string="Team")
    alert_loaners_approval_team_ids = fields.Many2many('hr.job', 'child_ticket_configuration_rel', 'job_id',
                                                       'child_ticket_configuration_id', string="Team")
    alert_warranty_approval_team_ids = fields.Many2many('hr.job', 'child_ticket_configuration_rel', 'job_id',
                                                        'child_ticket_configuration_id', string="Team")
    alert_diagnosis_approval_team_ids = fields.Many2many('hr.job', 'child_ticket_configuration_rel', 'job_id',
                                                         'child_ticket_configuration_id', string="Team")
    alert_repair_approval_team_ids = fields.Many2many('hr.job', 'child_ticket_configuration_rel', 'job_id',
                                                      'child_ticket_configuration_id', string="Team")
    alert_installation_approval_team_ids = fields.Many2many('hr.job', 'child_ticket_configuration_rel', 'job_id',
                                                            'child_ticket_configuration_id', string="Team")
    alert_maintenance_approval_team_ids = fields.Many2many('hr.job', 'child_ticket_configuration_rel', 'job_id',
                                                           'child_ticket_configuration_id', string="Team")
    alert_testing_approval_team_ids = fields.Many2many('hr.job', 'child_ticket_configuration_rel', 'job_id',
                                                       'child_ticket_configuration_id', string="Team")
    alert_repair_quality_approval_team_ids = fields.Many2many('hr.job', 'child_ticket_configuration_rel', 'job_id',
                                                              'child_ticket_configuration_id', string="Team")
    # approval_team_ids = fields.Many2many('multi.approval.type', string="Approval Team")
    is_installation = fields.Boolean(string="Installation")
    is_spares = fields.Boolean(string="Spare Request")
    is_loaners = fields.Boolean(string="Loaner Request")
    is_warranty_replacement = fields.Boolean(string="Warranty Replacement Request")
    # Email Template ID
    email_template_id = fields.Many2one('mail.template', string="Email Template",
                                        domain="[('model', '=', 'child.ticket')]")
    receipts_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                 domain="[('model', '=', 'child.ticket')]")
    delivery_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                 domain="[('model', '=', 'child.ticket')]")
    transfer_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                 domain="[('model', '=', 'child.ticket')]")
    spares_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                               domain="[('model', '=', 'child.ticket')]")
    loaners_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                domain="[('model', '=', 'child.ticket')]")
    warranty_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                 domain="[('model', '=', 'child.ticket')]")
    repair_quality_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                       domain="[('model', '=', 'child.ticket')]")
    alert_receipts_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                       domain="[('model', '=', 'child.ticket')]")
    alert_delivery_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                       domain="[('model', '=', 'child.ticket')]")
    alert_transfer_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                       domain="[('model', '=', 'child.ticket')]")
    alert_spares_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                     domain="[('model', '=', 'child.ticket')]")
    alert_loaners_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                      domain="[('model', '=', 'child.ticket')]")
    alert_warranty_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                       domain="[('model', '=', 'child.ticket')]")
    alert_diagnosis_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                        domain="[('model', '=', 'child.ticket')]")
    alert_repair_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                     domain="[('model', '=', 'child.ticket')]")
    alert_installation_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                           domain="[('model', '=', 'child.ticket')]")
    alert_maintenance_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                          domain="[('model', '=', 'child.ticket')]")
    alert_testing_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                      domain="[('model', '=', 'child.ticket')]")
    alert_repair_quality_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                             domain="[('model', '=', 'child.ticket')]")

    # Customer Email Template ID
    receipts_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                      domain="[('model', '=', 'child.ticket')]")
    delivery_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                      domain="[('model', '=', 'child.ticket')]")
    transfer_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                      domain="[('model', '=', 'child.ticket')]")
    spares_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                    domain="[('model', '=', 'child.ticket')]")
    loaners_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                     domain="[('model', '=', 'child.ticket')]")
    warranty_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                      domain="[('model', '=', 'child.ticket')]")
    repair_quality_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                            domain="[('model', '=', 'child.ticket')]")
    notification_template_id = fields.Many2one('mail.template', string="Notification Template",
                                               domain="[('model', '=', 'child.ticket')]")
    # is_child_ticket = fields.Boolean(string="Child Ticket")
    is_create_alert = fields.Boolean(string="On Ticket Create Alert / Notification")
    is_assign_engineer = fields.Boolean(string="Assign Engineer")
    is_auto_alert = fields.Boolean(string="Automatic Alert/ Notification")
    # Repair
    is_repair = fields.Boolean(string="Repair")
    is_repair_quality = fields.Boolean(string="Quality Check: Repair Quality Check")
    is_auto_send_report_repair = fields.Boolean(
        string="Automatically Send Repair/Service Report(On Completed/Cancelled)")
    is_auto_send_report_repair_quality = fields.Boolean(string="Automatically Send QC Report (On PASS/FAIL)")
    is_approval_required_repair = fields.Boolean(string="Approval Required?")
    repair_approval_team_ids = fields.Many2many('multi.approval.type', 'is_repair', string="Approval Team")
    repair_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                               domain="[('model', '=', 'child.ticket')]")
    repair_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                    domain="[('model', '=', 'child.ticket')]")
    # Diagnosis
    is_diagnosis = fields.Boolean(string="Diagnosis")
    is_approval_required_diagnosis = fields.Boolean(string="Approval Required?")
    is_auto_send_report_diagnosis = fields.Boolean(
        string="Automatically Send diagnostic Report(On Repairable/Non Repairable)")
    diagnosis_approval_team_ids = fields.Many2many('multi.approval.type', 'is_diagnosis', string="Approval Team")
    diagnosis_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                       domain="[('model', '=', 'child.ticket')]")
    diagnosis_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                  domain="[('model', '=', 'child.ticket')]")
    inprocess_inspection = fields.Boolean(string="Inprocess Inspection")
    # Quality
    is_quality = fields.Boolean(string="Quality Module")
    quality_check_after_repair = fields.Boolean(string="Quality Check After Repair(Repair Stage)")
    transfer_inspection = fields.Boolean(string="Transfer Inspection(Transfer)")
    work_flow_id = fields.Many2one('custom.workflow', string="Workflow(Selection)")
    is_auto_alert_notification_quality = fields.Boolean(string="Automatic Alert Notification (PASS/FAIL)")
    # Maintenance
    is_maintenance = fields.Boolean(string="Maintenance")
    is_approval_required_maintenance = fields.Boolean(string="Approval Required?")
    maintenance_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                    domain="[('model', '=', 'child.ticket')]")
    maintenance_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                         domain="[('model', '=', 'child.ticket')]")
    is_auto_send_report_maintenance = fields.Boolean(
        string="Automatically Send Maintenance Report (On Completed/Cancelled)")
    maintenance_approval_team_ids = fields.Many2many('multi.approval.type', 'is_maintenance', string="Approval Team")
    # Installation
    is_installation = fields.Boolean(string="Installation")
    is_auto_send_report_installation = fields.Boolean(
        string="Automatically Send Installation Report (On Completed/Cancelled)")
    installation_approval_team_ids = fields.Many2many('multi.approval.type', 'is_diagnosis', string="Approval Team")
    is_approval_required_installation = fields.Boolean(string="Approval Required?")
    installation_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                     domain="[('model', '=', 'child.ticket')]")
    installation_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                          domain="[('model', '=', 'child.ticket')]")
    # Testing
    is_testing = fields.Boolean(string="Testing")
    is_auto_alert_notification_testing = fields.Boolean(string="Automatic Alert Notification (PASS/FAIL)")
    is_auto_send_report_testing = fields.Boolean(string="Automatically Send Testing Report (On PASS/FAIL)")
    testing_approval_team_ids = fields.Many2many('multi.approval.type', 'child_testing_rel',
                                                 'child_ticket_configuration_id', 'multi_approval_type_id',
                                                 string="Approval Team")
    is_approval_required_testing = fields.Boolean(string="Approval Required?")
    testing_email_template_id = fields.Many2one('mail.template', string="Email Template",
                                                domain="[('model', '=', 'child.ticket')]")
    testing_cust_email_template_id = fields.Many2one('mail.template', string="Customer Email Template",
                                                     domain="[('model', '=', 'child.ticket')]")

    customer_type = fields.Selection([('oem', 'OEM'), ('end_customer', 'End Customer'), ('both', 'Both')],
                                     string="Customer Type")
    # is_child_ticket = fields.Boolean(string="Child Ticket")
    is_create_child_ticket_auto = fields.Boolean(string="Create Child Ticket Automatically")
    logical_check = fields.Boolean(string="Logical Check")
    paid_repair_approved = fields.Boolean(string="Paid Repair & Approved")
    is_outward_receipts = fields.Boolean(string="Outward Inspection(Delivery)")
    inward_receipts = fields.Boolean(string="Inward Inspection(Receipts)")

    @api.onchange('is_inventory')
    def _onchange_is_inventory(self):
        inventory_checks = self.env['child.ticket'].search(
            [('child_configuration_id', '=', self.child_config_name)])
        for record in inventory_checks:
            if record and self.is_inventory == False:
                self.is_inward_receipts = False
                self.receipts_operation_type_id = False
                self.alert_receipts = False
                self.is_approval_required_receipts = False
                self.receipts_approval_team_ids = False
                self.receipts_email_template_id = False
                self.receipts_cust_email_template_id = False
                self.delivery_operation_type_id = False
                self.alert_delivery = False
                self.is_approval_required_delivery = False
                self.delivery_approval_team_ids = False
                self.delivery_email_template_id = False
                self.delivery_cust_email_template_id = False
                self.transfer_operation_type_ids = False
                self.alert_transfer = False
                self.is_approval_required_transfer = False
                self.transfer_approval_team_ids = False
                self.transfer_email_template_id = False
                self.transfer_cust_email_template_id = False
                self.alert_spares = False
                self.is_approval_required_spares = False
                self.spares_approval_team_ids = False
                self.spares_email_template_id = False
                self.spares_cust_email_template_id = False
                self.alert_loaners = False
                self.is_approval_required_loaners = False
                self.loaners_approval_team_ids = False
                self.loaners_email_template_id = False
                self.loaners_cust_email_template_id = False
                self.alert_warranty = False
                self.is_approval_required_warranty = False
                self.warranty_approval_team_ids = False
                self.warranty_email_template_id = False
                self.warranty_cust_email_template_id = False
                record.is_inventory_checks = False

            elif record and self.is_inventory == True:
                record.is_inventory_checks = True

    @api.onchange('is_inward_receipts')
    def _onchange_is_inward_receipts(self):
        if self.is_inward_receipts == False:
            self.receipts_operation_type_id = False
            self.alert_receipts = False
            self.is_approval_required_receipts = False
            self.receipts_approval_team_ids = False
            self.receipts_email_template_id = False
            self.receipts_cust_email_template_id = False

    @api.onchange('is_outward_delivery_order')
    def _onchange_is_outward_delivery_order(self):
        if self.is_outward_delivery_order == False:
            self.delivery_operation_type_id = False
            self.alert_delivery = False
            self.is_approval_required_delivery = False
            self.delivery_approval_team_ids = False
            self.delivery_email_template_id = False
            self.delivery_cust_email_template_id = False

    @api.onchange('is_material_movement')
    def _onchange_is_material_movement(self):
        if self.is_material_movement == False:
            self.transfer_operation_type_ids = False
            self.alert_transfer = False
            self.is_approval_required_transfer = False
            self.transfer_approval_team_ids = False
            self.transfer_email_template_id = False
            self.transfer_cust_email_template_id = False

    @api.onchange('is_spares')
    def _onchange_is_spares(self):
        spare_checks = self.env['child.ticket'].search(
            [('child_configuration_id', '=', self.child_config_name)])
        for record in spare_checks:
            if record and self.is_spares == False:
                self.alert_spares = False
                self.is_approval_required_spares = False
                self.spares_approval_team_ids = False
                self.spares_email_template_id = False
                self.spares_cust_email_template_id = False
                record.is_spare_checks = False

            elif record and self.is_spares == True:
                record.is_spare_checks = True

    @api.onchange('is_loaners')
    def _onchange_is_loaners(self):
        loaner_checks = self.env['child.ticket'].search(
            [('child_configuration_id', '=', self.child_config_name)])
        for record in loaner_checks:
            if record and self.is_loaners == False:
                self.alert_loaners = False
                self.is_approval_required_loaners = False
                self.loaners_approval_team_ids = False
                self.loaners_email_template_id = False
                self.loaners_cust_email_template_id = False
                record.is_loaners_checks = False

            elif record and self.is_loaners == True:
                record.is_loaners_checks = True

    @api.onchange('is_warranty_replacement')
    def _onchange_is_warranty_replacement(self):
        if self.is_warranty_replacement == False:
            self.alert_warranty = False
            self.is_approval_required_warranty = False
            self.warranty_approval_team_ids = False
            self.warranty_email_template_id = False
            self.warranty_cust_email_template_id = False

    @api.onchange('is_create_alert')
    def _onchange_is_create_alert(self):
        if self.is_create_alert == False:
            self.is_create_alert = False
            self.notification_template_id = False
            self.customer_type = False

    @api.onchange('is_quality')
    def _onchange_is_quality(self):
        if self.is_quality == False:
            self.inward_receipts = False
            self.is_outward_receipts = False
            # self.report_quality_check = False
            self.inprocess_inspection = False
            self.transfer_inspection = False
            self.work_flow_id = False
            self.quality_check_after_repair = False

    @api.onchange('is_assign_engineer')
    def _onchange_is_assign_engineer(self):
        if self.is_assign_engineer == False:
            self.is_auto_alert = False

    @api.onchange('is_diagnosis')
    def _onchange_is_diagnosis(self):
        if self.is_diagnosis == False:
            self.is_auto_send_report_diagnosis = False
            self.is_approval_required_diagnosis = False
            self.diagnosis_approval_team_ids = False
            self.diagnosis_email_template_id = False

    @api.onchange('is_approval_required_diagnosis')
    def _onchange_is_approval_required_diagnosis(self):
        if self.is_approval_required_diagnosis == False:
            self.diagnosis_approval_team_ids = False
            self.diagnosis_email_template_id = False

    @api.onchange('is_auto_send_report_diagnosis')
    def _onchange_is_auto_send_report_diagnosis(self):
        if self.is_auto_send_report_diagnosis == False:
            self.alert_diagnosis_approval_team_ids = False
            self.alert_diagnosis_email_template_id = False

    @api.onchange('is_repair')
    def _onchange_is_repair(self):
        if self.is_repair == False:
            self.is_auto_send_report_repair = False
            self.is_approval_required_repair = False
            self.repair_approval_team_ids = False
            self.repair_email_template_id = False

    @api.onchange('is_approval_required_repair')
    def _onchange_is_approval_required_repair(self):
        if self.is_approval_required_repair == False:
            self.repair_approval_team_ids = False
            self.repair_email_template_id = False

    @api.onchange('is_auto_send_report_repair')
    def _onchange_is_auto_send_report_repair(self):
        if self.is_auto_send_report_repair == False:
            self.alert_repair_approval_team_ids = False
            self.alert_repair_email_template_id = False

    @api.onchange('is_installation')
    def _onchange_is_installation(self):
        if self.is_installation == False:
            self.is_auto_send_report_installation = False
            self.is_approval_required_installation = False
            self.installation_approval_team_ids = False
            self.installation_email_template_id = False

    @api.onchange('is_approval_required_installation')
    def _onchange_is_approval_required_installation(self):
        if self.is_approval_required_installation == False:
            self.installation_approval_team_ids = False
            self.installation_email_template_id = False

    @api.onchange('is_auto_send_report_installation')
    def _onchange_is_auto_send_report_installation(self):
        if self.is_auto_send_report_installation == False:
            self.alert_installation_approval_team_ids = False
            self.alert_installation_email_template_id = False

    @api.onchange('is_maintenance')
    def _onchange_is_maintenance(self):
        if self.is_maintenance == False:
            self.is_auto_send_report_maintenance = False
            self.is_approval_required_maintenance = False
            self.maintenance_approval_team_ids = False
            self.maintenance_email_template_id = False

    @api.onchange('is_approval_required_maintenance')
    def _onchange_is_approval_required_maintenance(self):
        if self.is_approval_required_maintenance == False:
            self.maintenance_approval_team_ids = False
            self.maintenance_email_template_id = False

    @api.onchange('is_auto_send_report_maintenance')
    def _onchange_is_auto_send_report_maintenance(self):
        if self.is_auto_send_report_maintenance == False:
            self.alert_maintenance_approval_team_ids = False
            self.alert_maintenance_email_template_id = False

    @api.onchange('is_testing')
    def _onchange_is_testing(self):
        if self.is_testing == False:
            self.is_auto_alert_notification_testing = False
            self.is_auto_send_report_testing = False
            self.is_approval_required_testing = False
            self.testing_approval_team_ids = False
            self.testing_email_template_id = False

    @api.onchange('is_approval_required_testing')
    def _onchange_is_approval_required_testing(self):
        if self.is_approval_required_testing == False:
            self.testing_approval_team_ids = False
            self.testing_email_template_id = False

    @api.onchange('is_auto_send_report_testing')
    def _onchange_is_auto_send_report_testing(self):
        if self.is_auto_send_report_testing == False:
            self.alert_testing_approval_team_ids = False
            self.alert_testing_email_template_id = False

    @api.onchange('is_repair_quality')
    def _onchange_is_repair_quality(self):
        if self.is_repair_quality == False:
            self.is_auto_alert_notification_quality = False
            self.is_auto_send_report_testing = False
            self.is_auto_send_report_repair_quality = False
            self.is_approval_required_repair_quality = False
            self.repair_quality_approval_team_ids = False
            self.repair_quality_email_template_id = False

    @api.onchange('is_approval_required_repair_quality')
    def _onchange_is_approval_required_repair_quality(self):
        if self.is_approval_required_repair_quality == False:
            self.repair_quality_approval_team_ids = False
            self.repair_quality_email_template_id = False

    @api.onchange('is_auto_send_report_repair_quality')
    def _onchange_is_auto_send_report_repair_quality(self):
        if self.is_auto_send_report_repair_quality == False:
            self.alert_repair_quality_approval_team_ids = False
            self.alert_repair_quality_email_template_id = False

            # End Child Ticket Configuration
