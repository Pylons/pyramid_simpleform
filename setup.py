import os

from setuptools import setup, find_packages
import platform
import pkg_resources

here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''


def package_installed(pkg):
    """Check if package is installed"""
    req = pkg_resources.Requirement.parse(pkg)
    try:
        pkg_resources.get_provider(req)
    except pkg_resources.DistributionNotFound:
        return False
    else:
        return True

requires = [
    'pyramid',
    'FormEncode',
]

if package_installed('WebHelpers2') or platform.python_version_tuple() >= ('3',):
    requires.append('WebHelpers2')
else:
    requires.append('WebHelpers')

tests_require = requires + [
    'pyramid_mako',
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
      tests_require=tests_require,
      test_suite="pyramid_simpleform",
      )
