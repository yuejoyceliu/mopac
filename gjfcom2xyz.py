#!/usr/bin/env python

'''
 AUTHOR: Yue Liu
 EMAIL: yueliu96@uw.edu
 Created on 11/28/2018
 Usage: python gjfcom2xyz.py input-file
 Descriptions:
Use charge and multipicity as a key to locate where to find coordinates.
All lines contain 4 elements after chg and mp are considered as coordinates lines; valid delimter: one or more spaces and the comma
'''
import sys,os,re

def checkcommand(n):
    if n==2:
        infl = sys.argv[1]
        if os.path.isfile(infl):
            return infl,infl.split('.')[0]+'.xyz'
        else:
            raise SystemExit(':::>_<:::%s Not Found!' % infl)
    else:
        raise SystemExit('\npython gjfcom2xyz.py inputfile\n')

def ischgmp(line):
    lss = re.split(r"[,\s\t]\s*\t*", line.strip())
    if len(lss)==2 and lss[0].isdigit() and lss[1].isdigit():
        return True
    else:
        return False

def findstrt(fl):
    keyline = 'check'
    with open(fl,'r') as fo:
        lines = fo.readlines()
    for i in range(len(lines)):
        line = lines[i]
        if ischgmp(line):
            keyline = i+1
            break
    if isinstance(keyline,int):
        return keyline
    else:
        raise SystemExit(':::>_<:::charge and multiplicity not found, %s is not gaussian input file!' % fl)

def isxyz(line):

    def isfloat(x):
        try:
            float(x)
            return True
        except:
            return False

    lss = re.split(r"[,\s\t]\s*\t*", line.strip())
    if len(lss) == 4 and isfloat(lss[1]) and isfloat(lss[2]) and isfloat(lss[3]):
        return True
    return False

def gjfcom2xyz(fl1,fl2):
    strt = findstrt(fl1)
    with open(fl1,'r') as fo:
        lines = fo.readlines()
    newlines = [x for x in lines[strt:] if isxyz(x)]
    natoms = len(newlines)
    with open(fl2,'w') as f2o:
        f2o.write(str(natoms)+'\n')
        f2o.write('\n')
        f2o.writelines(newlines)
    print('**\(^O^)/** %s --> %s: %s atoms found!' % (fl1,fl2,natoms))

if __name__=='__main__':
    gfile,xfile = checkcommand(len(sys.argv))
    gjfcom2xyz(gfile,xfile)
        

