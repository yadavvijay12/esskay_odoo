# -*- coding: utf-8 -*-
#############################################################################
#
#    Point Perfect Technology Solutions.
#
#############################################################################
import base64
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _, modules, tools
from odoo.exceptions import Warning, UserError, ValidationError


class CallSource(models.Model):
    _name = 'call.source'
    _rec_name = 'name'
    _description = "Call Source"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('call.source'))
    
    #Code Unique Constrains
    _sql_constraints = [('code_unique', 'unique(code)','Code already exists!')]
    
class ServiceCategory(models.Model):
    _name = 'service.category'
    _rec_name = 'name'
    _description = "Service Category"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('service.category'))
    category_type = fields.Selection([
        ('is_amc', 'AMC Services'),
        ('is_cmc', 'CMC Services'),
        ('is_warranty', 'Warranty Based Services'),
        ('is_repair_warranty', 'Repair Warranty Based Services'),
        ('is_extended_warranty', 'Extended Warranty Based Services'),
        ('is_paid', 'Paid Services'),
        ('is_billable', 'Billable Services'),
        ('is_installable', 'Installation Call')
    ],
        string="Type",
        help="Specify ticket type",
    )
    
    #Code Unique Constrains
    _sql_constraints = [('code_unique', 'unique(code)','Code already exists!')]
    
class ServiceType(models.Model):
    _name = 'service.type'
    _rec_name = 'name'
    _description = "Service Type"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('service.type'))
    service_category_ids = fields.Many2many('service.category', string="Service Category")
    request_type_ids = fields.Many2many('request.type', string='Approval Types')
    ticket_type = fields.Selection([
        ('sr_loaner', 'SR-Loaner'),
        ('sr_wr', 'SR-WR'),
        ('sr_factory_repair', 'SR-Factory Repair'),
        ('sr_fsm', 'SR-FSM'),
        ('sr_installation', 'SR-Installation'),
        ('sr_maintenance', 'SR-Maintenance'),
        ('sr_remote_support', 'SR-Remote Support'),
        ('sr_survey_escalation', 'SR-Survey Escalation'),
        ('so_call', 'SO Call')
    ],
        string="Ticket Type",
        help="Specify ticket type",
        required=True
    )

    
    #Code Unique Constrains
    _sql_constraints = [('code_unique', 'unique(code)','Code already exists!')]
    

class RequestType(models.Model):
    _name = 'request.type'
    _rec_name = 'name'
    _description = "Request Type"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('request.type'))
    team_id = fields.Many2one('crm.team', string='Team', copy=False, domain="[('is_service_request', '=', True)]", required=True)
    is_required_approval = fields.Boolean('Approval Required?', copy=False, help='If this enabled then the approval process will be enabled in service support')
    ticket_type = fields.Selection([
        ('sr_loaner', 'SR-Loaner'),
        ('sr_wr', 'SR-WR'),
        ('sr_factory_repair', 'SR-Factory Repair'),
        ('sr_fsm', 'SR-FSM'),
        ('sr_installation', 'SR-Installation'),
        ('sr_maintenance', 'SR-Maintenance'),
        ('sr_remote_support', 'SR-Remote Support'),
        ('sr_survey_escalation', 'SR-Survey Escalation'),
        ('so_call', 'SO Call')
    ],
        string="Ticket Type",
        help="Specify ticket type",
    ) #Kathir
    image_icon = fields.Binary(string="icon")
    is_auto_approval = fields.Boolean('Automatic Approval', copy=False, help='If this enabled then the approval process will be automatic in service support')
    assigned_count = fields.Integer(compute='_get_assigned_ticket_count', string='Assigned Tickets')
    unassigned_count = fields.Integer(compute='_get_unassigned_ticket_count', string='Assigned Tickets')
    closed_count = fields.Integer(compute='_get_closed_ticket_count', string='Closed Tickets')
    rejected_count = fields.Integer(compute='_get_rejected_ticket_count', string='Rejected Tickets')
    ticket_type_image = fields.Binary(String='Ticket Type Image')

    @api.onchange('ticket_type_image','ticket_type')
    def onchange_ticket_type_image(self):
        if self.ticket_type_image:
            ticket_type = self.search([('ticket_type', '=', self.ticket_type)])
            ticket_type.ticket_type_image = self.ticket_type_image

    @api.onchange('ticket_type')
    def request_get_image(self):
        image_path = None
        if self.ticket_type == 'sr_loaner':
            image_path = modules.get_module_resource('ppts_service_request', 'static/src/img', 'loaner.png')
        elif self.ticket_type == 'sr_wr':
            image_path = modules.get_module_resource('ppts_service_request', 'static/src/img','replacement.png')
        elif self.ticket_type == 'sr_factory_repair':
            image_path = modules.get_module_resource('ppts_service_request', 'static/src/img','factory_repair.png')
        elif self.ticket_type == 'sr_fsm':
            image_path = modules.get_module_resource('ppts_service_request', 'static/src/img', 'fsm.png')
        elif self.ticket_type == 'sr_installation':
            image_path = modules.get_module_resource('ppts_service_request', 'static/src/img','installation.png')
        elif self.ticket_type == 'sr_maintenance':
            image_path = modules.get_module_resource('ppts_service_request', 'static/src/img','maintenance.png')
        elif self.ticket_type == 'sr_remote_support':
            image_path = modules.get_module_resource('ppts_service_request', 'static/src/img', 'remote.png')
        elif self.ticket_type == 'so_call':
            image_path = modules.get_module_resource('ppts_service_request', 'static/src/img', 'call.png')
        else:
            image_path = modules.get_module_resource('ppts_service_request', 'static/src/img', 'survey.png')
        if image_path:
            self.image_icon = base64.b64encode(open(image_path, 'rb').read())

    
    def get_closed_tickets(self):
        return {
            'name': "closed",
            'type': 'ir.actions.act_window',
            'domain': [('request_type_id', '=', self.id), ('state', '=', 'closed')],
            'view_mode': 'tree,form',
            'res_model': 'parent.ticket',
        }
    
    def get_rejected_tickets(self):
        return {
            'name': "Rejected",
            'type': 'ir.actions.act_window',
            'domain': [('request_type_id', '=', self.id), ('state', '=', 'rejected')],
            'view_mode': 'tree,form',
            'res_model': 'parent.ticket',
        }
    
    def assigned_tickets(self):
        return {
            'name': "Assigned Engineer",
            'type': 'ir.actions.act_window',
            'domain': [('request_type_id', '=', self.id), ('child_assign_engineer_ids', '!=', False)],
            'view_mode': 'tree,form',
            'res_model': 'child.ticket',
        }
    
    def unassigned_tickets(self):
        return {
            'name': "Unassigned Engineer",
            'type': 'ir.actions.act_window',
            'domain': [('request_type_id', '=', self.id), ('child_assign_engineer_ids', '=', False)],
            'view_mode': 'tree,form',
            'res_model': 'child.ticket',
        }
    
    def _get_assigned_ticket_count(self):
        for record in self:
            record.assigned_count = self.env['child.ticket'].search_count(
                [('request_type_id', '=', record.id), ('child_assign_engineer_ids', '!=', False)])
    
    def _get_unassigned_ticket_count(self):
        for record in self:
            record.unassigned_count = self.env['child.ticket'].search_count(
                [('request_type_id', '=', record.id), ('child_assign_engineer_ids', '=', False)])
    
    def _get_closed_ticket_count(self):
        for record in self:
            record.closed_count = self.env['parent.ticket'].search_count(
                [('request_type_id', '=', record.id), ('state', '=', 'closed')])
    
    def _get_rejected_ticket_count(self):
        for record in self:
            record.rejected_count = self.env['parent.ticket'].search_count(
                [('request_type_id', '=', record.id), ('state', '=', 'rejected')])
    
    @api.onchange('is_required_approval')
    def onchange_approval(self):
        if not self.is_required_approval:
            self.is_auto_approval = False
    
    def _get_action(self, action_xmlid):
        action = self.env["ir.actions.actions"]._for_xml_id(action_xmlid)
        if self:
            action['display_name'] = self.display_name
        
        return action
    
    def overview_ticket_request_type(self):
        for record in self:
            return {
                'name': "Loaner Request with Approval",
                'type': 'ir.actions.act_window',
                'domain': [('request_type_id', '=', record.id)],
                'view_mode': 'tree,form',
                'res_model': 'parent.ticket',
            }
    
    #Code Unique Constrains
    _sql_constraints = [('code_unique', 'unique(code)','Code already exists!')]
    
class CallReceived(models.Model):
    _name = 'call.received'
    _rec_name = 'name'
    _description = "Call Received"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('call.received'))
    
    #Code Unique Constrains
    _sql_constraints = [('code_unique', 'unique(code)','Code already exists!')]

class BioMedicalEngineer(models.Model):
    _name = 'bio.medical.engineer'
    _rec_name = 'name'
    _description = "Bio Medical Engineer"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('bio.medical.engineer'))
    
    #Code Unique Constrains
    _sql_constraints = [('code_unique', 'unique(code)','Code already exists!')]
    

class ServiceRequestStatus(models.Model):
    _name = 'service.request.status'
    _rec_name = 'name'
    _description = "Service Request Status"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('service.request.status'))
    
    #Code Unique Constrains
    _sql_constraints = [('code_unique', 'unique(code)','Code already exists!')]
    

class Dispatchlocation(models.Model):
    _name = 'dispatch.location'
    _rec_name = 'name'
    _description = "Dispatch location"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('dispatch.location'))
    
    #Code Unique Constrains
    _sql_constraints = [('code_unique', 'unique(code)','Code already exists!')]
    

class OEMWarrantyStatus(models.Model):
    _name = 'oem.warranty.status'
    _rec_name = 'name'
    _description = "OEM Warranty Status"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('oem.warranty.status'))
    
    #Code Unique Constrains
    _sql_constraints = [('code_unique', 'unique(code)','Code already exists!')]
    
class RepairWarrantyStatus(models.Model):
    _name = 'repair.warranty.status'
    _rec_name = 'name'
    _description = "Repair Warranty Status"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('repair.warranty.status'))
    
    #Code Unique Constrains
    _sql_constraints = [('code_unique', 'unique(code)','Code already exists!')]

class RepairCenterLocation(models.Model):
    _name = 'repair.center.location'
    _rec_name = 'name'
    _description = "Repair Center Location"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('repair.center.location'))
    
    #Code Unique Constrains
    _sql_constraints = [('code_unique', 'unique(code)','Code already exists!')]


class CaseCompletedSuccessfully(models.Model):
    _name = 'case.completed.successfully'
    _rec_name = 'name'
    _description = "Was the case completed successfully"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('case.completed.successfully'))
    
    #Code Unique Constrains
    _sql_constraints = [('code_unique', 'unique(code)','Code already exists!')]
    
class MedicalIntervention(models.Model):
    _name = 'medical.intervention'
    _rec_name = 'name'
    _description = "Was medical intervention needed"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('medical.intervention'))
    
    #Code Unique Constrains
    _sql_constraints = [('code_unique', 'unique(code)','Code already exists!')]

class PatientInvolved(models.Model):
    _name = 'patient.involved'
    _rec_name = 'name'
    _description = "Was a patient involved"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('patient.involved'))
    
    #Code Unique Constrains
    _sql_constraints = [('code_unique', 'unique(code)','Code already exists!')]
    
class SurgicalDelay(models.Model):
    _name = 'surgical.delay'
    _rec_name = 'name'
    _description = "Was there a surgical delay"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('surgical.delay'))
    
    #Code Unique Constrains
    _sql_constraints = [('code_unique', 'unique(code)','Code already exists!')]

class ChildTicketType(models.Model):
    _name = 'child.ticket.type'
    _rec_name = 'name'
    _description = "Child Ticket Type"

    code = fields.Char(string="Code", size=4, required=True)
    name = fields.Char(string="Name", required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('child.ticket.type'))
    
    #Code Unique Constrains
    _sql_constraints = [('code_unique', 'unique(code)','Code already exists!')]
