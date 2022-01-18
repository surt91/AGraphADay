import os
import pickle

import tweepy

from .helper import api
from twitter import helper


os.makedirs("cache", exist_ok=True)


def get_followers(id):
    try:
        lst = pickle.load(open(f"cache/{id}_fo.p", "rb"))
    except:
        print("download followers", id)
        try:
            lst = [user_id for user_id in tweepy.Cursor(api.get_follower_ids, user_id=id).items()]
        except tweepy.errors.TweepyException as e:
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
            lst = [user_id for user_id in tweepy.Cursor(api.get_friend_ids, user_id=id).items()]
        except tweepy.errors.TweepyException as e:
            print("twitter error:", e)
            lst = []
        else:
            pickle.dump(lst, open(f"cache/{id}_fr.p", "wb"))
    else:
        print("cached friends", id)

    return lst


def get_list_members(list_id):
    try:
        lst = pickle.load(open(f"cache/list_{list_id}.p", "rb"))
    except:
        print("download list members", list_id)
        try:
            users = tweepy.Cursor(api.get_list_members, list_id=list_id).items()
            lst = [user.id for user in tweepy.Cursor(api.get_list_members, list_id=list_id).items()]
        except tweepy.errors.TweepyException as e:
            print("twitter error:", e)
            lst = []
        else:
            pickle.dump(lst, open(f"cache/list_{list_id}.p", "wb"))
    else:
        print("cached list_members", list_id)

    try:
        with open("list_nodes.csv", "w") as f:
            for u in users:
                f.write(f"{u.id},@{u.screen_name}\n")
    except:
        pass

    return lst


def ego_network(id=None):
    if id is None:
        id = helper.get_my_id()
    followers = set(get_followers(id))
    friends = set(get_friends(id))

    with open("ego.csv", "w") as f:
        f.write("source,target\n")
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


def list_network(list_id=1393908329584398340):
    members = get_list_members(list_id)
    for id in members:
        followers = set(get_followers(id))
        friends = set(get_friends(id))

        with open(f"list_{list_id}.csv", "a") as f:
            for i in followers:
                if i in members:
                    f.write(f"{i},{id}\n")
            for i in friends:
                if i in members:
                    f.write(f"{id},{i}\n")
