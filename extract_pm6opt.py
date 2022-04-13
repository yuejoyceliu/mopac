#!/usr/bin/env python

#AUTHOR: Yue Liu
#ENAIL: yueliu96@uw.edu
#CREATED: 12/01/2018
# Usage: python extract_pm6opt.py

import os,sys,glob

STRT = ['%mem=100gb\n','%nprocshared=28\n']
#ROUTE = '# opt wb97xd/6-31+g(d,p) pop=min scf=(xqc,tight)\n'
ROUTE = '# opt freq b3lyp/6-31+g(d,p) pop=none scf=(xqc,tight)\n'
TARGET='optimized.xyz'

def readpm6opt(fl):
    with open(fl,'r') as fo:
        lines = fo.readlines()
    natom = lines[0].strip()
    energy = lines[1].split()[1] #+','+lines[1].split()[2]
    xyz = lines[2:]
    if int(natom)!=len(xyz):
        raise SystemExit(':::>_<:::Not Found %s Atoms in %s' %(natom,fl))
    else:
        return energy,xyz

def writecom(nm,pos,xyz,chg,mp):
    with open(pos+'/'+nm+'.com','w') as fo:
        fo.writelines(STRT)
        fo.write('%chk='+nm+'.chk\n')
        fo.write(ROUTE)
        fo.write('\n')
        fo.write('Complex '+nm+'\n')
        fo.write('\n')
        fo.write(str(chg)+' '+str(mp)+'\n')
        fo.writelines(xyz)
        fo.write('\n') 

def myformat(s):
    return '{0:<30}'.format(s)

def writeE(pos,t_E):
    with open(pos+'/pm6energy.txt','w') as fo:
        for t in t_E:
            tt = t.strip().split(',')
            #fo.writelines(list(map(myformat,tt)))
            fo.writelines("\t".join(tt))
            fo.write('\n')                
    with open(pos+'/pm6energy.csv','w') as fo:
        fo.write('struct,energy/(kcal/mol)\n')
        fo.writelines(t_E)
             
def chgmp(folder):
    fl = glob.glob(folder+'/*yaml')[0]
    chg,mp = False,False
    with open(fl,'r') as fo:
        line = fo.readline()
        while line and (isinstance(chg,bool) or isinstance(mp,bool)):
            if line.startswith('charge:'):
                chg = line.split()[-1]
            elif line.startswith('multiplicity:'):
                mp = line.split()[-1]
            line = fo.readline()
    return chg,mp

def extract():
    allfd = os.listdir('.')
    alldirs = [x for x in allfd if os.path.isdir(x) and x.startswith('d')]
    alldirs.sort(key=lambda x: (len(x),x))
    newdir = 'optresult'
    if os.path.exists(newdir):
        raise SystemExit('~T^T~ %s Exists! Remove it and try again!' % newdir)
    else:
        os.mkdir(newdir)
    chg,mp = chgmp(alldirs[0])
    E=[]    
    for dd in alldirs:
        try:
            optxyz = dd+'/'+TARGET
            struct = dd[1:]
            t_E,t_xyz = readpm6opt(optxyz)
            writecom(struct,newdir,t_xyz,chg,mp)
            E.append(dd[1:]+','+t_E+'\n')
        except BaseException as err:
            length = 40+len(optxyz)
            print('WARNING'.center(length,'-'))
            print(err)
            print('-'*length)
    if bool(E):
        writeE(newdir,E)
        chdir(newdir)
        print('**\(^O^)/** %d %s Found! Check folder %s!' % (len(E),TARGET,newdir))
        print('Default Route, Charge and Multiplicity:\n %s %s %s' % (ROUTE,chg,mp))
    else:
        os.rmdir(newdir)
        print('~T^T~Too Bad! Not find any pm6opt jobs (%s)!' % TARGET)
        
def chdir(d):
    with open(d+'/chdir.sh', "w") as fo:
        fo.write("echo '#SBATCH --chdir='$(pwd) > temp;\ncp ~/yang/* .;\n sed -i '7d' submission_python.sh;\nsed -i '6rtemp' submission_python.sh;")
    

if __name__=='__main__':
    extract() 
