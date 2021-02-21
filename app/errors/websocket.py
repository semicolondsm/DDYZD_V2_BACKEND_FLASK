def Unauthorized(msg='401: Unauthorized'):
    if '401' not in msg:
        msg = '401: '+ msg
    return {'msg': msg}
    

def NotFound(msg="404: NotFound"):
    if '404' not in msg:
        msg = '404: '+ msg
    return {'msg': msg}


def Forbidden(msg="403: Forbidden"):
    if '403' not in msg:
        msg = '403: '+ msg
    return {'msg': msg}


def BadRequest(msg='400: BadRequest'):
    if '400' not in msg:
        msg = '400: '+ msg
    return {'msg': msg}