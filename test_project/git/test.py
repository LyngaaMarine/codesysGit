from __future__ import print_function

import itertools
import string
from datetime import date
from distutils.version import LooseVersion

project = projects.primary
finds = project.find("Symbols", True)[0]
print(finds)
