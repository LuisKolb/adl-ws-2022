# utils
from dotenv import load_dotenv
import json
import os
import re
import tensorflow as tf 
import tensorflow_text # required to load a saved model built with tf-text

# twitter SDK
import tweepy

def setup():
    # load API keys
    load_dotenv()
    CONSUMER_KEY = os.getenv('CONSUMER_KEY')
    CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
    ACCESS_TOKEN= os.getenv('ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

    #
    # authenticate to twitter
    #
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN,ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    user = api.verify_credentials()
    if user:
        handle = user.screen_name
        own_id = user.id
    else:
        raise Exception('[ERROR] Unable to verify_credentials() with OAuth1, check your .env file and API keys!')
    
    #
    # read in config and set globals
    #
    with open('bot_config.json', 'r') as file:
        config = json.load(file)

    global last_id_filename     # where to store the id of the oldest mention that's already processed
    global max_tweets_to_fetch  # max number of tweets to look at
    global step_size            # tweets to fetch at once
    global saved_model_path

    last_id_filename = config['last_id_filename']
    max_tweets_to_fetch = config['max_tweets_to_fetch']
    step_size = config['step_size']
    saved_model_path = config['saved_model_path']
    
    return api, handle, own_id


def check_mentions(api, handle, model):
    if os.path.isfile(last_id_filename):
        # load the stored id of the oldest mention that's already been processed
        with open(last_id_filename, 'r') as file:
            most_recent_ids = json.load(file)
    else:
        # first time fetching mentions for the authenticated user
        most_recent_ids = {handle: None}

    # we store most recent tweet id per account in a .gitignored file
    # if not present we don't need to pick up from where we left off
    if handle in most_recent_ids:
        newest_seen = most_recent_ids[handle]
    else:
        newest_seen = None

    oldest_seen = None
    highest_id_in_run = 0
    for i in range(0,int(max_tweets_to_fetch/step_size)):

        # get the next tweet batch to process, based on what's already been processed, utilizing since_id and max_id params from the twitter api
        if not oldest_seen:
            if not newest_seen:
                status_list = api.mentions_timeline(count=step_size)
            else:
                status_list = api.mentions_timeline(count=step_size, since_id=newest_seen)
        else:
            if not newest_seen:
                status_list = api.mentions_timeline(count=step_size, max_id=oldest_seen-1)
            else:
                status_list = api.mentions_timeline(count=step_size, max_id=oldest_seen-1, since_id=newest_seen)

        if not status_list:
            if highest_id_in_run > 0:
                # no more tweets left to fetch
                most_recent_ids[handle] = highest_id_in_run
                with open(last_id_filename, 'w') as file:
                    json.dump(most_recent_ids, file)
                print(f'[INFO] done fetching mentions for user {handle}. newest mention id: {most_recent_ids[handle]}')
                break
            else:
                # no mentions since last loop execution
                print(f'[INFO] no new mentions to fetch for user {handle}. newest mention id: {most_recent_ids[handle]}')
            break
        
        # process the mentions
        for status in status_list:
            if not oldest_seen or status.id < oldest_seen:
                oldest_seen = status.id
            if status.id > highest_id_in_run:
                highest_id_in_run = status.id
            
            # TODO: update transformers with inputs from twt?
            
            input = [re.sub(r'@\w+(\s)', r'\1', status.text)] # strip @usernames from text input
            reloaded_results = tf.sigmoid(model(tf.constant(input))) # run inference
            inference_conf = reloaded_results[0][0].numpy() # get score from model results, from [0...1]

            # label reminder: 0=human, 1=machine
            # TODO: more variation
            # TODO: test me
            reply_text = f'hi @{status.user.screen_name}! on a scale of 0=human to 1=GPT-3, the tweet you tagged me under got a score of {inference_conf:.6f}'
            api.update_status(reply_text, in_reply_to_status_id=status.id, auto_populate_reply_metadata=True)

        i = i+1


if __name__ == '__main__':
    api, handle, own_id = setup()
    reloaded_model = tf.saved_model.load(saved_model_path)

    # maybe set up a cron job to check mentions every day?
    check_mentions(api, handle, reloaded_model)