from odoo import fields, models, api, _

from odoo.exceptions import ValidationError, Warning


class ReopenTicket(models.TransientModel):
    _name = 'reopen.ticket'

    name = fields.Char("Ref")
    ticket_type = fields.Selection([('child', 'Child'), ('parent', 'Parent')], string="Ticket Type", required=True)
    child_ticket_id = fields.Many2one('child.ticket', "Child Ticket") 
    service_request_id = fields.Many2one('service.request', "Service Request")
    parent_ticket_id = fields.Many2one('parent.ticket', "Parent Ticket")

    def reopen_ticket(self):
        ticket_id = self.parent_ticket_id if self.ticket_type == 'parent' else self.child_ticket_id
        if ticket_id.state != 'closed':
            raise ValidationError(_("Ticket %s is already open", ticket_id.name))
        else:
            if self.ticket_type == 'child' and self.child_ticket_id:
                self.child_ticket_id.write({'state': 'esc_new',
                                            'survey_sent': False})
            if self.ticket_type == 'parent' and self.parent_ticket_id:
                self.parent_ticket_id.write({'state': 'esc_new',
                                             'survey_sent': False})

    @api.onchange('ticket_type')
    def _onchange_ticket(self):
        if self.ticket_type == 'child':
            return {'domain': {'child_ticket_id': [('id', '=', self.service_request_id.child_ticket_id.id)]}}
        elif self.ticket_type == 'parent':
            return {'domain': {'parent_ticket_id': [('id', '=', self.service_request_id.parent_ticket_id.id)]}}