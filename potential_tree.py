#!/usr/bin/python
import sys
import time
import numpy as np
# ------------------------------------------------------------------
# Print r_I (as defined in notes)
# corresponding to input integer displacement three-vector
# Use finite-volume discrete Fourier transform

# Parse arguments: Three-component integer vector and L
if len(sys.argv) < 5:
  print "Usage:", str(sys.argv[0]), "<n_x> <n_y> <n_z> <L>"
  sys.exit(1)
n_x = int(sys.argv[1])
n_y = int(sys.argv[2])
n_z = int(sys.argv[3])
L = int(sys.argv[4])
runtime = -time.time()

# Summation range will be -L / 2 + 1, ..., L / 2 inclusive
if not L % 2 == 0:
  print "Error: Need even L rather than", L
  sys.exit(1)
low  = 1 - L / 2
high = L / 2 + 1    # Account for range() dropping upper limit

# For later convenience
invSqrt2  = 1.0 / np.sqrt(2.0)
invSqrt6  = 1.0 / np.sqrt(6.0)
invSqrt12 = 1.0 / np.sqrt(12.0)
twopiOvL  = 2.0 * np.pi / float(L)

# Convert n_i to r_i (uses usual ehat basis)
tag = [n_x - n_y, n_x + n_y - 2 * n_z, n_x + n_y + n_z]
print "tag: %d, %d, %d" % (tag[0], tag[1], tag[2])
r = [tag[0] * invSqrt2, tag[1] * invSqrt6, tag[2] * invSqrt12]
mag = np.sqrt(np.dot(r, r))
print "|r| = %.4g" % mag
# ------------------------------------------------------------------



# ------------------------------------------------------------------
# Integrate over (p1, p2, p3), each from 0 to L-1,
# except for (0, 0, 0), which is treated separately
# Be lazy and re-compute (almost) everything within the lowest-level loop
one_ov_rI = 0.0 + 0.0j
for p1 in range(low, high):
  for p2 in range(low, high):
    for p3 in range(low, high):
      # Omit zero-mode contribution
      # TODO: Separate analytical computation possible?
      if p1 == 0 and p2 == 0 and p3 == 0:
        continue

      # Convert p_i to k_i using ghat basis
      # Pattern is same as tag above, but now have overall twopiOvL factor
      k = np.empty((3), dtype = np.float)
      k[0] = twopiOvL * (p1 - p2) * invSqrt2
      k[1] = twopiOvL * (p1 + p2 - 2.0 * p3) * invSqrt6
      k[2] = twopiOvL * (p1 + p2 + p3) * invSqrt12

      khat_mu = 2.0 * np.sin(0.5 * k)
      khatSq = (khat_mu**2).sum()

      # Sum \prod_i cos(r_i k_i) / khatSq
      num = np.exp(1.0j * np.dot(r, k))
      one_ov_rI += num / khatSq
#      print "%d %d %d --> %.4g / %.4g = %.4g" \
#            % (p1, p2, p3, num, khatSq, num / khatSq)

# Constant overall factor of 4pi / L^3,
# plus factor of 1/2 for determinant squared times trace normalization
one_ov_rI *= 2.0 * np.pi / float(L**3)

# Print along with r_I itself
rI = 1.0 / (one_ov_rI)
print "(%.4g, %.4g) --> (%.4g, %.4g)" \
      % (one_ov_rI.real, one_ov_rI.imag, rI.real, rI.imag)

runtime += time.time()
print("Runtime: %0.1f seconds" % runtime)
# ------------------------------------------------------------------