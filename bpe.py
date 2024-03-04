from util.mytimeit import timeit
from itertools import pairwise
from datastructures import Leap, Multiset, CountLeap


def build_pairs_leap(text):  # Build a leap of all overlapping pairs.
    # For text "aaabd" the leap will contain: (a,a), (a, a), (a, b), (b, d)
    return Leap(pairwise(t for t in text.encode('utf-8')))


def init_pairs_stats(text):  # Initialize a multiset with all overlapping pairs.
    # For text "aaabd" the multiset will contain: {(a,a): 2, (a, b): 1, (b, d): 1}
    return Multiset(pairwise(t for t in text.encode('utf-8')))


def merge(pair, new_id, leap):
    for node in list(leap.occurrences(pair)):
        if node.val != pair:  # Don't merge if current node was already updated (might happen if pair[0] == pair[1]).
            continue
        # Say we're merging "bc" to "X" in "abcd", so our leap holds (a, b), (b, c), (c, d) and we're visiting node (b, c)
        if node.prev is not None:  # Update the previous node: (a, X), (b, c), (c, d)
            leap.set_value(node.prev, (node.prev.val[0], new_id))
        if node.next is not None:  # Update the next node: (a, X), (b, c), (X, d)
            leap.set_value(node.next, (new_id, node.next.val[1]))
        leap.delete(node)  # Delete ourselves: (a, X), (X, d)


def train(text, vocab_size, verbose=False):
    print(f'Training tokenizer on text of length {len(text):,} with vocab of size {vocab_size:,}.')
    n_merges = vocab_size - 256
    vocab = {i: bytes([i]) for i in range(256)}
    merge_tree = []
    leap = timeit(lambda: build_pairs_leap(text), 'build_pairs_leap')
    stats = timeit(lambda: init_pairs_stats(text), 'init_pairs_stats')
    leap_with_stats = CountLeap(leap, stats)
    for i in range(n_merges):
        if not stats: break  # Stop if we only have one token (we should probably stop earlier).
        top_pair = stats.most_common
        new_id = len(vocab)
        merge_tree.append((top_pair, new_id))
        vocab[new_id] = vocab[top_pair[0]] + vocab[top_pair[1]]
        if verbose:
            print(f"Merge {i+1}/{n_merges}: {top_pair} -> {new_id} ({vocab[new_id]}) had {stats.count(top_pair)} occurrences")
        merge(top_pair, new_id, leap_with_stats)
        leap_with_stats.commit()
    return merge_tree, vocab


def tokenize(text, merge_tree):
    if len(text.encode('utf-8')) <= 1: return list(text.encode('utf-8'))
    leap = build_pairs_leap(text)
    leap.append((leap.end.val[1], -1))  # We'll lose this dummy 3 lines down.
    for pair, new_id in merge_tree:
        merge(pair, new_id, leap)
    return [node.val[0] for node in leap]


def detokenize(seq, vocab):
    return b''.join((vocab[t] for t in seq)).decode('utf-8')

