#!/usr/bin/python
import os
import sys
import glob
import numpy as np
# ------------------------------------------------------------------
# Print blocked Konishi and SUGRA correlator averages
# with blocked standard errors

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

# Extract Nt from first output file
firstfile = 'Out/' + tag + '.' + str(cfgs[0])
if not os.path.isfile(firstfile):
  print "ERROR:", firstfile, "does not exist"
  sys.exit(1)
for line in open(firstfile):
  if line.startswith('nt'):
    Nt = int((line.split())[1])
    break

# We exploit t <--> Nt - t symmetry
# To only print 0 through Nt / 2 (a total of Npts points)
Npts = Nt / 2 + 1  # Assume Nt is even
# ------------------------------------------------------------------



# ------------------------------------------------------------------
# Construct arrays of blocked measurements for each correlator
# For now just average over all 25 SUGRA components
# K = Konishi, S = SUGRA
Kdat = [[] for x in range(Npts)]
Sdat = [[] for x in range(Npts)]

# Monitor block lengths, starting and ending MDTU
block_data = [[], [], []]
count = 0         # How many measurements in each block
begin = cut       # Where each block begins, to be incremented

# Accumulators
tK = [0 for x in range(Npts)]
tS = [0 for x in range(Npts)]
for MDTU in cfgs:
  # If we're done with this block, record it and reset for the next
  if MDTU >= (begin + block_size):
    for t in range(Npts):
      Kdat[t].append(tK[t] / float(count))
      Sdat[t].append(tS[t] / float(25. * count))  # Average over all
    # Record and reset block data
    block_data[0].append(count)
    count = 0
    block_data[1].append(begin)
    begin += block_size
    block_data[2].append(begin)
    tK = [0 for x in range(Npts)]
    tS = [0 for x in range(Npts)]

  # Running averages
  filename = 'Out/' + tag + '.' + str(MDTU)
  toOpen = glob.glob(filename)
  if len(toOpen) > 1:
    print "ERROR: multiple files named %s:" % filename,
    print toOpen
  for line in open(toOpen[0]):
    # Format: KONISHI t dat
    if line.startswith('KONISHI '):
      temp = line.split()
      time = int(temp[1])
      if time == 0:
        count += 1    # Only increment once per measurement!
      dat = float(temp[2])
      tK[time] += dat
    # Format: SUGRA a b t dat
    elif line.startswith('SUGRA '):
      temp = line.split()
      time = int(temp[3])
      dat = float(temp[4])
      tS[time] += dat

# Check special case that last block is full
# Assume last few measurements are equally spaced
if cfgs[-1] >= (begin + block_size - cfgs[-1] + cfgs[-2]):
  for t in range(Npts):
    Kdat[t].append(tK[t] / float(count))
    Sdat[t].append(tS[t] / float(25. * count))  # Average over all
  # Record block data
  block_data[0].append(count)
  block_data[1].append(begin)
  block_data[2].append(begin + block_size)

Nblocks = len(Kdat[0])
# ------------------------------------------------------------------



# ------------------------------------------------------------------
# Now print mean and standard error, requiring N>1
if Nblocks == 1:
  print "ERROR: need multiple blocks to take average"
  sys.exit(1)

print "Averaging with %d blocks of length %d MDTU" % (Nblocks, block_size)
Kfile = open('results/konishi.dat', 'w')
print >> Kfile, "# Averaging with %d blocks of length %d MDTU" % (Nblocks, block_size)
Sfile = open('results/sugra.dat', 'w')
print >> Sfile, "# Averaging with %d blocks of length %d MDTU" % (Nblocks, block_size)
for t in range(Npts):
  # Konishi
  dat = np.array(Kdat[t])
  ave = np.mean(dat, dtype = np.float64)
  err = np.std(dat, dtype = np.float64) / np.sqrt(Nblocks - 1.)
  print >> Kfile, "%d %.6g %.4g # %d" % (t, ave, err, Nblocks)

  # SUGRA
  dat = np.array(Sdat[t])
  ave = np.mean(dat, dtype = np.float64)
  err = np.std(dat, dtype = np.float64) / np.sqrt(Nblocks - 1.)
  print >> Sfile, "%d %.6g %.4g # %d" % (t, ave, err, Nblocks)

# More detailed block information
#for i in range(Nblocks):
#  for outfile in [Kfile, Sfile]:
#    print >> outfile, \
#          "# Block %2d has %d measurements from MDTU in [%d, %d)" \
#          % (i + 1, block_data[0][i], block_data[1][i], block_data[2][i])
Kfile.close()
Sfile.close()
# ------------------------------------------------------------------
