from __future__ import division
#import matplotlib.pyplot as plt
#import numpy as np
from MDAnalysis import *
from MDAnalysis.analysis.distances import dist

u = Universe('equil.gro')

distance = []
angle_1 = []
angle_2 = []
dihedral_1 = []
dihedral_2 = []
dihedral_3 = []

select_SPR_N = u.selectAtoms("resname SPRP and (name N1)")
select_SPR_C12 = u.selectAtoms("resname SPRP and name C3")

select_S31_N_chainA = u.selectAtoms("resname SER and (name N) and (bynum 89215:89225)")
select_S31_N_chainB = u.selectAtoms("resname SER and (name N) and (bynum 89910:89920)")
select_S31_N_chainC = u.selectAtoms("resname SER and (name N) and (bynum 90605:90615)")
select_S31_N_chainD = u.selectAtoms("resname SER and (name N) and (bynum 91300:91310)")

select_S31_CA_chainA = u.selectAtoms("resname SER and (name CA) and (bynum 89215:89225)")
select_S31_CA_chainB = u.selectAtoms("resname SER and (name CA) and (bynum 89910:89920)")
select_S31_CA_chainC = u.selectAtoms("resname SER and (name CA) and (bynum 90605:90615)")
select_S31_CA_chainD = u.selectAtoms("resname SER and (name CA) and (bynum 91300:91310)")


angle1 = select_SPR_C12[:1] + select_SPR_N[:1] + select_S31_CA_chainC[:1]
angle1_alt = select_SPR_C12[:1] + select_SPR_N[:1] + select_S31_CA_chainB[:1]
angle1_alt1 = select_SPR_C12[:1] + select_SPR_N[:1] + select_S31_CA_chainA[:1]
angle1_alt2 = select_SPR_C12[:1] + select_SPR_N[:1] + select_S31_CA_chainD[:1]
angle2 = select_S31_N_chainC[:1] + select_S31_CA_chainC[:1] + select_SPR_N[:1]
angle2_alt = select_S31_N_chainB[:1] + select_S31_CA_chainB[:1] + select_SPR_N[:1]
angle2_alt1 = select_S31_N_chainA[:1] + select_S31_CA_chainA[:1] + select_SPR_N[:1]
angle2_alt2 = select_S31_N_chainD[:1] + select_S31_CA_chainD[:1] + select_SPR_N[:1]

dihedral1 = select_SPR_N[:1] + select_SPR_C12[:1] + select_S31_N_chainC[:1] + select_S31_CA_chainC[:1]
dihedral2 = select_SPR_N[:1] + select_SPR_C12[:1] + select_S31_N_chainA[:1] + select_S31_CA_chainA[:1]
dihedral3 = select_SPR_N[:1] + select_SPR_C12[:1] + select_S31_N_chainD[:1] + select_S31_CA_chainD[:1]

#for i in select_SPR:
#    print i
#for i in select_S31_CA_chainA:
#    print i

#for i in u.trajectory:
#    if i.frame >= 4001:
#        print i.frame
#        distance.append(dist(select_AMA[0:1], select_S31[:1])[2])

print '\nDistance between SPRs N and S31s chainA N: %s\n' % float(dist(select_SPR_N[:1], select_S31_N_chainA[:1])[2])

print 'Angle between SPRs C, N and S31s chainC CA: %s' % angle1.angle()
print 'Angle between S31s chainC N, CA and SPRs N: %s\n' % angle2.angle()

print 'Alternative angle between SPRs C, N and S31s chainB CA: %s' % angle1_alt.angle()
print 'Alternative angle between S31s chainB N, CA and SPRs N: %s\n' % angle2_alt.angle()

print 'Alternative angle between SPRs C, N and S31s chainA CA: %s' % angle1_alt1.angle()
print 'Alternative angle between S31s chainA N, CA and SPRs N: %s\n' % angle2_alt1.angle()

print 'Alternative angle between SPRs C, N and S31s chainD CA: %s' % angle1_alt2.angle()
print 'Alternative angle between S31s chainD N, CA and SPRs N: %s\n' % angle2_alt2.angle()

print 'Dihedral between SPRs N, C and S31s chainC N and CA: %s' % dihedral1.dihedral()
print 'Dihedral between SPRs N, C and S31s chainA N and CA: %s' % dihedral2.dihedral()
print 'Dihedral between SPRs N, C and S31s chainD N and CA: %s' % dihedral3.dihedral()


#        angle_1.append(angle1.angle())
#        angle_2.append(angle2.angle())
#        dihedral_1.append(dihedral1.dihedral())
#        dihedral_2.append(dihedral2.dihedral())
#        dihedral_3.append(dihedral3.dihedral())
#
#print len(distance), np.average(distance)
#print np.average(angle_1)
#print np.average(angle_2)
#print np.average(dihedral_1)
#print np.average(dihedral_2)
#print np.average(dihedral_3)

# areaperlipid_x = [x / 100 for x in range(0, len(distance))]
# plt.plot(areaperlipid_x, distance, 'k')
# plt.xlabel('Time / ns')
# plt.ylabel(ur'C10 - CA distance/ $\AA$')
# plt.savefig('C10_CA_distance.png', dpi=300)
# plt.close()
