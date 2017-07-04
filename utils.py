"""Miscellaneous utils."""

import random
import itertools
from collections import Counter


def weighted_choice(options, weights):
    """Choose an item from options using weights."""
    sum_of_weights = sum(weights)
    rand = random.uniform(0, sum_of_weights)
    total = 0
    for item, weight in zip(options, weights):
        total += weight
        if rand < total:
            return item


def group(iterable, n):
    """Group items in `iterable` into `n` sized chunks

    >>> list(group(range(4), 3))
    [[0, 1, 2], [3]]

    >>> list(group(range(5), 3))
    [[0, 1, 2], [3, 4]]

    >>> list(group(range(6), 3))
    [[0, 1, 2], [3, 4, 5]]

    """

    chunk = []
    for progress, item in enumerate(iterable):
        chunk.append(item)
        if progress % n == n - 1:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def counter_percentages(counter):
    """
    >>> c = Counter()
    >>> for x in range(5) + range(3):
    ...     c[x] += 1
    >>> counter_percentages(c)
    [(0, 25.0), (1, 25.0), (2, 25.0), (3, 12.5), (4, 12.5)]
    """
    total = float(sum(counter.values()))
    return [(key, round((count / total) * 100, 1)) for key, count in counter.most_common()]


def pairwise(iterable):
    """
    >>> list(pairwise(range(5)))
    [(0, 1), (1, 2), (2, 3), (3, 4)]

    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def n_wise(iterable, n):
    """Iterate through `iterable` in groups of `n` items.

    >>> list(n_wise(range(5), 2))
    [(0, 1), (1, 2), (2, 3), (3, 4)]

    >>> list(n_wise(range(5), 3))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4)]

    >>> list(n_wise(range(5), 4))
    [(0, 1, 2, 3), (1, 2, 3, 4)]

    """
    iterators = itertools.tee(iterable, n)
    for index, iterator in enumerate(iterators):
        for _ in range(index):
            next(iterator, None)
    return itertools.izip(*iterators)


def ngrams(iterable, n):
    """
    >>> list(ngrams(range(6), 3))
    [[0, 1, 2], [1, 2, 3], [2, 3, 4], [3, 4, 5]]

    """
    if n == 1:
        for item in iterable:
            yield [item]
    for i, item in enumerate(iterable[:-n + 1]):
        yield iterable[i:i + n]


def get_first_item(items, value, key='id'):
    """
    >>> items = [{'c': 'd', 'bacon': 5}, {'a': 'b', 'bacon': 4}]
    >>> get_first_item(items, 4, key='bacon')
    {'a': 'b', 'bacon': 4}

    """
    return next((item for item in items if item.get(key) == value), None)


def get_multiple_items(items, value, key='id'):
    """
    >>> items = [{'c': 'd', 'bacon': 5}, {'a': 'b', 'bacon': 4}, {1: 7, 'bacon': 4}]
    >>> get_multiple_items(items, 4, key='bacon')
    [{'a': 'b', 'bacon': 4}, {1: 7, 'bacon': 4}]

    """
    return [item for item in items if item.get(key) == value]


def is_prime(N):
    """is_prime(N:long):bool
    Return true if N is prime.

    Taken from number.py in the Python Cryptography Toolkit

    """

    # Small primes used for checking primality; these are all the primes
    # less than 256.  This should be enough to eliminate most of the odd
    # numbers before needing to do a Rabin-Miller test at all.
    sieve=[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59,
           61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127,
           131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193,
           197, 199, 211, 223, 227, 229, 233, 239, 241, 251]

    N = long(N)

    if N == 1:
        return False
    if N in sieve:
        return True
    for i in sieve:
        if (N % i) == 0:
            return False

    # Compute the highest bit that's set in N
    N1 = N - 1L
    n = 1L
    while (n < N):
        n = n << 1L
    n = n >> 1L

    # Rabin-Miller test
    for c in sieve[:7]:
        a = long(c)
        d = 1L
        t = n
        while (t):  # Iterate over the bits in N1
            x = (d * d) % N
            if x == 1L and d != 1L and d != N1:
                return False  # Square root of 1 found
            if N1 & t:
                d = (x * a) % N
            else:
                d = x
            t = t >> 1L
        if d != 1L:
            return False
    return True


def fibonacci(n):
    a, b = 0, 1
    for x in xrange(n):
        a, b = b, a + b
    return a


def flatten(l):
    """flatten a (shallow) list of lists of items"""
    return [item for sublist in l for item in sublist]


def split_list(lst, n_chunks):
    '''Break a list into `n_chunks` lists of approximately equal length

    >>> list(split_list(range(6), 3))
    [0, 1], [2, 3], [4, 5]
    >>> list(split_list(range(7), 3))
    [0, 1], [2, 3, 4], [5, 6]

    '''
    chunk_size = len(lst) / float(n_chunks)
    for bottom, top in pairwise(chunk_size * i for i in xrange(n_chunks + 1)):
        chunk = [p for i, p in enumerate(lst) if bottom <= (i + .5) < top]
        yield chunk


if __name__ == '__main__':
    import doctest
    doctest.testmod()
