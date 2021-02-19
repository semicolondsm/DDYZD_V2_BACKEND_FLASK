def Unauthorized(msg='401: Unauthorized'):
    return {'msg': msg}


def ExpiredSignatureError(msg='401: ExpiredSignatureError'):
    return {'msg': msg}