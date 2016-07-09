#!/usr/bin/python
from __future__ import print_function     # For vegas
import sys
import time
from numpy import sqrt, sin, exp, pi, dot
import vegas
# ------------------------------------------------------------------
# Print r_I (as defined in notes)
# corresponding to input integer displacement four-vector
# Use vegas to numerically calculate the infinite-volume Fourier transform

# Parse arguments: Four-component integer vector
# and number of evaluations in vegas calculation
if len(sys.argv) < 6:
  print("Usage:", str(sys.argv[0]), "<n_x> <n_y> <n_z> <n_t> <Neval>")
  sys.exit(1)
n_x = int(sys.argv[1])
n_y = int(sys.argv[2])
n_z = int(sys.argv[3])
n_t = int(sys.argv[4])
Neval = int(sys.argv[5])
Nwarm = int(Neval / 10)
runtime = -time.time()

# For later convenience
twopi = 2.0 * pi

# Print naive |r|
mag = sqrt(n_x * n_x + n_y * n_y + n_z * n_z + n_t * n_t)
print("|r| = %.4g" % mag)

# Function to integrate -- can only handle real part of exp
# Also can take the square root since negative evaluations seem possible
# Integrating over dp = dk / (2pi) removes 2pi factors from measure
# Use standard Tr[T^A T^B] = 0.5\de^{AB} trace normalization...
def f(p):
  k = twopi * p
  num = exp(1.0j * (n_x * k[0] + n_y * k[1] + n_z * k[2] + n_t * k[3]))
  denom = (sin(0.5 * k[0]))**2 + (sin(0.5 * k[1]))**2 \
        + (sin(0.5 * k[2]))**2 + (sin(0.5 * k[3]))**2
  return pi * pi * num.real / denom

integ = vegas.Integrator([[-0.5, 0.5], [-0.5, 0.5], [-0.5, 0.5], [-0.5, 0.5]])
integ(f, nitn=7, neval=Nwarm)             # Initial adaptation
result = integ(f, nitn=20, neval=Neval)   # Actual estimation

#print(result.summary())
print("result = %s    Q = %.2f" % (result, result.Q))

# Print r_I itself with propagated uncertainty
#   delta(1 / sqrt(r)) = delta(r) / 2r^(3 / 2)
# Some shenanigans necessary to get numerical results out of vegas class
temp = str(result).split('(')
val = 1.0 / sqrt(float(temp[0]))
err = float(((temp[1]).split(')'))[0])
for i in range(len(temp[0]) - 2):   # Restore leading zeroes to error
  err *= 0.1
print("--> r_I = %.8g %.4g" % (val, 0.5 * err * val**3))

runtime += time.time()
print("Runtime: %0.1f seconds" % runtime)
# ------------------------------------------------------------------
