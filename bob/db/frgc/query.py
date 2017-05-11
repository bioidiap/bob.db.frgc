#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""This module provides the Database interface allowing the user to query the
FRGC database in the most obvious ways.
"""

from .models import get_list, get_mask, get_annotations, client_from_file, client_from_model, File, FileSet

from .driver import Interface
interface = Interface()

import bob.db.base

import logging
logger = logging.getLogger("bob.db.frgc")

import os
import six


class Database(bob.db.base.Database):
  """The Database class reads the original XML lists and provides access
  using the common bob.db API.
  """

  def __init__(self, original_directory=interface.frgc_database_directory(), original_extension='.jpg'):
    # NOTE: For some images, the image extension is '.JPG' instead.
    # this interface will keep track of this automatically and always return
    # the correct image name

    if not os.path.exists(original_directory):
      logger.warn("The database directory '%s' does not exist. Please choose the correct path, or correct the path in the Interface.frgc_database_directory() function of the bob/db/frgc/driver.py file.", original_directory)

    # call base class constructor
    super(Database, self).__init__(original_directory, original_extension)

    self.m_groups = ('world', 'dev')
    self.m_purposes = ('enroll', 'probe')
    # other protocols might be supported later.
    self.m_protocols = ('2.0.1', '2.0.2', '2.0.4')
    # usually, only maskIII (the most difficult one) is used.
    self.m_mask_types = ('maskI', 'maskII', 'maskIII')

  def groups(self, protocol=None):
    """Returns a list of groups for the given protocol

    Keyword Parameters:

    protocol
      One or several of the FRGC protocols ('2.0.1', '2.0.2, '2.0.4'),

    Returns: a list of groups
    """
    return self.m_groups

  def provides_file_set_for_protocol(self, protocol):
    """Returns True for every protocol for which file sets (instead of single files) are used for enrollment and probing.
    Currently, this is only the '2.0.2', protocol."""
    protocol = self.check_parameter_for_validity(
        protocol, 'protocol', self.m_protocols)
    return protocol == '2.0.2'

  def client_ids(self, groups=None, protocol=None, purposes=None, mask_type='maskIII'):
    """Returns a list of client ids for the specific query by the user.

    Keyword Parameters:

    groups
      One or several groups to which the models belong ('world', 'dev').

    protocol
      One or several of the FRGC protocols ('2.0.1', '2.0.2, '2.0.4'),
      required only if one of the groups is 'dev'.

    purposes
      One or several groups for which files should be retrieved ('enroll', 'probe').
      Only used when the group is 'dev'·
      For some protocol/mask_type pairs, not all clients are used for enrollment / for probe.

    mask_type
      One of the mask types ('maskI', 'maskII', 'maskIII').

    Returns: A list containing all the client id's which have the given properties.
    """
    groups = self.check_parameters_for_validity(groups, "group", self.m_groups)

    retval = set()

    if 'world' in groups:
      for file in get_list(self.original_directory, 'world'):
        retval.add(file.m_signature)

    if 'dev' in groups:
      # validity checks
      purposes = self.check_parameters_for_validity(
          purposes, "purpose", self.m_purposes)
      protocol = self.check_parameter_for_validity(
          protocol, "protocol", self.m_protocols)
      if mask_type is not None:
        mask_type = self.check_parameter_for_validity(
            mask_type, "mask type", self.m_mask_types)

      # take only those models/probes that are really required by the current
      # mask
      mask = get_mask(self.original_directory, protocol, mask_type)

      if 'enroll' in purposes:
        files = get_list(self.original_directory, 'dev',
                         protocol, purpose='enroll')
        for index in range(len(files)):
          # check if this model is used by the mask
          if mask is None or (mask[:, index] > 0).any():
            retval.add(files[index].m_signature)

      if 'probe' in purposes:
        files = get_list(self.original_directory, 'dev',
                         protocol, purpose='probe')
        for index in range(len(files)):
          # check if this probe is used by the mask
          if mask is None or (mask[index, :] > 0).any():
            retval.add(files[index].m_signature)

    return sorted(list(retval))

  def model_ids(self, groups=None, protocol=None, mask_type='maskIII'):
    """Returns a set of model ids for the specific query by the user.

    The models are dependent on the protocol and the mask.
    Only those FRGC "target" files are returned that are required by the given mask!

    .. warning ::
      Clients, models, and files are not identical for the FRGC database!
      Model ids are neither client nor file id's, so please do not mix that up!

    Keyword Parameters:

    groups
      One or several groups to which the models belong ('world', 'dev').

    protocol
      One or several of the FRGC protocols ('2.0.1', '2.0.2, '2.0.4'),
      required only if one of the groups is 'dev'.

    mask_type
      One of the mask types ('maskI', 'maskII', 'maskIII').

    Returns: A list containing all the model id's belonging to the given group.
    """
    groups = self.check_parameters_for_validity(groups, "group", self.m_groups)
    # for models, purpose is always 'enroll'
    purpose = 'enroll'

    retval = set()
    if 'world' in groups:
      for file in get_list(self.original_directory, 'world'):
        retval.add(file.m_model)

    if 'dev' in groups:
      protocol = self.check_parameter_for_validity(
          protocol, "protocol", self.m_protocols)
      if mask_type is not None:
        mask_type = self.check_parameter_for_validity(
            mask_type, "mask type", self.m_mask_types)
      files = get_list(self.original_directory, 'dev', protocol, purpose)
      # take only those models that are really required by the current mask
      mask = get_mask(self.original_directory, protocol, mask_type)
      for index in range(len(files)):
        if mask is None or (mask[:, index] > 0).any():
          retval.add(files[index].m_model)

    return sorted(list(retval))

  def get_client_id_from_model_id(self, model_id, **kwargs):
    """Returns the client_id attached to the given model_id.

    Keyword Parameters:

    model_id
      The model_id to consider

      .. warning ::
        The given model_id must have been the result of a previous call to model_ids()
        of the **same** database object, otherwise it will not be known or might be corrupted.

    Returns: The client_id attached to the given model_id
    """
    return client_from_model(model_id)

  def get_client_id_from_file_id(self, file_id, **kwargs):
    """Returns the client_id (real client id) attached to the given file_id

    Keyword Parameters:

    file_id
      The file_id to consider

    Returns: The client_id attached to the given file_id
    """
    return client_from_file(file_id)

  def objects(self, groups=None, protocol=None, purposes=None, model_ids=None, mask_type='maskIII'):
    """Using the specified restrictions, this function returns a list of File objects.

    Keyword Parameters:

    groups
      One or several groups to which the models belong ('world', 'dev').
      'world' files are "Training", whereas 'dev' files are "Target" and/or "Query".

    protocol
      One or more of the FRGC protocols ('2.0.1', '2.0.2', '2.0.4').
      Only used, if 'dev' is amongst the groups.
      If not specified, all FRGC protocols will be taken into account.

    purposes
      One or several groups for which files should be retrieved ('enroll', 'probe').
      Only used when the group is 'dev'·
      In FRGC terms, 'enroll' is "Target", while 'probe' is "Target" (protocols '2.0.1' and '2.0.2') or "Query" (protocol '2.0.4')

    model_ids
      If given (as a list of model id's or a single one), only the files
      belonging to the specified model id is returned.

      .. warning ::
        When querying objects of group 'world', model ids are expected to be client ids (as returned by 'client_ids()'),
        whereas for group 'dev' model ids are real model ids (as returned by 'model_ids()')

    mask_type
      One of the mask types ('maskI', 'maskII', 'maskIII').
    """
    def extend_files(files, frgc_file):
      """Extends the given file list with File's created from the given FRGCFile."""
      for presentation in frgc_file.m_files:
        files[presentation] = File(
            frgc_file.m_signature, presentation, frgc_file.m_files[presentation])

    # check that every parameter is as expected
    groups = self.check_parameters_for_validity(groups, "group", self.m_groups)
    # we allow to specify more protocols here, just
    protocols = self.check_parameters_for_validity(
        protocol, "protocol", self.m_protocols)

    if isinstance(model_ids, six.integer_types):
      model_ids = (model_ids,)

    files = {}

    if 'world' in groups:
      # extract training files
      for file in get_list(self.original_directory, 'world'):
        if not model_ids or file.m_signature in model_ids:
          for id, path in list(file.m_files.items()):
            extend_files(files, file)

    if 'dev' in groups:
      # check protocol, mask, and purposes only in group dev
      if mask_type is not None:
        mask_type = self.check_parameter_for_validity(
            mask_type, "mask type", self.m_mask_types)
      purposes = self.check_parameters_for_validity(
          purposes, "purpose", self.m_purposes)

      for p in protocols:
        # extract dev files
        if 'enroll' in purposes:
          model_files = get_list(self.original_directory, 'dev', p, 'enroll')
          # return only those files that are required by the given protocol
          mask = get_mask(self.original_directory, p, mask_type)
          for model_index in range(len(model_files)):
            model = model_files[model_index]
            if not model_ids or model.m_model in model_ids:
              # test if the model is used by this mask
              if mask is None or (mask[:, model_index] > 0).any():
                extend_files(files, model)

        if 'probe' in purposes:
          probe_files = get_list(self.original_directory, 'dev', p, 'probe')
          # assure that every probe file is returned only once
          probe_indices = list(range(len(probe_files)))

          # select only that files that belong to the models of with the given ids,
          # or to any model if no model id is specified
          model_files = get_list(self.original_directory, 'dev', p, 'enroll')
          mask = get_mask(self.original_directory, p, mask_type)

          for model_index in range(len(model_files)):
            model = model_files[model_index]
            if not model_ids or model.m_model in model_ids:
              probe_indices_for_this_model = probe_indices[:]
              for probe_index in probe_indices_for_this_model:
                if mask is None or mask[probe_index, model_index]:
                  extend_files(files, probe_files[probe_index])
                  probe_indices.remove(probe_index)

    return [files[presentation] for presentation in sorted(files.keys())]

  def object_sets(self, groups=None, protocol='2.0.2', purposes=None, model_ids=None, mask_type='maskIII'):
    """Using the specified restrictions, this function returns a list of FileSet objects.

    Keyword Parameters:

    groups
      Here, only the 'dev' group is valid.

    protocol
      Here, only the FRGC protocol '2.0.2' is valid.
      Only used, if 'dev' is amongst the groups.

    purposes
      One or several groups for which files should be retrieved ('enroll', 'probe').
      In FRGC terms, 'enroll' is "Target", while 'probe' is "Target" (protocols '2.0.1' and '2.0.2') or "Query" (protocol '2.0.4')

    model_ids
      If given (as a list of model id's or a single one), only the files
      belonging to the specified model id is returned.

    mask_type
      One of the mask types ('maskI', 'maskII', 'maskIII').
    """
    def extend_files(files, frgc_file):
      """Extends the given file list with the FileSet created from the given FRGCFile."""
      files[frgc_file.m_model] = FileSet(frgc_file)

    # check that every parameter is as expected
    groups = self.check_parameters_for_validity(groups, "group", ('dev',))
    # we allow to specify more protocols here, just
    protocols = self.check_parameters_for_validity(
        protocol, "protocol", ('2.0.2',))

    if isinstance(model_ids, six.integer_types):
      model_ids = (model_ids,)

    files = {}

    if 'dev' in groups:
      # check protocol, mask, and purposes only in group dev
      if mask_type is not None:
        mask_type = self.check_parameter_for_validity(
            mask_type, "mask type", self.m_mask_types)
      purposes = self.check_parameters_for_validity(
          purposes, "purpose", self.m_purposes)

      for p in protocols:
        # extract dev files
        if 'enroll' in purposes:
          model_files = get_list(self.original_directory, 'dev', p, 'enroll')
          # return only those files that are required by the given protocol
          mask = get_mask(self.original_directory, p, mask_type)
          for model_index in range(len(model_files)):
            model = model_files[model_index]
            if not model_ids or model.m_model in model_ids:
              # test if the model is used by this mask
              if mask is None or (mask[:, model_index] > 0).any():
                extend_files(files, model)

        if 'probe' in purposes:
          probe_files = get_list(self.original_directory, 'dev', p, 'probe')
          # assure that every probe file is returned only once
          probe_indices = list(range(len(probe_files)))

          # select only that files that belong to the models of with the given ids,
          # or to any model if no model id is specified
          model_files = get_list(self.original_directory, 'dev', p, 'enroll')
          mask = get_mask(self.original_directory, p, mask_type)

          for model_index in range(len(model_files)):
            model = model_files[model_index]
            if not model_ids or model.m_model in model_ids:
              probe_indices_for_this_model = probe_indices[:]
              for probe_index in probe_indices_for_this_model:
                if mask is None or mask[probe_index, model_index]:
                  extend_files(files, probe_files[probe_index])
                  probe_indices.remove(probe_index)

    return [files[file_set_id] for file_set_id in sorted(files.keys())]

  def annotations(self, file):
    """Returns the annotations for the given file as a dictionary {'reye':(y,x), 'leye':(y,x), 'mouth':(y,x), 'nose':(y,x)}."""
    return get_annotations(self.original_directory, file.id)
