#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
import unittest

from apache_beam.yaml import yaml_testing

# Note that executing this pipeline will actually fail if the untested
# transforms are not in fact elided.
SIMPLE_PIPELINE = '''
pipeline:
  type: chain
  transforms:
    - type: Create
      name: MyCreate
      config:
        elements: [1, 2, 3]
    - type: MapToFields
      name: MyMapToFields
      config:
        append: True
        language: python
        fields:
          square: element**2
    - type: MapToFields
      name: ToBeExcluded
      config:
        language: python
        fields:
          bad:
            callable: |
              def non_shall_pass(row):
                raise ValueError(row)
'''


class YamlTestingTest(unittest.TestCase):
  def test_expected_outputs(self):
    yaml_testing.run_test(
        SIMPLE_PIPELINE,
        {
            'expected_outputs': [{
                'name': 'MyMapToFields',
                'elements': [
                    {
                        'element': 1, 'square': 1
                    },
                    {
                        'element': 2, 'square': 4
                    },
                    {
                        'element': 3, 'square': 9
                    },
                ]
            }]
        })

    # As well as passing, we want to ensure the test fails when it should.
    with self.assertRaisesRegex(Exception, 'unexpected.*9'):
      yaml_testing.run_test(
          SIMPLE_PIPELINE,
          {
              'expected_outputs': [{
                  'name': 'MyMapToFields',
                  'elements': [
                      {
                          'element': 1, 'square': 1
                      },
                      {
                          'element': 2, 'square': 4
                      },
                  ]
              }]
          })

  def test_expected_inputs(self):
    yaml_testing.run_test(
        SIMPLE_PIPELINE,
        {
            'expected_inputs': [{
                'name': 'ToBeExcluded',
                'elements': [
                    {
                        'element': 1, 'square': 1
                    },
                    {
                        'element': 2, 'square': 4
                    },
                    {
                        'element': 3, 'square': 9
                    },
                ]
            }]
        })

    # As well as passing, we want to ensure the test fails when it should.
    with self.assertRaisesRegex(Exception, 'unexpected.*9'):
      yaml_testing.run_test(
          SIMPLE_PIPELINE,
          {
              'expected_inputs': [{
                  'name': 'ToBeExcluded',
                  'elements': [
                      {
                          'element': 1, 'square': 1
                      },
                      {
                          'element': 2, 'square': 4
                      },
                  ]
              }]
          })


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  unittest.main()
