import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from firebase_admin import datetime

cred = credentials.Certificate('ddyzd-firebase-adminsdk.json')
default_app = firebase_admin.initialize_app(cred)

# This registration token comes from the cli
# ent FCM SDKs.
#registration_token = 'ANDROID_CLIENT_TOKEN'
token = 'fLfyEDFZAE4HuSRIIB7FuK:APA91bFdfN5CXf0Wsyjs8-vGeA0pBXo-7mGpC49BXu124s6ZIAluEC3i-pMZYEC_OtUzmZshfGyWRIEpzidHOXf5tPuIXJ-e59cvNbPdHHZ8oY4tKpEePkbarsIXgja5q1FLwVOyna85'
# See documentation on defining a message payload.
aps = messaging.Aps(messaging.ApsAlert(title="APs Alert Title", subtitle="APs Alert Subtitle", body="APs Alert Body"))
aps = messaging.APNSPayload(aps, custom='data')
message = messaging.Message(
    notification=messaging.Notification(
        title='넌',
        body='밤새 알림보낸다',
        ),
    # apns=messaging.APNSConfig(payload=aps),
    token=token
)
for i  in range(1):
    response = messaging.send(message)

# Send a message to the device corresponding to the provided
# registration token.
# Response is a message ID string.
print ('Successfully sent message:', response)
