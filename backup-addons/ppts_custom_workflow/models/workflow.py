from odoo import models, fields, api, _


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