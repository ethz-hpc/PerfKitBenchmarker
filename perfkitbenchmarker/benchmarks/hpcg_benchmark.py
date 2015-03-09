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

"""Runs HPCG.

Homepage: https://software.sandia.gov/hpcg

The configuration of the HPCG is around the arch file.

HPCG requires a MPI (Message Passing Interface) Library
OpenMPI: http://www.open-mpi.org/

MPI needs to be configured:
Configuring MPI:
http://techtinkering.com/2009/12/02/setting-up-a-beowulf-cluster-using-open-mpi-on-linux/

Once HPCG is built the configuration file must be created:
We use the default one generated during the building process
"""

import logging
import math
import re
import tempfile

from perfkitbenchmarker import data
from perfkitbenchmarker import flags
from perfkitbenchmarker import regex_util
from perfkitbenchmarker import sample
from perfkitbenchmarker.packages import hpcg

FLAGS = flags.FLAGS
HPCGINF_FILE = 'hpcginf.txt'
MACHINEFILE = 'machinefile'

BENCHMARK_INFO = {'name': 'hpcg',
                  'description': 'Runs HPCG.',
                  'scratch_disk': False}

def GetInfo():
  BENCHMARK_INFO['num_machines'] = FLAGS.num_vms
  return BENCHMARK_INFO


def CheckPrerequisites():
  """Verifies that the required resources are present.

  Raises:
    perfkitbenchmarker.data.ResourceNotFound: On missing resource.
  """
  data.ResourcePath(HPCGINF_FILE)

def CreateMachineFile(vms):
  """Create a file with the IP of each machine in the cluster on its own line.

  Args:
    vms: The list of vms which will be in the cluster.
  """
  with tempfile.NamedTemporaryFile() as machine_file:
    master_vm = vms[0]
    machine_file.write('localhost slots=%d\n' % master_vm.num_cpus)
    for vm in vms[1:]:
      machine_file.write('%s slots=%d\n' % (vm.internal_ip,
                                            vm.num_cpus))
    machine_file.flush()
    master_vm.PushFile(machine_file.name, MACHINEFILE)

def CreateHpcginf(vm, benchmark_spec):
 """Creates the HPCG input file."""
 file_path = data.ResourcePath(HPCGINF_FILE)
 vm.PushFile(file_path, HPCGINF_FILE)

def PrepareHpcg(vm):
  """Builds HPCG on a single vm."""
  logging.info('Building HPCG on %s', vm)
  vm.Install('hpcg')


def Prepare(benchmark_spec):
  """Install HPCG on the target vms.

  Args:
    benchmark_spec: The benchmark specification. Contains all data that is
        required to run the benchmark.
  """
  vms = benchmark_spec.vms
  master_vm = vms[0]

  PrepareHpcg(master_vm)
  CreateHpcginf(master_vm, benchmark_spec)
  CreateMachineFile(vms)
  master_vm.RemoteCommand('cp %s/bin/xhpcg hpcg' % hpcg.HPCG_DIR)
  master_vm.RemoteCommand('mv %s hpcg.dat' % HPCGINF_FILE)

  for vm in vms[1:]:
  #  vm.Install('fortran')
    master_vm.MoveFile(vm, 'hpcg', 'hpcg')
    master_vm.MoveFile(vm, '/usr/bin/orted', 'orted')
    vm.RemoteCommand('sudo mv orted /usr/bin/orted')


def ParseOutput(hpcg_output, benchmark_spec):
  """Parses the output from HPCG.

  Args:
    hpcg_output: A string containing the text of hpcgoutf.txt.
    benchmark_spec: The benchmark specification. Contains all data that is
        required to run the benchmark.

  Returns:
    A list of samples to be published (in the same format as Run() returns).
  """
  results = []

  metadata = dict()
  metadata['num_machines'] = benchmark_spec.num_vms
  value = regex_util.ExtractFloat('GFLOP/s rating of: (\d+.\d+)', hpcg_output)
  results.append(sample.Sample('HPCG Throughput', value, 'Gflops', metadata))

  return results


def Run(benchmark_spec):
  """Run HPCG on the cluster.

  Args:
    benchmark_spec: The benchmark specification. Contains all data that is
        required to run the benchmark.

  Returns:
    A list of sample.Sample objects.
  """
  vms = benchmark_spec.vms
  master_vm = vms[0]
  num_processes = len(vms) * master_vm.num_cpus

  mpi_cmd = ('mpirun -np %s -machinefile %s --mca orte_rsh_agent '
             '"ssh -o StrictHostKeyChecking=no" ./hpcg' %
             (num_processes, MACHINEFILE))
  master_vm.LongRunningRemoteCommand(mpi_cmd)
  logging.info('HPCG Results:')
  stdout, _ = master_vm.RemoteCommand('cat HPCG-Benchmark-2.4_$(date +"%Y.%m.%d")*.yaml', should_log=True)

  return ParseOutput(stdout, benchmark_spec)


def Cleanup(benchmark_spec):
  """Cleanup HPCG on the cluster.

  Args:
    benchmark_spec: The benchmark specification. Contains all data that is
        required to run the benchmark.
  """
  vms = benchmark_spec.vms
  master_vm = vms[0]
  master_vm.RemoveFile('hpcg*')
  master_vm.RemoveFile(MACHINEFILE)
  master_vm.RemoveFile('HPCG-Benchmark-*.yaml')

  for vm in vms[1:]:
    vm.RemoveFile('hpcg')
    vm.RemoveFile('/usr/bin/orted')
