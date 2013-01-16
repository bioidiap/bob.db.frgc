#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Thu Sep  6 09:01:32 CEST 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Sanity checks for the FRGC database.
"""

import os, sys
import unittest
import bob
import random
from nose.plugins.skip import SkipTest


import xbob.db.frgc

class FRGCDatabaseTest(unittest.TestCase):
  """Performs some tests on the FRGC database."""

  def setUp(self):
    interface = xbob.db.frgc.driver.Interface()
    if os.path.exists(interface.frgc_database_directory()):
      self.m_db = xbob.db.frgc.Database()
      self.m_skip_tests = False
    else:
      self.m_db_dir = interface.frgc_database_directory()
      self.m_skip_tests = True


  def test01_client_ids(self):
    # Tests that the 'client_ids()' and 'model_ids()' functions return the desired number of elements.
    if self.m_skip_tests:
      raise SkipTest("The database directory '%s' is not available."%self.m_db_dir)

    # the protocols training, dev, idiap
    protocols = self.m_db.m_protocols

    # client counter
    self.assertEqual(len(self.m_db.client_ids(groups='world')), 222)
    for protocol in protocols:
      self.assertEqual(len(self.m_db.client_ids(protocol=protocol)), 535)
      self.assertEqual(len(self.m_db.client_ids(groups='dev', protocol=protocol)), 466)

    # for different mask types, the client counters of 'enrol' and 'probe' are different
    for protocol in protocols:
      self.assertEqual(len(self.m_db.client_ids(groups='dev', protocol=protocol, purposes='enrol', mask_type='maskI')), 466)
      self.assertEqual(len(self.m_db.client_ids(groups='dev', protocol=protocol, purposes='probe', mask_type='maskI')), 450)
      self.assertEqual(len(self.m_db.client_ids(groups='dev', protocol=protocol, purposes='enrol', mask_type='maskII')), 466)
      self.assertEqual(len(self.m_db.client_ids(groups='dev', protocol=protocol, purposes='probe', mask_type='maskII')), 461)
      self.assertEqual(len(self.m_db.client_ids(groups='dev', protocol=protocol, purposes='enrol', mask_type='maskIII')), 370)
      self.assertEqual(len(self.m_db.client_ids(groups='dev', protocol=protocol, purposes='probe', mask_type='maskIII')), 345)

    # check the number of models
    self.assertEqual(len(self.m_db.model_ids(groups='world')), 12776)
    self.assertEqual(len(self.m_db.model_ids(groups='dev', protocol='2.0.1', mask_type='maskI')), 14628)
    self.assertEqual(len(self.m_db.model_ids(groups='dev', protocol='2.0.2', mask_type='maskI')), 3657)
    self.assertEqual(len(self.m_db.model_ids(groups='dev', protocol='2.0.4', mask_type='maskI')), 14628)
    self.assertEqual(len(self.m_db.model_ids(groups='dev', protocol='2.0.1', mask_type='maskII')), 15336)
    self.assertEqual(len(self.m_db.model_ids(groups='dev', protocol='2.0.2', mask_type='maskII')), 3834)
    self.assertEqual(len(self.m_db.model_ids(groups='dev', protocol='2.0.4', mask_type='maskII')), 15336)
    self.assertEqual(len(self.m_db.model_ids(groups='dev', protocol='2.0.1', mask_type='maskIII')), 7572)
    self.assertEqual(len(self.m_db.model_ids(groups='dev', protocol='2.0.2', mask_type='maskIII')), 1893)
    self.assertEqual(len(self.m_db.model_ids(groups='dev', protocol='2.0.4', mask_type='maskIII')), 7572)


  def test02_objects(self):
    # Tests that the 'objects()' function returns reasonable output.
    if self.m_skip_tests:
      raise SkipTest("The database directory '%s' is not available."%self.m_db_dir)

    # query all File objects
    self.assertEqual(len(self.m_db.objects(mask_type = None)), 36818)
    self.assertEqual(len(self.m_db.objects(mask_type = 'maskI')), 36110)
    self.assertEqual(len(self.m_db.objects(mask_type = 'maskII')), 36500)
    self.assertEqual(len(self.m_db.objects(mask_type = 'maskIII')), 33032)


    # The number of objects should always be identical to the number of models...
    protocols = self.m_db.m_protocols
    masks = self.m_db.m_mask_types

    self.assertEqual(len(self.m_db.objects(groups='world')), len(self.m_db.model_ids(groups='world')))

    for mask in masks:
      # the number of models and model files should be identical for protocol 1 and 4
      for protocol in ('2.0.1', '2.0.4'):
        self.assertEqual(len(self.m_db.objects(groups='dev', protocol=protocol, purposes='enrol', mask_type=mask)),
                         len(self.m_db.model_ids(groups='dev', protocol=protocol, mask_type=mask)))

      # for protocol 2, there are 4 files for each model
      self.assertEqual(len(self.m_db.objects(groups='dev', protocol='2.0.2', purposes='enrol', mask_type=mask)),
                       len(self.m_db.model_ids(groups='dev', protocol='2.0.2', mask_type=mask)) * 4)

    # the number of probes actually differ between the masks, and between the protocols
    self.assertEqual(len(self.m_db.objects(groups='dev', protocol='2.0.1', purposes='probe', mask_type='maskI')), 14612)
    self.assertEqual(len(self.m_db.objects(groups='dev', protocol='2.0.1', purposes='probe', mask_type='maskII')), 15392)
    self.assertEqual(len(self.m_db.objects(groups='dev', protocol='2.0.1', purposes='probe', mask_type='maskIII')), 8456)
    self.assertEqual(len(self.m_db.objects(groups='dev', protocol='2.0.2', purposes='probe', mask_type='maskI')), 14612)
    self.assertEqual(len(self.m_db.objects(groups='dev', protocol='2.0.2', purposes='probe', mask_type='maskII')), 15392)
    self.assertEqual(len(self.m_db.objects(groups='dev', protocol='2.0.2', purposes='probe', mask_type='maskIII')), 8456)
    self.assertEqual(len(self.m_db.objects(groups='dev', protocol='2.0.4', purposes='probe', mask_type='maskI')), 7306)
    self.assertEqual(len(self.m_db.objects(groups='dev', protocol='2.0.4', purposes='probe', mask_type='maskII')), 7696)
    self.assertEqual(len(self.m_db.objects(groups='dev', protocol='2.0.4', purposes='probe', mask_type='maskIII')), 4228)

    # as far as I know, the number of probes should be identical for each model...
    for model_id in random.sample(self.m_db.model_ids(groups='dev', protocol='2.0.4', mask_type='maskIII'), 50):
      self.assertEqual(len(self.m_db.objects(groups='dev', protocol='2.0.4', purposes='probe', mask_type='maskIII', model_ids=model_id)), 4228)


  def test03_file_ids(self):
    # Tests that the client id's returned by the 'get_client_id_from_file_id()' and 'get_client_id_from_model_id()' functions are correct.
    if self.m_skip_tests:
      raise SkipTest("The database directory '%s' is not available."%self.m_db_dir)

    # this test might take a while...
    protocol = self.m_db.m_protocols[0]
    # extract all models
    for model_id in random.sample(self.m_db.model_ids(groups='dev', protocol=protocol), 100):
      # get the client id of the model
      client_id = self.m_db.get_client_id_from_model_id(model_id)
      # check that all files with the same model id share the same client id
      for file in self.m_db.objects(groups='dev', protocol=protocol, model_ids=(model_id,), purposes='enrol'):
        self.assertEqual(self.m_db.get_client_id_from_file_id(file.id), client_id)


  def test04_annotations(self):
    # Tests that the annotations are available for all files
    # we test only one of the protocols
    if self.m_skip_tests:
      raise SkipTest("The database directory '%s' is not available."%self.m_db_dir)

    for protocol in random.sample(self.m_db.m_protocols, 1):
      files = self.m_db.objects(protocol=protocol)
      for file in random.sample(files, 1000):
        annotations = self.m_db.annotations(file.id)
        for t in 'leye', 'reye', 'mouth', 'nose':
          self.assertTrue(t in annotations)
          self.assertEqual(len(annotations[t]), 2)


  def test05_driver_api(self):
    # Tests the frgc driver API.
    if self.m_skip_tests:
      raise SkipTest("The database directory '%s' is not available."%self.m_db_dir)

    from bob.db.script.dbmanage import main
    self.assertEqual( main('frgc dumplist --self-test'.split()), 0 )
    self.assertEqual( main('frgc dumplist --group=dev --protocol=2.0.4 --purpose=enrol --self-test'.split()), 0 )
    self.assertEqual( main('frgc checkfiles --self-test'.split()), 0 )
    # This function is deprecated, it is not tested any more
    #self.assertEqual( main('frgc create-annotation-files --directory . --self-test'.split()), 0 )

