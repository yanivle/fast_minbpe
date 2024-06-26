A minimal, clean, and *fast* Python implementation of the [BPE algorithm](https://en.wikipedia.org/wiki/Byte_pair_encoding).

I just watched [Karpathy's BPE video](https://www.youtube.com/watch?v=zduSFxRajkE) (thanks Andrej for all the fun videos!) and got inspired. Karpathy's code is really nice (as always), and [his implementation](https://github.com/karpathy/minbpe) is obviously not meant to be fast, _but_ with the right data structures, we should be able to make the code much faster without sacrificing clarity too much. Hopefully, faster code can make experimentation (e.g. with different scores, instead of always taking the most popular pair) easier. So... here's my late night take on a simple, clean, and fast BPE implementation!

For example, on my laptop, training/tokenizing the [taylorswift.txt](data/taylorswift.txt) file with a vocab size of 10K takes:

|              |  minbpe (Karpathy's)       |   fast_minbpe (this repo)|
|--------------|---------------|--------------|
|Training      |  110.10 secs  | 1.00 secs   |
|Tokenizing    |  190.91 secs  | 0.52 secs    |

**So 100X faster training in this case.**

Training a vocab size of 100K on [Swann's Way](data/0300511.txt) (~1MB) takes 8.15 seconds, on [the bible](data/bible.txt) (~4.3MB) 24.49 seconds, and on [a corpus of reddit jokes](data/reddit_jokes.json) (~69MB) just under 5 minutes.


- [bpe.py](bpe.py) - the BPE impl.
- [fast_minbpe.ipynb](fast_minbpe.ipynb) - brief analysis and results.
- [datastructures/](datastructures/) - [IndexedList](datastructures/indexedlist.py) and [Multiset](datastructures/multiset.py) (the data structures that make this fast).
- [my website](https://yanivle.github.io/ai/2024/02/23/fast_minbpe.html) - short writeup.
