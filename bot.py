import tweepy
import requests
import json
import gspread
# from credentials import *
# from access import access_token, access_token_secret
import random
import sys
from os import environ

consumer_key = environ['API_KEY']
bearer_token = environ['BEARER_TOKEN']
consumer_secret = environ['API_SECRET_KEY']
access_token = environ['ACCESS_TOKEN']
access_token_secret = environ['ACCESS_TOKEN_SECRET']

url = "https://docs.google.com/spreadsheets/d/11OTeOnK-QuCrvYfEiNXQ3CGOz3YOIvCzNbpomVZIi5E/htmlview"

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


def get_sheet():
    gc = gspread.service_account(filename='client_secrets.json')

    sht1 = gc.open_by_key('11OTeOnK-QuCrvYfEiNXQ3CGOz3YOIvCzNbpomVZIi5E')

    worksheet = sht1.get_worksheet(0)
    values_list = worksheet.col_values(1)[2:]
    return values_list



def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


def set_rules(delete):
    # You can adjust the rules if needed
    sample_rules = [
        {"value": ("@wgmi_bot wgmi? -is:retweet -from:wgmi_bot"), "tag": "conditions met"},
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


def get_stream(set):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream?expansions=author_id", auth=bearer_oauth, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            json_r = print(json.dumps(json_response, indent=4, sort_keys=True))
            data = json_response['data']
            username = f"@{json_response['includes']['users'][0]['username']}"
            tweet_id = int(data['id'])
            return json_r, tweet_id, username


def upload(media):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    file = media
    media_data = api.media_upload(media, media_category='tweet_gif')
    media_id = media_data.media_id
    return media_id


def tweet1(tweet_id, media_id):
    api = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret, return_type=dict)
    api.create_tweet(in_reply_to_tweet_id=tweet_id, text=f'Congratulations! You made it.\n You can confirm in: {url}', media_ids=[media_id])

def tweet2(tweet_id, media_id):
    api = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret, return_type=dict)
    api.create_tweet(in_reply_to_tweet_id=tweet_id, text="Yes, you'll make it eventually.\n Keep trying.", media_ids=[media_id])

def tweet3(tweet_id, media_id):
    api = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret, return_type=dict)
    api.create_tweet(in_reply_to_tweet_id=tweet_id, text='No.', media_ids=[media_id])

def tweet4(tweet_id, media_id):
    api = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret, return_type=dict)
    api.create_tweet(in_reply_to_tweet_id=tweet_id, text='Who knows, Maybe!?', media_ids=[media_id])
    

# def get_username(author_id):
#     user_id = author_id
#     api = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret, return_type=dict)

#     user = api.get_user(id=user_id)

#     user = user['data']['username']
#     username = f'@{user}'
#     return username


def main():
    rules = get_rules()
    delete = delete_all_rules(rules)
    set = set_rules(delete)
    sheet = get_sheet()
    rand = [0, 1, 2]
    api = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret, return_type=dict)
    while True:
        full_tweet, my_id, username = get_stream(set)
        if username in sheet:
            up = upload("in.gif")
            tweets = tweet1(my_id, up)
        else:
            twt = random.choice(rand)
            if twt == 0:
                up = upload("yes.gif")
                tweets = tweet2(my_id, up)
            elif twt == 1:
                up = upload("NO.gif")
                tweets = tweet3(my_id, up)
            elif twt == 2:
                up = upload("maybe.gif")
                tweets = tweet4(my_id, up)


if __name__ == "__main__":
    main()
