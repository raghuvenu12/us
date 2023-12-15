import twilio
from twilio.rest import Client

account_sid = 'ACb619e4e6639fea826319162fac4e585c'
auth_token = '2f06e34253eb8005ced48e0893075811'
client = Client(account_sid, auth_token)

message = client.messages.create(
    from_='+12052936739',
    to='+918095400436',
    body="sdfsdf"
)

print(message.sid)