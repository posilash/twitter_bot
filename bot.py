import requests
import json
import gspread
from credentials import *
import random
import sys


# The impoted twitter api keys from credentials.py

consumer_key = ['API_KEY']
bearer_token = ['BEARER_TOKEN']
consumer_secret = ['API_SECRET_KEY']
access_token = ['ACCESS_TOKEN']
access_token_secret = ['ACCESS_TOKEN_SECRET']

# Enter google sheets url here

google_url = ()


# Twitter Api Authorization using the Bearer Token

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


# Get and parse the google sheets file using the google cloud project api and gspread
# The client secret is stored in a json file

def get_sheet():
    gc = gspread.service_account(filename='client_secrets.json')

    sht1 = gc.open_by_key(google_cloud_project_api_key)

    worksheet = sht1.get_worksheet(0)
    values_list = worksheet.col_values(1)[2:]
    return values_list


# Get the twitter api stream function rules

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


# Flush and delete the existing twitter api stream function rules

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


"""
Set the twitter api stream function rules
For this you'll need the bot account username and the bot command
"""

def set_rules(delete):
    # You can adjust the rules if needed
    sample_rules = [
        {"value": ("@{bot_account_username} {bot_command} -is:retweet -from:{bot_account_username}"), "tag": "conditions met"},
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

    
"""
Stream live tweets from twitter
This function returns the tweet(id and the username of the tweet author
"""

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
        

# Upload image to twitter and get the media id

def upload(media):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    file = media
    media_data = api.media_upload(media, media_category='tweet_gif')
    media_id = media_data.media_id
    return media_id


""" 
Tweet functions for the various results.
This will be used to select the response based on if the account is present in the google sheets
"""

def tweet1(tweet_id, media_id):
    api = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret, return_type=dict)
    api.create_tweet(in_reply_to_tweet_id=tweet_id, text="Enter text here", media_ids=[media_id])

def tweet2(tweet_id, media_id):
    api = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret, return_type=dict)
    api.create_tweet(in_reply_to_tweet_id=tweet_id, text="Enter text here", media_ids=[media_id])
    
    
# Depending on the number of options you have

# def tweet1(tweet_id, media_id):
#     api = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret, return_type=dict)
#     api.create_tweet(in_reply_to_tweet_id=tweet_id, text="Enter text here", media_ids=[media_id])

# def tweet2(tweet_id, media_id):
#     api = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret, return_type=dict)
#     api.create_tweet(in_reply_to_tweet_id=tweet_id, text="Enter text here", media_ids=[media_id])
    
    

# This can be used to get the username of the tweet author 

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
            up = upload("image1.gif")
            tweets = tweet1(my_id, up)
        else:
            twt = random.choice(rand)
            if twt == 0:
                up = upload("image2.gif")
                tweets = tweet2(my_id, up)
                
# This depends on the number of options you have.
#             elif twt == 1:
#                 up = upload("image3.gif")
#                 tweets = tweet3(my_id, up)
#             elif twt == 2:
#                 up = upload("image4.gif")
#                 tweets = tweet4(my_id, up)


if __name__ == "__main__":
    main()
