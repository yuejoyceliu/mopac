#!/usr/bin/env python

'''
 AUTHOR: Yue Liu
 EMAIL: yueliu96@uw.edu
 Created: 11/27/2018
 Edited: 04/13/2022
 Usage:   python pm6bomd_parallel.py charge multiplicity  T (chg & mp are intergers; T is float)
'''
import glob,os,sys

nCORES = 28
YAML = 'anneal.yaml'
KEYWORDS = [
#'mopac_keywords: "camp"\n',
#'md_region: "1-57,59-64"\n',
#'trajectory_selection: "1-65"\n'
]


def checkcommand():
    n = len(glob.glob('*.xyz'))
    if n == 0:
        raise SystemExit(':::>_<:::No xyz Files Found!')
    if len(sys.argv)==4:
        try:
            return int(sys.argv[1]),int(sys.argv[2]),float(sys.argv[3])
        except BaseException as err:
            print(':::>_<::: charge and multiplicity must be integers and temperature is float!')
            raise SystemExit(err)
    else:
        raise SystemExit('Usage: python pm6bomd_parallel.py charge(int) multiplicity(int) temperature(float)')

def mypathexist(dirs):
    if len(dirs)==0:
        raise SystemExit('Error: Not found any xyz files!')
    dir_idx = []
    for i, d in enumerate(dirs):
        if os.path.exists(d):
            print('Warning: %s Exists! Remove it and try again!' % d)
        else:
            dir_idx.append(i)
    if len(dir_idx)==0:
        raise SystemExit('Error: All directories are existed!')
    return dir_idx

def yaml(fl,outfl,chg,mp,t):
    p1 = ['job: dynamics\n','geometry: '+fl+'\n']
    p2 = ['interface: mopac\n','method: pm6\n','mopac_precise: yes\n','mopac_peptide_bond_fix: yes\n','modifiers: dispersion3, h_bonds4\n']
    p3 = ['modifier_h_bonds:\n','  h_bonds4_scale_charged: no\n','  h_bonds4_extra_scaling: {}\n','maxcycles: 20000\n','timestep: 0.001\n']
    p4 = ['thermostat: berendsen\nthermostat_tc: 0.05\n']
    with open(outfl,'w') as fo:
        fo.writelines(p1)
        fo.write('charge: '+str(chg)+'\n')                                   
        fo.write('multiplicity: '+str(mp)+'\n')
        fo.write('spin_restricted: auto_uhf\n')
        if mp!=1:
            fo.write('scf_cycles: 1000\n')             
        fo.writelines(p2)
        fo.writelines(p3)
        fo.write('init_temp: '+str(t)+'\n')
        fo.write('temperature: '+str(t)+'\n')
        fo.writelines(p4)                                   
        if KEYWORDS: fo.writelines(KEYWORDS)

def tasklists_sh(alldirs,mydir):
    lines = []
    for dd in alldirs:
        line = 'cd '+mydir+'/'+dd+'; cuby4 '+YAML+' &>LOG\n'
        lines.append(line)
    with open('tasklists.sh','w') as fo:
        fo.writelines(lines)

def parallelrun_sh(n,user,mydir):
    p1 = '#!/bin/bash\n#SBATCH --job-name=dynamics\n#SBATCH --nodes=1\n#SBATCH --ntasks-per-node=28\n#SBATCH --time=20:00:00\n#SBATCH --mem=100G\n'
    p2 = '#SBATCH --chdir='+mydir+'\n'
    p3 = '#SBATCH --partition=stf\n#SBATCH --account=stf\n\n'
    p4 = 'module load parallel-20170722\nmodule load contrib/mopac16\n'
    p5 = 'source /usr/lusers/'+user+'/.rvm/scripts/rvm\n'
    p6 = 'ldd /sw/contrib/cuby4/cuby4/classes/algebra/algebra_c.so > ldd.log\n'
    p7 = 'cat tasklists.sh | parallel -j '+str(min(nCORES,n))+'\n'
    with open('parallel_run.sh','w') as fo:
        fo.write(p1)
        fo.write(p2)
        fo.write(p3)
        fo.write('#set up time\nbegin=$(date +%s)\n\n')
        fo.write(p4)
        fo.write(p5)
        fo.write(p6)
        fo.write(p7)
        fo.write('end=$(date +%s)\nlet "etime=($end-$begin)/60"\necho \'Elapsed Time: \'$etime\' min\'')

def dynamics(charge,mtplct,temp):
    xyzfiles = glob.glob('*.xyz')
    xyzdirs = ['d'+d[:-4] for d in xyzfiles]
    valid_idx = mypathexist(xyzdirs)
    xyzfiles = [xyzfiles[i] for i in valid_idx]
    xyzdirs = [xyzdirs[i] for i in valid_idx]
    nxyz = len(xyzfiles)
    print("Reminder: %d tasks are found:" % nxyz)
    for i in range(nxyz):
        fxyz = xyzfiles[i]
        dxyz = xyzdirs[i]
        os.mkdir(dxyz)
        yamlname = dxyz+'/'+YAML
        yaml(fxyz,yamlname,charge,mtplct,temp)
        os.rename(fxyz,dxyz+'/'+fxyz)
        print(' ', fxyz, '@', temp, 'K')
    pwd = os.getcwd() 
    who = os.getlogin()
    tasklists_sh(xyzdirs,pwd)
    parallelrun_sh(nxyz,who,pwd)
    print('**\(^O^)/** Check and run: sbatch parallel_run.sh')
    if KEYWORDS: print("Additional keywords are added:\n", " ".join(KEYWORDS))

if __name__=='__main__':
    chg,mp,t = checkcommand()
    dynamics(chg,mp,t)
                

        
