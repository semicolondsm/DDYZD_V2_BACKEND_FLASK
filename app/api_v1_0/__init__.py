from flask import Blueprint

api_v1_0 = Blueprint('v1.0', __name__)

from . import chatting
from . import chathelper

@api_v1_0.route("/ping")
def ping():
    return {"msg": "ping successfully"}, 200