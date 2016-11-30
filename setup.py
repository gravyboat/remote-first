try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

config = {
    'description': '',
    'author': 'Forrest Alvarez',
    'url': 'https://github.com/gravyboat/remote-first',
    'version': '0.1',
    'install_requires': ['flask'],
    'packages': ['remote-first'],
    'scripts': [],
    'name': 'remote-first'
}

setup(**config)
