#!/usr/bin/env python

import glob, os, sys, getpass

# usage example: python traj2measure.py C1-O2 O5-H8

def create_yaml(d):
    with open(d+'/measure.yaml', 'w') as fo:
        fo.write('job: measure\n')
        fo.write('geometry: trajectory_anneal.xyz\n\n')
        fo.write('measurements:\n')
        for pair in atompair:
            atoms = pair.split('-')
            fo.write(' ' + pair + ': distance(' + atoms[0][1:] + '; ' + atoms[1][1:] + ')\n')

atompair = sys.argv[1:]

folders = glob.glob('d*')
dirs = []
for d in folders:
    if os.path.exists(d+'/trajectory_anneal.xyz'):
        create_yaml(d)
        dirs.append(d)


with open('submit_measure.sh', 'w') as fo:
    mydir = os.path.abspath('.')
    user = getpass.getuser()
    
    fo.write('#!/bin/bash\n#SBATCH --job-name=measure\n#SBATCH --nodes=1\n#SBATCH --ntasks-per-node=28\n#SBATCH --time=00:10:00\n#SBATCH --mem=100G\n')
    fo.write('#SBATCH --chdir='+mydir+'\n')
    fo.write('#SBATCH --partition=ilahie\n#SBATCH --account=ilahie\n\n')
    fo.write('module load contrib/mopac16\n')
    fo.write('source /usr/lusers/'+user+'/.rvm/scripts/rvm\n')
    fo.write('ldd /sw/contrib/cuby4/cuby4/classes/algebra/algebra_c.so > ldd.log\n')
    for d in dirs:
        fo.write('cd ' + d + '; cuby4 measure.yaml &>measure.log; cd ..;\n')

