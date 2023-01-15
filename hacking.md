# Assignment 2 - Hacking

The specified error metric was accuracy in the binary classification (human vs. machine). I would have been very happy to achieve >70%, since the best benchmarks on [turingbench](https://turingbench.ist.psu.edu/) have an accuracy of around 79% on input by modern text generators. This is an outlier, the other benchmark achieve an average 0.5534. The leaderboard is not a perfect analogue by far, though.

For data set size, with my $18.00 free credit, I got `6344` completions from GPT-3 using the `text-davinci-003` model (the most popular and complex one). If it turns out that this number is not sufficient for training, more capacity/credit can be bought.

The actual best results for binary classification accuracy were:

- **0.9747** - HOWEVER this was on the first "test" run, where no preprocessing was done (could probably be achieved just by looking at the first few letters of the reply, since the machine-generated text didn't start with `@user_i_am_replying_done`, while most human-generated replies did)
- **0.9457** - this was for the "actual" dataset with 6000 records each for human and machine generated tweet replies, with the default 80-20 train-test split. This dataset also had any `@usernames` stripped, to remove the advantage introduced by the Twitter API mentioned in the [README.md](./README.md). It is attached as a release in the GitHub repository [here](https://github.com/LuisKolb/adl-ws-2022/releases/tag/v0.1).

These accuracy reading were obtained from a very basic model using a pretrained BERT encoding layer, to serve as a baseline performance measure. For more info on the model implementation, see the [README.md](./README.md). There are some very obvious overfitting concerns in addition to the conceptual challenges mentioned in the [README.md](./README.md), simply because the accuracy scores are "too good".

Time breakdown for this assignment:

- building methods to pull tweets and gpt-completions: ~3 days, with some additional effort of ~1 day to work out bugs
- implementing a DL pipeline: ~1.5 days, most of the time spent on finding a way to make the data set format compatible with the tensorflow data loader functions
- finetuning: ~0.5 days, due to sickness this part unfortuantely had to be cut short, only stripping @usernames was implemented as a preprocessing step, and no model customization was possible
- documentation: ~1 day for cleanup, code documentations
