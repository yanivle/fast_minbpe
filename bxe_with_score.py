from util.mytimeit import timeit
from datastructures import Multiset, IndexedXList
from datastructures.multiset import Node as MultisetNode
from functools import partial
try:
    from tqdm import tqdm
except ModuleNotFoundError:
    tqdm = lambda x: x

def build_indexed_list(text, x):  # Create an IndexedXList with the encoded bytes.
    return IndexedXList((t for t in text.encode('utf-8')), x)


default_score = lambda val, count: (len(val) - 1) * (count - 1)

class ScoredNode(MultisetNode):
    def __init__(self, count, val, pos, key_fn):
        super().__init__(count, val, pos)
        self.key_fn = key_fn

    @property
    def key(self):
        return self.key_fn(self.val, self.count)

def init_stats_from_indexed_list(indexed_list: IndexedXList, node_type):
    res = Multiset(node_type=node_type)
    for tup, nodes in indexed_list.index.items():
        res.add(tup, len(nodes))
    return res

def merge(tup, new_id, indexed_list: IndexedXList, stats:Multiset|None=None):
    n_merges = 0
    k = len(tup)
    for node in indexed_list.index[tup]:
        if node.tuple(k) != tup: continue
        n_merges += 1
        # Remove old items from stats:
        if stats is not None:
            def remove_all_touching(node, include_prev:bool):
                for t, _ in indexed_list.touching_nodes(node, include_prev):
                    stats.remove(t)
            remove_all_touching(node, True)
            n = node.next
            for _ in range(1, k):
                remove_all_touching(n, False)
                n = n.next
        # Merge:
        for n in node.next_nodes(k)[1:]:
            n.delete()
        node.val = new_id
        indexed_list.update_index(node)
        # Add new items to stats:
        if stats is not None:
            for t, _ in indexed_list.touching_nodes(node):
                stats.add(t)
    return n_merges

def train(text, vocab_size, x=10, verbose=False, score_fn=None, merge_counts=None):
    print(f'Training tokenizer on text of length {len(text):,} with vocab of size {vocab_size:,}.')
    n_merges = vocab_size - 256
    vocab = {i: bytes([i]) for i in range(256)}
    merge_tree = []
    indexed_list = timeit(lambda: build_indexed_list(text, x), 'build_indexed_list')
    multiset_node_type = MultisetNode if score_fn is None else partial(ScoredNode, key_fn=score_fn)
    score_fn = score_fn or default_score
    stats = timeit(lambda: init_stats_from_indexed_list(indexed_list, multiset_node_type), 'init_stats')
    for i in tqdm(range(n_merges)):
        if not stats: break
        top_tup = stats.most_common
        new_id = len(vocab)
        merge_tree.append((top_tup, new_id))
        vocab[new_id] = b''.join([vocab[top_tup[i]] for i in range(len(top_tup))])
        if verbose:
            count = stats.count(top_tup)
            print(f"Merge {i+1}/{n_merges}: {top_tup} -> {new_id} ({vocab[new_id]}) had {count} occurences and score {score_fn(top_tup, count)}")
        merge_count = merge(top_tup, new_id, indexed_list, stats)
        if merge_counts is not None:
            merge_counts.append(merge_count)
    return merge_tree, vocab


def tokenize(text, merge_tree, x):
    l = build_indexed_list(text, x)
    for pair, new_id in merge_tree:
        merge(pair, new_id, l, None)
    return [node.val for node in l]


def detokenize(seq, vocab):
    return b''.join((vocab[t] for t in seq)).decode('utf-8')

