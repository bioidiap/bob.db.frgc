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

"""
The FRGC (Face Recognition Grand Challenge) ver2.0 Database is provided by the NIST webpage: http://face.nist.gov/frgc/
Please contact the responsible person to get your own copy of the database (be aware that it is **huge**).
Due to the size of the database, experiments using this package might require a lot of memory.
Already running the tests will need up to 2 GB of free memory.

In opposition to other databases, there is no .sql3-file for this database, but instead the XML lists provided in the database are used directly.
In order for the database interface to work properly, you have to specify the correct path on each usage.
To avoid that, you can set the path in the ``Interface.frgc_database_directory()`` function of the ``bob/db/frgc/driver.py`` file to your FRGC image database main directory.
(Of course, you have to download the source package from git to do that, see below.)
For use at Idiap, the right directory is preset.

In opposition to the original FRGC protocols, here only those image files and models that are required by the mask are used.
This saves some time and space, but ensures identical results.

.. warning ::
  Do not store the model ids between sessions.
  These model id's are generated 'on the fly' and might change between database sessions.

.. note ::
  During one database session, model ids are unique and stable.

Enjoy!
"""

from .query import Database

def get_config():
  """Returns a string containing the configuration information.
  """

  import pkg_resources

  packages = pkg_resources.require(__name__)
  this = packages[0]
  deps = packages[1:]

  retval =  "%s: %s (%s)\n" % (this.key, this.version, this.location)
  retval += "  - python dependencies:\n"
  for d in deps: retval += "    - %s: %s (%s)\n" % (d.key, d.version, d.location)

  return retval.strip()

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
