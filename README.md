A minimal, clean, and *fast* Python implementation of the [BPE algorithm](https://en.wikipedia.org/wiki/Byte_pair_encoding).

I just watched [Karpathy's BPE video](https://www.youtube.com/watch?v=zduSFxRajkE) (thanks Andrej for all the fun videos!) and got inspired. Karpathy's code is really nice (as always), and [his implementation](https://github.com/karpathy/minbpe) is obviously not meant to be fast, _but_ with the right datastructures, we should be able to make the code much faster without sacrificing clarity too much. Hopefully, faster code can make experimentation (e.g. with different scores, instead of always taking the most popular pair) easier. So... here's my late night take on a simple, clean, and fast BPE implementation!

For example, on my laptop, training/tokenizing the [taylorswift.txt](data/taylorswift.txt) file with a vocab size of 10K takes:

|              |  minbpe (Karpathy's)       |   fast_minbpe (this repo)|
|--------------|---------------|--------------|
|Training      |  110.10 secs  | 1.59 secs   |
|Tokenizing    |  190.91 secs  | 0.98 secs    |

**So 69X faster training in this case.**

Training on [Swann's Way](data/0300511.txt) (~1MB) with a vocab size of 100K takes 64.16 seconds.


- [bpe.py](bpe.py) - the BPE impl.
- [fast_minbpe.ipynb](fast_minbpe.ipynb) - results.
- [datastructures/](datastructures/) - [Leap](datastructures/leap.py) and [Multiset](datastructures/multiset.py) (the datastructures that make this fast).
- [my website](https://yanivle.github.io/ai/2024/02/23/fast_minbpe.html) - short writeup.
