from datetime import datetime
from datetime import timedelta

def isoformat(date):
    try:
        date = date = date.strftime('%Y-%m-%dT%H:%M:%S')+'.000+09:00'
    except:
        date = None
    return date


def kstnow():
    return datetime.utcnow()+timedelta(hours=9)