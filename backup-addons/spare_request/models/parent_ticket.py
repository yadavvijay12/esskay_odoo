from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class ParentTicketInherit(models.Model):
    _inherit = "parent.ticket"

    spare_request_ids = fields.Many2many('spare.request', string="Spare Request", compute='_compute_spare_request_line')
    is_create_spare_request = fields.Boolean(string="Create Spare Request")

    # @api.depends('event_type_id')
    def _compute_spare_request_line(self):
        lists = []
        for record in self:
            spare_ids = self.env["spare.request"].search([("parent_ticket_id", "=", record.id)])
            if spare_ids:
                record.spare_request_ids = spare_ids.ids
            else:
                record.spare_request_ids = None

    @api.onchange('task_list_ids')
    def _onchange_task_list_ids(self):
        res = super(ParentTicketInherit, self)._onchange_task_list_ids()
        for record in self:
            spare_request = record.task_list_ids.task_id.filtered(lambda r: r.python_code == 'spare_request')
            if spare_request:
                record.is_create_spare_request = True
            else:
                record.is_create_spare_request = False
        return res

    def action_spare_request(self):
        # self.is_spare_request = False
        # raise ValidationError(_("Please select the Spare Parts."))

        # if not self.asset_ids:
        #  raise ValidationError(_("Please select the Spare Parts."))
        self.ensure_one()
        context = {
            "default_name": "Spare Request",
            "default_is_spare_request": True,
            "default_parent_ticket_id": self.id or False,
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
            'domain': [('parent_ticket_id', '=', self.id)],
            'context': "{'create': False}"
        }


class Request(models.Model):
    _inherit = 'request'
    _description = "Request"

    spare_request_id = fields.Many2one('spare.request', string="Spare Request", copy=False)

    @api.model
    def create(self, vals):
        result = super(Request, self).create(vals)

        if vals.get('is_spare_request'):
            mails = ''
            subject = ''
            partner = self.env["res.partner"].search([("id", "=", vals.get('partner_id'))], limit=1)
            stock_checking = partner.customer_account_id.stock_checking_process_ids.filtered(
                lambda l: l.request_type == 'spare_parts')
            if stock_checking.stock_request_type == 'external':
                mails = partner.customer_account_id.email
                subject = 'External'

                # Task Update For External Process
                task_id = self.env.ref('spare_request.task_data_spare_request')
                # PT
                if result.parent_ticket_id:
                    result.parent_ticket_id.update({
                        'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                    })

                # CT
                if result.child_ticket_id:
                    result.child_ticket_id.update({
                        'task_list_ids': [(0, 0, {'task_id': task_id.id})],
                    })
            else:
                teams = result.sudo().parent_ticket_id and result.sudo().parent_ticket_id.assign_engineer_ids.mapped(
                    'login') or result.sudo().child_ticket_id and result.sudo().child_ticket_id.parent_ticket_id.assign_engineer_ids.mapped(
                    'login')
                mails += ', '.join(teams)
                subject = 'Internal'
            action_id = self.env.ref('ppts_parent_ticket.action_request', raise_if_not_found=False)
            template_id = self.env.ref('spare_request.mail_template_external_stock_check_spare')
            base_url = '/web#id=%d&cids=1&action=%r&model=request&view_type=form' % (result.id, action_id.id)
            if template_id:
                template_id.with_context(email_to=mails, subject=subject, rec_url=base_url).sudo().send_mail(result.id,
                                                                                                             force_send=True)
        return result
