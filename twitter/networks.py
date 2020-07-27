import os
import pickle

import tweepy

from .helper import api


os.makedirs("cache", exist_ok=True)

def get_followers(id):
    try:
        lst = pickle.load(open(f"cache/{id}_fo.p", "rb"))
    except:
        print("download followers", id)
        try:
            lst = [user_id for user_id in tweepy.Cursor(api.followers_ids, id=id).items()]
        except tweepy.error.TweepError as e:
            print("twitter error:", e)
            lst = []
        else:
            pickle.dump(lst, open(f"cache/{id}_fo.p", "wb"))
    else:
        print("cached followers", id)

    return lst


def get_friends(id):
    try:
        lst = pickle.load(open(f"cache/{id}_fr.p", "rb"))
    except:
        print("download friends", id)
        try:
            lst = [user_id for user_id in tweepy.Cursor(api.friends_ids, id=id).items()]
        except tweepy.error.TweepError as e:
            print("twitter error:", e)
            lst = []
        else:
            pickle.dump(lst, open(f"cache/{id}_fr.p", "wb"))
    else:
        print("cached friends", id)

    return lst


def ego_network(id=None):
    if id is None:
        id = api.me().id
    followers = set(get_followers(id))
    friends = set(get_friends(id))

    with open("ego.csv", "w") as f:
        f.write(f"source,target\n")
        for i in followers:
            f.write(f"{i},{id}\n")
        for i in friends:
            f.write(f"{id},{i}\n")

    for j in followers | friends:
        ffollowers = get_followers(j)
        ffriends = get_friends(j)

        with open("ego.csv", "a") as f:
            for i in ffollowers:
                if i in friends or i in followers:
                    f.write(f"{i},{j}\n")
            for i in ffriends:
                if i in friends or i in followers:
                    f.write(f"{j},{i}\n")
