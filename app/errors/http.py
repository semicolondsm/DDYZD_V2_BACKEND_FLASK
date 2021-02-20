def Unauthorized(msg='Unauthorized'):
    return {'msg': msg}, 401


def Forbidden(msg='Forbidden'):
    return {'msg': msg}, 403