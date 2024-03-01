I just watched [Karpathy's BPE video](https://www.youtube.com/watch?v=zduSFxRajkE) (thanks Andrej for all the fun videos!) and got inspired. Karpathy's code is really nice (as always), and [his implementation](https://github.com/karpathy/minbpe) is obviously not meant to be fast, _but_, we should be able to make the code much faster without sacrificing clarity too much. Hopefully, faster code can make experimentation (e.g. with different scores, instead of always taking the most popular pair) easier. So... here's my late night take on a simple, clean, and fast BPE implementation!

For example, on my laptop, training/tokenizing the taylorswift.txt file with a vocab size of 10K takes:

|              |  minbpe (Karpathy's)       |   fast_minbpe (this repo)|
|--------------|---------------|--------------|
|Training      |  110.10 secs  | 1.59 secs   |
|Tokenizing    |  190.91 secs  | 0.98 secs    |

So 69X faster training in this case.

Training fast_minbpe on the same text with a GPT-4-sized vocab of 100K takes only slightly longer at 3.00 secs (and results in a single token :laughing: - need to run it on more text).

Please find the BPE impl in [fast_minbpe.ipynb](fast_minbpe.ipynb) and the two data structures that it is based on in [leap.py](leap.py) and [multiset.py](multiset.py).

You can find a short writeup on [my website](https://yanivle.github.io/ai/2024/02/23/fast_minbpe.html) (including a more compact code that's unfortunately slower :)).
