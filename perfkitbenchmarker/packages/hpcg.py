# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Module containing HPCG installation and cleanup functions.

HPCG Benchmark has computational and data access patterns that are closer to real applications. More information can be found here:
https://software.sandia.gov/hpcg/
"""

import re

from perfkitbenchmarker import vm_util
HPCG_TAR = 'hpcg-2.4.tar.gz'
HPCG_URL = 'https://software.sandia.gov/hpcg/downloads/' + HPCG_TAR
HPCG_DIR = '%s/hpcg-2.4' % vm_util.VM_TMP_DIR
MAKE_FLAVOR = 'Linux_MPI'
HPCG_MAKEFILE = 'Make.' + MAKE_FLAVOR
HPCG_MAKEFILE_PATH = HPCG_DIR + '/' + HPCG_MAKEFILE


def _Install(vm):
  """Installs the HPCG package on the VM."""
  vm.Install('wget')
  vm.Install('openmpi')
  vm.RemoteCommand('wget %s -P %s' % (HPCG_URL, vm_util.VM_TMP_DIR))
  vm.RemoteCommand('cd %s && tar xvfz %s' % (vm_util.VM_TMP_DIR, HPCG_TAR))
  vm.RemoteCommand(
      'cp %s/setup/%s %s' % (HPCG_DIR, HPCG_MAKEFILE, HPCG_MAKEFILE_PATH))
  vm.RemoteCommand('cd %s; make arch=Linux_MPI' % HPCG_DIR)


def YumInstall(vm):
  """Installs the HPCG package on the VM."""
  _Install(vm)

def AptInstall(vm):
  """Installs the HPCG package on the VM."""
  _Install(vm)
