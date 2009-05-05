#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Apply basic example in Python Doc Module Unittest 5.3.1

file:///usr/share/doc/packages/python/html/lib/node160.html
"""

import random
import unittest

class TestSequenceFunctions(unittest.TestCase):
    
    def setUp(self):
        self.seq = range(10)

    def testshuffle(self):
        # make sure the shuffled sequence does not lose any elements
        random.shuffle(self.seq)
        self.seq.sort()
        self.assertEqual(self.seq, range(10))

    def testchoice(self):
        element = random.choice(self.seq)
        element = -1
        self.assert_(element in self.seq)

    def testsample(self):
        self.assertRaises(ValueError, random.sample, self.seq, 20)
        for element in random.sample(self.seq, 5):
            self.assert_(element in self.seq)

if __name__ == '__main__':
    #print unittest.getTestCaseNames(TestSequenceFunctions,'test')
    #unittest.main()
    suite = unittest.makeSuite(TestSequenceFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)



