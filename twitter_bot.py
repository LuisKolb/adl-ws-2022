# utils
from dotenv import load_dotenv
import json
import os
import re
import time
from tqdm import trange
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
    try:
        user = api.verify_credentials()
    except tweepy.errors.TweepyException:
        print('[ERROR] authentication timeout')
        exit()
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
    global batch_size           # tweets to fetch at once
    global saved_model_path     # which saved model to use

    last_id_filename = config['last_id_filename']
    batch_size = config['batch_size']
    saved_model_path = config['saved_model_path']

    if not os.path.isfile(last_id_filename):
        with open(last_id_filename, 'w') as file:
            json.dump({handle: None}, file)
    
    return api, handle, own_id


def check_mentions(api, handle, model):

    with open(last_id_filename, 'r') as file:
        most_recent_ids = json.load(file)
    newest_seen = most_recent_ids[handle]

    oldest_seen = None
    highest_id_in_run = 0

    #
    # run until we break when all mentions are processed and api.mentions_timeline() returns [] (an empty list)
    #
    while True:
        #
        # get the next tweet batch to process, based on what's already been processed, utilizing since_id and max_id params from the twitter api
        #
        if not oldest_seen:
            if not newest_seen:
                status_list = api.mentions_timeline(count=batch_size)
            else:
                status_list = api.mentions_timeline(count=batch_size, since_id=newest_seen)
        else:
            if not newest_seen:
                status_list = api.mentions_timeline(count=batch_size, max_id=oldest_seen-1)
            else:
                status_list = api.mentions_timeline(count=batch_size, max_id=oldest_seen-1, since_id=newest_seen)

        #
        # check if any new mentions have been posted, if not, save last id and exit the loop
        #
        if not status_list:
            if highest_id_in_run > 0:
                # no more tweets left to fetch
                most_recent_ids[handle] = highest_id_in_run
                with open(last_id_filename, 'w') as file:
                    json.dump(most_recent_ids, file)
                print(f'[INFO] done fetching mentions for user @{handle}. newest mention id: {most_recent_ids[handle]}')
            else:
                # no mentions since last loop execution
                print(f'[INFO] no new mentions to fetch for user @{handle}. newest mention id: {most_recent_ids[handle]}')
            break
        
        #
        # process the mentions
        #
        for status in status_list:
            if not oldest_seen or status.id < oldest_seen:
                oldest_seen = status.id
            if status.id > highest_id_in_run:
                highest_id_in_run = status.id

            parent_status_id = status.in_reply_to_status_id # get parent tweet

            if not parent_status_id:
                continue # do nothing if not a reply under a tweet

            # get parent tweet object
            try:
                parent_status = api.get_status(parent_status_id, trim_user=True, include_entities=False)
            except tweepy.errors.Forbidden:
                # need to account for tweets from private accounts
                #print('[INFO] encountered private account, cannot fetch parent tweet')
                continue
            except tweepy.errors.NotFound:
                # parent tweet was deleted
                #print('[INFO] encountered deleted parent tweet')
                continue

            # TODO: update transformers with inputs from twt?   
            input = re.sub(r'@\w+(\s)', r'\1', parent_status.text) # strip @usernames from text input
            input = re.sub(r'http\S+', '', input) # strip media urls
            reloaded_results = tf.sigmoid(model(tf.constant([input]))) # run inference
            inference_conf = reloaded_results[0][0].numpy() # get score from model results, from [0...1]

            # label reminder: 0=human, 1=machine
            # TODO: more variation in reply text? emojis as indicators at a glance?
            # TODO: test me
            reply_text = f'hi @{status.user.screen_name}! on a scale of 0=human to 1=GPT-3, the tweet you replied to got a score of {inference_conf:.4f}'
            try:
                api.update_status(reply_text, in_reply_to_status_id=status.id, auto_populate_reply_metadata=True)
            except tweepy.errors.Forbidden:
                # tweet we tried to post was a duplicate
                print('[INFO] tried to post duplicate tweet, does recent_ids.json exist?')
                continue
    
    return()


if __name__ == '__main__':
    api, handle, own_id = setup()
    reloaded_model = tf.saved_model.load(saved_model_path)
    # maybe set up a cron job to check mentions every day?
    # for the demo, just use a loop
    while True:
        check_mentions(api, handle, reloaded_model)
        for _ in trange(10):
            time.sleep(1)