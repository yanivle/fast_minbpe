I just watched [Karpathy's BPE video](https://www.youtube.com/watch?v=zduSFxRajkE) (thanks Andrej for all the fun videos!) and got inspired. Karpathy's code is really nice (as always), and [his implementation](https://github.com/karpathy/minbpe) is obviously not meant to be fast, _but_, we should be able to make the code much faster without sacrificing clarity too much. Hopefully, faster code can make experimentation (e.g. with different scores, instead of always taking the most popular pair) easier. So... here's my late night take on simple, clean, but faster BPE!

For example, on my laptop, training/tokenizing the taylorswift.txt file with a vocab size of 10K takes:

|              |  minbpe (Karpathy's)       |   fast_minbpe (this colab)|
|--------------|---------------|--------------|
|Training      |  110.10 secs  | 13.65 secs   |
|Tokenizing    |  190.91 secs  | 0.84 secs    |
