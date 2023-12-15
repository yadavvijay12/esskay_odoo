from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class ChildTicketInherit(models.Model):
    _inherit = "child.ticket"

    spare_request_ids = fields.Many2many('spare.request', string="Spare Request", compute='_compute_spare_request_line')
    is_create_spare_request = fields.Boolean(string="Create Spare Request")

    # @api.depends('event_type_id')
    def _compute_spare_request_line(self):
        lists = []
        for record in self:
            spare_ids = self.env["spare.request"].search([("child_ticket_id", "=", record.id)])
            if spare_ids:
                record.spare_request_ids = spare_ids.ids
            else:
                record.spare_request_ids = None

    @api.onchange('task_list_ids')
    def _onchange_task_list_ids(self):
        res = super(ChildTicketInherit, self)._onchange_task_list_ids()
        for record in self:
            spare_request = record.task_list_ids.task_id.filtered(lambda r: r.python_code == 'spare_request')
            if spare_request:
                record.is_create_spare_request = True
            else:
                record.is_create_spare_request = False
        return res


    def action_spare_request(self):
        self.ensure_one()
        context = {
            "default_name": "Spare Request",
            "default_is_spare_request": True,
            "default_child_ticket_id": self.id or False,
            "default_team_id": self.team_id.id,
            "default_user_id": self.env.user.id,
            "default_partner_id": self.partner_id.id,
        }
        context.update(self.env.context)
        return {
            'name': "Request",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'request',
            "target": "new",
            "context": context,
        }

    def view_spare_request(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Spare Request',
            'view_mode': 'tree,form',
            'res_model': 'spare.request',
            'domain': [('child_ticket_id', '=', self.id)],
            'context': "{'create': False}"
        }
