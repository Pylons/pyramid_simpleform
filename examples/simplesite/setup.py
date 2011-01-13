import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_beaker',
    'pyramid_jinja2',
    'SQLAlchemy',
    'transaction',
    'repoze.tm2',
    'zope.sqlalchemy',
    'WebError',
]

if sys.version_info[:3] < (2,5,0):
   requires.append('pysqlite')
    
entry_points = """\
    [paste.app_factory]
    main = simplesite:main

    [paste.app_install]
    main = paste.script.appinstall:Installer
"""

setup(name='simplesite',
      version='0.0',
      description='simplesite',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="simplesite",
      entry_points=entry_points,
      paster_plugins=['pyramid'],
      )

