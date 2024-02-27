# A max-heap that supports increasing/decreasing counts of internal elements.
# If you're interested in a much shorter impl (but about twice as slow) see my
# post here: https://yanivle.github.io/ai/2024/02/23/fast_minbpe.html


class HeapyKiYay:
    # Internally, the elements are lists of length 3: [count, value, pos]:
    # - count is first as we want to compare by count.
    # - value is second, so we're breaking ties by value.
    # - each item x maintains its own position at x[-1].
    # - count and pos are updated, so we use a mutable list.
    def __init__(self):
        self.l = []

    @property
    def max(self):
        return self.l[0][1]  # The value of the max item.

    def increase(self, x):
        x[0] += 1
        _item_increased(self.l, x[-1])

    def decrease(self, x):
        x[0] -= 1
        _item_decreased(self.l, x[-1])

    def insert(self, val):
        x = [0, val, len(self.l)]
        self.l.append(x)
        self.increase(x)
        return x

    def delete(self, x):
        last = self.l.pop()
        if x is not last:
            self.l[x[-1]] = last
            last[-1] = x[-1]
            if x < last:
                _item_increased(self.l, last[-1])
            else:
                _item_decreased(self.l, last[-1])


def _item_increased(heap, pos):
    # Adapted from heapq._siftdown_max
    item = heap[pos]
    while pos > 0:
        parentpos = (pos - 1) >> 1
        parent = heap[parentpos]
        if parent < item:
            heap[pos] = parent
            heap[pos][-1] = pos
            pos = parentpos
            continue
        break
    heap[pos] = item
    heap[pos][-1] = pos


def _item_decreased(heap, pos):
    # Adapted from heapq._siftup_max.
    endpos = len(heap)
    item = heap[pos]
    childpos = 2 * pos + 1  # leftmost child position
    while childpos < endpos:
        # Set childpos to index of larger child.
        rightpos = childpos + 1
        if rightpos < endpos and not heap[rightpos] < heap[childpos]:
            childpos = rightpos
        if item < heap[childpos]:  # Move the larger child up.
            heap[pos] = heap[childpos]
            heap[pos][-1] = pos
            pos = childpos
            childpos = 2*pos + 1
        else:
            break
    heap[pos] = item
    heap[pos][-1] = pos
