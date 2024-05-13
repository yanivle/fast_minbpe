from util.mytimeit import timeit
from datastructures import Multiset, IndexedXList
from functools import partial
try:
    from tqdm import tqdm
except ModuleNotFoundError:
    tqdm = lambda x: x
from bxe_with_score import build_indexed_list, merge, tokenize, detokenize, ScoredNode, init_stats_from_indexed_list
import copy
from itertools import pairwise


# Reverses the merge function.
def split(tup, new_id, indexed_list: IndexedXList, stats:Multiset|None=None):
    n_splits = 0
    k = len(tup)
    assert stats is not None
    for node in indexed_list.index[(new_id,)]:
        if node.val != new_id: continue
        n_splits += 1
        # Remove old items from stats:
        for t, _ in indexed_list.touching_nodes(node):
            stats.remove(t)
        # Split:
        new_nodes = [indexed_list.Node(v) for v in tup[1:]]
        for a, b in pairwise(new_nodes):
            a.link(b)
        if node.next is not None:
            new_nodes[-1].link(node.next)
        node.link(new_nodes[0])
        node.val = tup[0]
        # Update index and stats with new items:
        for i in range(k):
            include_prev = i == 0
            for t, n in indexed_list.touching_nodes(node, include_prev):
                indexed_list.add_to_index(t, n)
                stats.add(t)
    return n_splits


def get_score(tup, stats, indexed_list, vocab, steps):
    merge_counts = [merge(tup, len(vocab), indexed_list, stats)]
    vocab[len(vocab)] = b''.join([vocab[tup[i]] for i in range(len(tup))])
    _train(indexed_list, stats, steps - 1, vocab, greedy=True, merge_counts=merge_counts)
    return sum(merge_counts)

def get_top_tup(stats, indexed_list, vocab, top_k, forward_steps):
    candidates = stats.top_k(top_k)
    best, best_score = None, 0
    for tup, score in candidates:
        tmp_list = IndexedXList([n.val for n in indexed_list], indexed_list.x)
        tmp_stats = init_stats_from_indexed_list(tmp_list, stats.node_type)
        tmp_vocab = copy.deepcopy(vocab)
        score = get_score(tup, tmp_stats, tmp_list, tmp_vocab, forward_steps)
        if score > best_score:
            best, best_score = tup, score
    return best

def heuristic_bpe_score(val, count):
    if len(val) > 2: return 0
    return count

def train_bpe_heuristic(text, vocab_size, verbose=False, merge_counts=None):
    x = 3
    print(f'Training tokenizer on text of length {len(text):,} with vocab of size {vocab_size:,}.')
    n_merges = vocab_size - 256
    vocab = {i: bytes([i]) for i in range(256)}
    merge_tree = []
    indexed_list = timeit(lambda: build_indexed_list(text, x), 'build_indexed_list')
    multiset_node_type = partial(ScoredNode, key_fn=heuristic_bpe_score)
    stats = timeit(lambda: init_stats_from_indexed_list(indexed_list, multiset_node_type), 'init_stats')
    return _train(indexed_list, stats, n_merges, vocab, merge_tree, verbose, merge_counts, greedy=False)

def _train(indexed_list, stats, n_merges, vocab, merge_tree=None, verbose=False, merge_counts=None, greedy=True):
    for i in range(n_merges) if greedy else tqdm(range(n_merges)):
        if not stats: break
        if greedy:
            top_tup = stats.most_common
        else:
            top_tup = get_top_tup(stats, indexed_list, vocab, 10, min(n_merges - i, 100))
        if top_tup is None: break
        new_id = len(vocab)
        if not greedy:
            print(set(vocab.keys()) - set(range(256)))
        if merge_tree is not None:
            merge_tree.append((top_tup, new_id))
        vocab[new_id] = b''.join([vocab[top_tup[i]] for i in range(len(top_tup))])
        if verbose:
            count = stats.count(top_tup)
            print(f"Merge {i+1}/{n_merges}: {top_tup} -> {new_id} ({vocab[new_id]}) had {count} occurences and score {heuristic_bpe_score(top_tup, count)}")
        merge_count = merge(top_tup, new_id, indexed_list, stats)
        if merge_counts is not None:
            merge_counts.append(merge_count)
    return merge_tree, vocab
