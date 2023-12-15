from odoo import fields, models, api, _
from odoo.exceptions import Warning, UserError, ValidationError


class SpareApproval(models.TransientModel):
    _name = 'spare.approval'
    _description = 'Spare Approval'

    spare_id = fields.Many2one('spare.request', string="Spare ID")
    type_id = fields.Many2one(string="Type", comodel_name="multi.approval.type", required=True)
    is_spare_approval = fields.Boolean('From Spare Approval?',
                                       help="Paasing the value to this field to check whether this field valus is passed from the spare request approval. If yes calling separate method for an approval.")

    @api.onchange('type_id')
    def _onchange_approval_type(self):
        domain = {}
        if 'ticket_model' in self.env.context and 'ticket_id' in self.env.context:
            ticket_id = self.env.context.get('ticket_id')
            ticket_model = self.env.context.get('ticket_model')
            ticket_id = self.env[ticket_model].browse(ticket_id)
            domain = [('id', 'in', ticket_id.spares_approval_team_ids.ids)]
            return {'domain': {'type_id': domain}}
        else:
            return {'domain': {'type_id': []}}

    def action_send_for_spare_approval(self):
        # When you select the type of approver, the approver has in same team, if not the approver the team show the user error
        for rec in self:
            if rec.spare_id:
                if rec.type_id.user_id.id not in rec.spare_id.team_id.member_ids.ids:
                    raise ValidationError(
                        _('This user has not mapped in team'))
        self.spare_id.action_request_approval()
        # Approval notificaion
        title = _("Request Submit!")
        message = _("Approval has been submitted successfully!")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': title, 'message': message, 'next': {'type': 'ir.actions.act_window_close'}}
        }

    def action_send_for_approval(self):
        active_id = self._context.get('active_id')
        spare = self.env['spare.request'].search([('id', '=', active_id)])
        for record in self:
            request = {
                'name': spare.name,
                'type_id': record.type_id.id or False,
                'spare_request_id': spare.id,
            }
            requests = self.env['multi.approval'].create(request)
            requests.spare_request_id = spare.id
            requests.action_submit()
            action_id = self.env.ref('multi_level_approval.multi_approval_approval_action', raise_if_not_found=False)
            template_id = self.env.ref('spare_request.spare_mail_template_notify_approvers')
            base_url = '/web#id=%d&action=%r&model=multi.approval&view_type=form' % (requests.id, action_id.id)
            mail = ''
            for lines in requests.line_ids:
                mail = lines.user_id.mapped('login')
                break
            if template_id:
                template_id.with_context(rec_url=base_url, request_name=requests.name, email_to=mail).sudo().send_mail(
                    requests.id, force_send=True)
                spare.write({'state': 'waiting_approval', 'is_send_for_approvals': True})
        title = _("Request Submit!")
        message = _("Approval has been submitted successfully!")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': title, 'message': message, 'next': {'type': 'ir.actions.act_window_close'}}
        }
