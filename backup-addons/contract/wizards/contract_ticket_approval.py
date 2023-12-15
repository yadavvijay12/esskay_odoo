from odoo import api, models, fields, _

class MultiApproval(models.Model):
    _inherit = 'multi.approval'

    contract_id = fields.Many2one('contract.contract', string='Contract')

    def action_approve(self):
        values = super().action_approve()
        if self.contract_id.id:
            if self.state == 'Refused':
                self.contract_id.state = 'rejected'
            elif self.state == 'Approved' and self.contract_id.is_require_renewal:
                self.contract_id.state = 'approved'
                self.contract_id.date_end = self.contract_id.terminate_date
                self.contract_id.is_terminated = False
                self.contract_id.is_require_renewal = False
            elif self.state == 'Approved' and self.contract_id.is_require_cancel:
                self.contract_id.is_terminated = False
                self.contract_id.state = 'cancelled'
                self.contract_id.is_require_cancel = False
            elif self.state == 'Approved':
                self.contract_id.state = 'approved'
        return values


class ContractTicketApproval(models.TransientModel):
    _name = 'contract.ticket.approval'

    type_id = fields.Many2one(string="Type", comodel_name="multi.approval.type", required=True)

    def action_send_for_approval(self):
        active_id = self._context.get('active_id')
        contract_id = self.env['contract.contract'].browse(active_id)
        for record in self:
            request = {
                'name': contract_id.name,
                'type_id': record.type_id.id or False,
            }
            requests = self.env['multi.approval'].create(request)
            requests.action_submit()
            requests.contract_id = contract_id.id
            action_id = self.env.ref('multi_level_approval.multi_approval_approval_action',
                                     raise_if_not_found=False)
            template_id = self.env.ref('ppts_parent_ticket.pt_mail_template_notify_approvers')
            base_url = '/web#id=%d&action=%r&model=multi.approval&view_type=form' % (requests.id, action_id.id)
            mail = ''
            for lines in requests.line_ids:
                mail = lines.user_id.mapped('login')
                break
            if template_id:
                template_id.with_context(rec_url=base_url, email_to=mail).sudo().send_mail(requests.id,
                                                                                               force_send=True)
            contract_id.state = 'send_for_approval'