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
from functools import reduce
import time
import copy
import logging

logging.basicConfig(level=logging.INFO, format="%(name)s - [%(levelname)s]: %(message)s")
log = logging.getLogger('function_cache')


def set_cache_logLevel_to_debug():
    log.setLevel(logging.DEBUG)


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
            log.debug("func 'control_cache_size': Maximum cache size %s reached, shrinking ...")
            ccache = copy.deepcopy(cache)
            consume(starmap(ccache.pop,
                            ((a,) for a in takewhile(
                                lambda k: len(ccache) > size, cache.keys())
                             )), None
                    )
            cache = copy.deepcopy(ccache)
        log.debug("func 'control_cache_size': cache keys: %s" % list(cache.keys()))
    else:
        log.debug("func 'control_cache_size': cache keys: %s" % cache)


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


def list_or_tuple(obj):
    """Test if obj is either a list or a tuple.
    """
    return isinstance(obj, list) or isinstance(obj, tuple)


def hashable(obj):
    """Test if items in obj are hashable.
    """
    return (list_or_tuple(obj)
            and all(isinstance(key, Hashable) for key in obj))


def get_unhashable_item(obj):
    """Get one item in obj which is unhashable.
    """
    for it in obj:
        if not isinstance(it, Hashable):
            yield it


def remove_unhashable(obj, unh):
    """Remove unh from obj.
    """
    return tuple(it for it in obj if it is not unh)


def get_hashable_subset(obj):
    """Get a subset of obj (list or tuple) items that are hashable.
    """
    wh = lambda: ((hashable(
        remove_unhashable(obj, consume(get_unhashable_item(obj), 1)))
        or len(obj) == 0)
        or wh())
    return wh() and obj


def locally_cached(decorated=None, max_cache_size=50):
    """A decorator factory for turning a function into a locally cached one
    with the technique used here.
    """
    def decorator(func):
        def new_func(*args, local_cache=defaultdict(lambda: False), **kwargs):
            control_cache_size(local_cache, size=max_cache_size)
            map_fn = lambda x: ((isinstance(x, dict) and map(lambda k: x[k],
                                                             x.keys()))
                                or map(lambda y: y, x))
            obj = reduce(lambda x, y: tuple(
                [i for i in x] + [i for i in y]),
                (it for it in map(map_fn, [args, kwargs])))
            key = get_hashable_subset(obj)
            if key:
                log.debug("func '%s': Hashable key used for args '%s' "
                          "and kwargs '%s': %s",
                          func.__name__, args, kwargs, key)
                res = local_cache[key]
                if res:
                    log.debug("func '%s': Result retrieved from local cache",
                              func.__name__)
                    return res
                log.debug("The call with args '%s' and kwargs '%s' is absent "
                          "from cache for func '%s'",
                          args, kwargs, func.__name__)
                local_cache[key] = func(*args, **kwargs)
                return local_cache[key]
            log.debug("Unable to get a hashable subset of args '%s' and kwargs"
                      " '%s' for func '%s'",
                      args, kwargs, func.__name__)
            return func(*args, **kwargs)
        return new_func
    return (decorated and decorator(decorated)) or decorator


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
