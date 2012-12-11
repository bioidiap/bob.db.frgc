=============================================================
 The Face Recognition Grand Challenge (FRGC) ver2.0 Database
=============================================================

This package contains the access API and descriptions for `The Face Recognition Grand Challenge (FRGC) Database <http://face.nist.gov/frgc/>`_ in the version ver2.0.
The actual raw data for the database should be downloaded from the original URL.
This package only contains the `Bob <http://www.idiap.ch/software/bob/>`_ accessor methods to use the DB directly from python.
Note that currently only the experimental protocols *2.0.1*, *2.0.2*, and *2.0.4* (as defined in the FRGC tests) are implemented.

.. note::

  Since this database interface directly works with the file lists of the database directly, it requires the original image database to be available at your system.
  In order for the database interface to work properly, you have to specify the correct path on each usage.
  To avoid that, you can set the path in the ``Interface.frgc_database_directory()`` function of the ``xbob/db/frgc/driver.py`` file to your FRGC image database main directory.
  (Of course, you have to download the source package from git to do that, see below.)
  For use at Idiap, the right directory is preset.

You would normally not install this package unless you are maintaining it.
What you would do instead is to tie it in at the package you need to **use** it.
There are a few ways to achieve this:

1. You can add this package as a requirement at the ``setup.py`` for your own `satellite package <https://github.com/idiap/bob/wiki/Virtual-Work-Environments-with-Buildout>`_ or to your Buildout ``.cfg`` file, if you prefer it that way.
   With this method, this package gets automatically downloaded and installed on your working environment, or
2. You can manually download and install this package using commands like ``easy_install`` or ``pip``.

The package is available in two different distribution formats:

a) You can download it from `PyPI <http://pypi.python.org/pypi>`_, or
b) You can download it in its source form from `its git repository <https://github.com/bioidiap/xbob.db.frgc>`_.

You can mix and match points 1/2 and a/b above based on your requirements.
Here are some examples:

Modify your setup.py and download from PyPI
===========================================

That is the easiest.
Edit your ``setup.py`` in your satellite package and add the following entry in the ``install_requires`` section::

    install_requires=[
      ...
      "xbob.db.frgc",
    ],

Proceed normally with your ``boostrap/buildout`` steps and you should be all set.
That means you can now import the ``xbob.db.frgc`` namespace into your scripts.

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
         xbob.db.frgc

  [sources]
  xbob.db.frgc = git https://github.com/bioidiap/xbob.db.frgc.git
  ...
