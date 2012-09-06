=============================================================
 The Face Recognition Grand Challenge (FRGC) ver2.0 Database
=============================================================

TODO: FILL!!!

This package contains the access API and descriptions for `The Good, The Bad, and The Ugly Database <http://www.nist.gov/itl/iad/ig/focs.cfm>`_.
The actual raw data for the database should be downloaded from the original URL.
This package only contains the `Bob <http://www.idiap.ch/software/bob/>`_ accessor methods to use the DB directly from python.
Note that the default protocols *Good*, *Bad*, and *Ugly* as defined in the URL above will be respected.

You would normally not install this package unless you are maintaining it.
What you would do instead is to tie it in at the package you need to **use** it.
There are a few ways to achieve this:

1. You can add this package as a requirement at the ``setup.py`` for your own `satellite package <https://github.com/idiap/bob/wiki/Virtual-Work-Environments-with-Buildout>`_ or to your Buildout ``.cfg`` file, if you prefer it that way.
   With this method, this package gets automatically downloaded and installed on your working environment, or
2. You can manually download and install this package using commands like ``easy_install`` or ``pip``.

The package is available in two different distribution formats:

a) You can download it from `PyPI <http://pypi.python.org/pypi>`_, or
b) You can download it in its source form from `its git repository <https://github.com/bioidiap/xbob.db.gbu>`_.
   When you download the version at the git repository, you will need to run a command to recreate the backend SQLite file required for its operation.
   This means that the database raw files must be installed somewhere in this case.
   With option ``1`` you can run in `dummy` mode and only download the raw data files for the database once you are happy with your setup.

You can mix and match points 1/2 and a/b above based on your requirements.
Here are some examples:

Modify your setup.py and download from PyPI
===========================================

That is the easiest.
Edit your ``setup.py`` in your satellite package and add the following entry in the ``install_requires`` section::

    install_requires=[
      ...
      "xbob.db.gbu",
    ],

Proceed normally with your ``boostrap/buildout`` steps and you should be all set.
That means you can now import the ``xbob.db.gbu`` namespace into your scripts.

Modify your buildout.cfg and download from git
==============================================

You will need to add a dependence to `mr.developer <http://pypi.python.org/pypi/mr.developer/>`_ to be able to install from our git repositories.
Your ``buildout.cfg`` file should contain the following lines::

  [buildout]
  ...
  extensions = mr.developer
  auto-checkout = *
  eggs = bob
         ...
         xbob.db.gbu

  [sources]
  xbob.db.gbu = git https://github.com/bioidiap/xbob.db.gbu.git
  ...
