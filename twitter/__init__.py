import sys

try:
    from .helper import tweet_pic, get_my_handle, obtain_dm
    from .listener import answerMentions
    from .networks import ego_network, list_network
except:
    print("Twitter package is broken")
    print("unexpected error:", sys.exc_info())

    from traceback import print_exc
    print_exc()

    def tweet_pic(*args):
        print("Twitter package is broken")
    def get_my_handle(*args):
        print("Twitter package is broken")
        return "none"
    def obtain_dm(*args):
        print("Twitter package is broken")
        return []
    def answerMentions(*args):
        print("Twitter package is broken")
    def ego_network(*args):
        print("Twitter package is broken")
    def list_network(*args):
        print("Twitter package is broken")
