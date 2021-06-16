#
# Copyright (c) 2019 Analog Devices Inc.
#
# This file is part of libm2k
# (see http://www.github.com/analogdevicesinc/libm2k).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

# This example assumes the following connections:
# W1 -> 1+
# W2 -> 2+
# GND -> 1-
# GND -> 2-
#
# The application will generate a sinewave on W1 and a noise density on W2.
# The signal is fed back into the analog input
# and the voltage values are displayed on the screen

import libm2k
import matplotlib.pyplot as plt
import time
import numpy as np
import signal_chain_functions as scf

ctx=libm2k.m2kOpen("ip:192.168.2.1") # Explicitly call out default IP address
                                     # (avoids conflict with a second m2k set to a different address)
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
ain.setSampleRate(1000000)
ain.setRange(0,-10,10)
ain.setRange(1,-10,10)

### uncomment the following block to enable triggering
#trig.setAnalogSource(0) # Channel 0 as source
#trig.setAnalogCondition(0,libm2k.RISING_EDGE_ANALOG)
#trig.setAnalogLevel(0,0.5)  # Set trigger level at 0.5
#trig.setAnalogDelay(0) # Trigger is centered
#trig.setAnalogMode(1, libm2k.ANALOG)

aout.setSampleRate(0, 75000)
aout.setSampleRate(1, 75000)
aout.enableChannel(0, True)
aout.enableChannel(1, True)

n = 8192
x=np.linspace(-np.pi,np.pi,n)
#buffer1=np.linspace(-2.0,2.00,n)
buffer1 = np.sin(x)

#create some "bands" of noise
bands = np.concatenate((np.ones(n//16),np.zeros(n//16),
                        np.ones(n//16), np.zeros(n//16),
                        np.ones(n//16),np.zeros(n//16),
                        np.ones(n//16), np.zeros(n//16)))*1000e-6 # 1mV/rootHz
bands[0] = 0.0 # Set DC content to zero
buffer2=scf.time_points_from_freq(bands, fs=75000, density=True)
buffer = [buffer1, buffer2]

aout.setCyclic(True)
aout.push(buffer)

for i in range(1): # gets n triggered samples then quits
    ns = 32768
    data = ain.getSamples(ns)
    plt.figure(1)
    plt.plot(data[0])
    plt.plot(data[1])
    plt.show()
    plt.figure(1)
    my_window = np.blackman(ns)
    my_window /= np.sum(my_window) # Normalize to unity gain

    win_data = data[0]-np.average(data[0]) # remove DC
    win_data = win_data*my_window # Window
    spectrum=20*np.log10(np.abs(np.fft.fft(win_data)))

    plt.plot(spectrum)
    plt.show()
    time.sleep(0.1)

time.sleep(1)
print ("Pausing with noise output still running:")
x=input("Press any key to disable output and continue...")
libm2k.contextClose(ctx)
