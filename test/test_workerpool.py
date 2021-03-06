import unittest

from Queue import Queue, Empty
import sys
sys.path.append('../')

import workerpool


class TestWorkerPool(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self._pools = []
        super(TestWorkerPool, self).__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        try:
            super(TestWorkerPool, self).run(*args, **kwargs)
        finally:
            for pool in self._pools:
                pool.shutdown()

    def get_workerpool(self, *args):
        p = workerpool.WorkerPool(*args)
        self._pools.append(p)
        return p

    def double(self, i):
        return i * 2

    def add(self, *args):
        return sum(args)

    def test_map(self):
        "Map a list to a method to a pool of two workers."
        pool = self.get_workerpool(2)

        r = pool.map(self.double, [1, 2, 3, 4, 5])
        self.assertEquals(r, [2, 4, 6, 8, 10])

    def test_map_multiparam(self):
        "Test map with multiple parameters."
        pool = self.get_workerpool(2)
        r = pool.map(self.add, [1, 2, 3], [4, 5, 6])
        self.assertEquals(r, [5, 7, 9])

    def test_wait(self):
        "Make sure each task gets marked as done so pool.wait() works."
        pool = self.get_workerpool(5)
        q = Queue()
        for i in xrange(100):
            pool.put(workerpool.SimpleJob(q, sum, [range(5)]))
        pool.wait()

    def test_init_size(self):
        pool = self.get_workerpool(1)
        self.assertEquals(pool.size(), 1)

    def test_shrink(self):
        pool = self.get_workerpool(1)
        pool.shrink()
        self.assertEquals(pool.size(), 0)

    def test_grow(self):
        pool = self.get_workerpool(1)
        pool.grow()
        self.assertEquals(pool.size(), 2)

    def test_changesize(self):
        "Change sizes and make sure pool doesn't work with no workers."
        pool = self.get_workerpool(5)
        for i in xrange(5):
            pool.grow()
        self.assertEquals(pool.size(), 10)
        for i in xrange(10):
            pool.shrink()
        pool.wait()
        self.assertEquals(pool.size(), 0)

        # Make sure nothing is reading jobs anymore
        q = Queue()
        for i in xrange(5):
            pool.put(workerpool.SimpleJob(q, sum, [range(5)]))
        try:
            q.get(block=False)
        except Empty:
            pass  # Success
        else:
            assert False, "Something returned a result, even though we are"
            "expecting no workers."
