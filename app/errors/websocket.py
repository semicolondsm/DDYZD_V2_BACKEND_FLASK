def Unauthorized(msg='401: Unauthorized'):
    return {'msg': msg}
    

def NotFound(msg="404: NotFound"):
    return {'msg': msg}


def Forbidden(msg="403: Forbidden"):
    return {'msg': msg}