import tweepy

from keys_and_secrets import keys_and_secrets

auth = tweepy.OAuthHandler(keys_and_secrets["consumer_key"], keys_and_secrets["consumer_secret"])
auth.set_access_token(keys_and_secrets["access_token_key"], keys_and_secrets["access_token_secret"])

api = tweepy.API(auth)


def tweet_pic(path, text=None, reply_to=None):
    api.update_with_media(path, text, in_reply_to_status_id=reply_to)


def obtain_dm():
    try:
        with open("last_id.dat", "r") as f:
            last_id = int(f.read().strip())
    except:
        last_id = 0

    todo = []
    mentions = api.mentions_timeline(since_id=last_id)
    for i in mentions:
        print("@" + i.user.screen_name, ":", i.text)
        last_id = max(i.id, last_id)
        todo.append(dict(handle=i.user.screen_name, text=i.text, id=i.id))

    with open("last_id.dat", "w") as f:
        f.write(str(last_id))

    return todo
