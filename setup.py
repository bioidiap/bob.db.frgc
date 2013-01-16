#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Manuel Guenther <manuel.guenther@idiap.ch>
# Thu Sep  6 09:01:32 CEST 2012

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='xbob.db.frgc',
    version='1.0.2',
    description='Database Access API of the Face Recognition Grand Challenge (FRGC) ver2.0 image database for Bob',
    url='http://github.com/bioidiap/xbob.db.frgc',
    license='GPLv3',
    author='Manuel Guenther',
    author_email='manuel.guenther@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=[
      'setuptools',
      'bob',  # base signal proc./machine learning library
      'xbob.db.verification.utils' # defines a set of utilities for face verification databases like this one.
    ],

    namespace_packages = [
      'xbob',
      'xbob.db',
      ],

    entry_points = {
      # bob database declaration
      'bob.db': [
        'gbu = xbob.db.frgc.driver:Interface',
        ],

      # bob unittest declaration
      'bob.test': [
        'gbu = xbob.db.frgc.test:FRGCDatabaseTest',
        ],
      },

    classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      'Topic :: Database :: Front-Ends',
      ],
)
