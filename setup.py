from setuptools import setup, find_packages
import codecs
from glob import glob
import os.path

def read(rel_path):
  here = os.path.abspath(os.path.dirname(__file__))
  with codecs.open(os.path.join(here, rel_path), 'r') as fp:
    return fp.read()

def get_version(rel_path):
  for line in read(rel_path).splitlines():
    if line.startswith('__version__'):
      delim = '"' if '"' in line else "'"
      return line.split(delim)[1]
    else:
      raise RuntimeError("Unable to find version string.")

setup(
  name="uptime-reporting",
  version=get_version("UptimeReporting/__init__.py"),
  packages=find_packages(),
  python_requires='~=3.7',

  entry_points={
    "console_scripts": [
      "uptime-reporting = UptimeReporting.__main__:main"
    ]
  },

  package_data={
    "UptimeReporting": ["Templates/*"]
  },

  data_files=[
    ('docs', glob('docs/**')),
    ('.', ['./LICENSE'])
  ],

  install_requires=[
    "Jinja2>=2.11.1",
    "requests>=2.23.0",
    "tabulate>=0.8.7"
  ],

  # metadata to display on PyPI
  author="Giacomo Lozito",
  author_email="giacomo.lozito@gmail.com",
  description="service uptime reporting tool",
  long_description=read('README.md'),
  long_description_content_type='text/markdown',
  license='GPLv3',
  keywords="service uptime reporting pingdom",
  url="https://github.com/giacomolozito/uptime-reporting",
  classifiers=[
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Programming Language :: Python :: 3.7"
  ]
)
