# An unordered set that can holds multiple copies of an item.
# Supports these ops with a cost of at most amortized O(log(n)):
# - add(item, count): add count copies of item.
# - remove(item, count): remove count copies of item.
# - count(item): returns the number of copies of item in the multiset.
# - most_common(): returns the item with the most copies in the multiset.
#
# Internaly this is implemented with a modified max-heap that supports increasing
# and decreasing internal elements.
#
# This is essentially the same as collections.Counter but most_common and top_k
# queries are much faster (see multiset_tests.ipynb).
#
# As a final optimization, updates are aggregated (into the to_add and to_remove
# dicts) and only committed to the heap when needed. This pays off if we're
# updating the same element several times before performing a query. Lazy data
# structures are often better :)
#
# I have a shorter but slower impl here: https://yanivle.github.io/ai/2024/02/23/fast_minbpe.html

from collections import Counter, defaultdict
from typing import Any
import heapq

class Node:
    __slots__ = 'count', 'val', 'pos'

    def __init__(self, count: int, val: Any, pos: int):
        self.count = count
        self.val = val
        self.pos = pos

    @property
    def key(self):  # key for comparisons
        return self.count
        # Breaking ties explicitly, forcing more heap update, results in a significant slowdown:
        # return (self.count, self.val, self.pos)

    def __lt__(self, other):
        return self.key < other.key


class Multiset:
    def __init__(self, init=None, node_type=Node):
        self.l = []  # A heap of nodes.
        self.d = {}  # A map from value to its node.
        self.node_type = node_type
        self.to_add = defaultdict(int)
        self.to_remove = defaultdict(int)
        self.to_add.update(Counter(init))

    def add(self, item, count=1):
        self.to_add[item] += count

    def remove(self, item, count=1):
        self.to_remove[item] += count

    def _add(self, item, count=1):
        node = self.d.get(item)
        if node is None:
            node = self.d[item] = self.node_type(0, item, len(self.l))
            self.l.append(node)
        node.count += count
        self._item_increased(node.pos)

    def _remove(self, item, count=1):
        node = self.d[item]
        node.count -= count
        self._item_decreased(node.pos)
        # We could actually remove items with 0-count from the list, but
        # since for some scores its helpful to have items with arbitrary
        # counts, including negative, we're never actually removing items.

    def _commit(self):
        for pair, count in self.to_add.items():
            self._add(pair, count)
        for pair, count in self.to_remove.items():
            self._remove(pair, count)
        self.to_add.clear()
        self.to_remove.clear()

    def count(self, item):
        self._commit()
        if item not in self.d: return 0
        return self.d[item].count

    @property
    def most_common(self):
        self._commit()
        return self.l[0].val

    def top_k(self, k: int) -> list[tuple[Any, int]]:
        self._commit()
        totup = lambda n: (-n.key, n.val, n.count, n.pos)
        res, heap = [], [totup(self.l[0])]
        for _ in range(k):
            if not heap: break
            _key, val, count, pos = heapq.heappop(heap)
            res.append((val, count))
            for child_pos in [pos * 2 + 1, pos * 2 + 2]:
                if child_pos < len(self.l):
                    heapq.heappush(heap, totup(self.l[child_pos]))
        return res

    def __bool__(self):
        self._commit()
        return bool(self.l)

    # The below functions maintain the heap property:

    def _item_increased(self, pos):
        # Adapted from heapq._siftdown_max.
        node = self.l[pos]
        while pos > 0:
            parentpos = (pos - 1) >> 1
            parent = self.l[parentpos]
            if parent < node:
                self.l[pos] = parent
                parent.pos = pos
                pos = parentpos
                continue
            break
        self.l[pos] = node
        node.pos = pos

    def _item_decreased(self, pos):
        # Adapted from heapq._siftup_max.
        endpos = len(self.l)
        node = self.l[pos]
        childpos = 2 * pos + 1  # leftmost child position
        while childpos < endpos:
            # Set childpos to index of larger child.
            rightpos = childpos + 1
            if rightpos < endpos and not self.l[rightpos] < self.l[childpos]:
                childpos = rightpos
            childnode = self.l[childpos]
            if node < childnode:  # Move the larger child up.
                self.l[pos] = childnode
                childnode.pos = pos
                pos = childpos
                childpos = 2 * pos + 1
            else:
                break
        self.l[pos] = node
        node.pos = pos
