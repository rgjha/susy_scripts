#!/usr/bin/python
import os
import sys
import glob
import numpy as np
# ------------------------------------------------------------------
# Parse dygraph data files to construct averages and standard errors
# given a thermalization cut and block size
# Assume one ensemble per directory
# Assume Polyakov loop data are properly normalized by Nc

# Parse arguments: first is thermalization cut,
# second is block size (should be larger than autocorrelation time)
# We discard any partial blocks at the end
if len(sys.argv) < 3:
  print "Usage:", str(sys.argv[0]), "<cut> <block>"
  sys.exit(1)
cut = int(sys.argv[1])
block_size = int(sys.argv[2])
# ------------------------------------------------------------------



# ------------------------------------------------------------------
# First make sure we're calling this from the right place
if not os.path.isdir('data'):
  print "ERROR: data/ does not exist"
  sys.exit(1)

# Check that we actually have data to average
# and convert thermalization cut from MDTU to trajectory number
MDTUfile = 'data/TU.csv'
sav = 0
good = -1
for line in open(MDTUfile):
  if line.startswith('t'):
    continue
  temp = line.split(',')
  if float(temp[1]) > cut:
    good = 1
    t_cut = sav
    break
  sav = float(temp[0])

# Guess whether we should also convert the block size
# from MDTU to trajectory number
# They differ when tau=2 trajectories are used...
t_block = block_size
if t_cut < float(cut) / 1.5:
  t_block /= 2

final_MDTU = float(temp[1])
if good == -1:
  print "Error: no data to analyze",
  print "since cut=%d but we only have %d MDTU" % (cut, final_MDTU)
  sys.exit(1)
# ------------------------------------------------------------------



# ------------------------------------------------------------------
# Plaquette is special -- average two data per line
count = 0
ave = 0.          # Accumulate within each block
datList = []
begin = cut       # Where each block begins, to be incremented
plaqfile = 'data/plaq.csv'
for line in open(plaqfile):
  if line.startswith('M'):
    continue
  temp = line.split(',')
  MDTU = float(temp[0])
  if MDTU <= cut:
    continue
  elif MDTU > begin and MDTU < (begin + block_size):
    ave += (float(temp[1]) + float(temp[2])) / 2.0
    count += 1
  elif MDTU >= (begin + block_size):  # Move on to next block
    datList.append(ave / count)
    begin += block_size
    count = 1                     # Next block begins with this line
    ave = (float(temp[1]) + float(temp[2])) / 2.0

# Now print mean and standard error, assuming N>1
dat = np.array(datList)
N = np.size(dat)
if N == 0:
  print "WARNING: No", obs, "data"
else:
  ave = np.mean(dat, dtype = np.float64)
  err = np.std(dat, dtype = np.float64) / np.sqrt(N - 1)
  outfilename = 'results/plaq.dat'
  outfile = open(outfilename, 'w')
  print >> outfile, "%.8g %.4g # %d" % (ave, err, N)
  outfile.close()
# ------------------------------------------------------------------



# ------------------------------------------------------------------
# For the Polyakov loop, bosonic action, fermion action, average link,
# and monopole world line density
# we're interested in the first datum on each line
# For the Polyakov loop, this is the (Nc-normalized) modulus
for obs in ['poly_mod', 'SB', 'SF', 'Flink', 'mono']:
  count = 0
  ave = 0.          # Accumulate within each block
  datList = []
  begin = cut       # Where each block begins, to be incremented
  obsfile = 'data/' + obs + '.csv'
  for line in open(obsfile):
    if line.startswith('M'):
      continue
    temp = line.split(',')
    MDTU = float(temp[0])
    if MDTU <= cut:
      continue
    elif MDTU > begin and MDTU < (begin + block_size):
      ave += float(temp[1])
      count += 1
    elif MDTU >= (begin + block_size):  # Move on to next block
      if count == 0:
        print "ERROR: no %s data to average at %d MDTU" % (obs, int(MDTU))
        sys.exit(1)
      datList.append(ave / count)
      begin += block_size
      count = 1                         # Next block begins here
      ave = float(temp[1])

  # Now print mean and standard error, assuming N>1
  dat = np.array(datList)
  N = np.size(dat)
  if N == 0:
    print "WARNING: No", obs, "data"
    continue
  ave = np.mean(dat, dtype = np.float64)
  err = np.std(dat, dtype = np.float64) / np.sqrt(N - 1.0)
  outfilename = 'results/' + obs + '.dat'
  outfile = open(outfilename, 'w')
  print >> outfile, "%.8g %.4g # %d" % (ave, err, N)
  outfile.close()
# ------------------------------------------------------------------



# ------------------------------------------------------------------
# For the core-minutes per MDTU
# we're again interested in the first datum on each line
# but have to work in terms of trajectories rather than MDTU
for obs in ['wallTU', 'cg_iters', 'accP']:
  count = 0
  ave = 0.          # Accumulate within each block
  datList = []
  begin = t_cut     # Where each block begins, to be incremented
  obsfile = 'data/' + obs + '.csv'
  for line in open(obsfile):
    if line.startswith('M') or line.startswith('t'):
      continue
    temp = line.split(',')
    traj = float(temp[0])
    if traj <= t_cut:
      continue
    elif traj > begin and traj < (begin + t_block):
      ave += float(temp[1])
      count += 1
    elif traj >= (begin + t_block):     # Move on to next block
      if count == 0:
        print "ERROR: no %s data to average at %d traj" % (obs, int(traj))
        sys.exit(1)
      datList.append(ave / count)
      begin += t_block
      count = 1                         # Next block begins here
      ave = float(temp[1])

  # Now print mean and standard error, assuming N>1
  dat = np.array(datList)
  N = np.size(dat)
  if N == 0:
    print "WARNING: No", obs, "data"
    continue
  ave = np.mean(dat, dtype = np.float64)
  err = np.std(dat, dtype = np.float64) / np.sqrt(N - 1.0)
  outfilename = 'results/' + obs + '.dat'
  outfile = open(outfilename, 'w')
  print >> outfile, "%.8g %.4g # %d" % (ave, err, N)
  outfile.close()
# ------------------------------------------------------------------



# ------------------------------------------------------------------
# For the plaquette determinant and the susceptibilities
# we're interested in all three data on each line
# For the determinant these should be |det-1|^2, 1-Re(det) and Im(det)
# For the susceptibilities: plaq, Re(det) and Im(det)
for obs in ['det', 'suscept']:
  count = 0
  ave = [0.0, 0.0, 0.0]       # Accumulate within each block
  datList = [[], [], []]
  begin = cut       # Where each block begins, to be incremented
  obsfile = 'data/' + obs + '.csv'
  for line in open(obsfile):
    if line.startswith('M'):
      continue
    temp = line.split(',')
    MDTU = float(temp[0])
    if MDTU <= cut:
      continue
    elif MDTU > begin and MDTU < (begin + block_size):
      ave[0] += float(temp[1])
      ave[1] += float(temp[2])
      ave[2] += float(temp[3])
      count += 1
    elif MDTU >= (begin + block_size):  # Move on to next block
      if count == 0:
        print "ERROR: no %s data to average at %d MDTU" % (obs, int(MDTU))
        sys.exit(1)
      for i in range(len(ave)):
        datList[i].append(ave[i] / count)
        ave[i] = float(temp[i + 1])     # Next block begins here
      begin += block_size
      count = 1

  # Now print mean and standard error, assuming N>1
  outfilename = 'results/' + obs + '.dat'
  outfile = open(outfilename, 'w')
  for i in range(len(ave)):
    dat = np.array(datList[i])
    N = np.size(dat)
    if N == 0:
      print "WARNING: No", obs, "data"
      continue
    ave[i] = np.mean(dat, dtype = np.float64)
    err = np.std(dat, dtype = np.float64) / np.sqrt(N - 1.0)
    print >> outfile, "%.8g %.4g" % (ave[i], err),
  print >> outfile, "# %d" % N
  outfile.close()
# ------------------------------------------------------------------
