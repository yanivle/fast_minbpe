from util.mytimeit import timeit
from itertools import pairwise
from datastructures import Multiset, IndexedList


def build_indexed_list(text):  # Create an IndexedList with the encoded bytes.
    return IndexedList(t for t in text.encode('utf-8'))


def init_pairs_stats(text):  # Initialize a Multiset with all overlapping pairs.
    # For text "aaabd" the multiset will contain: {(a,a): 2, (a, b): 1, (b, d): 1}
    return Multiset(pairwise(t for t in text.encode('utf-8')))


def merge(pair, new_id, indexed_list: IndexedList, stats:Multiset=None):
    for node in indexed_list.stale_index[pair]:
        if node.val != pair[0] or node.next is None or node.next.val != pair[1]:
            continue  # The index was stale - continue.
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


def train(text, vocab_size, verbose=False):
    print(f'Training tokenizer on text of length {len(text):,} with vocab of size {vocab_size:,}.')
    n_merges = vocab_size - 256
    vocab = {i: bytes([i]) for i in range(256)}
    merge_tree = []
    indexed_list = timeit(lambda: build_indexed_list(text), 'build_indexed_list')
    stats = timeit(lambda: init_pairs_stats(text), 'init_pairs_stats')
    for i in range(n_merges):
        if not stats: break  # Stop if we don't have any pairs (we should probably stop earlier).
        top_pair = stats.most_common
        new_id = len(vocab)
        merge_tree.append((top_pair, new_id))
        vocab[new_id] = vocab[top_pair[0]] + vocab[top_pair[1]]
        if verbose:
            print(f"Merge {i+1}/{n_merges}: {top_pair} -> {new_id} ({vocab[new_id]}) had {stats.count(top_pair)} occurrences")
        merge(top_pair, new_id, indexed_list, stats)
    return merge_tree, vocab


def tokenize(text, merge_tree):
    l = build_indexed_list(text)
    for pair, new_id in merge_tree:
        merge(pair, new_id, l, None)
    return [node.val for node in l]


def detokenize(seq, vocab):
    return b''.join((vocab[t] for t in seq)).decode('utf-8')

