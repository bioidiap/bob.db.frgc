#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""XML file reader and stored lists for FRGC database
"""

import xml.sax
import os
import numpy

import bob.db.base

class File (bob.db.base.File):
  """This class is just the File object that is returned by the objects function.
  It will be created on need and is not stored anywhere."""
  def __init__(self, signature, presentation, path):
    # just call the base class constructor
    bob.db.base.File.__init__(self, file_id = presentation, path = path)
    self.client_id = signature

  # overwrite default make_path behaviour
  def make_path(self, directory=None, extension=None):
    """Wraps the current path so that a complete path is formed.
    If directory and extension '.jpg' are specified,
    extensions are automatically replaced by '.JPG' if necessary.

    Keyword parameters:

    directory
      An optional directory name that will be prefixed to the returned result.

    extension
      An optional extension that will be suffixed to the returned filename. The
      extension normally includes the leading ``.`` character as in ``.jpg`` or
      ``.hdf5``.

    Returns a string containing the newly generated file path.
    """
    if not directory: directory = ''
    if not extension: extension = ''

    # if extension is '.jpg', we have to check if we need to change it to '.JPG'
    full_path = os.path.join(directory, self.path + extension)
    if extension == '.jpg' and not os.path.isfile(full_path):
      capital_path = os.path.join(directory, self.path + '.JPG')
      if os.path.exists(capital_path):
        return capital_path
    return full_path


class FileSet:
  """This class is just the FileSet object that is returned by the object_sets function.
  It will be created on need and is not stored anywhere."""
  def __init__(self, frgc_file):
    # The id is simply taken from the FRGCFile model id; WARNING: this ID is not stable and should not be stored anywhere.
    self.id = frgc_file.m_model
    self.client_id = frgc_file.m_signature
    self.files = [File(frgc_file.m_signature, presentation, frgc_file.m_files[presentation]) for presentation in frgc_file.m_files]
    # the path is simply a concatenation of the file names of all the files in the set; it is not really used anywhere
    self.path = self.files[0].path[:3] + self.files[0].path[3:].split('d')[0] + "d" + "+".join([self.files[i].path[3:].split('d')[1] for i in range(len(self.files))])

  def __lt__(self, other):
    """Defines an order in the file sets."""
    return self.path < other.path


################################################################################
############# Internal IO and represenations of the FRGC files #################

# Global model index. This model index is generated on the fly and should not be stored between sessions.
global model_index
model_index = 1

class FRGCFile:
  """This class holds all desired information about a specific file, or set of files"""
  def __init__(self, signature):
    # the client id
    self.m_signature = signature
    # a unique model id, which is generated on the fly
    global model_index
    self.m_model = model_index
    model_index += 1
    # the files: map from record id to path (w/o file extension)
    self.m_files = {}

  def add(self, presentation, path):
    # add the path to the list of files for this file (list)
    assert presentation not in self.m_files
    self.m_files[presentation] = os.path.splitext(path)[0]


class ListFileReader (xml.sax.handler.ContentHandler):
  """Class for reading the FRGC xml image file lists"""
  def __init__(self):
    self.m_file = None
    self.m_file_list = []

  def startDocument(self):
    pass

  def endDocument(self):
    pass

  def startElement(self, name, attrs):
    if name == 'biometric-signature' or name == 'complex-biometric-signature':
      self.m_file = FRGCFile(attrs['name'])
    elif name == 'presentation':
      assert self.m_file
      self.m_file.add(attrs['name'], attrs['file-name'])
    else: # other name
      pass

  def endElement(self, name):
    if name == 'biometric-signature' or name == 'complex-biometric-signature':
      # add a file(s) to the list
      self.m_file_list.append(self.m_file)
      # new identity
      self.m_file = None
    else: # other name
      pass


class AnnotationFileReader (xml.sax.handler.ContentHandler):
  """Class for reading the FRGC metadata list"""
  def __init__(self):
    self.m_annotations = {}
    self.m_signature = None
    self.m_annotation_map = {}

  def startDocument(self):
    pass

  def endDocument(self):
    pass

  def startElement(self, name, attrs):
    if name == 'Recording':
      assert self.m_signature is None
      self.m_signature = attrs['recording_id']
      self.m_annotations = {}
      self.m_use_recording = False
    elif name == 'LeftEyeCenter':
      self.m_annotations['leye'] = (int(attrs['y']), int(attrs['x']))
      self.m_use_recording = True
    elif name == 'RightEyeCenter':
      self.m_annotations['reye'] = (int(attrs['y']), int(attrs['x']))
    elif name == 'Nose':
      self.m_annotations['nose'] = (int(attrs['y']), int(attrs['x']))
    elif name == 'Mouth':
      self.m_annotations['mouth'] = (int(attrs['y']), int(attrs['x']))
    else: # other name
      pass

  def endElement(self, name):
    if name == 'Recording':
      assert self.m_signature
      assert self.m_signature not in self.m_annotation_map
      # add a file(s) to the list
      if self.m_use_recording:
        assert len(self.m_annotations) == 4
        self.m_annotation_map[self.m_signature] = self.m_annotations
      # new identity
      self.m_signature = None
    else: # other name
      pass


def read_mask(mask_file):
  """Reads the mask from file"""
  # open the file
  f = open(mask_file, 'rb')
  # read until the phrase "MB" is read
  b = None
  while b not in ('B', '', b'B', b''):
    m = None
    while m not in ('M', '', b'M', b''):
      m = f.read(1)
    b = f.read(1)
  if m not in ('M', b'M') or b not in ('B', b'B'):
    raise ValueError("The given mask file '" + mask_file + "' is invalid.")

  # read the mask size
  queries, targets = f.readline().split(b' ')[1:3]

  # read mask
  mask = numpy.fromfile(f, dtype = numpy.uint8)
  mask.shape = (int(queries), int(targets))

  return mask


# directories inside the FRGC database
list_dir = "BEE_DIST/%(v)sFRGC2.0/signature_sets/experiments"
mask_dir = "BEE_DIST/%(v)sFRGC2.0/Experiment%(e)s/output"
meta_data_dir = "BEE_DIST/%(v)sFRGC2.0/metadata"

dir_variants = ('linux/FRGC/', '')


######################################################
##### lists ##########################################

# the xml files for training, target and query
xml_files = {'world':'FRGC_Exp_2.0.1_Training.xml',
               'dev':{'2.0.1':'FRGC_Exp_2.0.1_Target.xml',
                      '2.0.2':'FRGC_Exp_2.0.2_Target.xml',
                      '2.0.4':{'enroll':'FRGC_Exp_2.0.4_Target.xml',
                               'probe':'FRGC_Exp_2.0.4_Query.xml'}}}

# collector for lists that we already read.
known_lists = {'world':None,
               'dev':{'2.0.1':None, '2.0.2':None, '2.0.4':{'enroll':None, 'probe':None}}}

# collector for files and models that have been read
file_dict = {}
model_dict = {}

def get_list(base_dir, group, protocol=None, purpose=None):
  """Reads and returns the list of file names for the given group, purpose and protocol."""

  def read_if_needed(file, list):
    """Reads the given list (if it has not been read yet) and fills the file and model dictionaries."""
    if not list:
      files = [file % {'v':v} for v in dir_variants]
      found = None
      for f in files:
        if os.path.exists(f):
          found = f
      if found is None:
        raise xml.sax.SAXException("Could not find the any of the list files '%s'. Your FRGC base directory '%s' seems to be wrong or incomplete."%(files, base_dir))
      handler = ListFileReader()
#      print "Reading xml list '" + file + "'"
      xml.sax.parse(found, handler)
      list = handler.m_file_list
      # integrate in dicts
      for g in list:
        for k,v in g.m_files.items():
          file_dict[k] = g.m_signature
        model_dict[g.m_model] = g.m_signature

    return list

  if group == 'world':
    known_lists[group] = read_if_needed(os.path.join(base_dir, list_dir, xml_files[group]), known_lists[group])
    return known_lists[group]

  if group == 'dev':
    if protocol in ('2.0.1', '2.0.2'):
      known_lists[group][protocol] = read_if_needed(os.path.join(base_dir, list_dir, xml_files[group][protocol]), known_lists[group][protocol])
      return known_lists[group][protocol]
    if protocol == '2.0.4':
      known_lists[group][protocol][purpose] = read_if_needed(os.path.join(base_dir, list_dir, xml_files[group][protocol][purpose]), known_lists[group][protocol][purpose])
      return known_lists[group][protocol][purpose]

def client_from_file(file_id):
  """Returns the client id attached to the given file id. The file id must be already known (i.e., it must have been read from any list)."""
  assert file_id in file_dict
  return file_dict[file_id]

def client_from_model(model_id):
  """Returns the client id attached to the given model id. The model id must be already known."""
  assert model_id in model_dict
  return model_dict[model_id]



###############################################################
##### masks ###################################################

# static collector for the mask files
known_masks = {'2.0.1':{'maskI':None, 'maskII':None, 'maskIII':None},
               '2.0.2':{'maskI':None, 'maskII':None, 'maskIII':None},
               '2.0.4':{'maskI':None, 'maskII':None, 'maskIII':None}}

def get_mask(base_dir, protocol, mask_type):
  """Returns the mask ([query_index], [target_index]) for the given protocol and mask type."""
  if mask_type is None:
    return None
  if known_masks[protocol][mask_type] is None:
    mask_files = [os.path.join(base_dir, mask_dir%{'v':v, 'e':protocol[-1:]}, mask_type + ".mtx") for v in dir_variants]
    found = None
    for f in mask_files:
      if os.path.exists(f):
        found = f
    if found is None:
      raise xml.sax.SAXException("Could not find any of the mask files '%s'. Your FRGC base directory '%s' seems to be wrong or incomplete."%(mask_files, base_dir))
    known_masks[protocol][mask_type] = read_mask(found)

  return known_masks[protocol][mask_type]



###############################################################
##### annotations ###############################################

# static collector of the annotations
global annotations
annotations = None

def get_annotations(base_dir, file_id):
  """Returns the eye, mouth and nose positions for the given file id."""
  global annotations
  # check if annotations need to be read
  if not annotations:
    # read annotations file
    metadata_files = [os.path.join(base_dir, meta_data_dir%{'v':v}, "FRGC_2.0_Metadata.xml") for v in dir_variants]
    found = None
    for f in metadata_files:
      if os.path.exists(f):
        found = f
    if found is None:
      raise xml.sax.SAXException("Could not find one of the metadata file '%s'. Your FRGC base directory '%s' seems to be wrong or incomplete."%(metadata_files, base_dir))
#    print "Reading positions file '" + metadata_file + "'"
    annotation_reader = AnnotationFileReader()
    xml.sax.parse(found, annotation_reader)
    annotations = annotation_reader.m_annotation_map

  return annotations[file_id]
