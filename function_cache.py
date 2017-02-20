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
    if len(cache) > size:
        ccache = copy.deepcopy(cache)
        consume(starmap(ccache.pop,
                        ((a,) for a in takewhile(lambda k: len(ccache) > size,
                                                 cache.keys()))), None)
        cache = copy.deepcopy(ccache)
    print("cache keys: %s" % list(cache.keys()))


def heavy_func(key, local_cache=defaultdict(lambda: False)):
    control_cache_size(local_cache)
    computed = None
    if isinstance(key, Hashable):
        computed = local_cache[key]
        if computed:
            return computed
    time.sleep(0.1)   # Simulate heavy computation
    ret_val = key
    if computed is not None:
        local_cache[key] = ret_val
    return ret_val


if __name__ == '__main__':
    for i in range(50):
        heavy_func(i)
