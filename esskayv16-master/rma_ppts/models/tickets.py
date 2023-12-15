from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ChildTicketInherit(models.Model):
    _inherit = "child.ticket"

    is_create_repair = fields.Boolean(string="Is Create Repair", copy=False)
    is_repair_created = fields.Boolean(string="Is Repair Created")
    repair_id = fields.Many2one('crm.claim.ppts', string="Repair ID")
    repair_count = fields.Integer(compute='_count_total_repair')
    repair_ids = fields.Many2many('crm.claim.ppts', string="Repair", compute='_compute_repair_line')

    @api.onchange('task_list_ids')
    def _onchange_task_list_ids(self):
        res = super(ChildTicketInherit, self)._onchange_task_list_ids()
        for record in self:
            mr = record.task_list_ids.task_id.filtered(lambda r: r.python_code == 'perform_repair')
            if mr:
                record.is_create_repair = True
            else:
                record.is_create_repair = False
        return res

    def _compute_repair_line(self):
        for record in self:
            repair_ids = self.env["crm.claim.ppts"].search([("child_ticket_id", "=", record.id)])
            if repair_ids:
                record.repair_ids = repair_ids.ids
            else:
                record.repair_ids = None

    # Smart Button - Maintenance
    def action_view_repair(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Repair',
            'view_mode': 'tree',
            'views': [(self.env.ref('rma_ppts.crm_claims_ppts_tree_view').id, 'tree'),
                      (self.env.ref('rma_ppts.crm_claims_ppts_form_view').id, 'form')],
            'res_model': 'crm.claim.ppts',
            'domain': [('child_ticket_id', '=', self.sudo().id)],
            'context': "{'create': False}"
        }

    def _count_total_repair(self):
        for record in self:
            record.repair_count = self.env['crm.claim.ppts'].sudo().search_count(
                [('child_ticket_id', '=', record.id)])

    def action_perform_repair(self):
        if not self.sudo().parent_ticket_id.inward_picking_ids.ids:
            raise UserError(_("There is no Inward Transfer to perform Repair!"))
        if not self.stock_lot_id:
            raise UserError(_("Please Select Asset Serial No"))
        record = {
            "name": self.name + " Ticket Repair Order",
            "user_id": self.env.user.id,
            "child_ticket_id": self.id or False,
            "partner_id": self.partner_id.id,
            "section_id": self.team_id.id,
            "team_id": self.team_id.id,
            "picking_id": self.sudo().parent_ticket_id.inward_picking_ids.ids[0],
        }
        record = self.env['crm.claim.ppts'].create(record)
        view = self.env.ref("rma_ppts.crm_claims_ppts_form_view")
        self.is_repair_created = True
        return {
            'type': 'ir.actions.act_window',
            'name': 'Repair',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view.id,
            'res_model': 'crm.claim.ppts',
            'res_id': record.id,
            'target': 'current',
            'domain': [('child_ticket_id', '=', self.sudo().id)],
        }
