# A "Leap" (or should I call it a "Leaped-List"?) is a data strucure
# representing an ordered array, supporting the same ops as a basic
# doubly-linked list in O(1):
#
# - append(x): appends x to the end of the leap.
# - delete(n): removes node n from the leap.
# - start(x): returns the first node in the leap.
# - end(x): returns the last node in the leap.
# - next(n): returns the node following node n.
# - prev(n): returns the node preceding node n.
#
# It also supports these leap operations in O(1) as well:
# - first(x): returns the first node in the leap *with value x*.
# - last(x): returns the last node in the leap *with value x*.
# - leap(n): returns first node after node n *with the same value as n*.
# - leapback(n): returns last node before node n *with the same value as n*.
# - setvalue(n, x): set the value of node n to x (keep its position).
#
# In addition to standard efficient in-order iteration on all elements, a leap
# also allows efficient in-order iteration on all elements with a given value.
#
# I guess this data structure must exist, so if you know it and know its name,
# please lmk :)


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
            self.next = self.prev = None  # Not actually needed.

        def _delete_from_val(self):
            if self.leapback is not None:
                self.leapback.leap = self.leap
            if self.leap is not None:
                self.leap.leapback = self.leapback
            self.leap = self.leapback = None  # Not actually needed.

        def append_to_pos(self, next):
            self.next, next.prev = next, self

        def append_to_val(self, next):
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
        node = self.first[val]
        while node is not None:
            yield node
            node = node.leap

    def to_python_list(self):
        return [x.val for x in self]

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
            self.end.append_to_pos(node)
        self.end = node

    def _append_to_val(self, node):
        if node.val not in self.first:  # First item.
            self.first[node.val] = node
        else:
            self.last[node.val].append_to_val(node)
        self.last[node.val] = node
