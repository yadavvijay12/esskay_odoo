# Copyright PPTS

import logging

from odoo import Command, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.translate import _
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    contract_id = fields.Many2one('contract.contract', copy=False, string='Contract')
    ticket_creation_date = fields.Date('Automatic Ticket Creation Date', copy=False)

    def action_create_service_ticket(self,):
        return {
            'name': _('Service Ticket'),
            'view_mode': 'form',
            'domain': [],
            'res_model': 'service.request',
            'type': 'ir.actions.act_window',
            'context': {'default_customer_name': self.contract_id.partner_id.name, 'default_partner_id': self.contract_id.partner_id.id,
                        'default_street': self.contract_id.partner_id.street, 'default_phone': self.contract_id.partner_id.phone, 'default_mobile': self.contract_id.partner_id.mobile,
                        'default_email': self.contract_id.partner_id.email, 'default_contract_id':self.contract_id.id},
        }

    def service_ticket_creation(self, record):
        asset_ids = []
        for asset in record.contract_id.contract_line_fixed_ids:
            vals = (0, 0, {'stock_lot_id': asset.stock_lot_id.id, 'product_id': asset.product_id.id})
            asset_ids.append(vals)
        data = {
            'is_from_ct': False,
            'service_request_date': datetime.today(),
            'customer_name': record.contract_id.partner_id.name,
            'customer_email': record.contract_id.partner_id.email,
            'partner_id': record.contract_id.partner_id.id,
            'request_type_id': record.contract_id.user_id.company_id.request_type_id.id or False,
            'team_id': record.contract_id.user_id.team_ids[0].id or False,
            'service_category_id': record.contract_id.user_id.company_id.service_category_id.id or False,
            'service_type_id': record.contract_id.user_id.company_id.service_type_id.id or False,
            'contract_id': record.contract_id.id or False,
            'customer_asset_ids': asset_ids,
            'calendar_event_id': record.id,
            'user_id': record.contract_id.user_id.id,
            'company_id': record.contract_id.user_id.company_id.id
        }
        service_id = self.env['service.request'].create(data)
        service_id._onchange_partner()

    def create_service_request(self):
        for record in self.search([('contract_id', '!=',None)]):
            if not self.env['service.request'].search([('calendar_event_id', '=',record.id)]):
                if record.contract_id.partner_id.customer_account_id.automatic_ticket_creation:
                    date_today = fields.Date.to_date(fields.Date.today() - timedelta(days=record.contract_id.partner_id.customer_account_id.automatic_ticket_creation))
                    ticket_date = datetime.strftime(record.start, '%d-%m-%Y')
                    today_date = datetime.strftime(date_today, '%d-%m-%Y')
                    if ticket_date == today_date:
                        self.service_ticket_creation(record)

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            if record.contract_id.partner_id.customer_account_id.automatic_ticket_creation:
                date_today = fields.Date.to_date(fields.Date.today() - timedelta(
                    days=record.contract_id.partner_id.customer_account_id.automatic_ticket_creation))
                ticket_date = datetime.strftime(record.start, '%d-%m-%Y')
                today_date = datetime.strftime(date_today, '%d-%m-%Y')
                if ticket_date == today_date:
                    self.service_ticket_creation(record)
        return res

class ContractContract(models.Model):
    _name = "contract.contract"
    _description = "Contract"
    _order = "code, name asc"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "contract.abstract.contract",
        "contract.recurrency.mixin",
        "portal.mixin",
    ]

    active = fields.Boolean(
        default=True,
    )
    code = fields.Char(
        string="Reference",
    )
    group_id = fields.Many2one(
        string="Group",
        comodel_name="account.analytic.account",
        ondelete="restrict",
    )
    currency_id = fields.Many2one(
        compute="_compute_currency_id",
        inverse="_inverse_currency_id",
        comodel_name="res.currency",
        string="Currency",
    )
    manual_currency_id = fields.Many2one(
        comodel_name="res.currency",
        readonly=True,
    )
    contract_template_id = fields.Many2one(
        string="Contract Template", comodel_name="contract.template"
    )
    contract_line_ids = fields.One2many(
        string="Contract lines",
        comodel_name="contract.line",
        inverse_name="contract_id",
        copy=True,
    )
    # Trick for being able to have 2 different views for the same o2m
    # We need this as one2many widget doesn't allow to define in the view
    # the same field 2 times with different views. 2 views are needed because
    # one of them must be editable inline and the other not, which can't be
    # parametrized through attrs.
    contract_line_fixed_ids = fields.One2many(
        string="Contract lines (fixed)",
        comodel_name="contract.line",
        inverse_name="contract_id",
    )

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        index=True,
        default=lambda self: self.env.user,
    )
    create_invoice_visibility = fields.Boolean(
        compute="_compute_create_invoice_visibility"
    )
    date_end = fields.Date(compute="_compute_date_end", store=True, readonly=False)
    payment_term_id = fields.Many2one(
        comodel_name="account.payment.term", string="Payment Terms", index=True
    )
    invoice_count = fields.Integer(compute="_compute_invoice_count")
    fiscal_position_id = fields.Many2one(
        comodel_name="account.fiscal.position",
        string="Fiscal Position",
        ondelete="restrict",
    )
    invoice_partner_id = fields.Many2one(
        string="Invoicing contact",
        comodel_name="res.partner",
        ondelete="restrict",
        domain="['|',('id', 'parent_of', partner_id), ('id', 'child_of', partner_id)]",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner", inverse="_inverse_partner_id", required=True
    )

    commercial_partner_id = fields.Many2one(
        "res.partner",
        compute_sudo=True,
        related="partner_id.commercial_partner_id",
        store=True,
        string="Commercial Entity",
        index=True,
    )
    tag_ids = fields.Many2many(comodel_name="contract.tag", string="Tags")
    note = fields.Text(string="Notes")
    is_terminated = fields.Boolean(string="Terminated", readonly=True, copy=False)
    terminate_reason_id = fields.Many2one(
        comodel_name="contract.terminate.reason",
        string="Termination Reason",
        ondelete="restrict",
        readonly=True,
        copy=False,
        tracking=True,
    )
    terminate_comment = fields.Text(
        string="Termination Comment",
        readonly=True,
        copy=False,
        tracking=True,
    )
    terminate_date = fields.Date(
        string="Termination Date",
        readonly=True,
        copy=False,
        tracking=True,
    )
    modification_ids = fields.One2many(
        comodel_name="contract.modification",
        inverse_name="contract_id",
        string="Modifications",
    )
    #custom fields
    state = fields.Selection(
        selection=[
            ('new', "New"),
            ('started', "Started"),
            ('to_renew', " To Renew"),
            ('approved', "Approved"),
            ('rejected', "Rejected"),
            ('send_for_approval', 'Send for Approval'),
            ('cancelled', "Cancelled"),
            ('completed', "Completed"),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='new')
    # Fields added based on Contracts Sheet
    contract_seq = fields.Char('Sequence', copy=False, readonly=True, default=lambda x: _('New'))
    contract_alias = fields.Text(string='Contract ID Alias')
    contract_created_date = fields.Date(string='Contract Created Date', readonly=True, default=datetime.today())
    contract_date = fields.Date(string='Contract Date', default=datetime.today())
    delivery_partner_id = fields.Many2one(string='Delivery Address', comodel_name="res.partner", ondelete="restrict",
                                          domain="['|',('id', 'parent_of', partner_id), ('id', 'child_of', partner_id)]")
    custom_contract_type = fields.Selection([('amc', 'AMC'), ('cmc', 'CMC'), ('both', 'Both AMC/CMC'), ('warranty', 'Warranty PM')], string='Contract Type', required=True)
    recurring_contract = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Recurring Contract')
    customer_account_id = fields.Many2one('res.partner', string="Customer Account")
    service_count = fields.Integer(string="Service Count", compute='compute_service_count')
    recurring_sr_next_date = fields.Date(string="Date of Next Action")
    maintenance_interval_line = fields.One2many('maintenance.contract.intervals', 'contract_id', string='Contract Intervals')
    request_type_id = fields.Many2one('request.type', string="Approval Type", copy=False, domain="[('ticket_type', '=', 'sr_maintenance')]")
    is_contract_maintenance = fields.Boolean(string="Maintenance Created", copy=False)
    sale_id = fields.Many2one('sale.order', string="Quotation Reference", copy=False)
    customer_contract_ref = fields.Char(string="Customer Contract Reference", copy=False)
    inco_terms_id = fields.Many2one('account.incoterms', string="Inco-terms", copy=False)
    delivery_terms_id = fields.Char(string="Delivery terms", copy=False)
    external_ref = fields.Char(string="External Reference", copy=False)
    location_id = fields.Many2one('asset.location', string="Location", copy=False)
    recurring_contract_percentage = fields.Integer( string="Recurring Contract % Increase", copy=False)
    billing_cycle = fields.Char( string="Billing Cycle", copy=False)
    so_ref = fields.Char(string="Sales Order Reference", copy=False)
    ccc_ref = fields.Many2one('sale.order', string="Cost Center Contract/SO Reference", copy=False)
    custom_attachment_ids = fields.Many2many('ir.attachment', 'contract_contract_attachment_rel', 'contract_contract_id',
                                      'attachment_id', 'Attachments',
                                      help="You may attach files to this Contract, to be added to all ")

    # This field is used for the renewal of the contract

    is_require_renewal = fields.Boolean('Waiting for Renewal')
    is_require_cancel = fields.Boolean('Waiting for Cancellation')
    approvals_count = fields.Integer(string='Approval Count', compute='_compute_approvals_count')

    # Automatic schedule creation
    schedule_creation_interval = fields.Integer(
        default=1,
        string="Automatic Schedule Creation",
        help="Create SR every (Days/Week/Month/Year)",
    )
    schedule_creation_rule_type = fields.Selection(
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
    meeting_ids = fields.Many2many('calendar.event', readonly=True)


    def _compute_approvals_count(self):
        for record in self:
            record.approvals_count = self.env['multi.approval'].search_count([('contract_id', '=', record.id)])


    def action_view_approvals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send for Approvals',
            'view_mode': 'tree,form',
            'res_model': 'multi.approval',
            'domain': [('contract_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def start_end_date(self):
        date_filter = self.search([('date_end', '<', date.today()), ('state', '!=', 'to_renew')])
        date_filter.state = 'to_renew'

    # This method is used to schedule the calendar from the contract
    def action_create_schedule(self):
        if not self.env['calendar.event'].search([('contract_id', '=',self.id)]):
            interval = self.schedule_creation_interval
            if self.schedule_creation_rule_type == "daily":
                interval_unit = relativedelta(days=interval)
            elif self.schedule_creation_rule_type == "weekly":
                interval_unit = relativedelta(weeks=interval)
            elif self.schedule_creation_rule_type == "monthly":
                interval_unit = relativedelta(months=interval)
            elif self.schedule_creation_rule_type == "monthlylastday":
                interval_unit = relativedelta(months=interval, day=1)
            elif self.schedule_creation_rule_type == "quarterly":
                interval_unit = relativedelta(months=3 * interval)
            elif self.schedule_creation_rule_type == "semesterly":
                interval_unit = relativedelta(months=6 * interval)
            else:
                interval_unit = relativedelta(years=interval)
            if not self.date_end:
                raise UserError('End date is not mapped on this contract. Select the end date to generate the schedule.')
            interval_dates = []  # All Interval Dates in List
            current_date = self.date_start
            # loop based on the company configuration int field.
            date_maintenance = current_date
            while date_maintenance < self.date_end:
                # interval_dates.append(current_date)
                interval_dates.append(date_maintenance.strftime('%Y-%m-%d'))
                date_maintenance += interval_unit
            event_ids = []
            for interval_date in interval_dates:
                event_id = self.env['calendar.event'].create({'name': 'Preventive Maintenance planned for ' + str(self.partner_id.name),
                                                'partner_ids':[(4, self.env.user.partner_id.id)],
                                                'start': interval_date,
                                                'stop': interval_date,
                                                'contract_id':self.id
                                                })
                event_ids.append(event_id.id)
            self.meeting_ids = [[4, record] for record in event_ids]
        else:
            raise ValidationError(_('Already schedule has been generated. Please delete all the records before generating new schedule for this contract.'))
    def _update_status_as_start(self):
        date_filter =  self.search([('date_start', '<=', date.today()),('date_end', '>=', date.today()), ('state', '=', 'approved')])
        date_filter.state = 'started'
    
    def get_formview_id(self, access_uid=None):
        if self.contract_type == "sale":
            return self.env.ref("contract.contract_contract_customer_form_view").id
        else:
            return self.env.ref("contract.contract_contract_supplier_form_view").id

    # @api.model_create_multi
    # def create(self, vals_list):
    #     records = super().create(vals_list)
    #     records._set_start_contract_modification()
    #     return records

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('contract_seq') or vals['contract_seq'] == _('New'):
                vals['contract_seq'] = self.env['ir.sequence'].next_by_code('contract.contract')
                vals['line_recurrence'] = False
        records = super().create(vals_list)
        records._set_start_contract_modification()
        return records

    def send_for_approval(self):
        if not self.contract_line_fixed_ids:
            raise UserError(_("Please Select Contract Products"))
        return {
            'name': _('Send for Approval'),
            'view_mode': 'form',
            'res_model': 'contract.ticket.approval',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def generate_maintenance_intervals(self):
        """Return a relativedelta for one period.

        When added to the first day of the period,
        it gives the first day of the next period.
        """
        self.maintenance_interval_line = None
        interval = self.recurring_interval
        if self.recurring_rule_type == "daily":
            interval_unit = relativedelta(days=interval)
        elif self.recurring_rule_type == "weekly":
            interval_unit = relativedelta(weeks=interval)
        elif self.recurring_rule_type == "monthly":
            interval_unit = relativedelta(months=interval)
        elif self.recurring_rule_type == "monthlylastday":
            interval_unit = relativedelta(months=interval, day=1)
        elif self.recurring_rule_type == "quarterly":
            interval_unit = relativedelta(months=3 * interval)
        elif self.recurring_rule_type == "semesterly":
            interval_unit = relativedelta(months=6 * interval)
        else:
            interval_unit = relativedelta(years=interval)

        interval_dates = []  # All Interval Dates in List
        current_date = self.date_start
        # loop based on the company configuration int field.
        date_maintenance = current_date - timedelta(days=int(self.company_id.parent_ticket_end_time))
        while date_maintenance < self.date_end:
            # interval_dates.append(current_date)
            interval_dates.append(date_maintenance.strftime('%Y-%m-%d'))
            date_maintenance += interval_unit

    
        self.maintenance_interval_line = [(0, 0, {'contract_id': self.id, 'interval_date': interval_date}) for interval_date in interval_dates]
        self.is_contract_maintenance = True
        self.state = 'started'

    def action_create_sr_maintenance(self):
        # request_id = self.env['request.type'].search([('ticket_type', '=', 'sr_maintenance')], limit=1)
        context = {
            'contract_id': self.id,
            'service_request_id_alias': self.contract_alias,
            'customer_name': self.partner_id.name,
            'partner_id': self.partner_id.id or False,
            'request_type_id': self.request_type_id.id or False,
            'team_id': self.request_type_id.team_id.id or False,
            'external_reference': self.code,
            'customer_asset_ids': [(0, 0, {
                'stock_lot_id': line.stock_lot_id.id,
                'product_id': line.product_id.id,
                'notes': line.name,
            }) for line in self.contract_line_fixed_ids],
        }
        self.env['service.request'].create(context)

    def action_view_service_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Request',
            'view_mode': 'tree,form',
            'res_model': 'service.request',
            'domain': [('contract_id', '=', self.id)],
            'context': "{'create': False}"
        }
    
    def compute_service_count(self):
        for record in self:
            record.service_count = self.env['service.request'].search_count([('contract_id', '=', record.id)])

    def write(self, vals):
        if "modification_ids" in vals:
            res = super(
                ContractContract, self.with_context(bypass_modification_send=True)
            ).write(vals)
            self._modification_mail_send()
        else:
            res = super(ContractContract, self).write(vals)
        return res

    @api.model
    def _set_start_contract_modification(self):
        subtype_id = self.env.ref("contract.mail_message_subtype_contract_modification")
        for record in self:
            if record.contract_line_ids:
                date_start = min(record.contract_line_ids.mapped("date_start"))
            else:
                date_start = record.create_date
            record.message_subscribe(
                partner_ids=[record.partner_id.id], subtype_ids=[subtype_id.id]
            )
            record.with_context(skip_modification_mail=True).write(
                {
                    "modification_ids": [
                        (0, 0, {"date": date_start, "description": _("Contract start")})
                    ]
                }
            )

    @api.model
    def _modification_mail_send(self):
        for record in self:
            modification_ids_not_sent = record.modification_ids.filtered(
                lambda x: not x.sent
            )
            if modification_ids_not_sent:
                if not self.env.context.get("skip_modification_mail"):
                    record.with_context(
                        default_subtype_id=self.env.ref(
                            "contract.mail_message_subtype_contract_modification"
                        ).id,
                    ).message_post_with_template(
                        self.env.ref("contract.mail_template_contract_modification").id,
                        email_layout_xmlid="contract.template_contract_modification",
                    )
                modification_ids_not_sent.write({"sent": True})

    def _compute_access_url(self):
        for record in self:
            record.access_url = "/my/contracts/{}".format(record.id)

    def action_preview(self):
        """Invoked when 'Preview' button in contract form view is clicked."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "target": "self",
            "url": self.get_portal_url(),
        }

    def _inverse_partner_id(self):
        for rec in self:
            if not rec.invoice_partner_id:
                rec.invoice_partner_id = rec.partner_id.address_get(["invoice"])[
                    "invoice"
                ]

    def _get_related_invoices(self):
        self.ensure_one()

        invoices = (
            self.env["account.move.line"]
            .search(
                [
                    (
                        "contract_line_id",
                        "in",
                        self.contract_line_ids.ids,
                    )
                ]
            )
            .mapped("move_id")
        )
        # we are forced to always search for this for not losing possible <=v11
        # generated invoices
        invoices |= self.env["account.move"].search([("old_contract_id", "=", self.id)])
        return invoices

    def _get_computed_currency(self):
        """Helper method for returning the theoretical computed currency."""
        self.ensure_one()
        currency = self.env["res.currency"]
        if any(self.contract_line_ids.mapped("automatic_price")):
            # Use pricelist currency
            currency = (
                self.pricelist_id.currency_id
                or self.partner_id.with_company(
                    self.company_id
                ).property_product_pricelist.currency_id
            )
        return currency or self.journal_id.currency_id or self.company_id.currency_id

    @api.depends(
        "manual_currency_id",
        "pricelist_id",
        "partner_id",
        "journal_id",
        "company_id",
    )
    def _compute_currency_id(self):
        for rec in self:
            if rec.manual_currency_id:
                rec.currency_id = rec.manual_currency_id
            else:
                rec.currency_id = rec._get_computed_currency()

    def _inverse_currency_id(self):
        """If the currency is different from the computed one, then save it
        in the manual field.
        """
        for rec in self:
            if rec._get_computed_currency() != rec.currency_id:
                rec.manual_currency_id = rec.currency_id
            else:
                rec.manual_currency_id = False

    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec._get_related_invoices())

    def action_show_invoices(self):
        self.ensure_one()
        tree_view = self.env.ref("account.view_invoice_tree", raise_if_not_found=False)
        form_view = self.env.ref("account.view_move_form", raise_if_not_found=False)
        ctx = dict(self.env.context)
        if ctx.get("default_contract_type"):
            ctx["default_move_type"] = (
                "out_invoice"
                if ctx.get("default_contract_type") == "sale"
                else "in_invoice"
            )
        action = {
            "type": "ir.actions.act_window",
            "name": "Invoices",
            "res_model": "account.move",
            "view_mode": "tree,kanban,form,calendar,pivot,graph,activity",
            "domain": [("id", "in", self._get_related_invoices().ids)],
            "context": ctx,
        }
        if tree_view and form_view:
            action["views"] = [(tree_view.id, "tree"), (form_view.id, "form")]
        return action

    @api.depends("contract_line_ids.date_end")
    def _compute_date_end(self):
        for contract in self:
            contract.date_end = False
            date_end = contract.contract_line_ids.mapped("date_end")
            if date_end and all(date_end):
                contract.date_end = max(date_end)

    @api.depends(
        "contract_line_ids.recurring_next_date",
        "contract_line_ids.is_canceled",
    )
    # pylint: disable=missing-return
    def _compute_recurring_next_date(self):
        for contract in self:
            recurring_next_date = contract.contract_line_ids.filtered(
                lambda l: (
                    l.recurring_next_date
                    and not l.is_canceled
                    and (not l.display_type or l.is_recurring_note)
                )
            ).mapped("recurring_next_date")
            # we give priority to computation from date_start if modified
            if (
                contract._origin
                and contract._origin.date_start != contract.date_start
                or not recurring_next_date
            ):
                super(ContractContract, contract)._compute_recurring_next_date()
            else:
                contract.recurring_next_date = min(recurring_next_date)

    @api.depends("contract_line_ids.create_invoice_visibility")
    def _compute_create_invoice_visibility(self):
        for contract in self:
            contract.create_invoice_visibility = any(
                contract.contract_line_ids.mapped("create_invoice_visibility")
            )

    @api.onchange("contract_template_id")
    def _onchange_contract_template_id(self):
        """Update the contract fields with that of the template.

        Take special consideration with the `contract_line_ids`,
        which must be created using the data from the contract lines. Cascade
        deletion ensures that any errant lines that are created are also
        deleted.
        """
        contract_template_id = self.contract_template_id
        if not contract_template_id:
            return
        for field_name, field in contract_template_id._fields.items():
            if field.name == "contract_line_ids":
                lines = self._convert_contract_lines(contract_template_id)
                self.contract_line_ids += lines
            elif not any(
                (
                    field.compute,
                    field.related,
                    field.automatic,
                    field.readonly,
                    field.company_dependent,
                    field.name in self.NO_SYNC,
                )
            ):
                if self.contract_template_id[field_name]:
                    self[field_name] = self.contract_template_id[field_name]

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        partner = (
            self.partner_id
            if not self.company_id
            else self.partner_id.with_company(self.company_id)
        )
        self.pricelist_id = partner.property_product_pricelist.id
        self.fiscal_position_id = partner.env[
            "account.fiscal.position"
        ]._get_fiscal_position(partner)
        self.customer_account_id = partner.customer_account_id
        self.delivery_partner_id = partner.id
        if self.contract_type == "purchase":
            self.payment_term_id = partner.property_supplier_payment_term_id
        else:
            self.payment_term_id = partner.property_payment_term_id
        self.invoice_partner_id = self.partner_id.address_get(["invoice"])["invoice"]

    def _convert_contract_lines(self, contract):
        self.ensure_one()
        new_lines = self.env["contract.line"]
        contract_line_model = self.env["contract.line"]
        for contract_line in contract.contract_line_ids:
            vals = contract_line._convert_to_write(contract_line.read()[0])
            # Remove template link field
            vals.pop("contract_template_id", False)
            vals["date_start"] = fields.Date.context_today(contract_line)
            vals["recurring_next_date"] = fields.Date.context_today(contract_line)
            new_lines += contract_line_model.new(vals)
        new_lines._onchange_is_auto_renew()
        return new_lines

    def _prepare_invoice(self, date_invoice, journal=None):
        """Prepare the values for the generated invoice record.

        :return: A vals dictionary
        """
        self.ensure_one()
        if not journal:
            journal = (
                self.journal_id
                if self.journal_id.type == self.contract_type
                else self.env["account.journal"].search(
                    [
                        ("type", "=", self.contract_type),
                        ("company_id", "=", self.company_id.id),
                    ],
                    limit=1,
                )
            )
        if not journal:
            raise ValidationError(
                _(
                    "Please define a %(contract_type)s journal "
                    "for the company '%(company)s'."
                )
                % {
                    "contract_type": self.contract_type,
                    "company": self.company_id.name or "",
                }
            )
        invoice_type = (
            "in_invoice" if self.contract_type == "purchase" else "out_invoice"
        )
        vals = {
            "move_type": invoice_type,
            "company_id": self.company_id.id,
            "partner_id": self.invoice_partner_id.id,
            "ref": self.code,
            "currency_id": self.currency_id.id,
            "invoice_date": date_invoice,
            "journal_id": journal.id,
            "invoice_origin": self.name,
            "invoice_line_ids": [],
        }
        if self.payment_term_id:
            vals.update(
                {
                    "invoice_payment_term_id": self.payment_term_id.id,
                }
            )
        if self.fiscal_position_id:
            vals.update(
                {
                    "fiscal_position_id": self.fiscal_position_id.id,
                }
            )
        if invoice_type == "out_invoice" and self.user_id:
            vals.update(
                {
                    "invoice_user_id": self.user_id.id,
                }
            )
        return vals

    def action_contract_send(self):
        self.ensure_one()
        template = self.env.ref("contract.email_contract_template", False)
        compose_form = self.env.ref("mail.email_compose_message_wizard_form")
        ctx = dict(
            default_model="contract.contract",
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode="comment",
        )
        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }

    @api.model
    def _get_contracts_to_invoice_domain(self, date_ref=None):
        """
        This method builds the domain to use to find all
        contracts (contract.contract) to invoice.
        :param date_ref: optional reference date to use instead of today
        :return: list (domain) usable on contract.contract
        """
        domain = []
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        domain.extend([("recurring_next_date", "<=", date_ref)])
        return domain

    def _get_lines_to_invoice(self, date_ref):
        """
        This method fetches and returns the lines to invoice on the contract
        (self), based on the given date.
        :param date_ref: date used as reference date to find lines to invoice
        :return: contract lines (contract.line recordset)
        """
        self.ensure_one()

        def can_be_invoiced(contract_line):
            return (
                not contract_line.is_canceled
                and contract_line.recurring_next_date
                and contract_line.recurring_next_date <= date_ref
            )

        lines2invoice = previous = self.env["contract.line"]
        current_section = current_note = False
        for line in self.contract_line_ids:
            if line.display_type == "line_section":
                current_section = line
            elif line.display_type == "line_note" and not line.is_recurring_note:
                if line.note_invoicing_mode == "with_previous_line":
                    if previous in lines2invoice:
                        lines2invoice |= line
                    current_note = False
                elif line.note_invoicing_mode == "with_next_line":
                    current_note = line
            elif line.is_recurring_note or not line.display_type:
                if can_be_invoiced(line):
                    if current_section:
                        lines2invoice |= current_section
                        current_section = False
                    if current_note:
                        lines2invoice |= current_note
                    lines2invoice |= line
                    current_note = False
            previous = line
        return lines2invoice.sorted()

    def _prepare_recurring_invoices_values(self, date_ref=False):
        """
        This method builds the list of invoices values to create, based on
        the lines to invoice of the contracts in self.
        !!! The date of next invoice (recurring_next_date) is updated here !!!
        :return: list of dictionaries (invoices values)
        """
        invoices_values = []
        for contract in self:
            if not date_ref:
                date_ref = contract.recurring_next_date
            if not date_ref:
                # this use case is possible when recurring_create_invoice is
                # called for a finished contract
                continue
            contract_lines = contract._get_lines_to_invoice(date_ref)
            if not contract_lines:
                continue
            invoice_vals = contract._prepare_invoice(date_ref)
            invoice_vals["invoice_line_ids"] = []
            for line in contract_lines:
                invoice_line_vals = line._prepare_invoice_line()
                if invoice_line_vals:
                    # Allow extension modules to return an empty dictionary for
                    # nullifying line. We should then cleanup certain values.
                    if "company_id" in invoice_line_vals:
                        del invoice_line_vals["company_id"]
                    if "company_currency_id" in invoice_line_vals:
                        del invoice_line_vals["company_currency_id"]
                    invoice_vals["invoice_line_ids"].append(
                        Command.create(invoice_line_vals)
                    )
            invoices_values.append(invoice_vals)
            # Force the recomputation of journal items
            contract_lines._update_recurring_next_date()
        return invoices_values

    def recurring_create_invoice(self):
        """
        This method triggers the creation of the next invoices of the contracts
        even if their next invoicing date is in the future.
        """
        invoice = self._recurring_create_invoice()
        if invoice:
            self.message_post(
                body=_(
                    "Contract manually invoiced: "
                    "<a"
                    '    href="#" data-oe-model="%(model_name)s" '
                    '    data-oe-id="%(rec_id)s"'
                    ">Invoice"
                    "</a>"
                )
                % {
                    "model_name": invoice._name,
                    "rec_id": invoice.id,
                }
            )
        return invoice

    @api.model
    def _invoice_followers(self, invoices):
        invoice_create_subtype = self.env.ref(
            "contract.mail_message_subtype_invoice_created"
        )
        for item in self:
            partner_ids = item.message_follower_ids.filtered(
                lambda x: invoice_create_subtype in x.subtype_ids
            ).mapped("partner_id")
            if partner_ids:
                (invoices & item._get_related_invoices()).message_subscribe(
                    partner_ids=partner_ids.ids
                )

    @api.model
    def _add_contract_origin(self, invoices):
        for item in self:
            for move in invoices & item._get_related_invoices():
                move.message_post(
                    body=(
                        _(
                            (
                                "%(msg)s by contract <a href=# data-oe-model=contract.contract"
                                " data-oe-id=%(contract_id)d>%(contract)s</a>."
                            ),
                            msg=move._creation_message(),
                            contract_id=item.id,
                            contract=item.display_name,
                        )
                    )
                )

    def _recurring_create_invoice(self, date_ref=False):
        invoices_values = self._prepare_recurring_invoices_values(date_ref)
        moves = self.env["account.move"].create(invoices_values)
        self._add_contract_origin(moves)
        self._invoice_followers(moves)
        self._compute_recurring_next_date()
        return moves

    @api.model
    def _get_recurring_create_func(self, create_type="invoice"):
        """
        Allows to retrieve the recurring create function depending
        on generate_type attribute
        """
        if create_type == "invoice":
            return self.__class__._recurring_create_invoice

    @api.model
    def _cron_recurring_create(self, date_ref=False, create_type="invoice"):
        """
        The cron function in order to create recurrent documents
        from contracts.
        """
        _recurring_create_func = self._get_recurring_create_func(
            create_type=create_type
        )
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        domain = self._get_contracts_to_invoice_domain(date_ref)
        domain = expression.AND(
            [
                domain,
                [("generation_type", "=", create_type)],
            ]
        )
        contracts = self.search(domain)
        companies = set(contracts.mapped("company_id"))
        # Invoice by companies, so assignation emails get correct context
        for company in companies:
            contracts_to_invoice = contracts.filtered(
                lambda c: c.company_id == company
                and (not c.date_end or c.recurring_next_date <= c.date_end)
            ).with_company(company)
            _recurring_create_func(contracts_to_invoice, date_ref)
        return True

    @api.model
    def cron_recurring_create_invoice(self, date_ref=None):
        return self._cron_recurring_create(date_ref, create_type="invoice")

    def action_expired_contract(self):
        self.ensure_one()
        context = {"default_contract_id": self.id}
        return {
            "type": "ir.actions.act_window",
            "name": _("Expired Contract"),
            "res_model": "contract.contract.terminate",
            "view_mode": "form",
            "target": "new",
            "context": context,
        }

    def action_terminate_contract(self):
        self.ensure_one()
        context = {"default_contract_id": self.id, 'default_is_renewal':True}
        return {
            "type": "ir.actions.act_window",
            "name": _("Renew Contract"),
            "res_model": "contract.contract.terminate",
            "view_mode": "form",
            "target": "new",
            "context": context,
        }

    def action_send_for_approval(self, contract_id, approval_request_id):
        request = {
            'name': contract_id.name,
            'type_id': approval_request_id.id or False,
        }
        requests = self.env['multi.approval'].create(request)
        requests.action_submit()
        requests.contract_id = contract_id.id
        action_id = self.env.ref('multi_level_approval.multi_approval_approval_action',
                                 raise_if_not_found=False)
        template_id = self.env.ref('contract.contract_mail_template_notify_approvers')
        base_url = '/web#id=%d&action=%r&model=multi.approval&view_type=form' % (approval_request_id.id, action_id.id)
        mail = ''
        for lines in approval_request_id.line_ids:
            mail = lines.user_id.mapped('login')
            break
        if template_id:
            template_id.with_context(rec_url=base_url, email_to=mail).sudo().send_mail(requests.id,
                                                                                           force_send=True)
        contract_id.state = 'send_for_approval'

    def _terminate_contract(self, terminate_reason_id, terminate_comment, terminate_date):
        self.ensure_one()
        if 'is_renewal' in self.env.context and 'send_for_approval' in self.env.context:
            self.write(
                {
                    "is_require_renewal": True,
                    "terminate_reason_id": terminate_reason_id.id,
                    "terminate_comment": terminate_comment,
                    "terminate_date": terminate_date,
                })
            contract_id = self.env.context.get('contract_id')
            approval_request_id = self.env.context.get('approval_request_id')
            self.action_send_for_approval(contract_id, approval_request_id)
        elif 'is_renewal' in self.env.context and 'send_for_approval' not in self.env.context:
            self.write(
                {
                    "date_end": terminate_date,
                    'state':'started',
                    'is_terminated':False
                })

        elif 'is_cancel' in self.env.context and 'send_for_approval' in self.env.context:
            self.write(
                {
                    "is_require_cancel": True,
                    "terminate_reason_id": terminate_reason_id.id,
                    "terminate_comment": terminate_comment,
                    "terminate_date": terminate_date,
                })
            contract_id = self.env.context.get('contract_id')
            approval_request_id = self.env.context.get('approval_request_id')
            self.action_send_for_approval(contract_id, approval_request_id)
        elif 'is_cancel' in self.env.context and 'send_for_approval' not in self.env.context:
            self.write(
                {
                    'state':'cancelled',
                    'is_terminated':False
                })
        else:
            if not self.env.user.has_group("contract.can_terminate_contract"):
                raise UserError(_("You are not allowed to terminate contracts."))
            self.contract_line_ids.filtered("is_stop_allowed").stop(terminate_date)
            self.write(
                {
                    "is_terminated": True,
                    "terminate_reason_id": terminate_reason_id.id,
                    "terminate_comment": terminate_comment,
                    "terminate_date": terminate_date,
                    "state": 'completed',
                }
            )
        return True

    def action_cancel_contract_termination(self):
        self.ensure_one()
        context = {"default_contract_id": self.id, 'default_is_cancel': True}
        return {
            "type": "ir.actions.act_window",
            "name": _("Cancel Contract"),
            "res_model": "contract.contract.terminate",
            "view_mode": "form",
            "target": "new",
            "context": context,
        }


class ServiceRequest(models.Model):
    _inherit = 'service.request'

    contract_id = fields.Many2one("contract.contract", string="Contract", required=True)
    calendar_event_id = fields.Many2one("calendar.event", string="Calendar", copy=False)
    

class MaintenanceContractIntervals(models.Model):
    _name = 'maintenance.contract.intervals'
    _description = 'Maintenance Contract Intervals'

    @api.depends('contract_id')
    def _sequence_generation(self):
        no = 0
        self.sequence = no
        for line in self.contract_id.maintenance_interval_line:
            no += 1
            line.sequence = no
    
    name = fields.Char(string="Maintenance Contract Intervals")
    contract_id = fields.Many2one("contract.contract", string="Contract", ondelete="cascade")
    sequence = fields.Integer(string='Sequence', compute='_sequence_generation')
    interval_date = fields.Datetime(string='Interval Date')
    is_created = fields.Boolean(string="Is Done")

    def create_maintenance_sr_cron(self):
        now = fields.Datetime.now()
        records = self.env['maintenance.contract.intervals'].search([('is_created', '=', False), ('interval_date', '<=', now)])
        for record in records:
            if record:
                context = {
                    'contract_id': record.contract_id.id,
                    'service_request_id_alias': record.contract_id.contract_alias,
                    'customer_name': record.contract_id.partner_id.name,
                    'partner_id': record.contract_id.partner_id.id or False,
                    'request_type_id': record.contract_id.request_type_id.id or False,
                    'team_id': record.contract_id.request_type_id.team_id.id or False,
                    'external_reference': record.contract_id.code,
                    'customer_asset_ids': [(0, 0, {
                        'stock_lot_id': line.stock_lot_id.id,
                        'product_id': line.product_id.id,
                        'notes': line.name,
                    }) for line in record.contract_id.contract_line_fixed_ids],
                }
                self.env['service.request'].create(context)
                record.is_created = True
                contract = self.env['contract.contract'].search([('maintenance_interval_line', '=', record.id)],limit=1)
                if contract and all(contract.maintenance_interval_line.mapped('is_created')):
                    contract.state = 'completed'
