from dotenv import load_dotenv
import os
import tweepy
import time
import json
import sys

def get_client():
    # load API keys
    load_dotenv()
    CONSUMER_KEY = os.getenv('CONSUMER_KEY')
    CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
    ACCESS_TOKEN= os.getenv('ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
    BEARER_TOKEN=os.getenv('BEARER_TOKEN')

    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET)
    user = client.get_me()
    if not user.data:
        raise Exception('[ERROR] unable to make requests with Bearer Token, check your .env file and API keys!')
    
    print(f'[INFO] authenticated using account @{user.data.username}')

    return client

def get_streaming_client():
    """
    overload methods from inherited class to customize processing of incoming stream data
    """
    class CustomSC(tweepy.StreamingClient):

        def on_response(self, response):
            tweet = response.data
            # we want only replies, so we extract the relevant data only if it is a reply
            if tweet.referenced_tweets and tweet.referenced_tweets[0].type == 'replied_to':
                parent_id = tweet.referenced_tweets[0].id
                for parent_tweet in response.includes['tweets']:
                    if parent_tweet.id == parent_id:
                        # tweets are messy, OK?
                        parent_text = parent_tweet.text.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
                        tweet_id = tweet.id
                        tweet_text = tweet.text.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
                        with open('test_data/tweets.tsv', 'a') as f:
                            f.write(f'{tweet_id}\t"{tweet_text}"\t{parent_id}\t"{parent_text}"\n')
        
        def on_errors(self, errors):
            if errors and errors[0]['type'] == 'https://api.twitter.com/2/problems/not-authorized-for-resource':
                # ignore errors when protected tweets are accessed with expansions, can't prevent the request being made in the stream
                pass
            else:
                return super().on_errors(errors)
    
    load_dotenv()
    BEARER_TOKEN=os.getenv('BEARER_TOKEN')
    return CustomSC(bearer_token=BEARER_TOKEN)

def check_rule(streaming_client: tweepy.StreamingClient, rule: str):
    rules_response = streaming_client.get_rules()
    rules= [tweepy.StreamRule(value=rule, tag='default')]

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


def main(streaming_client: tweepy.StreamingClient):

    # threded is required to be able to disconnect the stream
    streaming_client.filter(tweet_fields='id,text,referenced_tweets', expansions=['referenced_tweets.id'], threaded=True)
    
    i = 0
    time_to_listen = 30
    print(f'[INFO] listening for {time_to_listen} seconds...')
    for i in range(1,time_to_listen):
        time.sleep(1)
        i += 1
    print("[INFO] done streaming")

    streaming_client.disconnect()

    return 0



if __name__ == '__main__':
    filter_rule = 'lang:en is:reply -has:links followers_count:100'

    streaming_client = get_streaming_client()
    
    #print(check_rule(streaming_client, filter_rule))

    sys.exit(main(streaming_client))