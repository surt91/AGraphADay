import twitter

from keys_and_secrets import keys_and_secrets

api = twitter.Api(**keys_and_secrets)


def tweet_pic(path):
    
    api.PostUpdate("", path)
