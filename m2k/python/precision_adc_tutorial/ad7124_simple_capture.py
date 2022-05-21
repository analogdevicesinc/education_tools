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

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import sys

# Set up AD7124

# Set a default ip address if none given as a command line argument
# hardcoded_ip = "ip:192.168.0.235" # Example if you want to hardcode a different address
hardcoded_ip = "ip:analog.local" # Default to analog.local if no argument given
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
n=1 # number of buffers

for i in range(n):
    data = np.asarray(my_ad7124.rx())*1000000.0
    plt.plot(data)
    plt.title('AD7124, G=1, 128sps', fontsize=28)
    plt.ylabel('Microvolts', fontsize=28)
    plt.xlabel("Sample Number", fontsize=28)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.show()

del my_ad7124 # Clean up

#print(data)
