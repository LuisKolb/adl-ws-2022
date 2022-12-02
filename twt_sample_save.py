from dotenv import load_dotenv
import os
import tweepy
import time
import json

def setup():
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
        raise Exception('[ERROR] Unable to make requests with Bearer Token, check your .env file and API keys!')
    
    print(f'[INFO] authenticated using account @{user.data.username}')

    return client

def setup_streaming_client():
    load_dotenv()
    BEARER_TOKEN=os.getenv('BEARER_TOKEN')

    class TweetSaver(tweepy.StreamingClient):
        def on_tweet(self, tweet):
            print(tweet.data)
            with open('test_data/tweets.txt', 'a') as f:
                f.write(json.dumps(tweet.data))
            
    sc = TweetSaver(bearer_token=BEARER_TOKEN)
    sc.sample()
    time.sleep(5)
    sc.disconnect()

def main(client: tweepy.Client):

    return client.get_me()






if __name__ == '__main__':
    #client = setup()
    #res = main(client)
    #print(res)

    setup_streaming_client()