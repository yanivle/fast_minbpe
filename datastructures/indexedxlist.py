# A simple linked-list that maintains a (possibly stale) index to its k-tuples
# for all 2 <= k <= x.
# The index maps from a k-tuple (X1, X2, ..., Xk) to all nodes that might
# contain X1 and whose next node might contain X2, etc until Xk.
# The index is stale in the sense that we only add things to it, never remove.
# So when actually iterating on elements from the index, we need to make sure
# that the nodes still hold the desired k-tuple.
#
# Same as IndexedKList but for all k-tuples for 2 <= k <= x instead of a single k.
# For k=2 this is exactly the same as IndexedKList (and IndexedList) but slower.
from itertools import pairwise
from .indexedklist import IndexedKList


class IndexedXList:
    Node = IndexedKList.Node

    def __init__(self, l, x):
        self.x = x
        self.index = {}  # Possibly stale.
        nodes = [IndexedXList.Node(v) for v in l]
        for a, b in pairwise(nodes):
            a.link(b)
        self.start = nodes[0]
        for n in self:
            self.update_index(n, include_prev=False)

    def __iter__(self):
        node = self.start
        while node is not None:
            yield node
            node = node.next

    def touching_nodes(self, node, include_prev:bool = True):
        start_node, n_prev = node, 0
        if include_prev:
            start_node, n_prev = node.go_back(self.x - 1)
        nodes = start_node.next_nodes(n_prev + self.x)
        vals = tuple([n.val for n in nodes])
        for k in range(2, self.x + 1):
            start = max(0, n_prev - (k - 1))
            end = min(n_prev + 1, len(nodes) - (k - 1))
            for i in range(start, end):
                yield vals[i:i + k], nodes[i]

    def update_index(self, node, include_prev:bool = True):
        for tup, n in self.touching_nodes(node, include_prev):
            self.add_to_index(tup, n)

    def add_to_index(self, key, node):
        self.index.setdefault(key, []).append(node)
