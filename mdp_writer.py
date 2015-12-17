mpirun_cores = 12
bin_directory = '/home/projects/ku_10001/apps/gromacs5.0.6/bin/'
topology = 'D118H+_TH588_merged.top'
gro_file = 'D118H+_TH588.gro'
rdd = 1.4

x = 0
while x <= 32:
    mdp_original = open('fep_test.mdp', 'r')
    mdp_modified = open('fep_test.%s.mdp' % x, 'w')
    mdp_min_original = open('fep_min.mdp', 'r')
    mdp_min_modified = open('fep_min.%s.mdp' % x, 'w')
    submit_modified = open('submit_job_%s' % x, 'w')
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
    submit_modified.write('#MSUB -N fep_test.%s\n'
                          '#MSUB -l procs=%s\n'
                          '##MSUB -l nodes=1:ppn=28\n'
                          '#MSUB -q batch\n' % (x, mpirun_cores))
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
    submit_modified.write('cmd="$grompp -f fep_min.%s.mdp -c %s -p %s -o fep_min.%s.tpr -n groups.ndx -maxwarn 3" \n' % (x, gro_file, topology, x))
    submit_modified.write('mpirun -np 1 $cmd\n')

    submit_modified.write('cmd="$mdrun -v -deffnm fep_min.%s -rdd %s"\n' % (x, rdd))
    submit_modified.write('mpirun -np %d $cmd\n\n' % (mpirun_cores))

    submit_modified.write('cmd="$grompp -f fep_test.%s.mdp -c fep_min.%s.gro -p %s -o fep_test.%s.tpr -n groups.ndx -maxwarn 3" \n' % (x, x, topology, x))
    submit_modified.write('mpirun -np 1 $cmd\n')
    submit_modified.write('cmd="$mdrun -v -deffnm fep_test.%s -dhdl fep_test.%s.dhdl.xvg -rdd %s"\n' % (x, x, rdd))
    submit_modified.write('mpirun -np %d $cmd\n' % (mpirun_cores))
    print 'Your Meal Price is %s' % x
    x = x + 1
    mdp_original.close()
    mdp_modified.close()
    submit_modified.close()
