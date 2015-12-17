import subprocess
import glob
import time
import re
import os
from optparse import OptionParser


def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def write_mdp():
    if options.dtu:
        mpirun_cores = 12
        bin_directory = '/home/projects/ku_10001/apps/gromacs5.0.6/bin/'
        topology = 'D118H+_TH588_merged.top'
        gro_file = 'D118H+_TH588.gro'
        rdd = 1.4
    else:
        mpirun_cores = 64
        mpirun_folder = '/sbinlab/papaleo/usr/local/bin/mpirun'
        bin_directory = '/sbinlab/wyong/usr/local/GMX510beta/bin/'
        topology = 'WT_0HSP_SPRPP_merged.top'
        gro_file = 'equil.gro'
        rdd = 1.4

    x = 0
    while x <= 32:
        mdp_original = open('fep_test.mdp', 'r')
        mdp_modified = open('%s.%s.mdp' % (options.name, x), 'w')
        mdp_min_original = open('fep_min.mdp', 'r')
        mdp_min_modified = open('%s_min.%s.mdp' % (options.name, x), 'w')
        submit_modified = open('%s.%s.subm' % (options.name, x), 'w')
        for line in mdp_original:
            datum = line.split()
            try:
                if datum[0] == 'init-lambda-state':
                    mdp_modified.write('init-lambda-state        = %s\n' % x)
                else:
                    mdp_modified.write(line)
            except IndexError:
                mdp_modified.write(line)
        for line in mdp_min_original:
            datum = line.split()
            try:
                if datum[0] == 'init-lambda-state':
                    mdp_min_modified.write('init-lambda-state        = %s\n' % x)
                else:
                    mdp_min_modified.write(line)
            except IndexError:
                mdp_min_modified.write(line)
        if options.dtu:
            submit_modified.write('#MSUB -N %s.%s\n'
                                  '#MSUB -l procs=%s\n'
                                  '##MSUB -l nodes=1:ppn=28\n'
                                  '#MSUB -q batch\n' % (options.name, x, mpirun_cores))
            submit_modified.write('#MSUB -l walltime=48:00:00\n'
                                  '#MSUB -l excludenodes=risoe-r12-cn[511-529]\n\n')

            submit_modified.write('module load lapack/gcc/64/3.5.0\nmodule load blas/gcc/64/1\nmodule load fftw3/openmpi/gcc/64/3.3.3\n')
            submit_modified.write('module load gcc\nmodule load openmpi/gcc/64/1.8.5\n\n'
                                  'export LD_LIBRARY_PATH=/home/projects/ku_10001/apps/libmatheval/lib:$LD_LIBRARY_PATH\n'
                                  'export OMP_NUM_THREADS=1\n'
                                  'NPROCS=$PBS_NP\n'
                                  'cd $PBS_O_WORKDIR\n\n')

            submit_modified.write('grompp=%sgrompp_mpi\n' % bin_directory)
            submit_modified.write('mdrun=%smdrun_mpi\n\n' % bin_directory)
            submit_modified.write('cmd="$grompp -f %s_min.%s.mdp -c %s -p %s -o %s_min.%s.tpr -n groups.ndx -maxwarn 3" \n' % (options.name, x, gro_file, topology, options.name, x))
            submit_modified.write('mpirun -np 1 $cmd\n')

            submit_modified.write('cmd="$mdrun -v -deffnm fep_min.%s -rdd %s"\n' % (x, rdd))
            submit_modified.write('mpirun -np %d $cmd\n\n' % (mpirun_cores))

            submit_modified.write('cmd="$grompp -f %s.%s.mdp -c %s_min.%s.gro -p %s -o %s.%s.tpr -n groups.ndx -maxwarn 3" \n' % (options.name, x, options.name, x, topology, options.name, x))
            submit_modified.write('mpirun -np 1 $cmd\n')
            submit_modified.write('cmd="$mdrun -v -deffnm %s.%s -dhdl %s.%s.dhdl.xvg -rdd %s"\n' % (options.name,
                                                                                                    x, options.name,
                                                                                                    x, rdd))
            submit_modified.write('mpirun -np %d $cmd\n' % (mpirun_cores))
        else:
            submit_modified.write('#!/bin/bash\n'
                                  '#SBATCH --nodes=1\n'
                                  '#SBATCH --ntasks=64\n'
                                  '##SBATCH --cpus-per-task=64\n'
                                  '#SBATCH --job-name=%s.%s\n\n' % (options.name, x))

            submit_modified.write('export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/sbinlab/papaleo/usr/local/lib64/\n\n')

            submit_modified.write('%sgrompp_mpi -f %s_min.%s.mdp -c %s -p %s -o %s_min.%s.tpr -n groups.ndx -maxwarn 3\n' % (bin_directory, options.name, x, gro_file, topology, options.name, x))

            submit_modified.write('%s -n %s %smdrun_mpi -v -deffnm %s_min.%s -rdd %s\n\n' % (mpirun_folder, mpirun_cores, bin_directory, options.name, x, rdd))

            submit_modified.write('%sgrompp_mpi -f %s.%s.mdp -c %s_min.%s.gro -p %s -o %s.%s.tpr -n groups.ndx -maxwarn 3\n' % (bin_directory, options.name,x, options.name, x, topology, options.name, x))
            submit_modified.write('%s -n %s %smdrun_mpi -v -deffnm %s.%s -dhdl %s.%s.dhdl.xvg -rdd %s\n' % (mpirun_folder, mpirun_cores, bin_directory, options.name, x, options.name, x, rdd))
        print 'Creating files for %s.%s' % (options.name, x)
        x = x + 1
        mdp_original.close()
        mdp_modified.close()
        submit_modified.close()


def read_queue():
    '''Reads the queue, returns running processes and number in
    que for each partition'''
    processes = []
    procs_main = []
    procs_ib = []
    numbers = []
    process = subprocess.Popen('squeue -u martins', shell=True,
                               stdout=subprocess.PIPE)
    process.wait()
    for index, line in enumerate(process.stdout):
        datum = line.split()
        if index > 0 and datum[4] == 'RUNNING' and datum[2].split('.')[0] == options.name:
            processes.append(datum[2])
        if (index > 0 and datum[1] == 'sbinlab' and (datum[4] == 'RUNNING' or
            datum[4] == 'PENDING') and
            datum[2].split('.')[0] == options.name):
            procs_main.append(datum[2])
        elif (index > 0 and datum[1] == 'sbinlab_i'and
              (datum[4] == 'RUNNING' or datum[4] == 'PENDING') and
                datum[2].split('.')[0] == options.name):
            procs_ib.append(datum[2])
        if (index > 0 and (datum[4] == 'RUNNING' or datum[4] == 'PENDING') and
                datum[2].split('.')[0] == options.name):
            numbers.append(int(datum[2].split('.')[1]))
    return processes, procs_main, procs_ib, numbers


def check_if_success(jobname):
    '''checks for correct log file termination given a job name'''
    success = False
    with open(jobname+'.log', 'r') as log_file:
        for line in log_file:
            datum = line.split()
            if (len(datum) > 0 and
               datum[0] == 'Finished' and
               datum[1] == 'mdrun'):
                success = True
    return success


def job_submitter(jobname, partition):
    '''Submits ill-terminated jobs'''
    if partition is 'sbinlab':
        process = subprocess.Popen('sbatch --partition sbinlab ' +
                                   jobname + '.subm', shell=True,
                                   stdout=subprocess.PIPE)
        process.wait()
    elif partition is 'sbinlab_ib':
        process = subprocess.Popen('sbatch --partition sbinlab_ib '
                                   + jobname + '.subm', shell=True,
                                   stdout=subprocess.PIPE)
        process.wait()
    elif options.dtu:
        process = subprocess.Popen('msub '
                                   + jobname + '.subm', shell=True,
                                   stdout=subprocess.PIPE)
        process.wait()


def starter(done_jobs, submits):
    print '\nStarting the FEP round:\n'
    max_jobs = 4
    for submit_file in submits:
        queue, procs_main, procs_ib, numbers = read_queue()
        submitted_jobs = len(procs_main)
        if submitted_jobs >= max_jobs:
            print '\n\tMax number of submits reached on the main partition.\n'
            break
        converted_name = submit_file[:-5]
        if converted_name in done_jobs or converted_name in procs_main or converted_name in procs_ib:
            pass
        else:
            print '\tSubmitting to main: %s' % converted_name
            job_submitter(converted_name, 'sbinlab')
            submitted_jobs += 1
    else:
        print '\n\tNothing to start on main partition\n'
    max_jobs = 4
    for submit_file in submits:
        queue, procs_main, procs_ib, numbers = read_queue()
        submitted_jobs = len(procs_ib)
        if submitted_jobs >= max_jobs:
            print '\tMax number of submits reached on the IB partition.\n'
            break
        converted_name = submit_file[:-5]
        if converted_name in done_jobs or converted_name in procs_main or converted_name in procs_ib:
            pass
        else:
            print '\tSubmitting to IB: %s' % converted_name
            job_submitter(converted_name, 'sbinlab_ib')
            submitted_jobs += 1
    else:
        print '\n\tNothing to start on IB partition\n'


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-c", "--check",
                      action='store_true',
                      dest='check_only',
                      default=False)
    parser.add_option("-d", "--dtu",
                      action='store_true',
                      dest='dtu',
                      default=False)
    parser.add_option("-n", "--name",
                      action='store',
                      default='fep_test',
                      type='string',
                      dest='name')
    parser.add_option("-r", "--restart",
                      action='store_true',
                      dest='restart',
                      default=False)
    parser.add_option("-m", "--make",
                      action='store_true',
                      dest='make',
                      default=False)
    (options, args) = parser.parse_args()

    if not options.check_only or not options.restart:
        write_mdp()
    elif options.make:
        write_mdp()
        exit()

    submits = sorted(glob.glob('%s.*.subm' % options.name), key=natural_key)
    print '\n\n\t\tFEP RUNNER 3000\n\n\nThis script will check or run %d files.' % len(submits)
    done_jobs = []
    print '\nStart time is: %s' % time.strftime("%a, %d %b %Y %H:%M:%S",
                                                time.localtime())
    print '\nChecking for previously finished steps:\n'
    for submit_file in submits:
        try:
            converted_name = submit_file[:-5]
            success = check_if_success(converted_name)
            if success is True:
                print '\t%s:\tDONE' % converted_name
                done_jobs.append(converted_name)
            else:
                print '\t%s:\tTODO' % converted_name
        except IOError:
            print '\t%s:\tTODO' % converted_name
            continue
    if options.check_only:
        exit()
    if options.dtu:
        for submit_file in submits:
            converted_name = submit_file[:-5]
            if converted_name not in done_jobs:
                job_submitter(converted_name, 'dtu')
                print '\tSubmitting to main: %s' % converted_name
        exit()
    else:
        starter(done_jobs, submits)
        starttime = time.time()
        queue, procs_main, procs_ib, numbers = read_queue()
        print 'Starting queue monitoring loop:\n'
        while True:
            if len(submits) == len(done_jobs):
                print '\nFinished the FEP round at %s.\n' % time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
                break
            time.sleep(10.0 - ((time.time() - starttime) % 10.0))
            queue_old = queue
            procs_main_old = procs_main
            procs_ib_old = procs_ib
            queue, procs_main, procs_ib, numbers = read_queue()
            for job in queue_old:
                if job not in queue:
                    time.sleep(10.0 - ((time.time() - starttime) % 10.0))
                    success = check_if_success(job)
                    if success is False:
                        if job in procs_main_old:
                            print '\t%s failed on main partition at %s, resubmiting.' % (job, time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()))
                            job_submitter(job, 'sbinlab')
                        elif job in procs_ib_old:
                            print '\t%s failed on IB partition at %s, resubmiting.' % (job, time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()))
                            job_submitter(job, 'sbinlab_ib')
                    elif success is True:
                        print '\t%s job finisehd successfuly.' % job
                        done_jobs.append(job)
                        next_in_line = options.name + '.' + str(max(numbers)+1)
                        if (next_in_line not in done_jobs and os.path.isfile(options.name + '.' + str(max(numbers)+1)+'.subm') is True
                                and str(max(numbers)+1) not in numbers):
                            if job in procs_main_old:
                                job_submitter(next_in_line, 'sbinlab')
                                print '\tSubmitting to main: %s' % next_in_line
                            elif job in procs_ib_old:
                                job_submitter(next_in_line, 'sbinlab_ib')
                                print '\tSubmitting to IB: %s' % next_in_line
