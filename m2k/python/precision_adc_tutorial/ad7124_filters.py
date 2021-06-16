# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------
# Copyright (c) 2015-2019 Analog Devices, Inc. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Modified versions of the software must be conspicuously marked as such.
# - This software is licensed solely and exclusively for use with
#   processors/products manufactured by or for Analog Devices, Inc.
# - This software may not be combined or merged with other code in any manner
#   that would cause the software to become subject to terms and conditions
#    which differ from those listed here.
# - Neither the name of Analog Devices, Inc. nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
# - The use of this software may or may not infringe the patent rights of one
#   or more patent holders. This license does not release you from the
#   requirement that you obtain separate licenses from these patent holders
#   to use this software.
#
# THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES, INC. AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# NON-INFRINGEMENT, TITLE, MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ANALOG DEVICES, INC. OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, PUNITIVE OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# DAMAGES ARISING OUT OF CLAIMS OF INTELLECTUAL PROPERTY RIGHTS INFRINGEMENT;
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# 2019-01-10-7CBSD SLA
# -----------------------------------------------------------------------


'''
Simulation of some of the AD7124's filters.
This program QUALITATIVELY derives a filter of a type similar to that
used in the AD7124 family of ADCs, that is, it is not bit-accurate, refer
to the datasheet for guaranteed specifications.

Tested with Python 3.7, Anaconda distribution

'''

from numpy import min, max, convolve, random, average, ones, zeros, amax, log
import numpy as np
from scipy import linspace, fft
from scipy import signal
from scipy.signal import lti, step
from matplotlib import pyplot as plt

plot_sinc4 = True

# Base sample rate in high-power mode, From AD7124 datasheet
f0 = 19200

# Calculate SINC1 oversample ratios for 50, 60Hz
osr50 = int(f0/50)
osr60 = int(f0/60)

# Create "boxcar" SINC1 filters
sinc1_50 = np.ones(osr50)
sinc1_60 = np.ones(osr60)

# Calculate higher order filters
sinc2_50 = np.convolve(sinc1_50, sinc1_50)
sinc3_50 = np.convolve(sinc2_50, sinc1_50)
sinc4_50 = np.convolve(sinc2_50, sinc2_50)

# Here's the filter from datasheet Figure 91,
# SINC4-ish filter with one three zeros at 50Hz, one at 60Hz.
filt_50_60_rej = np.convolve(sinc3_50, sinc1_60)

# Normalize to unity gain by dividing by sum of all taps
sinc1_50 /= np.sum(sinc1_50)
sinc1_60 /= np.sum(sinc1_60)
sinc2_50 /= np.sum(sinc2_50)
sinc3_50 /= np.sum(sinc3_50)
sinc4_50 /= np.sum(sinc4_50)
filt_50_60_rej /= np.sum(filt_50_60_rej)


# freqz: Compute the frequency response of a digital filter.
# Older versions of SicPy return w as radians / sample, newer take an optional
# sample rate argument (fs). Computing frequencies (freqs)
# manually for backwards compatibility.

w, h = signal.freqz(filt_50_60_rej, 1, worN=16385, whole=False) #, fs=f0)
freqs = w * f0/(2.0*np.pi)
hmax = abs(max(h)) #Normalize to unity
response_dB = 20.0 * np.log10(abs(h)/hmax)


plt.figure(1)
plt.title('50Hz SINC1,2,4, and 50/60Hz SINC4 impulse responses')
plt.ylabel('tap val.')
plt.plot(sinc1_50)
plt.plot(sinc2_50)
plt.plot(sinc4_50)
plt.plot(filt_50_60_rej)
plt.xlabel('tap number')
plt.xlim(left=-100, right= 1.1* len(filt_50_60_rej))
plt.grid()

plt.figure(2)
plt.plot(freqs, response_dB, zorder=1)
plt.title('50/60Hz reject filter response')
plt.xlabel('Frequency')
plt.ylabel('Rejection')
plt.axis([0, 150, -120, 1])
plt.show()
