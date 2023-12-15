# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import api, fields, models


class ChangeApprover(models.TransientModel):
    _name = 'change.approver'
    _description = 'Change Approver'

    new_pic_id = fields.Many2one(
        string="New Approver",
        comodel_name="res.users",
        required=True,
    )
    reason = fields.Text(string='Reason', required=True)
    group_ids = fields.Many2many(
        string="Deputy Groups",
        comodel_name="res.groups"
    )

    @api.model
    def default_get(self, fs):
        '''
        '''
        res = super(ChangeApprover, self).default_get(fs)
        ctx = self._context
        model_name = ctx.get('active_model')
        res_id = ctx.get('active_id')
        if model_name == 'multi.approval':
            request = self.env[model_name].browse(res_id)
            line_name = request.mapped('line_id.name')
            line_name = line_name and line_name[0] or None
            type_line = request.type_id.line_ids.filtered(lambda x: x.name == line_name)
            if type_line:
                res.update({'group_ids': type_line.mapped('group_ids.id')})
        return res

    def action_update(self):
        '''
        '''
        self.ensure_one()
        ctx = self._context
        if ctx.get('active_model') != 'multi.approval':
            return False
        request_ids = ctx.get('active_ids', [])
        requests = self.env[ctx['active_model']].search(
            [('id', 'in', request_ids), ('state', '=', 'Submitted')]
        )
        if not requests:
            return False
        requests.message_post(body=self.reason)
        vals = {'user_id': self.new_pic_id.id}
        lines = requests.mapped('line_id')
        lines.write(vals)
