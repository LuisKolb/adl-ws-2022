from dotenv import load_dotenv
import os
import sys
import openai
import csv
import time

"""
authorize the app using the openai api key in .env
"""


def auth():
    # load API keys
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')
    # TODO add auth OK check
    print('[INFO] auth OK')


"""
get a tweet completion from a gpt-3 model endpoint, defaults to the model 'text-davinci-003'
"""


def get_reply_from_model(tweet: str, model: str = 'text-davinci-003'):
    prompt = f'Write a reply to this tweet in less than 280 characters: "{tweet}"\nReply:\n'

    try:
        response_dict = openai.Completion.create(
            model=model, prompt=prompt, temperature=0.9, max_tokens=70, n=1)
        return (response_dict['id'], response_dict['choices'][0]['text'])

    except (openai.error.RateLimitError, openai.error.ServiceUnavailableError) as e:
        print(
            f'[INFO] openAI error {type(e)}, sleeping for 60 seconds and retrying request...')
        time.sleep(60)
        response_dict = openai.Completion.create(
            model=model, prompt=prompt, temperature=0.9, max_tokens=70, n=1)
        return (response_dict['id'], response_dict['choices'][0]['text'])


"""
take a file generated by twt_sample_save.py and get a completion for every tweet saved there

includes picking up from a previous run in case of errors during a previous run to save credits
"""


def generate_from_file(read_from: str, save_to: str, limit: int = 100):
    auth()

    # ensure file exists
    header = 'tweet_id\ttweet_text\treply_id\treply_text\n'
    if not os.path.isfile(save_to):
        with open(save_to, 'a') as f:
            f.write(header)

    # pick up from previous run in case of runtime error/rate limit during prev run
    skip_until = sum(1 for _ in open(save_to))

    i = 0
    with open(read_from) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        for row in rd:
            if skip_until == 0:
                tweet_id = row[0]
                tweet_text = row[1]
                reply_id, reply_text = get_reply_from_model(tweet_text)
                entry = f'{tweet_id}\t"{tweet_text}"\t{reply_id}\t"{reply_text}"\n'
                print(entry)
                with open(save_to, 'a') as f:
                    f.write(entry)

                i += 1
                if limit > 0 and i >= limit:
                    return 0
            else:
                skip_until -= 1
                pass
    return 0


if __name__ == '__main__':
    sys.exit(generate_from_file(read_from='test_data/tweets.tsv',
             save_to='test_data/gpt-replies.tsv', limit=0))
