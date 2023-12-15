# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    create_new_line_at_contract_line_renew = fields.Boolean(
        help="If checked, a new line will be generated at contract line renew "
        "and linked to the original one as successor. The default "
        "behavior is to extend the end date of the contract by a new "
        "subscription period",
    )
    parent_ticket_end_time = fields.Integer(string="SR Maintenance Reminder (In days)")

    recurring_interval = fields.Integer(
        default=1,
        string="Remainder Every",
        help="Invoice every (Days/Week/Month/Year)",
    )
    recurring_rule_type = fields.Selection(
        [
            ("daily", "Day(s)"),
            ("weekly", "Week(s)"),
            ("monthly", "Month(s)"),
            ("monthlylastday", "Month(s) last day"),
            ("quarterly", "Quarter(s)"),
            ("semesterly", "Semester(s)"),
            ("yearly", "Year(s)"),
        ],
        default="monthly",
        string="Recurrence",
        help="Specify Interval for automatic invoice generation.",
    )

    service_category_id = fields.Many2one('service.category', string="Service Category", copy=False, required=True)
    service_type_id = fields.Many2one('service.type', string="Service Type", copy=False, required=True)
    request_type_id = fields.Many2one('request.type', string="Approval Type", copy=False, required=True)

