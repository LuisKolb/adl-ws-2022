# adl-ws-2022: Applied Deep Learning @ TU Wien

## distinguishing human-authored text from machine-generated text

There is also [YouTube video](https://youtu.be/sAPBFAO1leY) with a quick overview of the project.

Course Deliverables:

- [Assignment 1 - Initiate](./concept.md)
- [Assignment 2 - Hacking](./hacking.md)
- [Assignment 3 - Deliver](./report.pdf)

---

### 📜 Running the Data Set Generator

1. You need an `.env` file with your own keys, provided in the format of `.env_example`. The Twitter API endopint used is [filtered stream](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/introduction), for which a developer account is obviously required, but all access levels should be authorized.
2. You should activate a python venv (recommended) and install the `requirements.txt`
3. There are a few python scripts provided in this repo. The important one is `main.py`, which calls functions from the other scripts. The other scripts can be used to perform individual tasks separately. They are described below.
4. The default output location is `./out/` and, by default, the dataset will be output as a folder structure parseable by `tf.keras.utils.text_dataset_from_directory` and zipped for uploading it to Google Colab.

- `twt_sample_save.py` filter a specified number of tweets from the volume stream, according to some rules (e.g. english only) and save them to a file
- `gpt_get_replies.py` get gpt answers to the filtered tweets and save them to a file
- `create_data_set.py` combines the two data files into a specified format, either for keras loading or combining the tweet ids and gpt-text into a single file.
- `main.py` do all of the above, configurable in a single place

For now, the scripts are only configurable by editing them directly at the end of the script in the `if name() == __main__` section. CLI args to override defaults will be added to `main.py` at a later point.

### ⚗️ Running the DL Pipeline and Evaluation

There is a Google Colab notebook available, which takes the data sets generated using the steps above, and uses a pretrained BERT encoding layer with a dense binary classification layer for very simple, baseline results. If the data is created correctly, it will be accepted by the respective keras `text_dataset_from_directory` function. This notebook closely follow a tutorial from [tensorflow.org](https://www.tensorflow.org/text/tutorials/classify_text_with_bert), to serve as a baseline implementation and to compare results. The aim of this project is to provide the methods to easily generate a dataset and customize the paramters that control this creation process. The model structure looks like this:  
![model structure](/media/model.png)

Some preprocessing is done in the previous step (during dataset creation), e.g. to remove the @user tags that are returned by the Twitter API but the machine doesn't generate in it's reply text (making calssification trivial).

To use the data set with the notebook, we use Google Drive. Upload the `.zip` file to the path specified in the notebook (by default `/content/drive/MyDrive/Colab Notebooks/data/<my_data_name>.zip` where `MyDrive` is the "root" folder of your Google Drive).

Click this Google Colab badge to get there:

[![Open In Collab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1Ao1Lzg3UZ2bYAiSdA1ThCYJNTnU2aczL?usp=sharing)

---

### 📦 Pre Created Data Sets

Since I'm unsure if tweet text can be shared according to the TOS, instead the `create_data_set.py` has a function to make a file contining

- the original tweet id
- the human reply tweet id (no text)
- GPT-3 generated text reply to the tweet

from the output files left behind by `main.py`. Such a data set is available attached to a release [here](https://github.com/LuisKolb/adl-ws-2022/releases/tag/v0.1) as a `.tsv` file.

The tweet text for the human reply will need to be fetched separately using the ids if 1-to-1 comparison is required, sorry!

### Other Thoughts

Even though nobody is sure of the share of Twitter users made up by bots, we just assume that all replies returned by the API are genuine (which they probably aren't). I heard there was a billion-dollar dispute about the topic...

Some other methodological errors are sure to be present, e.g. the DL algorithm actually classifies between *gpt-3 with a specific input vs. the average tweet response* instead of *gpt-3/machine vs. human*, and as such the generalizablity is probably rather limited.
