# A simple linked-list that maintains a (possibly stale) index to its k-tuples.
# The index maps from a k-tuple (X1, X2, ..., Xk) to all nodes that might
# contain X1 and whose next node might contain X2, etc until Xk.
# The index is stale in the sense that we only add things to it, never remove.
# So when actually iterating on elements from the index, we need to make sure
# that the nodes still hold the desired k-tuple.
#
# For k=2 this is exactly the same as IndexedList (but slower so keeping both).

from collections import deque
from itertools import pairwise
from typing import Self


class IndexedKList:
    class Node:
        __slots__ = 'val', 'prev', 'next'
        def __init__(self, val, prev=None, next=None):
            self.val, self.prev, self.next = val, prev, next

        def delete(self):  # Delete self from the linked list.
            if self.prev is not None:
                self.prev.next = self.next
            if self.next is not None:
                self.next.prev = self.prev
            self.next = self.prev = None

        def link(self, next: Self):  # Connect next after self.
            self.next, next.prev = next, self

        def next_nodes(self, n: int):
            # Return the next (at most) n nodes (including us).
            # If called on the first node, similar to lst[:n].
            nodes = []
            node = self
            for _ in range(n):
                if node is None: break
                nodes.append(node)
                node = node.next
            return nodes

        def go_back(self, n: int):
            # Return the node n nodes behind us (or less if there aren't enough
            # previous nodes) and the actual number of nodes we moved back.
            node = self
            for i in range(n):
                if node.prev is None: return node, i
                node = node.prev
            return node, n

        def tuple(self, k):
            return tuple([n.val for n in self.next_nodes(k)])

    # TODO: Maybe the impl from IndexedXList is a bit cleaner.
    def __init__(self, l, k):
        self.k = k
        self.index = {}  # Possibly stale.
        l = iter(l)
        prev_nodes = deque([], maxlen=k)
        for _ in range(k - 1):
            prev_nodes.append(IndexedKList.Node(next(l)))
        for a, b in pairwise(prev_nodes):
            a.link(b)
        self.start = prev_nodes[0]
        for b in l:
            prev_nodes.append(IndexedKList.Node(b))
            prev_nodes[-2].link(prev_nodes[-1])
            self.add_to_index(tuple([n.val for n in prev_nodes]), prev_nodes[0])


    def __iter__(self):
        node = self.start
        while node is not None:
            yield node
            node = node.next

    def update_index(self, node):
        start_node, i = node.go_back(self.k - 1)
        nodes = start_node.next_nodes(i + self.k)
        while len(nodes) >= self.k:
            self.add_to_index(tuple([n.val for n in nodes[:self.k]]), nodes[0])
            nodes = nodes[1:]

    def add_to_index(self, key, node):
        self.index.setdefault(key, []).append(node)

