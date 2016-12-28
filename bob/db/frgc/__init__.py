#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Bob database interface for the Face Recognition Grand Challange (FRGC) v2.0
"""

from .query import Database
from .models import File, FileSet
from .driver import Interface


def get_config():
  """Returns a string containing the configuration information.
  """
  import bob.extension
  return bob.extension.get_config(__name__)


# gets sphinx autodoc done right - don't remove it
def __appropriate__(*args):
  """Says object was actually declared here, an not on the import module.

  Parameters:

    *args: An iterable of objects to modify

  Resolves `Sphinx referencing issues
  <https://github.com/sphinx-doc/sphinx/issues/3048>`
  """

  for obj in args: obj.__module__ = __name__


__appropriate__(
    Database,
    File,
    FileSet,
    Interface,
    )


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
