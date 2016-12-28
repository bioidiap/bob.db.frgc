#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Commands the FRGC database can respond to.
"""

from __future__ import print_function

import os
import sys
import tempfile, shutil
import argparse

import bob.db.base

def dumplist(args):
  """Dumps lists of files based on your criteria"""

  output = sys.stdout
  if args.selftest:
    output = bob.db.base.utils.null()

  if args.selftest and not os.path.exists(args.database):
    output.write("The base directory of the database does not exist. We omit this self test.")
    return 0

  from .query import Database
  db = Database(args.database)

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
    output = bob.db.base.utils.null()

  if args.selftest and not os.path.exists(args.database):
    output.write("The base directory of the database does not exist. We omit this self test.")
    return 0

  from .query import Database
  db = Database(args.database)

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



class Interface(bob.db.base.driver.Interface):

  def name(self):
    return 'frgc'

  def version(self):
    import pkg_resources  # part of setuptools
    return pkg_resources.require('bob.db.%s' % self.name())[0].version

  def files(self):
    """Returns the list of files required for this interface to work, which is empty."""
    from pkg_resources import resource_filename
    raw_files = ()
    return [resource_filename(__name__, k) for k in raw_files]

  def frgc_database_directory(self):
    """Returnes the FRGC database base directory, where the original FRGC file lists (XML) are stored.
    You might want to adapt this directory to your needs."""
    return '/idiap/resource/database/frgc/FRGC-2.0-dist'

  def type(self):
    """Defines the type of the database, which is not SQL3, but text based"""
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
    dump_list_parser.add_argument('-u', '--purpose', help="if given, this value will limit the output files to those designed for the given purposes.", choices=('enroll', 'probe'))
    dump_list_parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    dump_list_parser.set_defaults(func=dumplist) #action

    # the "checkfiles" action
    check_files_parser = subparsers.add_parser('checkfiles', help=checkfiles.__doc__)
    check_files_parser.add_argument('-D', '--database', default=self.frgc_database_directory(), help="The base directory of the FRGC database.")
    check_files_parser.add_argument('-d', '--directory', help="if given, this path will be prepended to every entry returned.")
    check_files_parser.add_argument('-e', '--extension', default='.jpg', help="if given, this extension will be appended to every entry returned.")
    check_files_parser.add_argument('--self-test', dest="selftest", action='store_true', help=argparse.SUPPRESS)
    check_files_parser.set_defaults(func=checkfiles) #action
