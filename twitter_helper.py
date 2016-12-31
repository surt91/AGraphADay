import twitter

from keys_and_secrets import keys_and_secrets

api = twitter.Api(**keys_and_secrets)


def tweet_pic(path, text=""):
    api.PostUpdate(text, path)

def obtain_dm():
    try:
        with open("last_id.dat", "r") as f:
            last_id = int(f.read().strip())
    except:
        last_id = 0

#    print(last_id)
#    msg = api.GetDirectMessages()
    todo = []
    mentions = api.GetMentions(since_id=last_id + 1)
    for i in mentions:
        last_id = max(i.id, last_id)
        todo.append(dict(handle=i.user.screen_name, text=i.text))
#        print(i.id, i.text, i.user.screen_name)

    with open("last_id.dat", "w") as f:
        f.write(str(last_id))

    return todo
