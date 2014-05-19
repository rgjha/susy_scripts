#!/usr/bin/python
import os
import sys
import glob
import numpy as np
# ------------------------------------------------------------------
# Compute SUGRA correlator effective masses, using a blocked jackknife

# Parse arguments: first is thermalization cut,
# second is block size (should be larger than autocorrelation time)
# We discard any partial blocks at the end
# Third argument tells us whether to analyze "corr" or "stout" files
if len(sys.argv) < 4:
  print "Usage:", str(sys.argv[0]), "<cut> <block> <tag>"
  sys.exit(1)
cut = int(sys.argv[1])
block_size = int(sys.argv[2])
tag = str(sys.argv[3])
# ------------------------------------------------------------------



# ------------------------------------------------------------------
# First make sure we're calling this from the right place
if not os.path.isdir('Out'):
  print "ERROR: Out/ does not exist"
  sys.exit(1)

# Construct list of which configurations have been analyzed
cfgs = []
files = 'Out/' + tag + '.*'
for filename in glob.glob(files):
  cfg = int(filename.split('.')[-1])    # Number after last .
  if cfg not in cfgs and cfg > cut:
    cfgs.append(cfg)
cfgs.sort()

if len(cfgs) == 0:
  print "ERROR: no files", files, "found"
  sys.exit(1)

# If we're missing some initial measurements,
# increase thermalization cut
cut = cfgs[0]

# Extract lattice volume from path
# For now only Nt is used; we assume it is a two-digit number!!!
path = os.getcwd()
if 'Gauge' in path:   # Tom's runs
  temp = path.split('Gauge')
  L = int(temp[1][:1])      # First digit after 'Gauge'
  Nt = int(temp[1][1:3])    # Second and third digits after 'nt'
else:                 # My runs
  temp = path.split('nt')
  L = int((temp[0].split('_'))[-1])     # Everything between '_' and 'nt'
  Nt = int(temp[1][:2])                 # First two digits after 'nt'

# We exploit t <--> Nt - t symmetry
# To only print 0 through Nt / 2 (a total of Npts points)
Npts = Nt / 2 + 1  # Assume Nt is even
# ------------------------------------------------------------------



# ------------------------------------------------------------------
# Construct arrays of blocked measurements for each correlator
# For now just average over all 25 SUGRA components
# This constant factor will cancel out in the effective mass ratio
effm = [[] for x in range(Npts - 1)]

# Monitor block lengths, starting and ending MDTU
block_data = [[], [], []]
count = 0         # How many measurements in each block
begin = cut       # Where each block begins, to be incremented

# Accumulators
tM = [0 for x in range(Npts)]
for MDTU in cfgs:
  # If we're done with this block, record it and reset for the next
  if MDTU >= (begin + block_size):
    for t in range(Npts - 1):
      effm[t].append(np.log(tM[t] / tM[t + 1]))
    # Record and reset block data
    block_data[0].append(count)
    count = 0
    block_data[1].append(begin)
    begin += block_size
    block_data[2].append(begin)
    tM = [0 for x in range(Npts)]

  # Running averages
  filename = 'Out/' + tag + '.' + str(MDTU)
  toOpen = glob.glob(filename)
  if len(toOpen) > 1:
    print "ERROR: multiple files named %s:" % filename,
    print toOpen
  for line in open(toOpen[0]):
    # Format: SUGRA a b t dat
    if line.startswith('SUGRA '):
      temp = line.split()
      time = int(temp[3])
      dat = float(temp[4])
      tM[time] += dat

# Check special case that last block is full
# Assume last few measurements are equally spaced
if cfgs[-1] >= (begin + block_size - cfgs[-1] + cfgs[-2]):
  for t in range(Npts - 1):
    effm[t].append(np.log(tM[t + 1] / tM[t]))
  # Record block data
  block_data[0].append(count)
  block_data[1].append(begin)
  block_data[2].append(begin + block_size)

Nblocks = len(effm[0])
# ------------------------------------------------------------------



# ------------------------------------------------------------------
# Now print mean and standard error, requiring N>1
if Nblocks == 1:
  print "ERROR: need multiple blocks to take average"
  sys.exit(1)

print "Averaging with %d blocks of length %d MDTU" % (Nblocks, block_size)
outfile = open('results/sugra_effm.dat', 'w')
print >> outfile, "# Averaging with %d blocks of length %d MDTU" % (Nblocks, block_size)
for t in range(Npts - 1):
  dat = np.array(effm[t])
  ave = np.mean(dat, dtype = np.float64)
  err = np.std(dat, dtype = np.float64) / np.sqrt(Nblocks - 1.)
  print >> outfile, "%d %.6g %.4g # %d" % (t, ave, err, Nblocks)

# More detailed block information
#for i in range(Nblocks):
#  print >> outfile, \
#        "# Block %2d has %d measurements from MDTU in [%d, %d)" \
#        % (i + 1, block_data[0][i], block_data[1][i], block_data[2][i])
outfile.close()
# ------------------------------------------------------------------
