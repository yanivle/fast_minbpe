from util.mytimeit import timeit
from datastructures import Multiset, IndexedKList
from collections import deque


def build_indexed_list(text, k):  # Create an IndexedKList with the encoded bytes.
    return IndexedKList((t for t in text.encode('utf-8')), k)


def init_stats(text, k):  # Initialize a Multiset with all overlapping k-tuples.
    text = text.encode('utf-8')
    d = deque(text[:k-1], maxlen=k)
    res = Multiset()
    for t in text[k-1:]:
        d.append(t)
        res.add(tuple(d))
    return res


def merge(tup, new_id, indexed_list: IndexedKList, stats:Multiset|None=None):
    k = len(tup)
    for node in indexed_list.index[tup]:
        if node.tuple(k) != tup: continue
        # Remove old items from stats:
        if stats is not None:
            n, i = node.go_back(k - 1)
            for _ in range(k + i):
                t = n.tuple(k)
                if len(t) < k: break
                stats.remove(t)
                n = n.next
        # Merge:
        for n in node.next_nodes(k)[1:]:
            n.delete()
        node.val = new_id
        indexed_list.update_index(node)
        # Add new items to stats:
        if stats is not None:
            n, i = node.go_back(k - 1)
            for _ in range(i + 1):
                t = n.tuple(k)
                if len(t) < k: break
                stats.add(t)
                n = n.next


def train(text, vocab_size, k=2, verbose=False):
    print(f'Training tokenizer on text of length {len(text):,} with vocab of size {vocab_size:,}.')
    n_merges = vocab_size - 256
    vocab = {i: bytes([i]) for i in range(256)}
    merge_tree = []
    indexed_list = timeit(lambda: build_indexed_list(text, k), 'build_indexed_list')
    stats = timeit(lambda: init_stats(text, k), 'init_stats')
    for i in range(n_merges):
        if not stats: break
        top_tup = stats.most_common
        new_id = len(vocab)
        merge_tree.append((top_tup, new_id))
        vocab[new_id] = b''.join([vocab[top_tup[i]] for i in range(k)])
        if verbose:
            print(f"Merge {i+1}/{n_merges}: {top_tup} -> {new_id} ({vocab[new_id]}) had {stats.count(top_tup)} occurrences")
        merge(top_tup, new_id, indexed_list, stats)
    return merge_tree, vocab


def tokenize(text, merge_tree, k):
    l = build_indexed_list(text, k)
    for pair, new_id in merge_tree:
        merge(pair, new_id, l, None)
    return [node.val for node in l]


def detokenize(seq, vocab):
    return b''.join((vocab[t] for t in seq)).decode('utf-8')

