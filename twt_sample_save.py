from dotenv import load_dotenv
import os
import tweepy
import time
import sys

"""
get a tweepy Client with the credentials specified in .env
"""


def get_client():
    # load API keys
    load_dotenv()
    CONSUMER_KEY = os.getenv('CONSUMER_KEY')
    CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
    BEARER_TOKEN = os.getenv('BEARER_TOKEN')

    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET)
    user = client.get_me()
    if not user.data:
        raise Exception(
            '[ERROR] unable to make requests with Bearer Token, check your .env file and API keys!')

    print(f'[INFO] authenticated using account @{user.data.username}')

    return client


"""
use twitter bearer tokens to get a streamingClient with custom triggers on incoming responses and an optional limit of tweets to get
"""


def get_streaming_client(save_to: str, limit: int):
    """
    overload methods from inherited class to customize processing of incoming stream data
    """
    class CustomSC(tweepy.StreamingClient):

        def __init__(self, bearer_token, *, return_type=..., wait_on_rate_limit=False, **kwargs):
            self.already_fetched = 0

            super().__init__(bearer_token, return_type=return_type,
                             wait_on_rate_limit=wait_on_rate_limit, **kwargs)

        def on_response(self, response):
            if limit == -1 or limit > self.already_fetched:
                self.already_fetched += 1
                tweet = response.data
                # we want only replies, so we extract the relevant data only if it is a reply
                if tweet.referenced_tweets and tweet.referenced_tweets[0].type == 'replied_to':
                    parent_id = tweet.referenced_tweets[0].id
                    for parent_tweet in response.includes['tweets']:
                        if parent_tweet.id == parent_id:
                            # tweets are messy, OK?
                            parent_text = parent_tweet.text.replace(
                                '\r', ' ').replace('\n', ' ').replace('\t', ' ')
                            tweet_id = tweet.id
                            tweet_text = tweet.text.replace('\r', ' ').replace(
                                '\n', ' ').replace('\t', ' ')
                            entry = f'{parent_id}\t"{parent_text}"\t{tweet_id}\t"{tweet_text}"\n'
                            print(entry)
                            with open(save_to, 'a') as f:
                                f.write(entry)
            else:
                print(
                    f'[INFO] fetched {self.already_fetched} tweets, disconnecting...')
                self.disconnect()

        def on_errors(self, errors):
            if errors and errors[0]['type'] == 'https://api.twitter.com/2/problems/not-authorized-for-resource':
                # ignore errors when protected tweets are accessed with expansions, can't prevent the request being made in the stream
                pass
            else:
                return super().on_errors(errors)

    load_dotenv()
    BEARER_TOKEN = os.getenv('BEARER_TOKEN')
    return CustomSC(bearer_token=BEARER_TOKEN)


"""
supply a rule for the filtered stream and, if not present already, add it
"""


def check_rule(streaming_client: tweepy.StreamingClient, rule: str):
    rules_response = streaming_client.get_rules()
    rules = [tweepy.StreamRule(value=rule, tag='default')]

    if not rules_response.data:
        print('[INFO] no rules found, adding rule')
        return streaming_client.add_rules(add=rules)

    elif rules_response.data and rules_response.data[0].value != rule:
        print('[INFO] updating old rule')
        streaming_client.delete_rules(rules_response.data[0].id)
        return streaming_client.add_rules(add=rules)

    elif rules_response.data[0].value == rule:
        print('[INFO] current rule matches')
        return streaming_client.get_rules()


"""
open the streaming connection for a set amount of time
"""


def run_filtered_stream(streaming_client: tweepy.StreamingClient, save_to: str, max_listening_duration: int = 300):
    # ensure file exists
    header = 'parent_id\tparent_text\ttweet_id\ttweet_text\n'
    if not os.path.isfile(save_to):
        with open(save_to, 'a') as f:
            f.write(header)

    # threded is required to be able to disconnect the stream
    streaming_client.filter(tweet_fields='id,text,referenced_tweets', expansions=[
                            'referenced_tweets.id'], threaded=True)

    i = 0
    print(f'[INFO] listening for {max_listening_duration} seconds...')
    for i in range(1, max_listening_duration):
        time.sleep(1)
        i += 1
    streaming_client.disconnect()
    print("[INFO] done streaming")

    return 0


"""
get a client connection, ensure the filter rules are in place, and write incoming tweets to a file path
"""


def get_tweets(num_tweets: int, save_to: str, rule: str):

    streaming_client = get_streaming_client(save_to, num_tweets)
    check_rule(streaming_client, rule)
    run_filtered_stream(streaming_client, save_to)

    return save_to


if __name__ == '__main__':
    filter_rule = 'lang:en is:reply -has:links followers_count:100'
    filename = 'data/tweets.tsv'

    streaming_client = get_streaming_client(filename, 20)

    #print(check_rule(streaming_client, filter_rule))

    sys.exit(run_filtered_stream(streaming_client, 5, filename))
