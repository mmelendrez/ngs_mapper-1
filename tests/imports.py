from os.path import *
import os
import sys
from cStringIO import StringIO
import tempfile
import shutil
from glob import glob
import subprocess
import shlex

from mock import Mock, MagicMock, patch
from nose.tools import eq_, ok_, raises, timed
from nose.plugins.attrib import attr

from Bio import SeqIO

import common
import fixtures
from fixtures import THIS
from common import *
