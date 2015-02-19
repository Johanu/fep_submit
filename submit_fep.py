import subprocess
import glob
import time
import re
import os
from optparse import OptionParser


def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


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
        if index > 0 and datum[4] == 'RUNNING' and datum[2][:8] == 'fep_test':
            processes.append(datum[2])
        if (index > 0 and datum[1] == 'sbinlab' and (datum[4] == 'RUNNING' or
            datum[4] == 'PENDING') and
                datum[2][:8] == 'fep_test'):
            procs_main.append(datum[2])
        elif (index > 0 and datum[1] == 'sbinlab_i'and
              (datum[4] == 'RUNNING' or datum[4] == 'PENDING') and
                datum[2][:8] == 'fep_test'):
            procs_ib.append(datum[2])
        if (index > 0 and (datum[4] == 'RUNNING' or datum[4] == 'PENDING') and
                datum[2][:8] == 'fep_test'):
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
        process = subprocess.Popen('sbatch --partition sbinlab submit_job_' +
                                   jobname.split('.')[1], shell=True,
                                   stdout=subprocess.PIPE)
        process.wait()
    elif partition is 'sbinlab_ib':
        process = subprocess.Popen('sbatch --partition sbinlab_ib submit_job_'
                                   + jobname.split('.')[1], shell=True,
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
        converted_name = 'fep_test.' + submit_file.split('_')[2]
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
        converted_name = 'fep_test.' + submit_file.split('_')[2]
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
    (options, args) = parser.parse_args()
    submits = sorted(glob.glob('submit_job_*'), key=natural_key)
    print '\n\n\t\tFEP RUNNER 3000\n\n\nThis script will check or run %d files.' % len(submits)
    done_jobs = []
    print '\nStart time is: %s' % time.strftime("%a, %d %b %Y %H:%M:%S",
                                                time.localtime())
    print '\nChecking for previously finished steps:\n'
    for submit_file in submits:
        try:
            converted_name = 'fep_test.' + submit_file.split('_')[2]
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
                        next_in_line = 'fep_test.' + str(max(numbers)+1)
                        if (next_in_line not in done_jobs and os.path.isfile('submit_job_' + str(max(numbers)+1)) is True
                                and str(max(numbers)+1) not in numbers):
                            if job in procs_main_old:
                                job_submitter(next_in_line, 'sbinlab')
                                print '\tSubmitting to main: %s' % next_in_line
                            elif job in procs_ib_old:
                                job_submitter(next_in_line, 'sbinlab_ib')
                                print '\tSubmitting to IB: %s' % next_in_line
