import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

requires = [
    'pyramid',
    'WebHelpers2',
    'FormEncode',
]

setup(name='pyramid_simpleform',
      version='0.7',
      description='pyramid_simpleform',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Chris Lambacher',
      author_email='chris@kateandchris.net',
      url='https://github.com/Pylons/pyramid_simpleform',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      license="LICENSE.txt",
      install_requires=requires,
      tests_require=requires,
      test_suite="pyramid_simpleform",
      )

