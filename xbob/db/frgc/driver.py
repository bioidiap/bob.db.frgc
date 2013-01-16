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

"""Commands the FRGC database can respond to.
"""

import os
import sys
import tempfile, shutil
import argparse

import bob.db

def dumplist(args):
  """Dumps lists of files based on your criteria"""

  output = sys.stdout
  if args.selftest:
    output = bob.db.utils.null()

  if args.selftest and not os.path.exists(args.database):
    output.write("The base directory of the database does not exist. We omit this self test.")
    return 0

  from .query import Database
  db = Database()

  r = db.objects(
      groups=args.group,
      protocol=args.protocol,
      purposes=args.purpose,
      mask_type = 'maskII') # here we take mask II since this is the combination of mask I and mask III

  for f in r:
    output.write('%s\n' % f.make_path(args.directory, args.extension))

  return 0

def checkfiles(args):
  """Checks existence of files based on your criteria"""

  output = sys.stdout
  if args.selftest:
    output = bob.db.utils.null()

  if args.selftest and not os.path.exists(args.database):
    output.write("The base directory of the database does not exist. We omit this self test.")
    return 0

  from .query import Database
  db = Database()

  r = db.objects(mask_type = 'maskII') # here we take mask II since this is the combination of mask I and mask III

  # go through all files, check if they are available on the filesystem
  good = {}
  bad = {}
  for f in r:
    if os.path.exists(f.make_path(args.directory, args.extension)): good[f.id] = f
    else: bad[f.id] = f

  # report
  if bad:
    for id, f in bad.items():
      output.write('Cannot find file "%s"\n' % f.make_path(args.directory, args.extension))
    output.write('%d files (out of %d) were not found at "%s"\n' % \
        (len(bad), len(r), args.directory))

  return 0

def create_annotation_files(args):
  """Creates the position files for the FRGC database
  (using the positions stored in the xml files),
  so that FRGC position files share the same structure as the image files."""

  print >> sys.stderr, "Warning: this function is deprecated. Please use the Database.annotations() function to get the annotations."

  # report
  output = sys.stdout
  if args.selftest:
    output = bob.db.utils.null()
    if not os.path.exists(args.database):
      output.write("The base directory of the database does not exist. We omit this self test.")
      return 0

    args.directory = tempfile.mkdtemp(prefix='bob_db_frgc_')

  from .query import Database
  db = Database()

  # retrieve all files
  files = db.objects(protocol='2.0.4')
  for file in files:
    filename = file.make_path(args.directory, args.extension)
    if not os.path.exists(os.path.dirname(filename)):
      os.makedirs(os.path.dirname(filename))
    annotations = db.annotations(file.id)
    f = open(filename, 'w')
    # write eyes in the common order: left eye, right eye

    for type in ('reye', 'leye', 'nose', 'mouth'):
      f.writelines(type + ' ' + str(annotations[type][1]) + ' ' + str(annotations[type][0]) + '\n')
    f.close()


  if args.selftest:
    # check that all files really exist
    args.selftest = False
    args.groups = None
    args.purposes = None
    for args.protocol in ('2.0.1','2.0.2','2.0.4'):
      checkfiles(args)
    shutil.rmtree(args.directory)

  return 0


class Interface(bob.db.driver.Interface):

  def name(self):
    return 'frgc'

  def version(self):
    import pkg_resources  # part of setuptools
    return pkg_resources.require('xbob.db.%s' % self.name())[0].version

  def files(self):
    from pkg_resources import resource_filename
    raw_files = ()
    return [resource_filename(__name__, k) for k in raw_files]

  def frgc_database_directory(self):
    return '/idiap/resource/database/frgc/FRGC-2.0-dist'

  def type(self):
    return 'text'

  def add_commands(self, parser):
    from . import __doc__ as docs

    subparsers = self.setup_parser(parser,
       "The FRGC database", docs)

    # the "dumplist" action
    dump_list_parser = subparsers.add_parser('dumplist', help=dumplist.__doc__)
    dump_list_parser.add_argument('-D', '--database', default=self.frgc_database_directory(), help="The base directory of the FRGC database.")
    dump_list_parser.add_argument('-d', '--directory', help="if given, this path will be prepended to every entry returned.")
    dump_list_parser.add_argument('-e', '--extension', help="if given, this extension will be appended to every entry returned.")
    dump_list_parser.add_argument('-g', '--group', help="if given, this value will limit the output files to those belonging to a particular group.", choices=('world', 'dev'))
    dump_list_parser.add_argument('-p', '--protocol', default = '2.0.1', help="limits the dump to a particular subset of the data that corresponds to the given protocol.", choices=('2.0.1', '2.0.2', '2.0.4'))
    dump_list_parser.add_argument('-u', '--purpose', help="if given, this value will limit the output files to those designed for the given purposes.", choices=('enrol', 'probe'))
    dump_list_parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    dump_list_parser.set_defaults(func=dumplist) #action

    # the "checkfiles" action
    check_files_parser = subparsers.add_parser('checkfiles', help=checkfiles.__doc__)
    check_files_parser.add_argument('-D', '--database', default=self.frgc_database_directory(), help="The base directory of the FRGC database.")
    check_files_parser.add_argument('-d', '--directory', help="if given, this path will be prepended to every entry returned.")
    check_files_parser.add_argument('-e', '--extension', default='.jpg', help="if given, this extension will be appended to every entry returned.")
    check_files_parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    check_files_parser.set_defaults(func=checkfiles) #action

    # the "create-eye-files" action
    create_annotation_files_parser = subparsers.add_parser('create-annotation-files', help=create_annotation_files.__doc__)
    create_annotation_files_parser.add_argument('-D', '--database', default=self.frgc_database_directory(), help="The base directory of the FRGC database.")
    create_annotation_files_parser.add_argument('-d', '--directory', required=True, help="The eye position files will be stored in this directory.")
    create_annotation_files_parser.add_argument('-e', '--extension', default = '.pos', help="if given, this extension will be appended to every entry returned.")
    create_annotation_files_parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    create_annotation_files_parser.set_defaults(func=create_annotation_files) #action

