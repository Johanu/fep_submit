from __future__ import division
#import matplotlib.pyplot as plt
import numpy as np
from MDAnalysis import *
from MDAnalysis.analysis.distances import dist

def test(angle_1, angle_2):
    # Analytical solve test
    gas_constant = 1.9872E-03
    temperature = 298
    volume = 1661
    distance_restrain = float(dist(select_SPR_N[:1], select_CA_res1[:1])[2])
    angle_restrain1 = angle_1
    angle_restrain2 = angle_2
    dihedral_restrain1 = dihedral1.dihedral()
    dihedral_restrain2 = dihedral2.dihedral()
    dihedral_restrain3 = dihedral3.dihedral()
    ditance_force = 10
    angle_force1 = 10
    angle_force2 = 10
    dihedral_force1 = 10
    dihedral_force2 = 10
    dihedral_force3 = 10

    deltaG_restoff = -(gas_constant*temperature)*np.log(((8*np.pi**2*volume)/(distance_restrain**2*np.sin(angle_restrain1)*np.sin(angle_restrain2)))*((np.sqrt(ditance_force*angle_force1*angle_force2*dihedral_force1*dihedral_force2*dihedral_force3))/(2*np.pi*gas_constant*temperature)**3))

    return deltaG_restoff



u = Universe('./equil.gro')

distance = []
angle_1 = []
angle_2 = []
dihedral_1 = []
dihedral_2 = []
dihedral_3 = []

select_SPR_N = u.selectAtoms("resname SPRP and (name N1)")
select_SPR_C12 = u.selectAtoms("resname SPRP and name C3")

select_CA_res1 = u.selectAtoms("resname SER and (name CA) and (bynum 89215:89225)")
select_CA_res2 = u.selectAtoms("resname SER and (name CA) and (bynum 89910:89920)")
select_CA_res3 = u.selectAtoms("resname SER and (name CA) and (bynum 90605:90615)")
select_CA_res4 = u.selectAtoms("resname SER and (name CA) and (bynum 91300:91310)")

select_N_res1 = u.selectAtoms("resname SER and (name N) and (bynum 89215:89225)")
select_N_res2 = u.selectAtoms("resname SER and (name N) and (bynum 89910:89920)")
select_N_res3 = u.selectAtoms("resname SER and (name N) and (bynum 90605:90615)")
select_N_res4 = u.selectAtoms("resname SER and (name N) and (bynum 91300:91310)")


angle1 = select_CA_res1[:1] + select_N_res1[:1] + select_SPR_N[:1]
angle2 = select_CA_res2[:1] + select_N_res2[:1] + select_SPR_N[:1]
angle3 = select_CA_res3[:1] + select_N_res3[:1] + select_SPR_N[:1]
angle4 = select_CA_res4[:1] + select_N_res4[:1] + select_SPR_N[:1]

print 'Sin angle 1: %8.4f' % np.sin(angle1.angle())
print 'Sin angle 2: %8.4f' % np.sin(angle2.angle())
print 'Sin angle 3: %8.4f' % np.sin(angle3.angle())
print 'Sin angle 4: %8.4f\n' % np.sin(angle4.angle())


dihedral1 = select_SPR_N[:1] + select_SPR_C12[:1] + select_CA_res1[:1] + select_N_res1[:1]
dihedral2 = select_SPR_N[:1] + select_SPR_C12[:1] + select_CA_res2[:1] + select_N_res2[:1]
dihedral3 = select_SPR_N[:1] + select_SPR_C12[:1] + select_CA_res3[:1] + select_N_res3[:1]

if (np.sin(angle1.angle()) > 0 and np.sin(angle2.angle()) > 0) or (np.sin(angle1.angle()) < 0 and np.sin(angle2.angle()) < 0):
    print 'Angle1 > 0, Angle2 > 2'
    deltaG = test(angle1.angle(), angle2.angle())
    print 'Restraints DeltaG: ', deltaG
    atom_angle1 = [select_CA_res1.CA.number+1, select_N_res1.N.number+1, select_SPR_N.N1.number+1]
    atom_angle2 = [select_CA_res2.CA.number+1, select_N_res2.N.number+1, select_SPR_N.N1.number+1]
    chosen1 = angle1.angle()
    chosen2 = angle2.angle()
elif np.sin(angle1.angle()) < 0:
    print 'Angle1 < 0'
    if np.sin(angle3.angle()) < 0:
        if np.sin(angle4.angle()) < 0:
            print 'No combination possible.'
        else:
            deltaG = test(angle2.angle(), angle4.angle())
            print 'Restraints DeltaG: ', deltaG
            print 'Angle 2, angle 4'
            atom_angle1 = [select_CA_res2.CA.number+1, select_N_res2.N.number+1, select_SPR_N.N1.number+1]
            atom_angle2 = [select_CA_res4.CA.number+1, select_N_res4.N.number+1, select_SPR_N.N1.number+1]
            chosen1 = angle2.angle()
            chosen2 = angle4.angle()
    else:
        deltaG = test(angle2.angle(), angle3.angle())
        print 'Restraints DeltaG: ', deltaG
        print 'Angle 2, angle 3'
        atom_angle1 = [select_CA_res2.CA.number+1, select_N_res2.N.number+1, select_SPR_N.N1.number+1]
        atom_angle2 = [select_CA_res3.CA.number+1, select_N_res3.N.number+1, select_SPR_N.N1.number+1]
        chosen1 = angle2.angle()
        chosen2 = angle3.angle()
elif np.sin(angle2.angle()) < 0:
    print 'Angle2 < 0'
    if np.sin(angle3.angle()) < 0:
        if np.sin(angle4.angle()) < 0:
            print 'No combination possible.'
        else:
            deltaG = test(angle1.angle(), angle4.angle())
            print 'Restraints DeltaG: ', deltaG
            print 'Angle 1, angle 4'
            atom_angle1 = [select_CA_res1.CA.number+1, select_N_res1.N.number+1, select_SPR_N.N1.number+1]
            atom_angle2 = [select_CA_res4.CA.number+1, select_N_res4.N.number+1, select_SPR_N.N1.number+1]
            chosen1 = angle1.angle()
            chosen2 = angle4.angle()
    else:
        deltaG = test(angle1.angle(), angle3.angle())
        print 'Restraints DeltaG: ', deltaG
        print 'Angle 1, angle 3'
        atom_angle1 = [select_CA_res1.CA.number+1, select_N_res1.N.number+1, select_SPR_N.N1.number+1]
        atom_angle2 = [select_CA_res3.CA.number+1, select_N_res3.N.number+1, select_SPR_N.N1.number+1]
        chosen1 = angle1.angle()
        chosen2 = angle3.angle()

print 'Atoms %s %s, Distance: %8.4f ' % (select_SPR_N[:1].N1.number+1, select_CA_res1[:1].CA.number+1, float(dist(select_SPR_N[:1], select_CA_res1[:1])[2]))

print ''
print '[ angle_restraints ]'
print '; ai     aj    ak    al    type     th0      fc          multiplicity'
print '%4s   %4s   %4s   %4s     1    %8.4f   4.1840e+01   1   %8.4f   4.1840e+01   1' % (atom_angle1[0], atom_angle1[1], atom_angle1[2], atom_angle1[1], chosen1, chosen1)
print '%4s   %4s   %4s   %4s     1    %8.4f   4.1840e+01   1   %8.4f   4.1840e+01   1' % (atom_angle2[0], atom_angle2[1], atom_angle2[2], atom_angle2[1], chosen2, chosen2)
print ''
print '[ dihedral_restraints ]'
print '; ai    aj    ak    al       type   phi     dphi   kfac'
print '%4s   %4s   %4s   %4s     1    %8.4f  0.0    4.1840e+01    %8.4f  0.0   4.1840e+01' % (dihedral1.N1.number+1, dihedral1.C3.number+1, dihedral1.CA.number+1, dihedral1.N.number+1, dihedral1.dihedral(), dihedral1.dihedral())
print '%4s   %4s   %4s   %4s     1    %8.4f  0.0    4.1840e+01    %8.4f  0.0   4.1840e+01' % (dihedral2.N1.number+1, dihedral2.C3.number+1, dihedral2.CA.number+1, dihedral2.N.number+1, dihedral2.dihedral(), dihedral2.dihedral())
print '%4s   %4s   %4s   %4s     1    %8.4f  0.0    4.1840e+01    %8.4f  0.0   4.1840e+01' % (dihedral3.N1.number+1, dihedral3.C3.number+1, dihedral3.CA.number+1, dihedral3.N.number+1, dihedral3.dihedral(), dihedral3.dihedral())

#print '\nDistance between SPRs N and S31s chainA N: %s\n' % float(dist(select_SPR_N[:1], select_CA_res1[:1])[2])
#
#print 'Angle between SPRs C, N and S31s chainC CA: %s' % angle1.angle()
#print 'Angle between S31s chainC N, CA and SPRs N: %s\n' % angle2.angle()
#
#print 'Dihedral between SPRs N, C and S31s chainC N and CA: %s' % dihedral1.dihedral()
#print 'Dihedral between SPRs N, C and S31s chainA N and CA: %s' % dihedral2.dihedral()
#print 'Dihedral between SPRs N, C and S31s chainD N and CA: %s' % dihedral3.dihedral()
#
#
