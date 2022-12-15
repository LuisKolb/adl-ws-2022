import sys
import os
from twt_sample_save import get_tweets
from create_data_set import _ensure_dirs_exist, to_keras_dir_structure
from gpt_get_replies import generate_from_file

if __name__ == '__main__':

    # default args for config
    num_tweets = 8000
    limit_gpt_requests = -1
    base_data_dir = 'data'
    tweets_fn = 'tweets.tsv'
    gpt_fn = 'gpt.tsv'
    out_dir = 'out'
    tweet_filter = 'lang:en is:reply -has:links followers_count:100'

    _ensure_dirs_exist(base_data_dir)

    # get X amount of tweets
    # ~50 tweets per second
    tweets_save_to = os.path.join(base_data_dir, tweets_fn)
    get_tweets(num_tweets, tweets_save_to, tweet_filter)

    # get X amount of completions
    # ~500 completions equal roughly 1 dollar credit used
    gpt_save_to = os.path.join(base_data_dir, gpt_fn)
    generate_from_file(tweets_save_to, gpt_save_to, limit_gpt_requests)

    # process the files
    res = to_keras_dir_structure(gpt_save_to, tweets_save_to, out_dir)

    sys.exit(res)
