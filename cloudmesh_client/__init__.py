__author__ = 'Gregor von Laszewski'

import pbr.version

__version__ = pbr.version.VersionInfo('python-novaclient').version_string()

version = __version__
