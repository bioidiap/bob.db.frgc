.. vim: set fileencoding=utf-8 :
.. @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
.. @date:   Thu Dec  6 12:28:25 CET 2012

==============
 User's Guide
==============

The FRGC (Face Recognition Grand Challenge) ver2.0 Database is provided by the NIST webpage: http://face.nist.gov/frgc/
Please contact the responsible person to get your own copy of the database (be aware that it is **huge**).
Due to the size of the database, experiments using this package might require a lot of memory.
Already running the tests will need up to 2 GB of free memory.

In opposition to other databases, there is no .sql3-file for this database, but instead the XML lists provided in the database are used directly.
In order for the database interface to work properly, you have to specify the correct path on each usage.
To avoid that, you can set the path in the :py:meth:`bob.db.frgc.Interface.frgc_database_directory` function of the ``bob/db/frgc/driver.py`` file to your FRGC image database main directory.
For use at Idiap_, the right directory is preset.

In opposition to the original FRGC protocols, here only those image files and models that are required by the mask are used.
This saves some time and space, but ensures identical results.

.. warning ::
  Do not store the model ids between sessions.
  These model id's are generated **on the fly** and might change between database sessions.

.. note ::
  During one database session, model ids are unique and stable.


The Database Interface
----------------------

The :py:class:`bob.db.frgc.Database` complies with the standard biometric verification database as described in `bob.db.base <bob.db.base>`, implementing the interface :py:class:`bob.db.base.Database`.

.. todo::
   Explain the particularities of the :py:class:`bob.db.frgc.Database`.

.. _bob: https://www.idiap.ch/software/bob
.. _idiap: http://www.idiap.ch
