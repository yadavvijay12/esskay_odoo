from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class Workflow(models.Model):
    _name = "custom.workflow"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = "Custom Workflow Module"

    name = fields.Char(string="Name", required=True)
    task_list_ids = fields.One2many('tasks.master.line', 'workflow_id', string="Task Lists", copy=True)
    description = fields.Html(string="Description")
    active = fields.Boolean(string='active', default=True)

    # _sql_constraints = [
    #     ('name_uniq', 'unique (name)', "Workflow name is already exists. Please enter new workflow name."),
    # ]

    def copy(self, default=None):
        """This method sets a name + (copy) in name."""
        old_name = self.browse(self.id)
        default = dict(default or {}, name=_('%s (copy)') % old_name.name)
        result = super().copy(default)
        return result

    @api.model
    def create(self, vals):
        result = super().create(vals)
        if not result.task_list_ids.filtered(lambda r: r.task_id.name == 'Work End'):
            raise UserError('Please add Work End Status.')
        pi_required = result.task_list_ids.filtered(lambda r: r.task_id.name == 'PI Required')
        if len(pi_required) > 1:
            raise UserError('You Are Not Allowed To Add Same PI Required Again')
        pi_not_required = result.task_list_ids.filtered(lambda r: r.task_id.name == 'PI Not Required')
        if len(pi_not_required) > 1:
            raise UserError('You Are Not Allowed To Add Same PI Not Required Again')
        return result

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            if not record.task_list_ids.filtered(lambda r: r.task_id.name == 'Work End'):
                raise UserError('Please add Work End Status.')
            pi_required = record.task_list_ids.filtered(lambda r: r.task_id.name == 'PI Required')
            if len(pi_required) > 1:
                raise UserError('You Are Not Allowed To Add Same PI Required Again')
            pi_not_required = record.task_list_ids.filtered(lambda r: r.task_id.name == 'PI Not Required')
            if len(pi_not_required) > 1:
                raise UserError('You Are Not Allowed To Add Same PI Not Required Again')
        return res
