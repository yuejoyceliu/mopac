# MOPAC
[Mopac](http://openmopac.net/Manual/index.html) is a general-purpose semiempirical molecular orbital package for the study of solid state and molecular structures and reactions. Several semiempirical methods are used to calculate electronic part, among which we usually choose PM6 method to run geometry optimization and BOMD. Just like other computational software packages, Mopac works in 3 steps: create a data file which describes molecular system and specifies job types; command Mopac to carry out the calcualtion with that data-file (on Hyak node); extract the desired result from the output-file.

# Input Setup

[Cuby](http://cuby4.molecular.cz) provides an unified access to various computational methods available in different software packages, including gaussian, mopac, turbomole, etc. It is a computational chemistry framework written in ruby, which does very little for itself, but calls external softwares to do the calculations and works with their results. To work with cuby, two input files are needed: xyz file and yaml file. 

## xyz-file

xyz file contains the geometry of the molecule system -- the first line is the number of atoms, the second line is the comment line (could be blank) and the remaining lines are atoms Cartesian coordinates. Take $H_2O$ as an example:

  ```
  3

  O                 -0.54954964    0.83729475    0.01780404
  H                 -0.87000423    1.74223058    0.01780404
  H                  0.41045036    0.83729475    0.01780404
  ```

 Common input files we use are gaussian input files. The script, [gjfcom2xyz.py](https://raw.githubusercontent.com/yueliu96/scripts_for_lab/master/gjfcom2xyz.py) can convert the input file from gaussian input format to xyz format. 

- *Usage*
  - `python gjfcom2xyz.py input-file`
- *Descriptions*
  - use charge and multiplicity (chg&mp) as a key to locate the start of coordinates
  - every lines containing 4 elements after chg&mp is considered as coordinate line. Valid delimiters: space, spaces and comma.

python script [xyz2gjf.py](https://raw.githubusercontent.com/yueliu96/scripts_for_lab/master/xyz2gjf.py) can convert xyz format back to gaussian input format.

- *Usage*
  - `python xyz2gjf.py xyz-file`
- *Descriptions*
  - every line after the second line contains 4 elements and the last three elements are float is considered as coordinate line. Valid delimiters are space or spaces.
  - route card, charge and multiplicity are defined by default, could be changed later or modified in the scripts.

## yaml-file

yaml file is a list of keywords, which is the bridge to connect cuby with computational softwares. The format is `keyword: option` and there must be a space after colon (:).

### optimize-yaml

*Example--inp.yaml*:

```yaml
job: optimize
geometry: test.xyz
charge: 2
multiplicity: 1
interface: mopac
method: pm6
spin_restricted: auto_uhf
maxcycles: 2000
print: timing
mopac_precise: yes
mopac_peptide_bond_fix: yes
modifiers: dispersion3, h_bonds4
modifier_h_bonds:
  h_bonds4_scale_charged: no
  h_bonds4_extra_scaling: {}
```

*Explanations*:
- job: optimize
  - simple geometry optimization of molecule specified in test.xyz file
  - the calculation produces these additional files:
    - optimized.xyz - the optimized geometry
    - history_inp.xyz - record of all the steps
- spin_restricted: auto_uhf
  - uhf for any open-shell systems, rhf is used for closed shells
- maxcycles: 2000
  - maximum number of cycles of optimization or molecular dynamics
- print: timing
  - print time spent in the program
- [mopac_precise](http://openmopac.net/manual/precise.html): yes
  - use tight thresholds, needed for accurate gradient
- [mopac_peptide_bond_fix](http://openmopac.net/manual/mmok.html): yes
  - controls the corerction for peptide bond torsion
- modifiers
  - a list of interfaces applied as a modifiers to this calculations.

### dynamics-yaml

*Example--anneal.yaml*:

```yaml
job: dynamics
geometry: test.xyz
charge: 2
multiplicity: 1
spin_restricted: auto_uhf
interface: mopac
method: pm6
mopac_precise: yes
mopac_peptide_bond_fix: yes
modifiers: dispersion3, h_bonds4
modifier_h_bonds:
  h_bonds4_scale_charged: no
  h_bonds4_extra_scaling: {}
maxcycles: 20000
timestep: 0.001
init_temp: 310
temperature: 310
thermostat: berendsen
thermostat_tc: 0.05
```

*Explanations*:
- job: dynamics
  - molecular dynamics simulation of molecule specified in test.xyz file
  - the calculation produces these additional files:
    - last.xyz - the last geometry
    - trajectory_test.xyz - record of all the cycles (20000 here)
    - LOG - standard output and error information for every cycle
- maxcycles: 20000
  - 20 ps of MD simulation (the default step is 1 fs)
- init_temp: 310
  - temperature (K) used to generate initial random velocities
- temperature: 310
  - temperature (K) to be maintained by the thermostat
- thermostat: berendsen
  - selection of thermostat algorithm
- thermostat_tc: 0.05
  - Thermostat time constant (ps) setting strength of the coupling to the thermostat. The exact mening of the value is different in different algorithms.

*Note*:
- add `scf_cycles: 1000` for open-shell system to define the maximum number of SCF iterations

### Other Keywords
- `md_region: ""` & `trajectory_selection: ""`
  - ex: md_region: "1-19,22-100", trajectory_selection: "1-100": means load atoms from 1-100 and fix atoms 20-21
- `job_cleanup: yes | no`
  - delete directories with external calculations when job finishes successfuly, default is yes
- `mopac_keywords: ""`
  - extra keywords (in the MOPAC format) added into the input
  - add keyword "camp" if job fails with not self-consistency
- `scf_convergence: 7`
  - change SCF convergence threshold (energy): set to $10^{-7}$ a.u.
- click [here](http://cuby4.molecular.cz/keywords.html) to see more

# Submit to Hyak

Besides xyz and yaml (test.yaml) files, sbatch file (test.sh) also needed:

```bash
#!/bin/bash
#SBATCH --job-name=???
#SBATCH --nodes=1
#SBATCH --time=??:00:00
#SBATCH --mem=???GB
#SBATCH --workdir=????????????
#SBATCH --partition=???
#SBATCH --account=???

module load contrib/mopac16
source /usr/lusers/yueliu96/.rvm/scripts/rvm
ldd /sw/contrib/cuby4/cuby4/classes/algebra/algebra_c.so > ldd.log
cuby4 test.yaml &>LOG    
## results and error information will be written to file LOG
## cuby4 test.yaml: same information will be written to slurm file
```
run `sbatch test.sh` to submit it.

## Parallel-Run

Most nodes on hyak.mox have 28 processors, however, the code in MOPAC only allows a single processor to be used for a single calculation. If several calculations to be run, each calculation could be started on a different processor in one node.

```bash
#!/bin/bash
#SBATCH --job-name=??????
#SBATCH --nodes=1
#SBATCH --time=??:00:00
#SBATCH --mem=???G
#SBATCH --workdir=??????
#SBATCH --partition=???
#SBATCH --account=???

module load parallel-20170722
module load contrib/mopac16
source /usr/lusers/yueliu96/.rvm/scripts/rvm
ldd /sw/contrib/cuby4/cuby4/classes/algebra/algebra_c.so > ldd.log
cat tasklists.sh | parallel -j 28
```
where, tasklists$.$sh is :

```bash
cd absolute-directory-1; cuby4 test.yaml &>LOG
cd absolute-directory-2; cuby4 test.yaml &>LOG
......
```

there should exist xyz and yaml files in every absolute directory.

## Scripts for Parallel-Run
- [pm6opt_parallel.py](https://raw.githubusercontent.com/yueliu96/scripts_for_lab/master/pm6opt_parallel.py)
- [pm6bomd_parallel.py](https://raw.githubusercontent.com/yueliu96/scripts_for_lab/master/pm6bomd_parallel.py)
  
To run pm6-optimize or pm6-BOMD for several different molecules, create their xyz files in the working directory:

```
test1.xyz test2.xyz test3.xyz
```

and then run `python pm6opt_parallel.py` or `python pm6bomd_parallel.py`. Then, tasklists$.$sh file, parallel_run$.$sh file and sub-directories for every xyz file will be created. In every xyz sub-folder, xyz and yaml files are created correspondingly:

```
dtest1  dtest2 dtest3 taskslists.sh parallel_run.sh
```

in `dtest1`: `test1.xyz inp.yaml` if it is opt job; `test1.xyz anneal.yaml` if it is dynamics job.

# Output Analysis

## opt output

Optimization job produces optimized.xyz and histotry_xxx.xyz (xxx depends on the name of yaml file). The optimized.xyz is the optimized geometry in xyz formatted, where energy value is on the second line.

In the parallel-run case, one directory has several subdirectories containing finished optimized job (optimized.xyz), python script [extract_pm6opt.py](https://raw.githubusercontent.com/yueliu96/scripts_for_lab/master/extract_pm6opt.py) can be used to extract optimized geometry and energy.

- *Usage*:
  - `python extract_pm6opt.py`
  - run in the directory containing these subdirectories
- *Descriptions*:
  - read optimized.xyz in all subdirectories whose name starts with 'd', change their format from xyz to gaussian input and extract energies from these xyz files
  - all new files are written to a new directory optresult
  - the name of the structures and the gaussian input files depends on these subdirectories -- *test* if *dtest*

## dynamics output 

Dynamics job creates additional file trajectory_*.xyz containing geometry information of all steps, which can be visualized by [VMD](https://www.ks.uiuc.edu/Research/vmd/) software. The user can extract specific snapshots from the trajcetroy according to the stepsize set by VMD. Or use the python script [traj2xyz.py](https://raw.githubusercontent.com/yueliu96/scripts_for_lab/master/traj2xyzs.py) to achieve the same goal as VMD extractor.

- *Usage*:
  - `python traj2xyz.py stride`
  - stride must be an integer
  - stride=100: 200 snapshots out of 200000 will be extracted from trajectory
  - run in the directory containing child-directory where trajectory_*.xyz locates
- *Descriptions*:
  - go through all subdirectories to locate trajectory_*.xyz, extract an exact number of geometries from trajectory and wirtten them to new subdirectories correspondingly
  - the name of new subdirectories and snapshots are based on the name of subdirectories
  - if originally `dtesta dtestb`, then after run this script: `dtesta dtesta_snapshots dtestb dtestb_snapshots`; in `dtesta_snapshots`: `testa_snap1.xyz testa_snap2.xyz ...`
