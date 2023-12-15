from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class WorkflowTeamId(models.Model):
    _inherit = 'crm.team'

    workflow_properties_definition = fields.PropertiesDefinition('Product Properties')


class TasksMaster(models.Model):
    _name = "tasks.master"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = "Tasks Masters"

    name = fields.Char(string="Task", required=True)
    worksheet_id = fields.Many2one('survey.survey', string="Worksheet")
    team_id = fields.Many2one('crm.team', string="Team", copy=False)
    quality_inspection_id = fields.Many2one('quality.measure', string="Quality Type", copy=False)
    operation_type_id = fields.Many2one('stock.picking.type', string="Operation Type", copy=False)
    source_location_id = fields.Many2one("stock.location", string="Source Location", copy=False)
    destination_location_id = fields.Many2one("stock.location", string="Destination Location", copy=False)
    category = fields.Selection([('action', 'Python Code'), ('status', 'Status'), ('system', 'System Update')], string="Category", required=True)
    description = fields.Text(string="Description")
    is_file_attachment = fields.Boolean(string="File/Camera Attachment")
    is_sign_required = fields.Boolean(string="Sign Required")
    is_end_task = fields.Boolean(string="End Task")
    is_pi_required = fields.Boolean(string="PI required?")
    is_create_ticket = fields.Boolean(string="Create Parent Ticket")
    is_create_service_request = fields.Boolean(string="Create Request")
    is_enable_child_ticket = fields.Boolean(string="Create Child Ticket")
    is_notify = fields.Boolean(string="Notify")
    job_ids = fields.Many2many('hr.job',string="Position To")
    job_cc_ids = fields.Many2many('hr.job', 'tasks_master_rel', 'job_id', 'tasks_master_id', string="Position CC")

    is_camera_attachment = fields.Boolean(string="Camera Attachment")
    is_geo_location = fields.Boolean(string="Geo Location")
    is_hold_service = fields.Boolean(string="Hold Service")
    is_resume_service = fields.Boolean(string="Resume Service")
    is_request_to_send_quotation = fields.Boolean(string="Request to Send Quotation")
    is_request_approval = fields.Boolean(string="Request Approval")
    is_request_spares = fields.Boolean(string="Request Spares")
    is_request_raise_invoice = fields.Boolean(string="Request to Raise Invoice")
    is_inventory = fields.Boolean(string="Inventory")
    is_allow_edit_after_submit = fields.Boolean(string="Allow Edit after Submit")
    is_perform_diagnosis = fields.Boolean(string="Perform Diagnosis")
    is_perform_repair = fields.Boolean(string="Perform Repair")
    is_perform_testing = fields.Boolean(string="Perform Testing")
    is_perform_quality = fields.Boolean(string="Perform Quality")
    is_disable_status_update = fields.Boolean(string="Disable Status update")
    is_enable_status_update = fields.Boolean(string="Enable Status update")
    is_schedule = fields.Boolean(string="Schedule")
    is_ressign_engineer = fields.Boolean(string="Reassign engineer")
    is_send_email = fields.Boolean(string="Send Email")
    is_maintenance_completed = fields.Boolean(string="Maintenance Completed")
    is_check_oem_warranty = fields.Boolean(string="Check OEM Warranty")
    is_check_oem_repair_status = fields.Boolean(string="Check OEM Repair Status")

    service_request_type_id = fields.Many2one('request.type', string="Service Approval Type", copy=False)
    workflow_properties = fields.Properties('Properties',
                                           definition='team_id.workflow_properties_definition',
                                           copy=True)


    child_ticket_type_id = fields.Many2one('child.ticket.type', string="Child Ticket Type")
    python_code = fields.Char(string="Python Code")
    active = fields.Boolean("Active", default=True)
    check_extended_warranty_status = fields.Boolean("Check Extended Warranty", copy=False)
    is_work_order = fields.Boolean("Work Order", copy=False)
    is_work_end = fields.Boolean(string="Work End")
    is_repair_required = fields.Boolean(string="Repair Required")


    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Task name is already exists. Please enter any other new task name"),
    ]
    
    @api.onchange('is_inventory')
    def is_inventory_action(self):
        if not self.is_inventory:
            self.operation_type_id = False
            self.source_location_id = False
            self.destination_location_id = False
            
    def write(self, vals):
        if 'python_code' in vals and self.category == 'action' and not self.env.user.has_group('ppts_service_request.service_request_administrator'):
            raise UserError("You do not have permission to change python code")
        elif self.category == 'system' and 'category' in vals and not self.env.user.has_group('ppts_service_request.service_request_administrator'):
            raise UserError(_("You do not have permission to change the category from System Update to %s" %  dict(self._fields['category'].selection).get(vals.get('category'))))
        # complaint_type = dict(self._fields['category'].selection).get(vals.get('category'))
        rec = super().write(vals)
        return rec
      
    def unlink(self):
        if self.python_code or self.category == 'system' and not self.env.user.has_group('ppts_service_request.service_request_administrator'):
            raise UserError("You do not have permission to delete python code")
        return super().unlink()
        

class TasksMasterLine(models.Model):
    _name = 'tasks.master.line'
    _description = "Tasks Master Line"

    #Status - Function must start with (_) underscore
    def _assign_to_user(self):
        for record in self:
            return True
    
    def _request_reassign(self):
        for record in self:
            return True
    
    def _ar_hold(self):
        for record in self:
            record.parent_ticket_id.ar_hold()
    #End Status

    def button_scheduler(self):
        for record in self:
            if record.task_id:
                try:
                    value = "self._" + self.task_id.python_code + "()"
                    if value == 'self._assign_to_user()':
                        view = self.env.ref('ppts_parent_ticket.view_assign_engineer_wiz')
                        return {
                            'name': _('Assign Engineer'),
                            'type': 'ir.actions.act_window',
                            'view_mode': 'form',
                            'res_model': 'assign.engineer',
                            'view_id': view.id,
                            'target': 'new',
                        }
                    if value == 'self._request_reassign()':
                        context = {
                            "default_parent_ticket_id": self.id,
                        }
                        return {
                            'name': _('Service Request'),
                            'view_mode': 'form',
                            'res_model': 'service.request',
                            'type': 'ir.actions.act_window',
                            'target': 'new',
                            "context": context,
                        }
                    else:
                        print("\n function")
                        eval(value)
                except AttributeError:
                    raise UserError(_('Status with Action - Python Code Not Valid'))
    

    workflow_id = fields.Many2one('custom.workflow', string="Workflow")
    sequence = fields.Integer(string="Sequence",)
    task_id = fields.Many2one('tasks.master', string="Task Name", required=True)
    category = fields.Selection(related='task_id.category', string="Category")
    next_task_ids = fields.Many2many('tasks.master', string="Next Tasks", domain="[('id', '!=', task_id)]")
    status = fields.Char(string="Status")
    is_end_task = fields.Boolean(related='task_id.is_end_task', string="End Task")
    is_pi_required = fields.Boolean(related='task_id.is_pi_required', string="PI required?")
    worksheet_id = fields.Many2one(related='task_id.worksheet_id', string="Worksheet")
    is_file_attachment = fields.Boolean(related='task_id.is_file_attachment', string="Attachment")
    description = fields.Text(related='task_id.description', string="Description")
    workflow_product_properties_definition = fields.PropertiesDefinition('Product Properties')
    is_work_end = fields.Boolean(string="Work End", related='task_id.is_work_end')
    is_repair_required = fields.Boolean(related='task_id.is_repair_required', string="Repair Required")

        
        
