# distinguishing human-authored text from machine-generated text

## introduction

AI-generated content is becoming an ever more relevant concern as the generating models continue to improve - being able to distinguish if a piece of content originally came from a human or a machine is important. Not only for basic ethical concerns, but to increase acceptance by the general public as well.  
Unfortunately, humans themselves are rather bad at this task, as Crothers et al. state in [Machine Generated Text: A Comprehensive Survey of Threat Models and Detection Methods](https://arxiv.org/pdf/2210.07321.pdf).  
Deep learning, however, seems suited to at least attempt to solve this problem. Another comparison of different detection approaches in various settings was published in a very recent paper by Uchendu et al. here: [Attribution and Obfuscation of Neural Text Authorship: A Data Mining Perspective](https://arxiv.org/pdf/2210.10488.pdf). They call this type of problem "Authorship Attribution (AA)".

Rather than datasets like the ones provided at [turingbench](https://turingbench.ist.psu.edu/), I want to purely focus on detecting GPT-3 generated text as opposed to a diverse set of generators like turingbench provides. The reason for this decision is the recency, impressive performance and (media-) popularity of the model. Additionally, outputs of older models like GPT-2 are relativey easy to detect.  

The dataset to train the deep learning model will be created from scratch, in line with the "bring your own data" approach. As opposed to, for example, news stories (a popular "type" of text) I want to build a data set of tweet replies. The main features will be:

- a human-authored reply to a tweet
- a GPT-3 authored reply to the same tweet, using it as a prompt

Using this setup, we can directly compare labelled text passages with the same topic. Some text length considerations will have to be taken into account, since very short tweets can be hard to classify either way.

The number of tweet-replies will depend on the amount of text generation the starting credit of 18$ will get me, although I am not opposed to spending some money to get more data, if necessary. The twitter API should not present a problem at this scale.  

"Deploying" the model as a twitter bot, which can be tagged to give its "opinion" on the realness of a tweet (by calling an API endpoint) would be rather appropriate, in my opinion. I conincidentally have built a somewhat similar (rudimentary) bot this summer, see [the @detectatron3000 repo](https://github.com/LuisKolb/twitter-od-bot).

---

## expected work breakdown

- building the dataset: ~2-3 days of setup, fetching human tweets, plus letting the collector run until GPT-3 credits/tokens are used up
- model design: ~1-2 days to implement existing models like [RoBERTa](https://arxiv.org/pdf/1907.11692.pdf) that do well on turingbench and to get them working
- tuning the network and obtaining the best results I can get: ~5-7 days
- building an application to play with the model (twitter bot or webapp): ~1-2 days
- report: 1 day
- presentation: ~1 day
