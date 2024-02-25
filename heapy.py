# A max-heap that supports increasing/decreasing internal elements.
# Might have been nicer to do this with a standard array impl (and have each node hold itsown index), or maybe even reuse some of the heapq impl.
# Might also be nice to add a "remove" functionality at some point :)

class Heapy:
    class Node:
        def __init__(self, value=None, p=None, l=None, r=None):
            self.value = value  # A (__lt__ comparable) user supplied value.
            self.p = p  # Parent
            self.l = l  # Left child
            self.r = r  # Right child

        @property
        def leftmost_descendent(self):
            while self.l is not None:
                self = self.l
            return self

    def __init__(self):
        self.root = None
        self.last = None

    def swap_with_parent(self, node: Node):
        # Might be nicer to just implement a swap of 2 arbitrary elements (will also be easier to implement remove).
        # This function is really simple - just a bunch of pointers around:
        # - Update last and root if needed
        # - Fix 3 bidirectional pointers from node and node.p. Since we're swapping a child with its parent,
        #   2 pairs are counted twice, so we only need to fix 10 pointers.
        p = node.p
        if self.last is node:
            self.last = p
        if self.root is p:
            self.root = node
        if p.p is not None: # Fix the parent's parent.
            if p.p.l is p:
                p.p.l = node
            else:
                assert p.p.r is p
                p.p.r = node
        if node.l is not None:
            node.l.p = p
        if node.r is not None:
            node.r.p = p
        # Fix outgoing:
        if node is p.l:
            if p.r is not None:
                p.r.p = node
            node.p, node.l, node.r, p.p, p.l, p.r = p.p, p, p.r, node, node.l, node.r
        else:
            assert node is p.r
            p.l.p = node
            node.p, node.l, node.r, p.p, p.l, p.r = p.p, p.l, p, node, node.l, node.r

    def handle_increase(self, node: Node):  # Propagate node upwards
        while node.p is not None and node.value > node.p.value:
            self.swap_with_parent(node)

    def handle_decrease(self, node: Node):  # Propagate node downwards
        while node.l is not None:  # We have children
            bigger_child = node.r
            if node.r is None or node.r.value < node.l.value:
                bigger_child = node.l
            if node.value > bigger_child.value:
                return
            self.swap_with_parent(bigger_child)

    def insert(self, node: Node):
        assert node.p is None and node.r is None and node.l is None
        if self.root is None:  # Heap is empty
            self.root = self.last = node
            return
        # Now we find out where to insert:
        p = self.last
        while p.p and p is p.p.r:
            p = p.p
        if p.p is not None:
            right_sibling = p.p.r
            if right_sibling is not None:
                p = right_sibling.leftmost_descendent
            else:
                p = p.p
        else:
            p = p.leftmost_descendent

        # We need to insert as a child of p:
        self.last = node
        if p.l is None:
            p.l = node
        else:
            p.r = node
        node.p = p
        self.handle_increase(node)
