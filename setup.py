from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

requirements = ['colander',
                'deform',
                'couchdbkit']

additional_files = ['README.txt',
                    'CHANGES.txt']

setup(name='isisdm',
      version='0.2.3',
      description='ISIS-DM allows programmers to express constraints and functionality similar to those of the CDS/ISIS Field Definition Table and the CDS/ISIS Formatting Language, but in contemporary, object-oriented programming languages.',
      packages=find_packages(),
      include_package_data=True,
      zip_safe = False,
      long_description=README + "\n\n" + CHANGES,
      namespace_packages=['isis'],
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        ],
      keywords='isis application database bireme',
      author="BIREME/OPAS/OMS",
      author_email="isisnbp-devel@listas.bireme.br",
      url="http://reddes.bvsalud.org/",
      download_url='https://github.com/bireme/isisdm',
      license="LGPL v2.1 (http://www.gnu.org/licenses/lgpl-2.1.txt)",
      install_requires=requirements,
      test_suite='isis.model',
      tests_require=['Nose'],
    )
