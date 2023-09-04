
import requests
import configparser

config = configparser.RawConfigParser()
config.read('.credentials.properties')
cred_dict = dict(config.items('CREDENTIALS'))

def init_auth():
    print("https://www.strava.com/oauth/authorize?client_id=20458&redirect_uri=http%3A%2F%2Flocalhost%3A8282%2Fauthorized&approval_prompt=auto&scope=read%2Cactivity%3Aread&response_type=code")
    code = input("Code? ")

    parameters = {
        "client_id" : cred_dict["client_id"],
        "client_secret": cred_dict["client_secret"],
        "code": code,
        "grant_type": "authorization_code"
    }

    resp  = requests.post("https://www.strava.com/api/v3/oauth/token", params=parameters)
    data = resp.json()
    return data

def refresh_token():
    parameters = {
        "client_id" : cred_dict["client_id"],
        "client_secret": cred_dict["client_secret"],
        "grant_type": "refresh_token",
        "refresh_token": cred_dict["refresh_token"]
    }
    resp  = requests.post("https://www.strava.com/api/v3/oauth/token", params=parameters)
    data = resp.json()
    return data["access_token"]

if __name__ == "__main__":
    # print(init_auth())
    token = refresh_token()
    print(token)
