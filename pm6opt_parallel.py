#!/usr/bin/env python

'''
Usage: python pm6opt_parallel.py charge multiplicity
find all xyz files in the working directory and make directories and inp.yaml for every one.
generate tasklists.sh file and parallel_run.sh file
after finishing, run 'sbatch parallel_run.sh'
'''

import glob,os,sys

nCORES = 28
YAML = 'inp.yaml'
KEYWORDS = ''
#KEYWORDS = 'optimize_region: "1-59,61-64"\n'
#KEYWORDS = 'mopac_keywords: "camp"\n'

def checkcommand():
    n = len(glob.glob('*.xyz'))
    if n == 0:
        raise SystemExit(':::>_<:::No xyz Files Found!')
    if len(sys.argv) == 3:
        return int(sys.argv[1]),int(sys.argv[2])
    else:
        raise SystemExit('Usage: python pm6opt_parallel.py charge multiplicty')

def mypathexist(dirs):
    for d in dirs:
        if os.path.exists(d):
            raise SystemExit(':::>_<:::%s Exists! Remove it and try again!' % d)

def yaml(fl,outfl,chg,mp):
    p1 = ['job: optimize\n','geometry: '+fl+'\n']
    p2 = ['interface: mopac\n','method: pm6\n','spin_restricted: auto_uhf\n','maxcycles: 2000\n','print: timing\n','mopac_precise: yes\n','mopac_peptide_bond_fix: yes\n','modifiers: dispersion3, h_bonds4\n','modifier_h_bonds:\n','  h_bonds4_scale_charged: no\n','  h_bonds4_extra_scaling: {}\n']
    with open(outfl,'w') as fo:
        fo.writelines(p1)
        fo.write('charge: '+str(chg)+'\n')                                          
        fo.write('multiplicity: '+str(mp)+'\n')    
        fo.writelines(p2)
        if KEYWORDS: fo.write(KEYWORDS)

def tasklists_sh(alldirs,mydir):
    lines = []
    for dd in alldirs:
        line = 'cd '+mydir+'/'+dd+'; cuby4 '+YAML+' &>LOG\n'
        lines.append(line)
    with open('tasklists.sh','w') as fo:
        fo.writelines(lines)

def parallelrun_sh(ntasks,user,mydir):
    p1 = '#!/bin/bash\n#SBATCH --job-name=pm6opt\n#SBATCH --nodes=1\n#SBATCH --ntasks-per-node='+str(nCORES)+'\n#SBATCH --time=2:00:00\n#SBATCH --mem=110G\n'
    p2 = '#SBATCH --chdir='+mydir+'\n'
    p3 = '#SBATCH --partition=ilahie\n#SBATCH --account=ilahie\n\n'
    p4 = 'module load parallel-20170722\nmodule load contrib/mopac16\n'
    p5 = 'source /usr/lusers/'+user+'/.rvm/scripts/rvm\n'
    p6 = 'ldd /sw/contrib/cuby4/cuby4/classes/algebra/algebra_c.so > ldd.log\n'
    p7 = 'cat tasklists.sh | parallel -j '+str(min(ntasks,nCORES))+'\n'
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

def opt(charge,mtplct):
    xyzfiles = glob.glob('*.xyz')
    xyzfiles.sort()
    xyzdirs = ['d'+d[:-4] for d in xyzfiles]
    mypathexist(xyzdirs)
    nxyz = len(xyzfiles)
    for i in range(nxyz):
        fxyz = xyzfiles[i]
        dxyz = xyzdirs[i]
        os.mkdir(dxyz)
        yamlname = dxyz+'/'+YAML
        yaml(fxyz,yamlname,charge,mtplct)
        os.rename(fxyz,dxyz+'/'+fxyz)
    pwd = os.getcwd()
    who = os.getlogin()
    tasklists_sh(xyzdirs,pwd)
    parallelrun_sh(nxyz,who,pwd)
    if KEYWORDS: print("ADD:", KEYWORDS)
    print('**\(^O^)/**%s tasks found! check and run:\n sbatch parallel_run.sh' % nxyz) 

if __name__=='__main__':
    chg,mp = checkcommand()
    opt(chg,mp)
                

        
