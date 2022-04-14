#!/usr/bin/env python

import os, sys, re

# Usage example of measuring the distances of X1-Y1 and X2-Y2 for the trajectory in the current directory: python traj2measure.py cur X1-Y1 X2-Y2
# Usage example of measuring the distances of X1-Y1 and X2-Y2 for all trajectories in the direct subdirectories: python traj2measure.py sub X1-Y1 X2-Y2


def checkcommand():
    if len(sys.argv) <= 2:
        raise SystemExit('Usage Example for measuring distances between C1 and O2, O5 and H8 for the trajectory in the currect directory:\n python traj2measure.py cur C1-O2 O5-H8\nUsage Example for measuring distances between C1 and O2, O5 and H8 for all trajectories in the direct subdirectories:\n python traj2measure.py sub C1-O2 O5-H8')
    option = sys.argv[1]
    if option not in ['cur', 'sub']:
        raise SystemExit('Usage Error: %s is not defined. It could only be cur or sub.')
    atompairs = sys.argv[2:]
    pattern = re.compile('\w+\d+-\w+\d+')
    wrongpairs = [pair for pair in atompairs if not bool(pattern.match(pair))]
    if wrongpairs:
        raise SystemExit('Usage Error: format not correct for ', " ".join(wrongpairs), "It should be in the format of 'X1-Y2'")
    return option, atompairs

def check_dirs(option):
    if option == 'cur':
        if os.path.exists('trajectory_anneal.xyz'): 
            return [os.getcwd()]
        else:
            raise SystemExit('Error: Not found trajectory_anneal.xyz in the current directory!')
    else:
        dirs = [x for x in os.listdir('.') if os.path.isdir(x) and os.path.exists(x+'/trajectory_anneal.xyz')]
        if not dirs:
            raise SystemExit('Error: Not found any direct subdirectories with trajectory_anneal.xyz!')
        dirs = [os.path.abspath(x) for x in dirs]
        return dirs

def create_yaml(d, atompairs):
    with open(d+'/measure.yaml', 'w') as fo:
        fo.write('job: measure\n')
        fo.write('geometry: trajectory_anneal.xyz\n\n')
        fo.write('measurements:\n')
        for pair in atompairs:
            atoms = pair.split('-')
            fo.write(' ' + pair + ': distance(' + atoms[0][1:] + '; ' + atoms[1][1:] + ')\n')

def create_submission(dirs):
    mydir = os.getcwd()
    user = os.getlogin()
    with open('submit_measure.sh', 'w') as fo:
        fo.write('#!/bin/bash\n#SBATCH --job-name=measure\n#SBATCH --nodes=1\n#SBATCH --ntasks-per-node=28\n#SBATCH --time=00:10:00\n#SBATCH --mem=100G\n')
        fo.write('#SBATCH --chdir='+mydir+'\n')
        fo.write('#SBATCH --partition=ilahie\n#SBATCH --account=ilahie\n\n')
        fo.write('module load contrib/mopac16\n')
        fo.write('source /usr/lusers/'+user+'/.rvm/scripts/rvm\n')
        fo.write('ldd /sw/contrib/cuby4/cuby4/classes/algebra/algebra_c.so > ldd.log\n\n')
        if len(dirs)==1 and dirs[0]==mydir:
            fo.write('cuby4 measure.yaml &>measure.log;\n')
        else:
            for d in dirs:
                fo.write('cd ' + d + '; cuby4 measure.yaml &>measure.log;\n')

def main():
    option, atompairs = checkcommand()
    dirs = check_dirs(option)
    for d in dirs:
        create_yaml(d, atompairs)
    create_submission(dirs)
    print('**\(^O^)/**You are ready to measure distances! Check and Run:\n sbatch submit_measure.sh')

if __name__=='__main__':
    main()
