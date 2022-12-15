import pandas as pd
import sys
import os
from sklearn.model_selection import train_test_split
from datetime import datetime
import shutil
import re

"""
internal utility functions
"""


def _read_from_tsv(machine_replies_fn: str, human_replies_fn: str):
    # read data from .tsv files
    df_gpt = pd.read_csv(machine_replies_fn, sep='\t',
                         header=0, on_bad_lines='skip')
    df_human = pd.read_csv(human_replies_fn, sep='\t',
                           header=0, on_bad_lines='skip')

    df_gpt['reply_text'] = df_gpt['reply_text'].str.replace(
        '\n', '')  # fix read-in bug/errors
    df_gpt['human'] = 0
    df_human['human'] = 1

    return df_gpt, df_human


def _ensure_dirs_exist(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def _save_df_rowwise(path, df):
    _ensure_dirs_exist(path)

    i = 0
    for idx, row in df.iterrows():
        with open(f'{path}/{idx}.txt', 'w') as f:
            f.write(row[0])


def _save_df_to_dir(save_dir, df, label):

    train, test = train_test_split(df, test_size=0.2)

    p = os.path.join(save_dir, 'train', label)
    _save_df_rowwise(p, train)

    p = os.path.join(save_dir, 'test', label)
    _save_df_rowwise(p, test)

    return save_dir


"""
takes two files and combines them into a .tsv file with labels, stripping the tweet reply text and using IDs instead
"""


def combine_files(machine_replies_fn: str, human_replies_fn: str, save_dir: str):
    curr_dt = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    save_dir = f'{save_dir}/{curr_dt}'
    df_gpt, df_human = _read_from_tsv(machine_replies_fn, human_replies_fn)

    # fix column names and join
    df_gpt = df_gpt.rename(columns={'reply_text': 'gpt3'})[
        ['tweet_id', 'gpt3']]
    df_human = df_human.rename(columns={'parent_id': 'tweet_id', 'tweet_id': 'human_reply_id'})[
        ['tweet_id', 'human_reply_id']]
    df = df_human.join(df_gpt.set_index('tweet_id'), on='tweet_id')

    # remove missing values, duplicates from joining
    df = df.dropna()
    # keep only one human-machine pair per original tweet
    df = df.drop_duplicates('tweet_id')
    df = df.astype({'human_reply_id': 'int64'})

    # save to .tsv
    df.to_csv(save_dir, sep='\t', index=False)

    return 0


"""
takes two files as input and saves them to a .zip archive of the dir structure required by keras for easy data loading
"""


def to_keras_dir_structure(machine_replies_fn: str, human_replies_fn: str, save_dir: str):
    curr_dt = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    save_dir = f'{save_dir}/{curr_dt}'
    df_gpt, df_human = _read_from_tsv(machine_replies_fn, human_replies_fn)

    # select relevant columns, rename if necessary, and concat
    df_gpt = df_gpt[['reply_text']].dropna()
    df_human = df_human[['tweet_text']].rename(
        columns={'tweet_text': 'reply_text'}).dropna()

    # process data here
    def remove_usernames(text: str):
        return re.sub(r'@\w+(\s)', r'\1', text)

    df_human['reply_text'] = df_human['reply_text'].apply(
        lambda val: remove_usernames(val))

    _ensure_dirs_exist(os.path.join(save_dir))
    _save_df_to_dir(save_dir=save_dir, df=df_gpt, label='machine')
    _save_df_to_dir(save_dir=save_dir, df=df_human, label='human')

    # make a zip file to upload
    shutil.make_archive(save_dir, 'zip', root_dir=save_dir)

    return 0


if __name__ == '__main__':
    to_keras_dir_structure('data/gpt.tsv', 'data/tweets.tsv', 'out')
    combine_files('data/gpt.tsv', 'data/tweets.tsv', 'out')
    sys.exit(0)
