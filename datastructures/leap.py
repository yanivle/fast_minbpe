# A "Leap" (or should I call it a "Leaped-List"?) is a data strucure
# representing an ordered array, that supports efficient in-order iteration on
# all elements as well as efficient in-order iteration on all elements *with a
# given value*.
#
# Specifically, it supports the same ops as a basic doubly-linked list in O(1),
# but importantly trades insert(x) for append(x):
# - append(x): appends x to the end of the leap.
# - delete(n): removes node n from the leap.
# - start(x): returns the first node in the leap.
# - end(x): returns the last node in the leap.
# - next(n): returns the node following node n.
# - prev(n): returns the node preceding node n.
#
# In return, it supports these leap-specific operations in O(1) as well:
# - first(x): returns the first node in the leap *with value x*.
# - last(x): returns the last node in the leap *with value x*.
# - leap(n): returns first node after node n *with the same value as n*.
# - leapback(n): returns last node before node n *with the same value as n*.
# - set_value(n, x): sets the value of node n to x (must be last node with value x).
#
# I guess this data structure must exist, so if you know it and know its name,
# please lmk :)
#
# The code is about twice as long as it needs to be as the impls of the pos ops
# and the value ops are almost identical. Originally I had such a compact
# implementation, with the added benefit of being easily generalizable to
# leaping by any number of object properties, but it was slower than the more
# verbose one below, so I'm keeping this one.


class Leap:
    # Internally, a leap-node is just a superposition of 2 doubly-linked lists,
    # one for prev/next and another for leapback/leap.
    class Node:
        def __init__(self, val):
            self.val = val
            self.prev, self.next, self.leap, self.leapback = None, None, None, None

        def _delete_from_pos(self):
            if self.prev is not None:
                self.prev.next = self.next
            if self.next is not None:
                self.next.prev = self.prev
            self.next = self.prev = None

        def _delete_from_val(self):
            if self.leapback is not None:
                self.leapback.leap = self.leap
            if self.leap is not None:
                self.leap.leapback = self.leapback
            self.leap = self.leapback = None

        def _append_to_pos(self, next):
            self.next, next.prev = next, self

        def _append_to_val(self, next):
            self.leap, next.leapback = next, self

    def __init__(self, init=None):
        self.first = {}  # Map from a value to its first occurrence.
        self.last = {}  # Map from a value to its last occurrence.
        self.start = self.end = None
        if init is not None:
            for x in init:
                self.append(x)

    def __iter__(self):  # Iterate on all nodes.
        node = self.start
        while node is not None:
            yield node
            node = node.next

    def occurrences(self, val):  # Iterate on all nodes with value val.
        node = self.first.get(val)
        while node is not None:
            yield node
            node = node.leap

    def delete(self, node):
        self._delete_from_pos(node)
        self._delete_from_val(node)

    def append(self, val):
        node = Leap.Node(val)
        self._append_to_pos(node)
        self._append_to_val(node)

    def set_value(self, node, new_val): # Replaces the value of a node in-place.
        self._delete_from_val(node)
        node.val = new_val
        self._append_to_val(node)

    def _delete_from_pos(self, node):
        if self.start is node:
            self.start = node.next
        if self.end is node:
            self.end = node.prev
        node._delete_from_pos()

    def _delete_from_val(self, node):
        if self.first[node.val] is node:
            self.first[node.val] = node.leap
        if self.last[node.val] is node:
            self.last[node.val] = node.leapback
        node._delete_from_val()

    def _append_to_pos(self, node):
        if self.start is None:  # First item.
            self.start = node
        else:
            self.end._append_to_pos(node)
        self.end = node

    def _append_to_val(self, node):
        if self.first.get(node.val) is None:  # First item.
            self.first[node.val] = node
        else:
            self.last[node.val]._append_to_val(node)
        self.last[node.val] = node
