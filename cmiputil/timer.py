"""
Measuer execution time.

Bollowed from https://qiita.com/kazuhirokomoda/items/1e9b7ebcacf264b2d814
"""

from contextlib import contextmanager
import time

@contextmanager
def timer(name):
    """
    Measure execution time, contextmanager version.

    Args:
       name : identifier of measurement period.

    Examples:

    >>> from timer import timer
    >>> with timer('process train'):
    ...     hogehoge()


    """

    t0 = time.time()
    yield
    print(f'[{name}] done in {time.time() - t0:.0f} s')

