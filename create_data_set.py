import pandas as pd
import sys

def read_from_tsv(machine_replies_fn: str, human_replies_fn: str):
    # read data from .tsv files
    df_gpt = pd.read_csv(machine_replies_fn, sep='\t', header=0)
    df_human = pd.read_csv(human_replies_fn, sep='\t', header=0)
    
    df_gpt['reply_text'] = df_gpt['reply_text'].str.replace('\n', '') # fix read-in bug/errors
    df_gpt['human'] = 0
    df_human['human'] = 1

    return df_gpt, df_human

def combine_files(machine_replies_fn: str, human_replies_fn: str, save_to_fn: str):
    df_gpt, df_human = read_from_tsv(machine_replies_fn, human_replies_fn)

    # fix column names and join
    df_gpt = df_gpt.rename(columns={'reply_text': 'gpt3'})[['tweet_id', 'gpt3']]
    df_human = df_human.rename(columns={'parent_id': 'tweet_id', 'tweet_id': 'human_reply_id'})[['tweet_id', 'human_reply_id']]
    df = df_human.join(df_gpt.set_index('tweet_id'), on='tweet_id')

    # remove missing values, duplicates from joining
    df.dropna()
    df = df.drop_duplicates('tweet_id') # keep only one human-machine pair per original tweet
    
    # save to .tsv
    df.to_csv(save_to_fn, sep='\t', index=False)

    return 0

def get_data_with_labels(machine_replies_fn: str, human_replies_fn: str, save_to_fn: str):
    df_gpt, df_human = read_from_tsv(machine_replies_fn, human_replies_fn)

    # select relevant columns, rename if necessary, and concat
    df_gpt = df_gpt[['tweet_id', 'reply_text', 'human']]
    df_human = df_human[['parent_id','tweet_text', 'human']].rename(columns={'parent_id': 'tweet_id', 'tweet_text': 'reply_text'})
    df = pd.concat([df_gpt, df_human], axis=0)

    # save to .tsv
    df.to_csv(save_to_fn, sep='\t', index=False)
    
    return 0

if __name__ == '__main__':
    sys.exit(0)