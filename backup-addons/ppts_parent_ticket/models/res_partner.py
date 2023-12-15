from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    parent_ticket_ids = fields.Many2many('parent.ticket', string="Parent Tickets")
    child_ticket_ids = fields.Many2many('child.ticket', string="Child Tickets")

    def _compute_sale_order_count(self):
        res = super()._compute_sale_order_count()
        for sale in self:
            parent_ticket_ids = self.env['parent.ticket'].search(
                [('partner_id', '=', sale.id)])
            if parent_ticket_ids:
                sale.parent_ticket_ids = [(6, 0, [ticket.id for ticket in parent_ticket_ids])]
            child_ticket_ids = self.env['child.ticket'].search(
                [('partner_id', '=', sale.id)])
            if child_ticket_ids:
                sale.child_ticket_ids = [(6, 0, [ticket.id for ticket in child_ticket_ids])]
        return res
