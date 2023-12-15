from odoo import models, fields, api


class SpareDepartment(models.Model):
    _name = 'spare.department'
    _description = 'Spare Department'

    name = fields.Char(string='Name')
    sequence_id = fields.Many2one('ir.sequence', string='Department Sequence', copy=False)
    user_ids = fields.Many2many('res.users', 'department_user_rel', 'department_id', 'user_id',
                                domain=lambda self: [('groups_id', 'in', self.env.ref('base.group_user').id)],
                                string='User', copy=False)
