"""Common methods"""
import ast
import json
import werkzeug.wrappers


def valid_response(data,message=None, status=200):
    """Valid Response
    This will be return when the http request was successfully processed."""
    return json.loads(json.dumps([
        {
        'success': True,
        # "error": False,
        'status': status,
        'message':message,
        'data': data,
    }]))

def valid_response1(data,count=0, message=None, status=200):
    """Valid Response
    This will be return when the http request was successfully processed."""
    return json.loads(json.dumps([
        {
            'success': True,
            'count':count,
            # "error": False,
            'status': status,
            'message': message,
            'data': data,
        }]))

    # return werkzeug.wrappers.Response(
    #     status=status,
    #     content_type='application/json; charset=utf-8',
    #     response=json.dumps(data),
    # )


def invalid_response(typ, message=None, status=400):
    """Invalid Response
    This will be the return value whenever the server runs into an error
    either from the client or the server."""
    return json.loads(json.dumps([
            {'success': False,
            # "error":True,
            'status': status,
            # 'type': typ,
            'message': str(message) if message else 'wrong arguments (missing validation)'}
    ]))
    # return werkzeug.wrappers.Request(
    #     status=status,
    #     content_type="application/json; charset=utf-8",
    #     response=json.dumps({
    #         "type": typ,
    #         "message": str(message) if message else "wrong arguments (missing validation)",
    #     }),
    # )


def extract_arguments(payload, offset=0, limit=0, order=None):
    """."""
    fields, domain = [], []
    if payload.get('domain'):
        domain += ast.literal_eval(payload.get('domain'))
    if payload.get('fields'):
        fields += ast.literal_eval(payload.get('fields'))
    if payload.get('offset'):
        offset = int(payload['offset'])
    if payload.get('limit'):
        limit = int(payload['limit'])
    if payload.get('order'):
        order = payload.get('order')
    return [domain, fields, offset, limit, order]
