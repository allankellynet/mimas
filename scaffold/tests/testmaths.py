#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

import unittest
from google.appengine.ext import testbed

from scaffold import maths


class TestMaths(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_mean(self):
        self.assertEquals(1, maths.mean([1]))
        self.assertEquals(2, maths.mean([1,2,3]))
        self.assertEquals(2.5, maths.mean([1,2,3,4]))
        self.assertEquals(5, maths.mean([1,2,3,4,5,6,7,8,9]))

    def test_median(self):
        self.assertEquals(1, maths.median([1]))
        self.assertEquals(1.5, maths.median([1, 2]))
        self.assertEquals(2, maths.median([1,2,3]))
        self.assertEquals(1.5, maths.median([1,1,2,2]))
        self.assertEquals(2.5, maths.median([1,2,3,4]))
        self.assertEquals(5, maths.median([1, 1, 1, 5, 5, 5, 5, 5, 5]))
        self.assertEquals(2, maths.median([1, 2, 3, 4, 5, 1, 2, 2, 2]))
