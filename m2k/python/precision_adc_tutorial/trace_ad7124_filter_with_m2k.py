# Copyright (C) 2019 Analog Devices, Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#     - Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     - Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
#     - Neither the name of Analog Devices, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#     - The use of this software may or may not infringe the patent rights
#       of one or more patent holders.  This license does not release you
#       from the requirement that you obtain separate licenses from these
#       patent holders to use this software.
#     - Use of the software either in source or binary form, must be run
#       on or directly connected to an Analog Devices Inc. component.
#
# THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED.
#
# IN NO EVENT SHALL ANALOG DEVICES BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, INTELLECTUAL PROPERTY
# RIGHTS, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys, os
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import libm2k
import math
#sys.path.insert(0, "/home/cristinasuteu/pyadi-iio")
import adi
from time import sleep

available_sample_rates= [750, 7500, 75000, 750000, 7500000, 75000000]
max_rate = available_sample_rates[-1] # last sample rate = max rate
min_nr_of_points=10
max_buffer_size = 500000


def get_best_ratio(ratio):

    max_it = max_buffer_size/ratio
    best_ratio = ratio
    best_fract = 1

    for i in range(1, int(max_it)):
        new_ratio = i*ratio
        (new_fract, integral) = math.modf(new_ratio)
        if new_fract < best_fract:
            best_fract = new_fract
            best_ratio = new_ratio
        if new_fract == 0:
            break

    return best_ratio, best_fract


def get_samples_count(rate, frequency):

    ratio = rate/frequency
    if ratio < min_nr_of_points and rate < max_rate:
        return 0
    if ratio < 2:
        return 0

    ratio, fract = get_best_ratio(ratio)
    # ratio = number of periods in buffer
    # fract = what is left over - error

    size = int(ratio)
    while size & 0x03:
        size = size << 1
    while size < 1024:
        size = size << 1
    return size


def get_optimal_sample_rate(frequency):
    for rate in available_sample_rates:
        buf_size = get_samples_count(rate,frequency)
        if buf_size:
            return rate


def sine_buffer_generator(frequency, amplitude, offset, phase):

    buffer = []

    sample_rate = get_optimal_sample_rate(frequency)
    nr_of_samples = get_samples_count(sample_rate, frequency)
    samples_per_period = sample_rate / frequency
    phase_in_samples = ((phase/360) * samples_per_period)

    print("sample_rate:", sample_rate)
    print("number_of_samples", nr_of_samples)
    print("samples_per_period", samples_per_period)
    print("phase_in_samples", phase_in_samples)

    for i in range(nr_of_samples):
        buffer.append(offset + amplitude * (math.sin(((i + phase_in_samples)/samples_per_period) * 2*math.pi) ))

    return sample_rate, buffer


# Set up ADALM2000
def setup_m2k(m2k_backend = None):
    print("Setting up M2K...")
    context = libm2k.m2kOpen(m2k_backend)
    context.calibrateADC()
    context.calibrateDAC()
    siggen = context.getAnalogOut()
    input(" M2K Connected. Calibration done. \n  Press any key to start. \n")
    return context, siggen


def send_sinewave(siggen, frequency):

    samp0, buffer0 = sine_buffer_generator(frequency, 1, 1.25, 0)  # Parameters : Frequency, Amplitude, Offset, Phase
    siggen.enableChannel(0, True)
    siggen.setSampleRate(0, samp0)
    siggen.push(0, buffer0)


def m2k_close(context, siggen):

    siggen.stop()
    libm2k.contextClose(context)


# Set up AD7124
def setup_ad7124(my_ip):

    ad7124 = adi.ad7124(uri=my_ip)  # IP  Address for RaspberryPi Host
    print("connected to ad7124", ad7124)
    ad_channel = 0

    sc = ad7124.scale_available

    ad7124.channel[ad_channel].scale = sc[-1]  # get highest range
    ad7124.rx_output_type = "SI"

    ad7124.sample_rate = 128  # sets sample rate for all channels
    ad7124.rx_enabled_channels = [ad_channel]
    ad7124.rx_buffer_size = 1024  # sets buffer size
    ad7124._ctx.set_timeout(1000000)
    print("ADC Set up. Gathering data ...")
    return ad7124


def capture_data(ad7124):  # Let's move the plotting out of this routine
    captured_data = ad7124.rx()  # Should this append buffers? Right now this overwrights...
    return captured_data


# "main" program

# Set a default ip address if none given as a command line argument
# hardcoded_ip = "ip:192.168.0.235" # Example if you want to hardcode a different address
hardcoded_ip = "ip:localhost" # Default to localhost if no argument given
my_ip = sys.argv[1] if len(sys.argv) >= 2 else hardcoded_ip

plt_time_domain = True  # Super useful for debugging, but time domain plot gets messy if you

n_buff = 1 # number of buffers
# Default to network backend, default ip. USB context not working on Kuiper Linux.
ctx, my_siggen = setup_m2k("ip:192.168.2.1")
my_ad7124 = setup_ad7124(my_ip)
response = []

if plt_time_domain:
    plt.figure(1)
    plt.title('AD7124, G=1, 128sps')
    plt.ylabel('Volts')
    plt.xlabel("Sample Number")

freqs = np.linspace(1, 20, 10, endpoint=True)

for freq in freqs:
    print("testing ", freq, " Hz")
    send_sinewave(my_siggen, freq)
    sleep(5.0)
    data = capture_data(my_ad7124)
    response.append(np.std(data))  # Take RMS value of captured data
    if plt_time_domain:
        plt.plot(data)
        plt.show()
    capture_data(my_ad7124)  # Experiment - do we need to flush?? Was seeing some weird artifacts.

print("\n Response \n")
print(response)

response_dB = 20.0 * np.log10(response/np.sqrt(2))
print("\n Response [dB] \n")
print(response_dB)
plt.figure(2)
plt.plot(freqs, response_dB)
plt.title('AD7124 filter response')
plt.ylabel('attenuation')
plt.xlabel("frequency")
plt.show()
m2k_close(ctx, my_siggen)
del my_ad7124


#main()

