from odoo import models, fields, api, _

class CrmTeam(models.Model):
    _inherit = 'crm.team'
    _description = "Sales Team"

    is_service_request = fields.Boolean('Service Team', copy=False, help='If this field is enabled then this team will be available to select in service request.')
    customer_type = fields.Selection(
        [('stryker', 'Stryker'), ('epson', 'Epson'), ('termo_fisher', 'Thermofisher'), ('rational', 'Rational')],
        string='Web Form')
    customer_account_ids = fields.Many2many('res.partner',
                                            string='Customer Accounts')
 # domain="[('customer_account_id', '=', False),('customer_type_partner', '=',customer_type )]"

    @api.onchange('customer_type')
    def check_customer_type(self):
        domain = []
        cust = []
        if self.customer_type:
            customers = self.env['res.partner'].search([('customer_type_partner', '=', self.customer_type), ('customer_account_id', '=', False)])
            for rec in customers:
                cust.append(rec.id)
            domain = {'customer_account_ids': [('id', 'in', cust)]}
        return {'domain': domain}




class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def read_user_tickets(self, user_id=None):
        service_request_ticket_ids = None
        team_ids, customer_accounts = self.env.user.read_user_teams(is_user_tickets=True)
        # service_request_ticket_ids = self.env['service.request'].search(
        #     [('team_id', 'in', tuple(team_ids)), ('customer_account_id', 'in', tuple(customer_accounts))])
        service_request_ticket_ids = self.env['service.request'].search(
            [('team_id', 'in', tuple(team_ids))])
        service_request_ticket_ids += self.env['service.request'].search([('team_id', '=', False)])
        if service_request_ticket_ids:
            return service_request_ticket_ids.ids
        else:
            return False

    @api.model
    def read_user_teams(self, user_id=None, is_user_tickets=False):
        team_ids = [];
        customer_accounts = [];
        for team in self.env['crm.team'].search([]):
            if self.env.user.id in team.member_ids.ids:
                team_ids.append(team.id)
                customer_accounts += tuple(team.customer_account_ids.ids)
            if self.env.user.id == team.user_id.id and self.env.user.id not in team_ids:
                team_ids.append(team.id)
                customer_accounts += tuple(team.customer_account_ids.ids)
        if team_ids and not is_user_tickets:
            return team_ids
        elif team_ids and is_user_tickets:
            return team_ids, customer_accounts
        else:
            return False
