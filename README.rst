.. vim: set fileencoding=utf-8 :
.. Thu 18 Aug 14:10:40 CEST 2016

.. image:: http://img.shields.io/badge/docs-stable-yellow.png
   :target: http://pythonhosted.org/bob.db.frgc/index.html
.. image:: http://img.shields.io/badge/docs-latest-orange.png
   :target: https://www.idiap.ch/software/bob/docs/latest/bob/bob.db.frgc/master/index.html
.. image:: https://gitlab.idiap.ch/bob/bob.db.frgc/badges/v2.1.0/build.svg
   :target: https://gitlab.idiap.ch/bob/bob.db.frgc/commits/v2.1.0
.. image:: https://img.shields.io/badge/gitlab-project-0000c0.svg
   :target: https://gitlab.idiap.ch/bob/bob.db.frgc
.. image:: http://img.shields.io/pypi/v/bob.db.frgc.png
   :target: https://pypi.python.org/pypi/bob.db.frgc
.. image:: http://img.shields.io/pypi/dm/bob.db.frgc.png
   :target: https://pypi.python.org/pypi/bob.db.frgc
.. image:: https://img.shields.io/badge/original-data--files-a000a0.png
   :target: http://face.nist.gov/frgc/


==========================================================================
 Face Recognition Grand Challenge (FRGC) ver2.0 Database Interface for Bob
==========================================================================

This package is part of the signal-processing and machine learning toolbox
Bob_ and it contains an interface for the evaluation protocol of `The Face Recognition Grand Challenge (FRGC) Database <http://face.nist.gov/frgc/>`_ in the version ver2.0.
It worth noting that this package does not contain the original FRGC data files, which need to be obtained through the link above.


Installation
------------

Follow our `installation`_ instructions. Then, using the Python interpreter
provided by the distribution, bootstrap and buildout this package::

  $ python bootstrap-buildout.py
  $ ./bin/buildout


Contact
-------

For questions or reporting issues to this software package, contact our
development `mailing list`_.


.. Place your references here:
.. _bob: https://www.idiap.ch/software/bob
.. _installation: https://gitlab.idiap.ch/bob/bob/wikis/Installation
.. _mailing list: https://groups.google.com/forum/?fromgroups#!forum/bob-devel
