import sys

import tweepy

from .helper import api, tweet_pic, obtain_dm, get_my_handle

my_handle = get_my_handle()


class MyStreamListener(tweepy.StreamListener):
    def __init__(self, guess_graph, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guess_graph = guess_graph
        try:
            with open("last_id.dat", "r") as f:
                self.last_id = int(f.read().strip())
        except:
            self.last_id = 0

    def on_status(self, status):
        print(status.text)
        print("@" + status.user.screen_name, ":", status.text)
        # make sure that we are actually mentioned
        mentioned = False
        for i in status.entities["user_mentions"]:
            if status.text[:3] == "RT ":
                # this is a retweet, ignore it
                continue
            if i["screen_name"] == my_handle:
                mentioned = True
        if mentioned:
            print(status.text)
            text = status.text.replace(my_handle, "")
            path, answer = self.guess_graph(text=text,
                                            handle=status.user.screen_name)
            tweet_pic(path, answer, status.id)

            self.last_id = status.id
            with open("last_id.dat", "w") as f:
                f.write(str(self.last_id))


def answerMentions(guess_graph):
    """Answers mentions with images of graphs.

    guess_graph -- a function taking a string, parses it and returns the path
                   to an image and and answer text
    """
    try:
        # are there new mentions while we were not listening?
        todo = obtain_dm()
        print(len(todo), "new messages")
        for d in todo:
            text = d["text"].replace(my_handle, "")
            path, answer = guess_graph(text=text, handle=d["handle"])
            tweet_pic(path, answer, d["id"])
    except:
        print("something went wrong", sys.exc_info())

    # listen for new mentions
    print("listening for mentions")
    myStreamListener = MyStreamListener(guess_graph)
    myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
    myStream.filter(track=['randomGraphs'])
