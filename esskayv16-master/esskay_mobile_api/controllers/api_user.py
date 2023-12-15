import json
import logging
from odoo import http
from odoo.addons.esskay_mobile_api.common import invalid_response, valid_response
from odoo.http import request
from odoo.exceptions import AccessError, AccessDenied
from odoo import api, fields, models, _
import functools
_logger = logging.getLogger(__name__)

expires_in = "31536000"
magic_fields = ['__last_update','create_uid', 'create_date', 'write_uid', 'write_date','id']
def validate_token(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        params = json.loads(request.httprequest.data)
        access_token = params.get("access_token")
        login=params.get("login")
        session_id = request.httprequest.headers.get("Cookie")
        if not access_token:
            return invalid_response("access_token_not_found", "missing access token in request header", 401)
        access_token_data = (
            request.env["api.access_token"].sudo().search([("token", "=", access_token)], order="id DESC", limit=1)
        )
        if access_token_data:
            request.env.uid = access_token_data.user_id.id
            if access_token_data.user_id.login != login:
                return invalid_response("access_token miss match", "Invalid Access Token", 401)
        if access_token_data.find_one_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_response("access_token", "token seems to have expired or invalid", 401)
        # request.session.uid = access_token_data.user_id.id
        # request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)
    return wrap


class APITokenController(http.Controller):
    """."""
    def __init__(self):
        self._token = request.env["api.access_token"]
        self._expires_in = expires_in

    @http.route("/api/user/get_token",  type ='json', methods = ['POST'], auth = 'none', csrf = False)
    def token(self, **post):
        try:
            _logger.error('@ Successfully Created Token :%s', str('tessssssssssssssssssssssssss'))
            _token = request.env["api.access_token"]
            post = json.loads(request.httprequest.data)
            params = ["db", "login", "password"]
            params = {key: post.get(key) for key in params if post.get(key)}
            db, username, password = (
                request.env['res.users'].sudo()._get_db_name(),
                post.get("login"),
                post.get("password"),
            )
            _credentials_includes_in_body = all([db, username, password])
            if not _credentials_includes_in_body:
                headers = request.httprequest.headers
                db = headers.get("db")
                username = headers.get("login")
                password = headers.get("password")
                _credentials_includes_in_headers = all([db, username, password])
                if not _credentials_includes_in_headers:
                    return invalid_response(
                        "missing error", "either of the following are missing [db, username,password]", 403,
                    )
            # Login in odoo database:
            try:
                request.session.authenticate(db, username, password)
            except AccessError as aee:
                return invalid_response("Access error", "Error: %s" % aee.name)
            except AccessDenied as ade:
                return invalid_response("Access denied", "Login or password invalid.")
            except Exception as e:
                # Invalid database:
                info = "The database name is not valid {}".format((e))
                error = "invalid_database"
                _logger.error(info)
                return invalid_response("wrong database name", error, 403)

            uid = request.session.uid

            # odoo login failed:
            if not uid:
                info = "authentication failed"
                error = "authentication failed"
                _logger.error(info)
                return invalid_response(401, error, info)
            # Generate tokens
            access_token = _token.find_one_or_create_token(user_id=uid, create=True)
            # Successful response:
            user = request.env['res.users'].sudo().search([('id', '=', uid)])
            employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', uid),('company_id','=',user.company_id.id)])
            if access_token and employee_id:
                base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                base_url = base_url.replace(':8071', '')
                result = []
                image = employee_id.image_1920
                emp_image = base_url + '/web/image?' + 'model=hr.employee&id=' + str(employee_id.id) + '&field=image_1920'
                # emp_image = image.decode('UTF-8') if image else None

                attendance = request.env['hr.attendance'].sudo().search(
                    [('employee_id', '=', employee_id.id), ('check_out', '=', False)], limit=1)
                val = {
                    'uid': uid,
                    'login':username,
                    'success': True,
                    'access_token': access_token,
                    'employee_id': employee_id.id,
                    'employee_name': employee_id.name,
                    'identification_id': employee_id.identification_id if employee_id.identification_id else "",
                    'user_image': emp_image if emp_image else "",
                    'job_position': employee_id.job_id.name if employee_id.job_id else "",
                    'department': employee_id.department_id.name if employee_id.department_id else "",
                    'mobile': employee_id.phone if employee_id.phone else "",
                    'work_email': employee_id.work_email if employee_id.work_email else "",
                    'birthday': str(employee_id.birthday) if employee_id.birthday else "",
                    'street': employee_id.address_id.street if employee_id.address_id else "",
                    'street2': employee_id.address_id.street2 if employee_id.address_id else "",
                    'city': employee_id.address_id.city if employee_id.address_id else "",
                    'state': employee_id.address_id.state_id.name if employee_id.address_id.state_id else "",
                    'zip': employee_id.address_id.zip if employee_id.address_id else "",
                    'country': employee_id.address_id.country_id.name if employee_id.address_id else "",
                    'check_out' : True if attendance else False,
                    'check_in': True if not attendance else False,
                }
                result.append(val)
                _logger.error('@ Successfully Created Token :%s', str(access_token))
                return valid_response([result], 'log in successfully', 200)
                # return json.loads(json.dumps(result))
            else:
                info = "Emaployee id not found"
                error = "invalid employee id and check this user and company wise "
                return invalid_response(408, error, info)
        except Exception as e:
            result = {}
            result.update({'success': False, 'error': str(e)})
            _logger.info('@ Token Generation Error : %s',json.dumps(result))
            return json.dumps(result)

    @http.route("/api/auth/token", methods=["DELETE"], type="json", auth="none", csrf=False)
    def delete(self, **post):
        """."""
        access_token = request.httprequest.headers.get("access_token")
        access_token = self._token.search([("token", "=", access_token)])
        if not access_token:
            info = "No access token was provided in request!"
            error = "Access token is missing in the request header"
            _logger.error(info)
            return invalid_response(400, error, info)
        for token in access_token:
            token.unlink()
        # Successful response:
        return valid_response([{"desc": "access token successfully deleted", "delete": True}])
