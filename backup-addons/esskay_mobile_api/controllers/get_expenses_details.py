from odoo.addons.esskay_mobile_api.controllers.api_user import validate_token,magic_fields
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response
from odoo import http
from odoo.http import request

class APIController(http.Controller):

    @validate_token
    @http.route("/api/get_expenses_details", type="json", auth="none", methods=["POST"], csrf=False)
    def _api_get_expenses_details(self, **post,):
        uid = request.session.uid
        hr_expense_obj = request.env['hr.expense']
        hr_expense = hr_expense_obj.sudo().search_read([('employee_id.user_id', '=', uid)],fields=['name','state','product_id','total_amount','currency_id','tax_ids','company_id','employee_id','payment_mode','amount_tax'])
        for rec in hr_expense:
            expenses = hr_expense_obj.sudo().browse(rec.get('id'))
            rec['date'] = str(expenses.date)
        if hr_expense:
            return valid_response([hr_expense], 'Expenses loaded successfully', 200)
        else:
            return valid_response(hr_expense, 'there is no Expenses', 200)

