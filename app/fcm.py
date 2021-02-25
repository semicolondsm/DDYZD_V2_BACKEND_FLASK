from firebase_admin import credentials
from firebase_admin import messaging
from firebase_admin import datetime
from app import logger
import firebase_admin


cred = credentials.Certificate('ddyzd-firebase-adminsdk.json')
default_app = firebase_admin.initialize_app(cred)


def fcm_alarm(title, msg, token):
    aps = messaging.APNSPayload(messaging.Aps(sound="default"))
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=msg  
        ),
        apns=messaging.APNSConfig(payload=aps),
        token=token
    )
    try:
        messaging.send(message)
    except ValueError as e:
        logger.info(e)
