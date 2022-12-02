https://paperswithcode.com/dataset/retweet

RETWEET supplies tweet ids, not the text posts themself. We need to get those somewhat manually using e.g. https://github.com/seirasto/twitter_download/. (possibly outdated due to API changes)

NEW IDEA - use https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/introduction to sample tweets e.g. only those without media or URLs (might be necessary? we'll see...)

Downloaded tweets are saved to XYZ.

The twwets are then used to prompt GPT-3 to write an "original" reply with temperature=1 (random every time). These replies are saved to XYZ.

Tweet ids are used to match and combine "rows" later.
