from odoo import models, fields, api, _


class AssetHistoricalData(models.Model):
    _name = 'assets.historical.data'
    _description = "Asset Historical Data"
    _order = 'id'

    name = fields.Char(string='Asset Historical Data', copy=False, default="01")
    ref_ticket_id = fields.Many2one(comodel_name='child.ticket', string="Reference", ondelete='cascade', index=True,
                                    copy=False)
    ref_id = fields.Many2one(comodel_name='stock.lot', string="Assets Reference", ondelete='cascade', index=True,
                             copy=False)
    # TICKET DETAIL
    service_request_id = fields.Many2one('service.request', string="Service Request ID", copy=False)
    parent_ticket_id = fields.Many2one('parent.ticket', string="Parent Ticket ID", copy=False)
    child_ticket_id = fields.Many2one('child.ticket', string="Child Ticket ID", copy=False)
    # FROM JOB CLOSED STATUS
    problem_description = fields.Char(string='Problem Description')
    recommendation_customer = fields.Char(string='Recommendation to Customers')
    customer_remarks = fields.Char(string='Customer Remarks')
    action_taken = fields.Char(string='Action taken')
    final_report_comments = fields.Char(string='Final report(Comments)')
    company_id = fields.Many2one(comodel_name='res.company', default=lambda self: self.env.company)
