from util.mytimeit import timeit
from itertools import pairwise
from datastructures import Multiset, IndexedList
from datastructures.multiset import Node as MultisetNode
from collections import Counter


def merge(pair, new_id, indexed_list: IndexedList, stats:Multiset|None=None, singles_count=None):
    for node in indexed_list.index[pair]:
        if node.val != pair[0] or node.next is None or node.next.val != pair[1]:
            continue  # The index was stale - continue.
        if singles_count is not None:
            singles_count[new_id] += 1
        # Say we're merging "bc" to "X" in "abcd", and the node we're visiting now is "b".
        if stats is not None:  # Update the stats.
            stats.remove(pair)  # Remove "bc".
            if node.next.next is not None:
                stats.remove((node.next.val, node.next.next.val))  # Remove "cd".
                stats.add((new_id, node.next.next.val))  # Add "Xd".
            if node.prev is not None:
                stats.remove((node.prev.val, pair[0]))  # Remove "ab".
                stats.add((node.prev.val, new_id))  # Add "aX".
        node.next.delete()  # Delete "c", we now have "abd".
        node.val = new_id  # Update "b" to "X", we now have "aXd".
        indexed_list.update_index(node)  # Add "aX" and "Xd" to the index.


def train(text, vocab_size, p=3, q=1, r=1, verbose=False):
    print(f'Training tokenizer on text of length {len(text):,} with vocab of size {vocab_size:,}.')
    n_merges = vocab_size - 256
    vocab = {i: bytes([i]) for i in range(256)}
    merge_tree = []
    indexed_list = IndexedList(t for t in text.encode('utf-8'))
    singles_count = Counter(t for t in text.encode('utf-8'))
    class CondScoredNode(MultisetNode):
        @property
        def key(self):
            a, b = self.val
            return pow(self.count, p) / pow(singles_count[a], q) / pow(singles_count[b], r)
    stats = Multiset(pairwise(t for t in text.encode('utf-8')), node_type=CondScoredNode)
    for i in range(n_merges):
        if not stats: break  # Stop if we don't have any pairs (we should probably stop earlier).
        top_pair = stats.most_common
        new_id = len(vocab)
        merge_tree.append((top_pair, new_id))
        vocab[new_id] = vocab[top_pair[0]] + vocab[top_pair[1]]
        if verbose:
            print(f"Merge {i+1}/{n_merges}: {top_pair} -> {new_id} ({vocab[new_id]}) had {stats.count(top_pair)} occurrences")
        merge(top_pair, new_id, indexed_list, stats, singles_count)
    return merge_tree, vocab


def tokenize(text, merge_tree):
    l = IndexedList(t for t in text.encode('utf-8'))
    for pair, new_id in merge_tree:
        merge(pair, new_id, l, None)
    return [node.val for node in l]


def detokenize(seq, vocab):
    return b''.join((vocab[t] for t in seq)).decode('utf-8')

