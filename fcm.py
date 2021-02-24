import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from firebase_admin import datetime

cred = credentials.Certificate('ddyzd-firebase-adminsdk.json')
default_app = firebase_admin.initialize_app(cred)

# This registration token comes from the cli
# ent FCM SDKs.
#registration_token = 'ANDROID_CLIENT_TOKEN'
token = 'dhaLr2D6QkCqzQcljYgFfk:APA91bGCRFToQ0gPlrnumzcpQWzeE05-BI6Jk-aOvbkWCl9RluPUdhmA9zN996W15D1M3qwipDK-ocNH3xwxA1ti0bhht9Oh5s_E1DJnkkJdMu7fOhdaJM1YduR0-HoV4KIcO-_LDnyU'
# See documentation on defining a message payload.
aps = messaging.Aps(messaging.ApsAlert(title="APs Alert Title", subtitle="APs Alert Subtitle", body="APs Alert Body"),sound="default")
aps = messaging.APNSPayload(aps, custom='data')
message = messaging.Message(
    notification=messaging.Notification(
        title='우리 수완이',
        body='화이팅',  
        ),
    # apns=messaging.APNSConfig(payload=aps),
    token=token
)
for i  in range(50):
    response = messaging.send(message)

# Send a message to the device corresponding to the provided
# registration token.
# Response is a message ID string.
print ('Successfully sent message:', response)
