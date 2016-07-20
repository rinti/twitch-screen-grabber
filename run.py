import sys
from twitch import TwitchGrabber
from examples import overwatch


if __name__ == '__main__':
    with TwitchGrabber(sys.argv[1]) as stream:
        if sys.argv[2] == 'overwatch':
            overwatch.get_most_likely_hero(stream)
