import requests
import configparser
from datetime import datetime
from stravalib import Client

# Configutation input
config = configparser.RawConfigParser()
config.read('.credentials.properties')
cred_dict = dict(config.items('CREDENTIALS'))

client = Client()
tokens = client.refresh_access_token(
    client_id=cred_dict["client_id"],
    client_secret=cred_dict["client_secret"],
    refresh_token=cred_dict["refresh_token"]
)
access_token = tokens["access_token"]
headers = {"Authorization": f"Bearer {access_token}"}


utc_time = datetime.strptime("2023-08-01", "%Y-%m-%d")
print(utc_time)
epoch_time = (utc_time - datetime(1970, 1, 1)).total_seconds()

parameters = {
                    #  "before": "2023-08-30T16:27:47Z",
                     "after": epoch_time,
                      "page": "1",
                      "per_page": "10"
    }

resp = requests.get("https://www.strava.com/api/v3/activities",
                         params=parameters, headers=headers)
print(resp.text)
print(resp.status_code)
activities = resp.json()