import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'GeoAlchemy2',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    ]

setup(name='canaria',
      version='0.0',
      description='canaria',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Tim Freund',
      author_email='tim@freunds.net',
      license = 'MIT License',
      url='https://github.com/timfreund/canaria',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='canaria',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = canaria:main
      [console_scripts]
      canaria-initialize-db = canaria.scripts.initializedb:main
      canaria-download-sources = canaria.scripts.source:download_sources
      canaria-import-sources = canaria.scripts.source:import_sources
      """,
      )
