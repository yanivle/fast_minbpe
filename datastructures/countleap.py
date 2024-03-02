from collections import defaultdict
from . import Leap, Multiset


class CountLeap:
    # A lightweight Leap wrapper that also manages a Mutiset of its elements.
    def __init__(self, leap: Leap, stats: Multiset):
        self.leap = leap
        self.stats = stats
        # More verbose but cheaper to maintain these dicts and update our multiset only once per item affected.
        self.pairs_to_add = defaultdict(int)
        self.pairs_to_remove = defaultdict(int)

    def occurrences(self, val):
        return self.leap.occurrences(val)

    def delete(self, node):
        self.pairs_to_remove[node.val] += 1
        self.leap.delete(node)
    
    def set_value(self, node, new_pair):
        self.pairs_to_remove[node.val] += 1
        self.pairs_to_add[new_pair] += 1
        self.leap.set_value(node, new_pair)

    def commit(self):  # Commiting once is faster than adding/removing each element directly.
        for pair, count in self.pairs_to_add.items():
            self.stats.add(pair, count)
        for pair, count in self.pairs_to_remove.items():
            self.stats.remove(pair, count)
        self.pairs_to_add.clear()
        self.pairs_to_remove.clear()
