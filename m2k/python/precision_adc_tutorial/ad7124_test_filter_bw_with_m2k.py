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

import adi
import libm2k
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import sys
from time import sleep
from signal_chain_functions import *

aout_sr = 75000
ain_sr = 1000000


ctx=libm2k.m2kOpen("ip:192.168.2.1") # Explicitly call out default IP address
if ctx is None:
    print("Connection Error: No ADALM2000 device available/connected to your PC.")
    exit(1)

ctx.calibrateADC()
ctx.calibrateDAC()

ain=ctx.getAnalogIn()
aout=ctx.getAnalogOut()
trig=ain.getTrigger()

ain.enableChannel(0,True)
ain.enableChannel(1,True)
ain.setSampleRate(ain_sr)
ain.setRange(0,-10,10)
ain.setRange(1,-10,10)

aout.setSampleRate(0, aout_sr)
aout.setSampleRate(1, aout_sr)
aout.enableChannel(0, True)
aout.enableChannel(1, True)

n = 2**18 # 256k points, half a meg time record
x=np.linspace(-np.pi,np.pi,n)
#buffer1=np.linspace(-2.0,2.00,n)
buffer1 = np.sin(x)

#create 1/8 of a Nyquist zone "band" of noise, about 4.7kHz at 75ksps
en =  1000e-6
bands = np.concatenate((np.ones(n//8), np.zeros(7*n//8)))*en
bands[0] = 0.0 # Set DC content to zero
buffer2=time_points_from_freq(bands, fs=aout_sr, density=True)
buffer2 += 1.25 # Try DC coupling...

buffer = [buffer1, buffer2]

aout.setCyclic(True)
aout.push(buffer)
sleep(3.0)

# Set up AD7124

# Set a default ip address if none given as a command line argument
# hardcoded_ip = "ip:192.168.0.235" # Example if you want to hardcode a different address
#hardcoded_ip = "ip:localhost" # Default to localhost if no argument given
hardcoded_ip = "ip:analog.local"
my_ip = sys.argv[1] if len(sys.argv) >= 2 else hardcoded_ip

# Establish connection to the AD7124
my_ad7124 = adi.ad7124(uri=my_ip)
# Set channel. Buffered receive only supports one channel
ad_channel = 0

sc = my_ad7124.scale_available
my_ad7124.channel[ad_channel].scale = sc[-1]  # get highest range
print(my_ad7124.channel[ad_channel].scale)
scale = my_ad7124.channel[ad_channel].scale
my_ad7124.rx_output_type = "SI"

my_ad7124.sample_rate = 128  # sets sample rate for all channels
my_ad7124.rx_enabled_channels = [ad_channel]
my_ad7124.rx_buffer_size = 1024
my_ad7124._ctx.set_timeout(100000)
nbufs=1 # number of buffers

for i in range(nbufs):
    data = my_ad7124.rx()
    plt.plot(data)
    plt.title('AD7124, G=1, 128sps')
    plt.ylabel('Volts')
    plt.xlabel("Sample Number")
    plt.show()

print("total AD7124 output noise: ", np.std(data))

del my_ad7124 # Clean up

x=input("press any key to continue...")

libm2k.contextClose(ctx)

#print(data)
