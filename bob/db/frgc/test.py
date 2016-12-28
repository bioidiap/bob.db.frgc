#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Sanity checks for the FRGC database.
"""

import os, sys
import random
from nose.plugins.skip import SkipTest


import bob.db.frgc

db = None

def db_available(test):
  """Decorator for detecting if OpenCV/Python bindings are available"""
  import functools

  @functools.wraps(test)
  def wrapper(*args, **kwargs):
    interface = bob.db.frgc.driver.Interface()
    db_directory = interface.frgc_database_directory()
    if os.path.exists(db_directory):
      global db
      db = bob.db.frgc.Database()
      return test(*args, **kwargs)
    else:
      raise SkipTest("The database directory '%s' is not available."%db_directory)

  return wrapper


@db_available
def test_client_ids():
  # Tests that the 'client_ids()' and 'model_ids()' functions return the desired number of elements.

  # the protocols training, dev, idiap
  protocols = db.m_protocols

  # client counter
  assert len(db.client_ids(groups='world')) == 222
  for protocol in protocols:
    assert len(db.client_ids(protocol=protocol)) == 535
    assert len(db.client_ids(groups='dev', protocol=protocol)) == 466

  # for different mask types, the client counters of 'enroll' and 'probe' are different
  for protocol in protocols:
    assert len(db.client_ids(groups='dev', protocol=protocol, purposes='enroll', mask_type='maskI')) == 466
    assert len(db.client_ids(groups='dev', protocol=protocol, purposes='probe', mask_type='maskI')) == 450
    assert len(db.client_ids(groups='dev', protocol=protocol, purposes='enroll', mask_type='maskII')) == 466
    assert len(db.client_ids(groups='dev', protocol=protocol, purposes='probe', mask_type='maskII')) == 461
    assert len(db.client_ids(groups='dev', protocol=protocol, purposes='enroll', mask_type='maskIII')) == 370
    assert len(db.client_ids(groups='dev', protocol=protocol, purposes='probe', mask_type='maskIII')) == 345

  # check the number of models
  assert len(db.model_ids(groups='world')) == 12776
  assert len(db.model_ids(groups='dev', protocol='2.0.1', mask_type='maskI')) == 14628
  assert len(db.model_ids(groups='dev', protocol='2.0.2', mask_type='maskI')) == 3657
  assert len(db.model_ids(groups='dev', protocol='2.0.4', mask_type='maskI')) == 14628
  assert len(db.model_ids(groups='dev', protocol='2.0.1', mask_type='maskII')) == 15336
  assert len(db.model_ids(groups='dev', protocol='2.0.2', mask_type='maskII')) == 3834
  assert len(db.model_ids(groups='dev', protocol='2.0.4', mask_type='maskII')) == 15336
  assert len(db.model_ids(groups='dev', protocol='2.0.1', mask_type='maskIII')) == 7572
  assert len(db.model_ids(groups='dev', protocol='2.0.2', mask_type='maskIII')) == 1893
  assert len(db.model_ids(groups='dev', protocol='2.0.4', mask_type='maskIII')) == 7572


@db_available
def test_objects():
  # Tests that the 'objects()' function returns reasonable output.
  # query all File objects
  assert len(db.objects(mask_type = None)) == 36818
  assert len(db.objects(mask_type = 'maskI')) == 36110
  assert len(db.objects(mask_type = 'maskII')) == 36500
  assert len(db.objects(mask_type = 'maskIII')) == 33032


  # The number of objects should always be identical to the number of models...
  protocols = db.m_protocols
  masks = db.m_mask_types

  assert len(db.objects(groups='world')) == len(db.model_ids(groups='world'))

  for mask in masks:
    # the number of models and model files should be identical for protocol 1 and 4
    for protocol in ('2.0.1', '2.0.4'):
      assert len(db.objects(groups='dev', protocol=protocol, purposes='enroll', mask_type=mask)) == len(db.model_ids(groups='dev', protocol=protocol, mask_type=mask))

    # for protocol 2, there are 4 files for each model
    assert len(db.objects(groups='dev', protocol='2.0.2', purposes='enroll', mask_type=mask)) == len(db.model_ids(groups='dev', protocol='2.0.2', mask_type=mask)) * 4

  # the number of probes actually differ between the masks, and between the protocols
  assert len(db.objects(groups='dev', protocol='2.0.1', purposes='probe', mask_type='maskI')) == 14612
  assert len(db.objects(groups='dev', protocol='2.0.1', purposes='probe', mask_type='maskII')) == 15392
  assert len(db.objects(groups='dev', protocol='2.0.1', purposes='probe', mask_type='maskIII')) == 8456
  assert len(db.objects(groups='dev', protocol='2.0.2', purposes='probe', mask_type='maskI')) == 14612
  assert len(db.objects(groups='dev', protocol='2.0.2', purposes='probe', mask_type='maskII')) == 15392
  assert len(db.objects(groups='dev', protocol='2.0.2', purposes='probe', mask_type='maskIII')) == 8456
  assert len(db.objects(groups='dev', protocol='2.0.4', purposes='probe', mask_type='maskI')) == 7306
  assert len(db.objects(groups='dev', protocol='2.0.4', purposes='probe', mask_type='maskII')) == 7696
  assert len(db.objects(groups='dev', protocol='2.0.4', purposes='probe', mask_type='maskIII')) == 4228

  # as far as I know, the number of probes should be identical for each model...
  for model_id in random.sample(db.model_ids(groups='dev', protocol='2.0.4', mask_type='maskIII'), 50):
    assert len(db.objects(groups='dev', protocol='2.0.4', purposes='probe', mask_type='maskIII', model_ids=model_id)) == 4228


@db_available
def test_object_sets():
  # Test if the object_set function returns reasonable results
  # The number of objects should always be identical to the number of models...
  masks = db.m_mask_types

  for mask in masks:
    # the number of models and model files should be identical for protocol 1 and 4
    # for protocol 2, there are the same number of models as object_sets
    assert len(db.object_sets(groups='dev', protocol='2.0.2', purposes='enroll', mask_type=mask)) == len(db.model_ids(groups='dev', protocol='2.0.2', mask_type=mask))

  # the number of probes actually differ between the masks, and between the protocols
  assert len(db.objects(groups='dev', protocol='2.0.2', purposes='probe', mask_type='maskI')) == 14612
  assert len(db.objects(groups='dev', protocol='2.0.2', purposes='probe', mask_type='maskII')) == 15392
  assert len(db.objects(groups='dev', protocol='2.0.2', purposes='probe', mask_type='maskIII')) == 8456
  assert len(db.object_sets(groups='dev', protocol='2.0.2', purposes='probe', mask_type='maskI')) == 3653
  assert len(db.object_sets(groups='dev', protocol='2.0.2', purposes='probe', mask_type='maskII')) == 3848
  assert len(db.object_sets(groups='dev', protocol='2.0.2', purposes='probe', mask_type='maskIII')) == 2114

  # as far as I know, the number of probes should be identical for each model...
  for model_id in random.sample(db.model_ids(groups='dev', protocol='2.0.2', mask_type='maskIII'), 20):
    assert len(db.object_sets(groups='dev', protocol='2.0.2', purposes='probe', mask_type='maskIII', model_ids=model_id)) == 2114


@db_available
def test_file_ids():
  # Tests that the client id's returned by the 'get_client_id_from_file_id()' and 'get_client_id_from_model_id()' functions are correct.
  # this test might take a while...
  protocol = db.m_protocols[0]
  # extract all models
  for model_id in random.sample(db.model_ids(groups='dev', protocol=protocol), 100):
    # get the client id of the model
    client_id = db.get_client_id_from_model_id(model_id)
    # check that all files with the same model id share the same client id
    for file in db.objects(groups='dev', protocol=protocol, model_ids=(model_id,), purposes='enroll'):
      assert db.get_client_id_from_file_id(file.id) == client_id


@db_available
def test_annotations():
  # Tests that the annotations are available for all files
  # we test only one of the protocols
  for protocol in random.sample(db.m_protocols, 1):
    files = db.objects(protocol=protocol)
    for file in random.sample(files, 1000):
      annotations = db.annotations(file)
      for t in 'leye', 'reye', 'mouth', 'nose':
        assert t in annotations
        assert len(annotations[t]) == 2


@db_available
def test_driver_api():
  # Tests the frgc driver API.
  from bob.db.base.script.dbmanage import main
  assert  main('frgc dumplist --self-test'.split()) == 0
  assert  main('frgc dumplist --group=dev --protocol=2.0.4 --purpose=enroll --self-test'.split()) == 0
  assert  main('frgc checkfiles --self-test'.split()) == 0

