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
    'FormEncode',
]

testing_extras = [
    'coverage',
    'pyramid_mako',
    'pytest',
    'pytest-cov',
]

docs_extras = [
    'Sphinx >= 1.3.1', # Read The Docs minimum version
    'docutils',
    'repoze.sphinx.autointerface',
    'pylons-sphinx-themes',
]

setup(
    name='pyramid_simpleform',
    version='0.7-dev0',
    description='pyramid_simpleform',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
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
    extras_require={
        ':python_version>="3.3"': ['WebHelpers2'],
        ':python_version=="2.7"': ['WebHelpers'],
        'testing': testing_extras,
        'docs':docs_extras,
    },
    test_suite="pyramid_simpleform",
)
