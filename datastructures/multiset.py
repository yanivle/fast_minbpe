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
# This is essentially the same as collections.Counter (I should have just used
# their API in retrospect) BUT most_common is MUCH faster.
#
# I have a shorter but slower impl here: https://yanivle.github.io/ai/2024/02/23/fast_minbpe.html

from collections import Counter

class Multiset:
    class Node:
        __slots__ = 'count', 'val', 'pos'

        def __init__(self, count, val, pos):
            self.count = count
            self.val = val
            self.pos = pos

        def __lt__(self, other):  # We're breaking ties by value.
            return self.count < other.count or (self.count == other.count and self.val < other.val)
            # This nicer line is slower:
            # return (self.count, self.val, self.pos) < (other.count, other.val, other.pos)

    def __init__(self, init=None):
        self.l = []  # A heap of nodes.
        self.d = {}  # A map from value to its node.
        for item, count in Counter(init).items():  # Counter constructs faster than us.
            self.add(item, count)

    def add(self, item, count=1):
        node = self.d.get(item)
        if node is None:
            node = self.d[item] = Multiset.Node(0, item, len(self.l))
            self.l.append(node)
        node.count += count
        self._item_increased(node.pos)

    def remove(self, item, count=1):
        node = self.d[item]
        node.count -= count
        self._item_decreased(node.pos)
        if node.count == 0:
            last = self.l.pop()
            if node is not last:
                self.l[node.pos] = last
                last.pos = node.pos
                if node < last:
                    self._item_increased(last.pos)
                else:
                    self._item_decreased(last.pos)
            del self.d[item]

    def count(self, item):
        if item not in self.d: return 0
        return self.d[item].count

    @property
    def most_common(self):
        return self.l[0].val

    def __bool__(self):
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
