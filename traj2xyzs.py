#!/usr/bin/env python
'''
 AUTHOR: Yue Liu
 EMAIL: yueliu96@uw.edu
 Created: 12/04/2018
 Usage: python traj2xyz.py N
For all child directories in the working directory, it will find trajectory_anneal.xyz file to extract the 1st struct for every N structures.
If N=100 and it has 20,000 cycles in the trajectory_anneal.xyz, you will get 20,000/100=200 structures
'''

import sys,os,glob
TARGET = 'trajectory_anneal.xyz'
 
def checkcommand():
    if len(sys.argv)==2:
        try:
            return int(sys.argv[1])
        except:
            raise SystemExit('~T^T~ Invalid Input: %s' % sys.argv[1])
    else:
        raise SystemExit(' python traj2xyz.py N\nN=10: 20 snapshots out of 200 are extracted from trajectory.')

def readtraj(d,stride):
    name = os.path.basename(d)
    newd = name+'_snapshots'
    if os.path.exists(newd):
        print("Warning: %s Exists. Remove and try it again!" % newd)
        return
    os.mkdir(newd)
    fl = d+'/'+TARGET
    with open(fl,'r') as fo:
        lines = fo.readlines()
    natom = int(lines[0].strip())
    ncycle = len(lines)//(natom+2)
    n = ncycle//stride
    name = name[1:] if name[0]=='d' else name
    for i in range(n):
        snap = lines[i*stride*(natom+2):(i*stride+1)*(natom+2)]
        flname = newd + '/' + name + '_snap' + str(i+1) + '.xyz'
        convert2xyz(snap,flname)
    print(' ^_^ %s cycles in %s -->  %s *snap*xyz files in %s folder!' % (ncycle,fl,n,newd))

def convert2xyz(lss,flname):
    lxyz = [lss[0].strip()+'\n','\n']
    for ss in lss[2:]:
        ssp = ss.split()
        xyz = '%-4s%16s%16s%16s' % (ssp[0],ssp[1],ssp[2],ssp[3])
        lxyz.append(xyz+'\n')
    with open(flname,'w') as fo:
        fo.writelines(lxyz)

def traj2xyz(n):
    allfd = os.listdir('.')
    alldirs = [x for x in allfd if os.path.isdir(x) and os.path.exists(x+'/'+TARGET)]
    alldirs.sort(key=lambda x: (len(x),x))
    if TARGET in allfd:
        alldirs.append(os.getcwd())
    if len(alldirs)==0:
        raise SystemExit('Error: Not found %s in the current or direct sub- directory' % TARGET)
    for everydir in alldirs:
        readtraj(everydir,n)
    print('**\(^O^)/** Please check all snap files in the above folders!')

if __name__=='__main__':
    stride = checkcommand()
    traj2xyz(stride)
    
