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
# 2021-05-22
# -----------------------------------------------------------------------

# First, import goodies from standard libraries
import numpy as np
from matplotlib import pyplot as plt
from scipy import signal


# A function to fold up a noise spectrum, showing the effects of aliasing.
# Returns individual folded Nyquist zones, as well as the RMS sums of the folded zones.
def fold_spectrum(unfolded_spectrum, points_per_zone, num_zones):
    verbose = 0
    zonesign = 1
    folded_spectrum = [[0 for i in range(points_per_zone)] for j in range(num_zones)] #initialize array
    # This section slices up the unfolded spectrum, flipping for even Nyquist zones.
    for i in range(0, num_zones):
        if(zonesign == 1):
            folded_spectrum[i] = unfolded_spectrum[points_per_zone*(i):points_per_zone*(i+1) -1:1]
            zonesign = -1
            if(verbose == 1):
                print(str(i) + " " +str(points_per_zone*(i)) + " " + str(points_per_zone*(i+1)-1))
        else:
            folded_spectrum[i] = unfolded_spectrum[points_per_zone*(i+1)-1 : points_per_zone*(i) : -1]
            zonesign = 1
            if(verbose == 1):
                print(str(i) + " " +str(points_per_zone*(i+1)-1) + " " + str(points_per_zone*(i)))
    # Now RMS sum corresponding points from each zone
    rms_sum = [0 for i in range(points_per_zone)]
    for i in range(0, num_zones): # First, square noise densities of each zone, then add
        for j in range(0, points_per_zone-1):
            rms_sum[j] += folded_spectrum[i][j] ** 2

    for j in range(0, points_per_zone): # Then take the square root of each element
        rms_sum[j] = rms_sum[j] ** 0.5
    return folded_spectrum, rms_sum


# Function to integrate a power-spectral-density
# The last element represents the total integrated noise
def integrate_psd(psd, bw):
    integral_of_psd_squared = np.zeros(len(psd))
    integrated_psd = np.zeros(len(psd))
    integral_of_psd_squared[0] = psd[0]**2.0

    for i in range(1, len(psd)):
        integral_of_psd_squared[i] += integral_of_psd_squared[i-1] + psd[i-1] ** 2
        integrated_psd[i] += integral_of_psd_squared[i]**0.5
    integrated_psd *= bw**0.5
    return integrated_psd

# Equivalent noise bandwidth of an arbitrary filter, given
# frequency response magnitude and bandwidth per point
def arb_enbw(fresp, bw):
    integral_of_fresp_sqared = np.zeros(len(fresp))
    integral_of_fresp_sqared[0] = fresp[0]**2.0
    for i in range(1, len(fresp)):
        integral_of_fresp_sqared[i] += integral_of_fresp_sqared[i-1] + fresp[i-1] ** 2
    return integral_of_fresp_sqared[len(integral_of_fresp_sqared)-1]*bw

# Equivalent noise bandwidth of a FIR filter from filter taps
# Bandwidth implied by sample rate
def fir_enbw_from_taps(taps):
    return len(taps) * np.sum(np.square(taps)) / np.sum(taps)**2

# Magnitude spectrum of an FIR, points per coefficient
def freqz_by_fft(filter_coeffs, points_per_coeff):
    num_coeffs = len(filter_coeffs)
    fftlength = num_coeffs * points_per_coeff
    resp = abs(np.fft.fft(np.concatenate((filter_coeffs, np.zeros(fftlength - num_coeffs))))) # filter and a bunch more zeros
    return resp

# Magnitude spectrum of an FIR, in terms of total number of points (more similar to freqz)
def freqz_by_fft_numpoints(filter_coeffs, numpoints):
    num_coeffs = len(filter_coeffs)
    if numpoints < num_coeffs:
        print("freqz_by_fft_numpoints: numpoints must be greater than # filter coefficients")
        return []
    fftlength = numpoints
    resp = abs(np.fft.fft(np.concatenate((filter_coeffs, np.zeros(fftlength - num_coeffs))))) # filter and a bunch more zeros
    return resp

# Upsample an array and stuff zeros between data points.
# Upsample_factor is the total number of output points per
# input point (that is, the number of zeros stuffed is
# upsample_factor-1)
def upsample_zero_stuff(data, upsample_factor):
    # Starting with zeros makes things easy :)
    upsample_data = np.zeros(upsample_factor * len(data))
    for i in range (0, len(data)):
        upsample_data[upsample_factor*i] = data[i]
    return upsample_data

def downsample(data, downsample_factor):
    # Starting with zeros makes things easy :)
    downsample_data = np.zeros(len(data) / downsample_factor)
    for i in range (0, len(downsample_data)):
        downsample_data[i] = data[i * downsample_factor]
    return downsample_data

#freq=(np.random.normal(loc=0.0, scale=1, size=8))

# Generate time series from half-spectrum. DC in first element.
# Output length is 2x input length
def time_points_from_freq(freq, fs=1, density=False): #DC at element zero,
    N=len(freq)
    randomphase_pos = np.ones(N-1, dtype=np.complex)*np.exp(1j*np.random.uniform(0.0, 2.0*np.pi, N-1))
    randomphase_neg = np.flip(np.conjugate(randomphase_pos))
    randomphase_full = np.concatenate(([1],randomphase_pos,[1], randomphase_neg))
    r_spectrum_full = np.concatenate((freq, np.roll(np.flip(freq), 1)))
    r_spectrum_randomphase = r_spectrum_full * randomphase_full
    r_time_full = np.fft.ifft(r_spectrum_randomphase)
#    print("RMS imaginary component: ", np.std(np.imag(r_time_full)), " Should be close to nothing")
    if (density == True):
        r_time_full *= N*np.sqrt(fs/(N)) #Note that this N is "predivided" by 2
    return(np.real(r_time_full))

def linecount(fname): # A handy functon to count lines in a file.
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


if ((__name__ == "__main__") and (True)):
    fignum = 1
    #fold_spectrum(unfolded_spectrum, points_per_zone, num_zones)
    ppz = 64
    n_z = 8
    u_s = np.ones(ppz * n_z)
    f_s, rms_s = fold_spectrum(u_s, ppz, n_z)




