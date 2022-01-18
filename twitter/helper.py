from functools import lru_cache

import tweepy

from keys_and_secrets import keys_and_secrets

auth = tweepy.OAuthHandler(keys_and_secrets["consumer_key"],
                           keys_and_secrets["consumer_secret"])
auth.set_access_token(keys_and_secrets["access_token_key"],
                      keys_and_secrets["access_token_secret"])

# wait if we hit twitters rate limit (15 requests in 15 minutes)
# this way all tweets will be accepted and we have a rudimentary DOS protection
# if this bot is too successful. Twitter itself will protect us from malicious DOS
api = tweepy.API(auth, wait_on_rate_limit=True)


def tweet_pic(path, text=None, reply_to=None):
    api.update_status_with_media(status=text, filename=path, in_reply_to_status_id=reply_to)


def obtain_dm():
    try:
        with open("last_id.dat", "r") as f:
            last_id = int(f.read().strip())
    except:
        last_id = 0

    print(last_id)

    todo = []
    mentions = api.mentions_timeline(since_id=last_id)
    for i in mentions:
        if i.text[:3] == "RT ":
            # this is a retweet, ignore it
            print("ignored retweet: @" + i.user.screen_name, ":", i.text)
            continue
        print("@" + i.user.screen_name, ":", i.text)
        last_id = max(i.id, last_id)
        todo.append(dict(handle=i.user.screen_name, text=i.text, id=i.id))

    with open("last_id.dat", "w") as f:
        f.write(str(last_id))

    return todo


@lru_cache()
def get_my_user():
    return api.verify_credentials()


def get_my_handle():
    myself = get_my_user()
    return myself.screen_name


def get_my_id():
    myself = get_my_user()
    return myself.id
