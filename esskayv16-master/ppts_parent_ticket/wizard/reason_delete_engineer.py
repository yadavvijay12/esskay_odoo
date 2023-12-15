from odoo import fields, models, api


class ReasonEngineer(models.TransientModel):
    _name = 'reason.engineer'
    _description = 'Reason'

    name = fields.Text("Reason")

    def confirm(self):
        user_id = self.env.context.get('active_id')
        active_child_id = self.env['child.ticket'].browse(int(self.env.context.get('child_id')) if self.env.context.get('child_id') else self.env.context['params']['id'])
        for record in active_child_id.child_assign_engineer_ids:
            if record.id == user_id:
                active_child_id.engineer_reason = self.name
                active_child_id.child_assign_engineer_ids = [(3, record.id)]
                break

    def Cancel(self):
        pass
