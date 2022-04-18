#!/usr/bin/env python

import os, csv

energyfile = "pm6energy.csv"

def creat_slurm_task():
    lines = ["#!/bin/bash\n",
    "#SBATCH --job-name=kmeans\n",
    "#SBATCH --nodes=1\n",
    "#SBATCH --ntasks-per-node=28\n",
    "#SBATCH --time=0:5:00\n",
    "#SBATCH --mem=64Gb\n",
    "#SBATCH --chdir="+os.getcwd()+"\n",
    "#SBATCH --partition=ilahie\n"
    "#SBATCH --account=ilahie\n\n",
    "# load module for python3 and related packages\n",
    "module load anaconda3_5.3\n\n",
    "~/mopac/geometry_clustering/conformer_selector.py " + energyfile + "\n"
    ]
    with open("submission.sh", "w") as fo:
        fo.writelines(lines)

def check_file_existance():
    if not os.path.exists(energyfile):
        raise SystemExit("Error: %s not exsits!" % energyfile)
    exists = True
    with open(energyfile, "r") as fo:
        csv_reader = csv.reader(fo)
        line_cnt = 0
        for line in csv_reader:
            if line_cnt > 0:
                if not os.path.exists(line[0]):
                    exists = False
                    print("Error: %s not exits" % line[0])
            line_cnt += 1
    return exists

def main():
    if not check_file_existance():
        return
    creat_slurm_task()
    print("Please submit the submission.sh!")

if __name__ == "__main__":
    main()
