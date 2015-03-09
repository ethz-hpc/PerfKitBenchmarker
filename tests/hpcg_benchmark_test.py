# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for HPCG benchmark."""
import os
import unittest

import mock

from perfkitbenchmarker.benchmarks import hpcg_benchmark


class HPCGTestCase(unittest.TestCase):

  def setUp(self):
    p = mock.patch(hpcg_benchmark.__name__ + '.FLAGS')
    p.start()
    self.addCleanup(p.stop)

    path = os.path.join(os.path.dirname(__file__), 'data', 'hpcg-sample.txt')
    with open(path) as fp:
      self.contents = fp.read()

  def testParseHpcc(self):
    benchmark_spec = mock.MagicMock()
    result = hpcg_benchmark.ParseOutput(self.contents, benchmark_spec)
    self.assertEqual(6, len(result))
    results = {i[0]: i[1] for i in result}

    self.assertAlmostEqual(10.50, results['HPCG Throughput'])


if __name__ == '__main__':
  unittest.main()
