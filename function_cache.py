"""
This file demonstrates a technique that can help accelerating function calls
with a very simple cache.
We use the property of mutable objects passed as default values in function
signatures: when the mutable is modified, its value is remembered in the
function scope, so that each time a user calls the function, the default value
is available to the function scope.
Note that if a user calls the function overriding the default parameter, the
function looses its superpower :-( ! (At least, the cache is wiped and a the
last state of the cache is retrieved for subsequent calls that don't
override it)
"""


from collections import defaultdict
from collections import Hashable
from collections import deque
from itertools import starmap
from itertools import takewhile
from itertools import islice
import time
import copy


def consume(iterator, n):
    """Advance the iterator n-steps ahead. If n is none, consume entirely.

    Source: https://docs.python.org/2/library/itertools.html#recipes
    """
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)


def control_cache_size(cache, size=20):
    """A function controlling the growth of the cache.
    """
    if cache is not None:
        if len(cache) > size:
            ccache = copy.deepcopy(cache)
            consume(starmap(ccache.pop,
                            ((a,) for a in takewhile(
                                lambda k: len(ccache) > size, cache.keys())
                             )), None
                    )
            cache = copy.deepcopy(ccache)
        print("cache keys: %s" % list(cache.keys()))
    else:
        print("cache keys: %s" % cache)


def heavy_func(key, local_cache=defaultdict(lambda: False)):
    control_cache_size(local_cache)
    computed = None
    if isinstance(key, Hashable) and local_cache is not None:
        computed = local_cache[key]
        if computed:
            return computed
    time.sleep(0.1)   # Simulate heavy computation
    ret_val = key
    if computed is not None:
        local_cache[key] = ret_val
    return ret_val


if __name__ == '__main__':
    # First use case: Full use of the superpower !
    print("First use case (populate the cache):")
    start = time.time()
    for i in range(50):
        heavy_func(i)
    print("Elapsed: %s" % str(time.time() - start))
    print("First use case (show the superpower):")
    start = time.time()
    for i in range(50):
        heavy_func(i)
    print("Elapsed: %s" % str(time.time() - start))
    # Second use case: Don't use the cache alternately => a little bit faster
    # than without a cache at all (values are computed each time the cache is
    # ignored, but retrieved from the last state of the cache)
    print("Second use case:")
    start = time.time()
    for i in range(50):
        if i % 2 == 0:
            heavy_func(i, local_cache=None)
        else:
            heavy_func(i)
    print("Elapsed: %s" % str(time.time() - start))
    # Third use case: Always flush the cache => We loose the superpower :-(
    print("Third use case:")
    start = time.time()
    for i in range(50):
        heavy_func(i, local_cache=None)
    print("Elapsed: %s" % str(time.time() - start))
